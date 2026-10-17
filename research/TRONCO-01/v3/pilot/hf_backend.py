"""Local Hugging Face backend (transformers + lm-format-enforcer), greedy decoding, schema-constrained.

First real start failed on an import incompatibility (see _transformers_compat); smoke-tested with smoke_hf.py. It mirrors the stack recorded in the frozen v2.7 manifest:
transformers 5.17.0, lm-format-enforcer 0.11.3. It deliberately accepts NO `state` argument.
"""
from __future__ import annotations

from pilot_harness import Backend


def _transformers_compat():
    """lm-format-enforcer 0.11.3 imports PreTrainedTokenizerBase from transformers.tokenization_utils, which
    transformers 5.x no longer exposes there (found on the first real start, 17/10/2026, 0 model calls).
    Re-export the class under the old name instead of changing installed packages. Returns what was done."""
    import transformers
    try:
        import transformers.tokenization_utils as tu
    except ImportError:
        import sys, types
        tu = types.ModuleType("transformers.tokenization_utils")
        sys.modules["transformers.tokenization_utils"] = tu
        transformers.tokenization_utils = tu
    if hasattr(tu, "PreTrainedTokenizerBase"):
        return "none"
    tu.PreTrainedTokenizerBase = transformers.PreTrainedTokenizerBase
    return "reexported PreTrainedTokenizerBase"


class HFBackend(Backend):
    def __init__(self, snapshot_dir: str, max_new_tokens: int = 256, max_context_tokens: int = 4096):
        import torch
        self.compat = _transformers_compat()
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
