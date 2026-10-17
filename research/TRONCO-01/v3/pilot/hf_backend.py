"""Local Hugging Face backend (transformers + lm-format-enforcer), greedy decoding, schema-constrained.

NOT EXECUTED where this file was written (no torch there). It mirrors the stack recorded in the frozen v2.7 manifest:
transformers 5.17.0, lm-format-enforcer 0.11.3. It deliberately accepts NO `state` argument.
"""
from __future__ import annotations

from pilot_harness import Backend


class HFBackend(Backend):
    def __init__(self, snapshot_dir: str, max_new_tokens: int = 256, max_context_tokens: int = 4096):
        import torch
        from lmformatenforcer import JsonSchemaParser
        from lmformatenforcer.integrations.transformers import build_transformers_prefix_allowed_tokens_fn
        from transformers import AutoModelForCausalLM, AutoTokenizer
        self.torch, self.JsonSchemaParser, self.build = torch, JsonSchemaParser, build_transformers_prefix_allowed_tokens_fn
        self.tok = AutoTokenizer.from_pretrained(snapshot_dir, local_files_only=True)
        self.model = AutoModelForCausalLM.from_pretrained(snapshot_dir, local_files_only=True, device_map="auto")
        self.max_new, self.max_ctx = max_new_tokens, max_context_tokens
        self.name = f"hf:{snapshot_dir}"

    def generate(self, system: str, user: str, schema: dict) -> str:
        msgs = [{"role": "system", "content": system}, {"role": "user", "content": user}]
        ids = self.tok.apply_chat_template(msgs, add_generation_prompt=True, return_tensors="pt").to(self.model.device)
        if ids.shape[1] > self.max_ctx:
            raise RuntimeError(f"prompt has {ids.shape[1]} tokens > {self.max_ctx}")
        prefix = self.build(self.tok, self.JsonSchemaParser(schema))
        out = self.model.generate(ids, do_sample=False, max_new_tokens=self.max_new, prefix_allowed_tokens_fn=prefix,
                                  pad_token_id=self.tok.eos_token_id)
        return self.tok.decode(out[0, ids.shape[1]:], skip_special_tokens=True)
