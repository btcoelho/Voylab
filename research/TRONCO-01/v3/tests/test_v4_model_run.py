"""Corrida de modelos na V4 (§15): retoma sem chamadas duplicadas, falhas de execução separadas das do modelo, chave nunca
registada, recusa quando o pré-registo congelado não coincide. Sem chamadas reais à API."""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

V3 = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(V3), str(V3 / "pilot"), str(V3 / "instrument")]
import pilot_harness as H  # noqa: E402
import run_v4_models as R  # noqa: E402
from anthropic_backend import AnthropicBackend, ExecutionError  # noqa: E402


class Scripted(H.Backend):
    """Valid but naive: queries q1, commits 'undetermined' with all cards false, keeps. Counts calls; can fail at call k."""
    name = "fake:scripted"

    def __init__(self, fail_at=None):
        self.calls, self.fail_at = 0, fail_at

    def generate(self, system, user, schema, state=None):
        self.calls += 1
        if self.fail_at is not None and self.calls == self.fail_at:
            raise ExecutionError("simulated interruption")
        if "orçamento restante 1" in user:
            return '{"action":"query","query_id":"q1"}'
        if "CONSULTAS DISPONÍVEIS" in user:
            ids = [l.split(" (")[0][2:] for l in user.splitlines() if l.startswith("- ") and " (" in l and "Output depends" in l]
            return json.dumps({"action": "commit", "verdict": "undetermined", "admissible_cards": {i: False for i in ids},
                               "predictions": {"1": "0", "2": "0", "3": "0", "4": "0"}})
        return '{"action":"keep"}'


class Resume(unittest.TestCase):
    def test_interrupted_run_resumes_without_duplicate_calls(self):
        with tempfile.TemporaryDirectory() as d:
            ref = R.run(Path(d) / "ref", Scripted(), limit=6)
            total = ref["fresh_calls_this_session"]
            self.assertGreater(total, 6)
            b1 = Scripted(fail_at=8)                     # dies in the middle of an episode
            with self.assertRaises(ExecutionError):
                R.run(Path(d) / "run", b1, limit=6)
            b2 = Scripted()
            res = R.run(Path(d) / "run", b2, limit=6)
            self.assertEqual((b1.calls - 1) + b2.calls, total)   # the failed call never produced an answer
            a = [json.loads(l) for l in (Path(d) / "ref" / "episodes.jsonl").read_text().splitlines()]
            b = [json.loads(l) for l in (Path(d) / "run" / "episodes.jsonl").read_text().splitlines()]
            self.assertEqual([x["result"] for x in a], [x["result"] for x in b])
            self.assertEqual(res["episodes"], 6)
            keys = [json.loads(l)["key"] for l in (Path(d) / "run" / "calls.jsonl").read_text().splitlines()]
            self.assertEqual(len(keys), len(set(keys)))

    def test_only_development_worlds(self):
        ws = R.worlds()
        self.assertEqual(len(ws), 225)
        self.assertTrue(all(int(w["world_id"].split("-")[1]) in R.DEV_SEED_RANGE for w in ws))


class Resp:
    def __init__(self, status, body=None):
        self.status_code, self._b, self.headers = status, body or {}, {"request-id": "req_test"}

    def json(self):
        return self._b


class Session:
    def __init__(self, seq):
        self.seq, self.seen = list(seq), []

    def post(self, url, headers, data, timeout, verify):
        self.seen.append((headers, json.loads(data)))
        return self.seq.pop(0)


OK = Resp(200, {"model": "claude-test-served", "stop_reason": "end_turn", "usage": {"input_tokens": 3, "output_tokens": 2},
                "content": [{"type": "text", "text": '{"action":"keep"}'}]})


class Backend(unittest.TestCase):
    @mock.patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test-SECRET"})
    def test_retryable_errors_are_execution_failures_and_key_is_never_recorded(self):
        s = Session([Resp(529), Resp(429), OK])
        b = AnthropicBackend("claude-x", session=s, sleep=lambda _: None)
        out = b.generate("sys", "user", {})
        self.assertEqual(out, '{"action":"keep"}')
        self.assertEqual([e["status"] for e in b.execution_log], [529, 429])
        self.assertEqual(b.last_meta["model_served"], "claude-test-served")
        self.assertEqual(s.seen[0][1]["temperature"], 0.0)
        blob = json.dumps([b.execution_log, b.last_meta, b.name])
        self.assertNotIn("SECRET", blob)

    @mock.patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"})
    def test_configuration_error_stops_the_run(self):
        b = AnthropicBackend("claude-x", session=Session([Resp(400)]), sleep=lambda _: None)
        with self.assertRaises(ExecutionError):
            b.generate("s", "u", {})

    def test_missing_key_stops_before_any_request(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            s = Session([OK])
            with self.assertRaises(ExecutionError):
                AnthropicBackend("claude-x", session=s).generate("s", "u", {})
            self.assertEqual(s.seen, [])


class DeepSeek(unittest.TestCase):
    OKD = Resp(200, {"model": "deepseek-served", "id": "r1", "usage": {"prompt_tokens": 3},
                     "choices": [{"finish_reason": "stop", "message": {"content": '{"action":"keep"}', "reasoning_content": "x"}}]})

    @mock.patch.dict(os.environ, {"DEEPSEEK_API_KEY": "sk-test-SECRET"})
    def test_retry_content_only_and_key_never_recorded(self):
        from deepseek_backend import DeepSeekBackend
        s = Session([Resp(503), self.OKD])
        b = DeepSeekBackend("deepseek-x", session=s, sleep=lambda _: None)
        self.assertEqual(b.generate("sys", "user", {}), '{"action":"keep"}')
        self.assertEqual(b.last_meta["model_served"], "deepseek-served")
        self.assertTrue(b.last_meta["reasoning_present"])
        self.assertEqual(s.seen[0][1]["messages"][0], {"role": "system", "content": "sys"})
        self.assertEqual(s.seen[0][1]["temperature"], 0.0)
        self.assertNotIn("SECRET", json.dumps([b.execution_log, b.last_meta, b.name]))

    def test_missing_key_and_fatal_status(self):
        from deepseek_backend import DeepSeekBackend
        with mock.patch.dict(os.environ, {}, clear=True):
            s = Session([self.OKD])
            with self.assertRaises(ExecutionError):
                DeepSeekBackend("d", session=s).generate("s", "u", {})
            self.assertEqual(s.seen, [])
        with mock.patch.dict(os.environ, {"DEEPSEEK_API_KEY": "k"}):
            with self.assertRaises(ExecutionError):
                DeepSeekBackend("d", session=Session([Resp(401)]), sleep=lambda _: None).generate("s", "u", {})


class Frozen(unittest.TestCase):
    def test_refuses_when_section15_or_model_differ(self):
        p = R.FROZEN_DIR / R.PROVIDERS["deepseek_v32"]
        if not p.exists():
            self.skipTest("not frozen yet")
        f = json.loads(p.read_text())
        R.check_frozen(f["model_requested"], "deepseek_v32")            # passes as is
        with self.assertRaises(SystemExit):
            R.check_frozen("other-model", "deepseek_v32")
        with mock.patch.object(R, "section", lambda n=15: "changed"):
            with self.assertRaises(SystemExit):
                R.check_frozen(f["model_requested"], "deepseek_v32")


if __name__ == "__main__":
    unittest.main()
