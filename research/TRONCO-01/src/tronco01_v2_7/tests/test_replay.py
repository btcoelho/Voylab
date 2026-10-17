from pathlib import Path
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
import replay


class HistoricalReplayTests(unittest.TestCase):
    def test_replay_reconstructs_historical_counts_without_model(self):
        result=replay.replay(HERE.parent/"fixtures/v23")
        self.assertEqual(result["new_model_calls"],0)
        self.assertEqual(result["summary"]["generation_calls"],19)
        self.assertEqual(result["summary"]["malformed_at_token_limit_without_eos"],4)
        self.assertEqual(result["summary"]["legal_reports"],3)
        self.assertEqual(result["summary"]["illegal_decoded_actions"],12)
        self.assertEqual(result["summary"]["accepted_queries"],0)
        self.assertEqual(result["summary"]["joint_successes"],0)

    def test_every_initial_state_has_an_immediate_correct_report(self):
        schedule=replay.load_jsonl(HERE.parent/"fixtures/v23/public_schedule.jsonl")
        for item in schedule:
            state=item["public_state"]; truth=replay.labels(state)
            report={"action":"report","verdict":truth["verdict"],
                "candidate_model_codes":truth["candidates"],"diagnosis":truth["diagnosis"],
                "sufficiency":truth["sufficiency"],
                "evidence_ids":[x["id"] for x in state["observations"]],
                "location":{"feature":"none","values":[]}}
            with self.subTest(episode=item["episode_id"]):
                self.assertTrue(replay.score(state,report)["joint_success"])


if __name__=="__main__": unittest.main()
