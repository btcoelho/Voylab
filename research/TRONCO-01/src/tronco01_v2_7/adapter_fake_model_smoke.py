"""Exercise the v2.7 generator call path with real tokenizer/LMFE and a fake CPU model."""
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import torch
import transformers.tokenization_utils as tokenization_utils
from transformers import AutoTokenizer, PreTrainedTokenizerBase
tokenization_utils.PreTrainedTokenizerBase = PreTrainedTokenizerBase
from harness import public_action_schema
from model_backend import Qwen25Generator, build_chat_prompt

TOKENIZER = Path(os.environ.get("TRONCO_TOKENIZER_PATH", "/home/bcoelho/.cache/huggingface/hub/models--unsloth--Qwen2.5-0.5B-Instruct-bnb-4bit/snapshots/216d96b52c97a3c8294776df8477592f6828981c"))


class ScriptedModel:
    device = torch.device("cpu")

    def __init__(self, tokenizer, payload):
        self.tokenizer, self.payload, self.calls = tokenizer, payload, 0

    def generate(self, **kwargs):
        self.calls += 1
        assert kwargs["do_sample"] is False and kwargs["max_new_tokens"] == 256 and kwargs["max_length"] is None
        sequence = kwargs["input_ids"][0].tolist()
        tokens = self.tokenizer.encode(self.payload, add_special_tokens=False) + [self.tokenizer.eos_token_id]
        grammar = kwargs["prefix_allowed_tokens_fn"]
        for token in tokens:
            if token not in grammar(0, torch.tensor(sequence, dtype=torch.long)):
                raise AssertionError(f"LMFE rejected scripted token {token}")
            sequence.append(token)
        return torch.tensor([sequence], dtype=torch.long)


def main():
    tokenizer = AutoTokenizer.from_pretrained(str(TOKENIZER), local_files_only=True)
    payload = '{"action":"report","verdict":"undetermined","candidate_model_codes":["A","B","C"],"diagnosis":"ambiguous","sufficiency":"no_observations","evidence_ids":[],"location":{"feature":"none","values":[]}}'
    fake = ScriptedModel(tokenizer, payload)
    adapter = Qwen25Generator(fake, tokenizer)
    adapter.weights_sha256 = "SIMULATED_NO_WEIGHTS"
    adapter.tokenizer_sha256 = "SIMULATED_REAL_TOKENIZER"
    state = {"candidate_models": [{"id": x} for x in "ABC"], "observations": [],
             "query_menu": [], "remaining_query_budget": 0}
    prompt = build_chat_prompt(tokenizer, (ROOT / "SYSTEM_PROMPT.txt").read_text(encoding="utf-8"), state)
    raw, metadata = adapter(prompt, public_action_schema(state))
    assert raw == payload and metadata["eos_terminated"] and fake.calls == 1
    result = {"protocol": "TRONCO-01-v2.7-offline-preflight", "adapter_call_exercised": True,
              "fake_generate_calls": fake.calls, "checkpoint_loaded": False,
              "learned_model_inference": False, "real_tokenizer_and_lmfe_callback": True,
              "eos_recorded": metadata["eos_terminated"], "prompt_token_count": metadata["prompt_token_count"],
              "generated_token_count": metadata["generated_token_count"]}
    output = ROOT / "results/adapter_fake_model_v2_7.json"
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
