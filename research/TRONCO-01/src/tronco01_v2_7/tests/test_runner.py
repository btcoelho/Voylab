import hashlib
import json
import hashlib
from pathlib import Path
import sys
import shutil
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import harness
import model_backend
import replay
import trial_runner
import runtime_environment


class TrialRunnerTests(unittest.TestCase):
    def state(self):
        return {"candidate_models": [
            {"id": "A", "statement": "Output depends only on glyph.", "table": {"g0": "0", "g1": "1"}},
            {"id": "B", "statement": "Output depends only on setting.", "table": {"s0": "0", "s1": "1"}},
            {"id": "C", "statement": "Output depends on glyph and phase.",
             "table": {"g0|t0": "0", "g0|t1": "1", "g1|t0": "1", "g1|t1": "0"}}],
            "observations": [], "query_menu": [], "remaining_query_budget": 0,
            "working_model": {"id": "A", "statement": "Output depends only on glyph.",
                              "table": {"g0": "0", "g1": "1"}}}

    def correct_empty_report(self):
        return {"action": "report", "verdict": "undetermined", "candidate_model_codes": ["A", "B", "C"],
                "diagnosis": "ambiguous", "sufficiency": "no_observations", "evidence_ids": [],
                "location": {"feature": "none", "values": []}}

    def test_runner_scorer_distinguishes_fixed_correct_and_incorrect_answers(self):
        state = self.state()
        good = trial_runner.apply_scientific_action(state, self.correct_empty_report())
        wrong = dict(self.correct_empty_report(), verdict="supported")
        bad = trial_runner.apply_scientific_action(state, wrong)
        self.assertTrue(good["accepted"] and good["evaluation"]["joint_success"])
        self.assertTrue(bad["accepted"])
        self.assertFalse(bad["evaluation"]["joint_success"])
        self.assertFalse(trial_runner.apply_scientific_action(
            state, {"action": "query", "query_id": "q0"})["accepted"])

    def test_independent_scorer_accepts_expected_reports_for_all_ten_public_cases(self):
        schedule = trial_runner.load_schedule(Path(__file__).resolve().parents[1] / "development_schedule.jsonl")
        for item in schedule:
            state = item["public_state"]
            labels = replay.labels(state)
            rows = state["observations"]
            if labels["verdict"] == "supported":
                evidence = [row["id"] for row in rows]
            elif labels["verdict"] == "rejected":
                working = next(c for c in state["candidate_models"] if c["id"] == state["working_model"]["id"])
                evidence = [next(row["id"] for row in rows if not replay.prediction(working, row))]
            else:
                evidence = []
            action = {"action": "report", "verdict": labels["verdict"],
                      "candidate_model_codes": labels["candidates"], "diagnosis": labels["diagnosis"],
                      "sufficiency": labels["sufficiency"], "evidence_ids": evidence,
                      "location": {"feature": "none", "values": []}}
            with self.subTest(episode=item["episode_id"]):
                result = trial_runner.apply_scientific_action(state, action)
                self.assertTrue(result["accepted"])
                self.assertTrue(result["evaluation"]["joint_success"])
                corrupted = dict(action, verdict="supported" if action["verdict"] != "supported" else "rejected")
                self.assertFalse(trial_runner.apply_scientific_action(state, corrupted)["evaluation"]["joint_success"])

    def test_same_harness_runner_records_eos_and_resumes_without_extra_call(self):
        root = Path(tempfile.mkdtemp())
        state = self.state()
        schedule = [{"episode_id": "fixed_01", "public_state": state}]
        prereg_hash = "b" * 64
        guard = lambda: {"__manifest_status__": "frozen_before_inference",
                         "preregistration_draft.json": prereg_hash}
        calls = []
        def generate(prompt, schema):
            calls.append(prompt)
            return json.dumps(self.correct_empty_report()), {"eos_terminated": True, "backend": "fixed-test-output"}
        args = dict(schedule=schedule, generate=generate, apply=trial_runner.apply_scientific_action,
                    prompt_for=lambda s: json.dumps(s, sort_keys=True),
                    event_path=root / "events.jsonl", outcomes_path=root / "outcomes.json",
                    summary_path=root / "summary.json", generation_guard=guard,
                    max_calls=1, preregistration_sha256=prereg_hash)
        first = harness.execute_trial(**args)
        second = harness.execute_trial(**args)
        events = [json.loads(line) for line in (root / "events.jsonl").read_text().splitlines()]
        generation = next(e for e in events if e["kind"] == "generation")
        self.assertEqual(first["joint_successes"], 1)
        self.assertEqual(second["joint_successes"], 1)
        self.assertEqual(len(calls), 1)
        self.assertTrue(generation["eos_terminated"])

    def test_backend_failure_is_recorded_as_technical_sentinel(self):
        root = Path(tempfile.mkdtemp())
        prereg_hash = "c" * 64
        schedule = [{"episode_id": "fixed_technical", "public_state": self.state()}]
        summary = harness.execute_trial(
            schedule, lambda prompt, schema: (_ for _ in ()).throw(RuntimeError("backend unavailable")),
            trial_runner.apply_scientific_action, lambda state: json.dumps(state),
            root / "events.jsonl", root / "outcomes.json", root / "summary.json",
            generation_guard=lambda: {"__manifest_status__": "frozen_before_inference",
                                      "preregistration_draft.json": prereg_hash},
            max_calls=1, preregistration_sha256=prereg_hash)
        events = [json.loads(line) for line in (root / "events.jsonl").read_text().splitlines()]
        self.assertEqual(summary["technical_failures"], 1)
        self.assertEqual(summary["sentinel_stop_events"], 1)
        self.assertTrue(any(event["kind"] == "generation_error" for event in events))

    def test_draft_status_is_rejected_before_loader_import(self):
        root = Path(tempfile.mkdtemp())
        for name, content in (("model.safetensors", b"weights"), ("tokenizer.json", b"tokenizer"),
                              ("tokenizer_config.json", b"config")):
            (root / name).write_bytes(content)
        prereg_hash = hashlib.sha256(b"draft").hexdigest()
        guard = lambda: {"__manifest_status__": "draft_not_frozen",
                         "preregistration_draft.json": prereg_hash}
        with self.assertRaisesRegex(RuntimeError, "requires a verified frozen_before_inference manifest"):
            model_backend.Qwen25Generator.from_verified_checkpoint(
                root, "0" * 64, "0" * 64, "0" * 64, guard, prereg_hash)

    def test_schedule_loader_keeps_only_the_frozen_public_payload(self):
        root = Path(tempfile.mkdtemp())
        path = root / "schedule.jsonl"
        path.write_text(json.dumps({"episode_id": "e1", "public_state": self.state(), "stratum": "empty"}) + "\n")
        result = trial_runner.load_schedule(path)
        self.assertEqual(set(result[0]), {"episode_id", "public_state"})

    def test_runner_prompt_must_match_manifest_bytes(self):
        root = Path(tempfile.mkdtemp())
        path = root / "SYSTEM_PROMPT.txt"
        path.write_text("frozen prompt")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        prereg = {"experimental_condition": {"system_prompt": "SYSTEM_PROMPT.txt"}}
        self.assertEqual(trial_runner.load_verified_system_prompt(path, prereg, {"SYSTEM_PROMPT.txt": digest}),
                         "frozen prompt")
        path.write_text("changed prompt")
        with self.assertRaises(harness.ResumeIntegrityError):
            trial_runner.load_verified_system_prompt(path, prereg, {"SYSTEM_PROMPT.txt": digest})

    def test_manual_semantic_certificate_and_component_cases(self):
        cards = [
            {"id":"A", "statement":"Output depends only on glyph.", "table":{"g0":"0","g1":"1"}},
            {"id":"B", "statement":"Output depends only on setting.", "table":{"s0":"0","s1":"1"}},
        ]
        state = {"candidate_models":cards, "working_model":cards[0], "query_menu":[], "remaining_query_budget":0,
            "observations":[
                {"id":"o1","input":{"glyph":"g0","setting":"s0","partner":"p0","phase":"t0"},"output":"0"},
                {"id":"o2","input":{"glyph":"g0","setting":"s1","partner":"p0","phase":"t0"},"output":"1"}]}
        rejected = {"action":"report","verdict":"rejected","candidate_model_codes":["B"],
            "diagnosis":"identified","sufficiency":"identity_resolved","evidence_ids":["o2"],
            "location":{"feature":"none","values":[]}}
        cases=[(state,rejected,True),
               (state,dict(rejected,evidence_ids=[]),False),
               (state,dict(rejected,evidence_ids=["o1"]),False),
               (state,dict(rejected,candidate_model_codes=["A"]),False),
               (state,dict(rejected,diagnosis="ambiguous"),False),
               (state,dict(rejected,sufficiency="identity_ambiguous"),False),
               (state,dict(rejected,evidence_ids=["o1","o2"],location={"feature":"setting","values":["s0","s1"]}),True),
               (state,dict(rejected,location={"feature":"setting","values":["s0","s1"]}),False)]
        supporting=json.loads(json.dumps(state)); supporting["working_model"]=cards[1]
        support=dict(rejected,verdict="supported",evidence_ids=["o1","o2"])
        cases += [(supporting,support,True),(supporting,dict(support,evidence_ids=["o1"]),False)]
        for current, action, expected in cases:
            with self.subTest(action=action):
                self.assertEqual(replay.score(current,action)["joint_success"],expected)

    def make_frozen_runner_fixture(self, root):
        package=Path(__file__).resolve().parents[1]
        schedule=root/"development_schedule.jsonl"; prompt=root/"SYSTEM_PROMPT.txt"
        shutil.copy2(package/"development_schedule.jsonl",schedule)
        shutil.copy2(package/"SYSTEM_PROMPT.txt",prompt)
        prereg=json.loads((package/"preregistration_draft.json").read_text(encoding="utf-8"))
        prereg["status"]="frozen_before_inference"; prereg["frozen"]=True
        artifacts={}; external=[]
        contents={".gitattributes":b"attrs", "README.md":b"readme", "added_tokens.json":b"added",
            "config.json":b"config", "generation_config.json":b"gen", "merges.txt":b"merges",
            "model.safetensors":b"weights", "special_tokens_map.json":b"special", "tokenizer.json":b"tok",
            "tokenizer_config.json":b"tokcfg", "vocab.json":b"vocab"}
        for name,data in contents.items():
            file=root/name; file.write_bytes(data); digest=hashlib.sha256(data).hexdigest()
            artifacts[name]=digest; external.append({"path":str(file),"sha256":digest})
        condition=prereg["experimental_condition"]
        condition["checkpoint_artifacts"]=artifacts
        condition["weights_sha256"]=artifacts["model.safetensors"]
        condition["tokenizer_json_sha256"]=artifacts["tokenizer.json"]
        condition["tokenizer_config_sha256"]=artifacts["tokenizer_config.json"]
        prereg["software_environment"]={"python":"test", "transformers":"test", "lm_format_enforcer":"test",
            "unsloth":"test", "torch":"test", "bitsandbytes":"test"}
        prereg_path=root/"preregistration_draft.json"
        prereg_path.write_text(json.dumps(prereg),encoding="utf-8")
        internal=[{"path":name,"sha256":hashlib.sha256((root/name).read_bytes()).hexdigest()}
                  for name in [schedule.name,prompt.name,prereg_path.name]]
        manifest=root/"manifest.json"
        manifest.write_text(json.dumps({"status":"frozen_before_inference","files":internal,"external_files":external}),encoding="utf-8")
        return package,schedule,prompt,prereg_path,manifest,condition,artifacts

    def test_full_trial_runner_with_fixed_outputs_and_failure_policy(self):
        package=Path(__file__).resolve().parents[1]
        schedule_items=replay.load_jsonl(package/"development_schedule.jsonl")
        refs={x["episode_id"]:x["expected"] for x in replay.load_jsonl(package/"development_reference_private.jsonl")}
        reports=[]
        for item in schedule_items:
            ref=refs[item["episode_id"]]; state=item["public_state"]
            reports.append({"action":"report","verdict":ref["verdict"],"candidate_model_codes":ref["candidates"],
                "diagnosis":ref["diagnosis"],"sufficiency":ref["sufficiency"],
                "evidence_ids":[row["id"] for row in state["observations"]],
                "location":{"feature":"none","values":[]}})

        class FixedTokenizer:
            def apply_chat_template(self,messages,tokenize,add_generation_prompt): return json.dumps(messages)
        class FixedBackend:
            tokenizer=FixedTokenizer()
            def __init__(self,outputs): self.outputs=iter(outputs); self.calls=0
            def __call__(self,prompt,schema):
                messages=json.loads(prompt); current=json.loads(messages[1]["content"])
                if "expected" in current or current["query_menu"] or current["remaining_query_budget"]!=0:
                    raise AssertionError("prompt includes private labels or active queries")
                self.calls+=1; value=next(self.outputs)
                if isinstance(value,Exception): raise value
                return value if isinstance(value,str) else json.dumps(value),{"eos_terminated":True}

        def run_case(outputs):
            root=Path(tempfile.mkdtemp()); _,schedule,prompt,prereg,manifest,cond,_=self.make_frozen_runner_fixture(root)
            backend=FixedBackend(outputs); out=root/"run"
            with patch.object(trial_runner,"verify_runtime_environment",return_value={}), \
                 patch.object(model_backend.Qwen25Generator,"from_verified_checkpoint",return_value=backend) as loader:
                summary=trial_runner.run(schedule,prompt,root,manifest,out,cond["weights_sha256"],
                    cond["tokenizer_json_sha256"],cond["tokenizer_config_sha256"],prereg,1)
            summary["fake_calls"]=backend.calls; summary["loader_calls"]=loader.call_count
            return summary

        good=run_case(reports); self.assertEqual(good["joint_successes"],10)
        wrong=[dict(x,verdict="supported" if x["verdict"]!="supported" else "rejected") for x in reports]
        bad=run_case(wrong); self.assertEqual(bad["joint_successes"],0)
        malformed=run_case(["{bad"]+reports[1:])
        self.assertEqual((malformed["model_output_failures"],malformed["episodes_attempted"]),(1,10))
        technical=run_case(reports[:2]+[RuntimeError("controlled outage")]+reports[3:])
        self.assertEqual((technical["technical_failures"],technical["sentinel_stop_events"],technical["fake_calls"]),(1,1,3))

    def test_resume_identity_is_checked_before_model_loader(self):
        root=Path(tempfile.mkdtemp()); _,schedule,prompt,prereg,manifest,cond,_=self.make_frozen_runner_fixture(root)
        out=root/"run"; out.mkdir()
        (out/"events.jsonl").write_text(json.dumps({"sequence":1,"kind":"trial_start","trial_fingerprint":"0"*64})+"\n")
        with patch.object(trial_runner,"verify_runtime_environment",return_value={}), \
             patch.object(model_backend.Qwen25Generator,"from_verified_checkpoint") as loader:
            with self.assertRaises(harness.ResumeIntegrityError):
                trial_runner.run(schedule,prompt,root,manifest,out,cond["weights_sha256"],
                    cond["tokenizer_json_sha256"],cond["tokenizer_config_sha256"],prereg,1)
        loader.assert_not_called()

    def test_runtime_versions_are_a_preregistered_gate(self):
        expected={"python":"3.12.3","transformers":"5.17.0","lm_format_enforcer":"0.11.3",
                  "unsloth":"2026.10.6","torch":"2.14.1+cu132","bitsandbytes":"0.50.2"}
        with patch.object(runtime_environment,"inspect_runtime",return_value=expected.copy()):
            self.assertEqual(runtime_environment.verify_runtime(expected),expected)
        changed=dict(expected,torch="wrong-version")
        with patch.object(runtime_environment,"inspect_runtime",return_value=expected.copy()):
            with self.assertRaisesRegex(RuntimeError,"runtime differs"):
                runtime_environment.verify_runtime(changed)

    def test_checkpoint_extra_or_changed_artifact_is_rejected_before_loader(self):
        root=Path(tempfile.mkdtemp()); model_dir=root/"model"; model_dir.mkdir()
        contents={".gitattributes":b"attrs", "README.md":b"readme", "added_tokens.json":b"added",
            "config.json":b"config", "generation_config.json":b"gen", "merges.txt":b"merges",
            "model.safetensors":b"weights", "special_tokens_map.json":b"special", "tokenizer.json":b"tok",
            "tokenizer_config.json":b"tokcfg", "vocab.json":b"vocab"}
        expected={}
        for name,data in contents.items():
            (model_dir/name).write_bytes(data); expected[name]=hashlib.sha256(data).hexdigest()
        prereg=root/"preregistration_draft.json"; prereg.write_text("draft")
        prereg_hash=hashlib.sha256(prereg.read_bytes()).hexdigest()
        verified={"__manifest_status__":"frozen_before_inference","preregistration_draft.json":prereg_hash}
        for name,digest in expected.items(): verified[f"external:{(model_dir/name).resolve()}"]=digest
        args=(model_dir,expected["model.safetensors"],expected["tokenizer.json"],expected["tokenizer_config.json"],
              lambda:verified,prereg_hash)
        changed=dict(expected); changed["config.json"]="0"*64
        with self.assertRaisesRegex(RuntimeError,"artifact hash mismatch: config.json"):
            model_backend.Qwen25Generator.from_verified_checkpoint(*args,expected_artifact_hashes=changed)
        (model_dir/"unexpected.json").write_text("extra")
        with self.assertRaisesRegex(RuntimeError,"file set differs"):
            model_backend.Qwen25Generator.from_verified_checkpoint(*args,expected_artifact_hashes=expected)


if __name__ == "__main__":
    unittest.main()
