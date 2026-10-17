import json
import hashlib
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import harness
import model_backend

PREREG_HASH = "a" * 64


class HarnessTests(unittest.TestCase):
    def sample_state(self):
        return {"candidate_models":[{"id":"A"}], "observations":[],
                "query_menu":[{"id":"q0","input":{"x":"0"}}],
                "remaining_query_budget":1}

    def report(self):
        return json.dumps({"action":"report","verdict":"undetermined",
            "candidate_model_codes":["A"],"diagnosis":"identified",
            "sufficiency":"no_observations","evidence_ids":[],
            "location":{"feature":"none","values":[]}})

    def frozen_test_guard(self, root, source):
        prereg=root/"preregistration.json"
        prereg.write_text('{"protocol":"test"}')
        prereg_hash=hashlib.sha256(prereg.read_bytes()).hexdigest()
        manifest=root/"manifest.json"
        manifest.write_text(json.dumps({"status":"frozen_before_inference","files":[
            {"path":"schedule.json","sha256":hashlib.sha256(source.read_bytes()).hexdigest()},
            {"path":"preregistration.json","sha256":prereg_hash}]}))
        return harness.FrozenManifestGuard(manifest).verify, prereg_hash

    def test_strict_json_rejects_duplicate_nonfinite_trailing_and_nonobject(self):
        for raw in ('{"a":1,"a":2}','{"x":NaN}','{"x":1} extra','[1]'):
            with self.subTest(raw=raw), self.assertRaises(harness.ModelOutputError):
                harness.strict_json_object(raw)

    def test_schema_allows_semantic_choices_but_scopes_public_ids(self):
        state=self.sample_state()
        harness.validate_action_shape({"action":"query","query_id":"q0"},state)
        harness.validate_action_shape(json.loads(self.report()),state)
        with self.assertRaises(harness.ModelOutputError):
            harness.validate_action_shape({"action":"query","query_id":"q9"},state)

    def test_exhausted_budget_removes_query_action_from_dynamic_schema(self):
        state=self.sample_state(); state["remaining_query_budget"]=0
        schema=harness.public_action_schema(state)
        self.assertEqual(len(schema["oneOf"]),1)
        self.assertEqual(schema["oneOf"][0]["properties"]["action"]["const"],"report")
        with self.assertRaises(harness.ModelOutputError):
            harness.validate_action_shape({"action":"query","query_id":"q0"},state)

    def test_location_values_must_come_from_public_observations(self):
        state=self.sample_state()
        state["observations"]=[
            {"id":"o1","input":{"glyph":"g0"},"output":"0"},
            {"id":"o2","input":{"glyph":"g1"},"output":"1"}]
        action=json.loads(self.report())
        action.update({"verdict":"supported","candidate_model_codes":["A"],
                       "diagnosis":"identified","sufficiency":"identity_resolved",
                       "evidence_ids":["o1","o2"],
                       "location":{"feature":"glyph","values":["g0","g1"]}})
        harness.validate_action_shape(action,state)
        action["location"]["values"]=["g0","invented"]
        with self.assertRaises(harness.ModelOutputError):
            harness.validate_action_shape(action,state)

    def test_duplicate_candidate_evidence_and_location_values_are_rejected(self):
        state=self.sample_state()
        state["candidate_models"].append({"id":"B"})
        state["observations"]=[{"id":"o1","input":{"glyph":"g0"},"output":"0"},
                               {"id":"o2","input":{"glyph":"g1"},"output":"1"}]
        for field, value in (("candidate_model_codes",["A","A"]),
                             ("evidence_ids",["o1","o1"])):
            action=json.loads(self.report())
            action[field]=value
            with self.subTest(field=field), self.assertRaises(harness.ModelOutputError):
                harness.validate_action_shape(action,state)
        action=json.loads(self.report())
        action["location"]={"feature":"glyph","values":["g0","g0"]}
        with self.assertRaises(harness.ModelOutputError):
            harness.validate_action_shape(action,state)

    def test_rejection_feedback_changes_prompt_and_allows_recovery(self):
        state=self.sample_state(); prompts=[]
        path=Path(tempfile.mkdtemp())/"events.jsonl"; journal=harness.Journal(path)
        outputs=iter([json.dumps({"action":"query","query_id":"q0"}),self.report()])
        def gen(p,schema): prompts.append(p); return next(outputs)
        def apply(s,a):
            if a["action"]=="query": return {"accepted":False,"legal_errors":["query service declined action"]}
            return {"accepted":True,"terminal":True,"evaluation":{"joint_success":True}}
        outcome=harness.execute_episode("x1",state,gen,apply,
            lambda s:json.dumps(s,sort_keys=True),journal,lambda:None,max_calls=2)
        self.assertEqual((outcome["status"],outcome["calls"],outcome["rejected_actions"]),
                         ("reported",2,1))
        self.assertNotEqual(prompts[0],prompts[1])
        feedback=json.loads(prompts[1])["action_feedback"]
        self.assertEqual(feedback["messages"],["query service declined action"])
        self.assertNotIn("expected",json.dumps(feedback).lower())

    def test_malformed_output_is_logged_and_not_retried(self):
        path=Path(tempfile.mkdtemp())/"events.jsonl"; journal=harness.Journal(path); calls=[]
        out=harness.execute_episode("x1",self.sample_state(),
            lambda p,schema:(calls.append(p) or "{bad"),lambda s,a:None,
            lambda s:json.dumps(s),journal,lambda:None)
        events=[json.loads(x) for x in path.read_text().splitlines()]
        self.assertEqual((out["status"],out["calls"],len(calls)),("model_output_failure",1,1))
        self.assertEqual(sum(e["kind"]=="raw_action" for e in events),1)

    def test_accepted_query_updates_public_state_and_resets_feedback(self):
        state=self.sample_state()
        state["remaining_query_budget"]=1
        path=Path(tempfile.mkdtemp())/"events.jsonl"; journal=harness.Journal(path)
        query=json.dumps({"action":"query","query_id":"q0"})
        report=json.dumps({"action":"report","verdict":"supported",
            "candidate_model_codes":["A"],"diagnosis":"identified",
            "sufficiency":"identity_resolved","evidence_ids":["o1"],
            "location":{"feature":"none","values":[]}})
        prompts=[]; outputs=iter([query,report])
        def apply(current,action):
            if action["action"]=="query":
                return {"accepted":True,"observation":{"id":"o1","input":{"x":"0"},"output":"1"}}
            return {"accepted":True,"terminal":True,"evaluation":{"joint_success":True}}
        outcome=harness.execute_episode("x1",state,
            lambda p,schema:(prompts.append(p) or next(outputs)),apply,
            lambda s:json.dumps(s,sort_keys=True),journal,lambda:None,max_calls=2)
        self.assertEqual(outcome["status"],"reported")
        self.assertEqual(outcome["queries"],1)
        updated=json.loads(prompts[1])
        self.assertEqual(updated["observations"][0]["id"],"o1")
        self.assertNotIn("action_feedback",updated)

    def test_resume_rejects_interrupted_and_duplicate_episode(self):
        with self.assertRaises(harness.ResumeIntegrityError):
            harness.completed_episodes([{"kind":"episode_start","episode_id":"x1"}],["x1"])
        duplicate=[{"kind":"episode_start","episode_id":"x1"},
            {"kind":"episode_outcome","outcome":{"episode_id":"x1"}},
            {"kind":"episode_start","episode_id":"x1"},
            {"kind":"episode_outcome","outcome":{"episode_id":"x1"}}]
        with self.assertRaises(harness.ResumeIntegrityError):
            harness.completed_episodes(duplicate,["x1"])

    def test_journal_rebuild_fixes_legacy_class_and_sentinel(self):
        events=[{"kind":"episode_start","episode_id":"x1"},
            {"kind":"generation","episode_id":"x1"},
            {"kind":"episode_error","episode_id":"x1","error":"JSONDecodeError(...)"},
            {"kind":"sentinel_stop","reason":"JSONDecodeError(...)"},
            {"kind":"episode_outcome","outcome":{"episode_id":"x1","calls":1,"queries":0,
             "status":"technical_failure","evaluation":{}}}]
        fixed=harness.outcomes_from_journal(events,["x1"])
        summary=harness.summarize(events,fixed,["x1"])
        self.assertEqual(fixed[0]["status"],"model_output_failure")
        self.assertEqual(summary["sentinel_stop_events"],1)

    def test_rates_are_calculated_for_success_empty_and_failure(self):
        good=[{"episode_id":"x1","status":"reported","calls":1,"queries":0,
               "evaluation":{"joint_success":True}}]
        self.assertEqual(harness.summarize([],good,["x1"])["joint_success_rate_planned"],1.0)
        self.assertIsNone(harness.summarize([],[],["x1"])["joint_success_rate_completed"])
        self.assertIsNone(harness.summarize([],[],["x1"])["joint_success_rate_planned"])

    def test_summary_is_atomic_json(self):
        path=Path(tempfile.mkdtemp())/"summary.json"
        harness.atomic_write_json(path,{"value":1})
        self.assertEqual(json.loads(path.read_text()),{"value":1})
        self.assertFalse(path.with_suffix(".json.tmp").exists())

    def test_frozen_manifest_blocks_changed_source_before_generation(self):
        root=Path(tempfile.mkdtemp()); source=root/"prompt.txt"; source.write_text("frozen")
        manifest=root/"manifest.json"
        manifest.write_text(json.dumps({"status":"frozen_before_inference","files":[{"path":"prompt.txt",
            "sha256":hashlib.sha256(b"frozen").hexdigest()}]}))
        harness.FrozenManifestGuard(manifest).verify()
        source.write_text("changed")
        with self.assertRaises(harness.ResumeIntegrityError):
            harness.FrozenManifestGuard(manifest).verify()

    def test_failed_frozen_gate_makes_zero_generation_calls(self):
        path=Path(tempfile.mkdtemp())/"events.jsonl"; journal=harness.Journal(path)
        calls=[]
        def blocked(): raise RuntimeError("manifest changed")
        outcome=harness.execute_episode("x1",self.sample_state(),
            lambda p,schema:(calls.append(p) or self.report()),
            lambda s,a:{"accepted":True,"terminal":True},
            lambda s:json.dumps(s),journal,blocked)
        self.assertEqual(outcome["status"],"technical_failure")
        self.assertEqual(outcome["calls"],0)
        self.assertEqual(calls,[])

    def test_trial_persists_each_result_and_stops_after_infrastructure_failure(self):
        root=Path(tempfile.mkdtemp())
        schedule=[{"episode_id":"x1","public_state":self.sample_state()},
                  {"episode_id":"x2","public_state":self.sample_state()}]
        report=self.report()
        call=0
        def gen(prompt,schema):
            nonlocal call
            call+=1
            if call==2: raise RuntimeError("backend disconnected")
            return report
        def apply(state,action):
            return {"accepted":True,"terminal":True,"evaluation":{"joint_success":True}}
        test_guard=lambda:{"__manifest_status__":"frozen_before_inference",
                           "preregistration_draft.json":PREREG_HASH}
        summary=harness.execute_trial(schedule,gen,apply,lambda s:json.dumps(s,sort_keys=True),
            root/"events.jsonl",root/"outcomes.json",root/"summary.json",generation_guard=test_guard,
            preregistration_sha256=PREREG_HASH)
        self.assertEqual(summary["episodes_attempted"],2)
        self.assertEqual(summary["technical_failures"],1)
        self.assertEqual(summary["sentinel_stop_events"],1)
        self.assertEqual(summary["joint_successes"],1)
        self.assertEqual(summary["joint_success_rate_planned"],0.5)
        before=(root/"events.jsonl").read_text()
        with self.assertRaises(harness.ResumeIntegrityError):
            harness.execute_trial(schedule,gen,apply,lambda s:json.dumps(s),
                root/"events.jsonl",root/"outcomes.json",root/"summary.json",generation_guard=test_guard,
                preregistration_sha256=PREREG_HASH)
        self.assertEqual((root/"events.jsonl").read_text(),before)

    def test_complete_resume_checks_manifest_and_schedule_identity(self):
        root=Path(tempfile.mkdtemp())
        state=self.sample_state()
        schedule=[{"episode_id":"x1","public_state":state}]
        source=root/"schedule.json"
        source.write_text(json.dumps(schedule))
        guard,prereg_hash=self.frozen_test_guard(root,source)
        calls=[]
        apply=lambda s,a:{"accepted":True,"terminal":True,"evaluation":{"joint_success":True}}
        prompt=lambda s:json.dumps(s,sort_keys=True)
        args=(lambda p,schema:(calls.append(p) or self.report()),apply,prompt,
              root/"events.jsonl",root/"outcomes.json",root/"summary.json")
        harness.execute_trial(schedule,*args,generation_guard=guard,
                              preregistration_sha256=prereg_hash)
        before=len(calls)
        changed=json.loads(json.dumps(schedule))
        changed[0]["public_state"]["remaining_query_budget"]=0
        source.write_text(json.dumps(changed))
        with self.assertRaises(harness.ResumeIntegrityError):
            harness.execute_trial(changed,*args,generation_guard=guard,
                                  preregistration_sha256=prereg_hash)
        self.assertEqual(len(calls),before)

    def test_complete_resume_runs_guard_even_when_schedule_is_unchanged(self):
        root=Path(tempfile.mkdtemp()); state=self.sample_state()
        schedule=[{"episode_id":"x1","public_state":state}]
        source=root/"schedule.json"; source.write_text(json.dumps(schedule))
        guard,prereg_hash=self.frozen_test_guard(root,source); calls=[]
        args=(lambda p,schema:(calls.append(p) or self.report()),
              lambda s,a:{"accepted":True,"terminal":True,"evaluation":{"joint_success":True}},
              lambda s:json.dumps(s),root/"events.jsonl",root/"outcomes.json",root/"summary.json")
        harness.execute_trial(schedule,*args,generation_guard=guard,
                              preregistration_sha256=prereg_hash)
        source.write_text("tampered schedule")
        before=len(calls)
        with self.assertRaises(harness.ResumeIntegrityError):
            harness.execute_trial(schedule,*args,generation_guard=guard,
                                  preregistration_sha256=prereg_hash)
        self.assertEqual(len(calls),before)

    def test_preregistration_hash_must_match_verified_manifest(self):
        root=Path(tempfile.mkdtemp()); source=root/"schedule.json"
        schedule=[{"episode_id":"x1","public_state":self.sample_state()}]
        source.write_text(json.dumps(schedule)); guard,_=self.frozen_test_guard(root,source)
        calls=[]
        with self.assertRaises(harness.ResumeIntegrityError):
            harness.execute_trial(schedule,lambda p,schema:calls.append(p),lambda s,a:{},lambda s:"{}",
                root/"events.jsonl",root/"outcomes.json",root/"summary.json",
                generation_guard=guard,preregistration_sha256=PREREG_HASH)
        self.assertEqual(calls,[])

    def test_draft_manifest_blocks_trial_entry_before_generation(self):
        root=Path(tempfile.mkdtemp())
        prereg=root/"preregistration.json"; prereg.write_text('{"protocol":"draft"}')
        prereg_hash=hashlib.sha256(prereg.read_bytes()).hexdigest()
        manifest=root/"manifest.json"
        manifest.write_text(json.dumps({"status":"draft_not_frozen","files":[
            {"path":"preregistration.json","sha256":prereg_hash}]}))
        calls=[]; state=self.sample_state()
        with self.assertRaisesRegex(harness.ResumeIntegrityError,"not frozen"):
            harness.execute_trial([{"episode_id":"x1","public_state":state}],
                lambda p,schema:calls.append(p),lambda s,a:{},lambda s:"{}",
                root/"events.jsonl",root/"outcomes.json",root/"summary.json",
                harness.FrozenManifestGuard(manifest).verify,preregistration_sha256=prereg_hash)
        self.assertEqual(calls,[])

    def test_declared_external_checkpoint_hash_is_verified_without_loading_it(self):
        root=Path(tempfile.mkdtemp())
        prereg=root/"preregistration.json"; prereg.write_text('{"protocol":"test"}')
        checkpoint=root/"model.safetensors"; checkpoint.write_bytes(b"mock-weights")
        prereg_hash=hashlib.sha256(prereg.read_bytes()).hexdigest()
        checkpoint_hash=hashlib.sha256(checkpoint.read_bytes()).hexdigest()
        manifest=root/"manifest.json"
        manifest.write_text(json.dumps({"status":"frozen_before_inference","files":[{"path":"preregistration.json","sha256":prereg_hash}],
            "external_files":[{"path":str(checkpoint),"sha256":checkpoint_hash}]}))
        guard=harness.FrozenManifestGuard(manifest)
        self.assertIn(f"external:{checkpoint.resolve()}",guard.verify())
        checkpoint.write_bytes(b"changed")
        with self.assertRaises(harness.ResumeIntegrityError):
            guard.verify()

    def test_model_backend_rejects_weight_mismatch_before_importing_loader(self):
        root=Path(tempfile.mkdtemp())
        (root/"model.safetensors").write_bytes(b"mock-weights")
        (root/"tokenizer.json").write_bytes(b"mock-tokenizer")
        (root/"tokenizer_config.json").write_bytes(b"mock-config")
        prereg=root/"preregistration_draft.json"; prereg.write_text('{"protocol":"test"}')
        prereg_hash=hashlib.sha256(prereg.read_bytes()).hexdigest()
        entries=[{"path":x.name,"sha256":hashlib.sha256(x.read_bytes()).hexdigest()}
                 for x in (prereg,)]
        manifest=root/"manifest.json"
        manifest.write_text(json.dumps({"status":"frozen_before_inference","files":entries,
            "external_files":[{"path":str(root/name),"sha256":hashlib.sha256((root/name).read_bytes()).hexdigest()}
                              for name in ("model.safetensors","tokenizer.json","tokenizer_config.json")]}))
        guard=harness.FrozenManifestGuard(manifest).verify
        with self.assertRaisesRegex(RuntimeError,"checkpoint SHA-256"):
            model_backend.Qwen25Generator.from_verified_checkpoint(
                root,"0"*64,hashlib.sha256(b"mock-tokenizer").hexdigest(),
                hashlib.sha256(b"mock-config").hexdigest(),guard,prereg_hash)

    def test_changed_in_memory_schedule_is_blocked_by_journal_fingerprint(self):
        root=Path(tempfile.mkdtemp()); state=self.sample_state()
        schedule=[{"episode_id":"x1","public_state":state}]
        calls=[]
        args=(lambda p,schema:(calls.append(p) or self.report()),
              lambda s,a:{"accepted":True,"terminal":True,"evaluation":{"joint_success":True}},
              lambda s:json.dumps(s),root/"events.jsonl",root/"outcomes.json",root/"summary.json")
        test_guard=lambda:{"__manifest_status__":"frozen_before_inference",
                           "preregistration_draft.json":PREREG_HASH}
        harness.execute_trial(schedule,*args,generation_guard=test_guard,
                              preregistration_sha256=PREREG_HASH)
        changed=json.loads(json.dumps(schedule))
        changed[0]["public_state"]["remaining_query_budget"]=0
        before=len(calls)
        with self.assertRaises(harness.ResumeIntegrityError):
            harness.execute_trial(changed,*args,generation_guard=test_guard,
                                  preregistration_sha256=PREREG_HASH)
        self.assertEqual(len(calls),before)

    def test_missing_preregistration_hash_blocks_before_generation(self):
        root=Path(tempfile.mkdtemp()); calls=[]
        with self.assertRaises(harness.ResumeIntegrityError):
            harness.execute_trial([],lambda p,schema:calls.append(p),lambda s,a:{},lambda s:"{}",
                root/"events.jsonl",root/"outcomes.json",root/"summary.json",generation_guard=lambda:None)
        self.assertEqual(calls,[])


if __name__=="__main__":
    unittest.main()
