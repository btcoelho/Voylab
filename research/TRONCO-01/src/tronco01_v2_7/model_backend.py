"""Lazy Qwen 2.5 backend, adapted from the frozen v2.3 runner.

Importing this module does not import Unsloth, load tokenizer/model files, or run inference.
Call Qwen25Generator.from_verified_checkpoint only after the mandatory analysis gate.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import time
from typing import Callable


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def build_chat_prompt(tokenizer, system_prompt: str, state: dict) -> str:
    user = json.dumps(state, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return tokenizer.apply_chat_template(
        [{"role": "system", "content": system_prompt}, {"role": "user", "content": user}],
        tokenize=False, add_generation_prompt=True)


class Qwen25Generator:
    def __init__(self, model, tokenizer, max_new_tokens: int = 256, max_context_tokens: int = 2048):
        self.model = model
        self.tokenizer = tokenizer
        self.max_new_tokens = max_new_tokens
        self.max_context_tokens = max_context_tokens

    @classmethod
    def from_verified_checkpoint(cls, model_path: Path, expected_weights_sha256: str,
                                 expected_tokenizer_sha256: str,
                                 expected_tokenizer_config_sha256: str,
                                 generation_guard: Callable[[], dict[str, str]],
                                 expected_preregistration_sha256: str,
                                 max_new_tokens: int = 256, max_context_tokens: int = 2048,
                                 expected_artifact_hashes: dict[str, str] | None = None):
        verified = generation_guard()
        if (not isinstance(verified, dict)
                or verified.get("__manifest_status__") != "frozen_before_inference"):
            raise RuntimeError("model loading requires a verified frozen_before_inference manifest")
        prereg_hashes = {digest for name, digest in verified.items()
                         if Path(name.removeprefix("external:")).name in {"preregistration_draft.json", "preregistration.json"}}
        if expected_preregistration_sha256 not in prereg_hashes:
            raise RuntimeError("frozen manifest does not verify the expected preregistration")
        model_path = Path(model_path).expanduser().resolve()
        weights = model_path / "model.safetensors"
        actual_weights_hash = sha256_file(weights)
        if actual_weights_hash != expected_weights_sha256:
            raise RuntimeError("checkpoint SHA-256 does not match the frozen preregistration")
        actual_tokenizer_hash = sha256_file(model_path / "tokenizer.json")
        if actual_tokenizer_hash != expected_tokenizer_sha256:
            raise RuntimeError("tokenizer SHA-256 does not match the frozen preregistration")
        actual_tokenizer_config_hash = sha256_file(model_path / "tokenizer_config.json")
        if actual_tokenizer_config_hash != expected_tokenizer_config_sha256:
            raise RuntimeError("tokenizer config SHA-256 does not match the frozen preregistration")
        external_hashes = {str(Path(name.removeprefix("external:")).resolve()): digest
                           for name, digest in verified.items() if name.startswith("external:")}
        for path, digest in ((weights, actual_weights_hash), (model_path / "tokenizer.json", actual_tokenizer_hash),
                             (model_path / "tokenizer_config.json", actual_tokenizer_config_hash)):
            if external_hashes.get(str(path.resolve())) != digest:
                raise RuntimeError(f"model input is not covered by the frozen manifest: {path.name}")
        if expected_artifact_hashes is not None:
            actual_names = {path.name for path in model_path.iterdir() if path.is_file()}
            if actual_names != set(expected_artifact_hashes):
                raise RuntimeError("checkpoint file set differs from the frozen preregistration")
            for name, expected_hash in expected_artifact_hashes.items():
                artifact = model_path / name
                actual_hash = sha256_file(artifact)
                if actual_hash != expected_hash:
                    raise RuntimeError(f"checkpoint artifact hash mismatch: {name}")
                if external_hashes.get(str(artifact.resolve())) != actual_hash:
                    raise RuntimeError(f"checkpoint artifact is not covered by the frozen manifest: {name}")
        os.environ["HF_HUB_OFFLINE"] = "1"
        os.environ["TRANSFORMERS_OFFLINE"] = "1"
        import unsloth
        from unsloth import FastLanguageModel
        import transformers.tokenization_utils as tokenization_utils
        from transformers.tokenization_utils_base import PreTrainedTokenizerBase
        tokenization_utils.PreTrainedTokenizerBase = PreTrainedTokenizerBase
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name=str(model_path), max_seq_length=max_context_tokens,
            dtype=None, load_in_4bit=True)
        FastLanguageModel.for_inference(model)
        instance = cls(model, tokenizer, max_new_tokens, max_context_tokens)
        instance.weights_sha256 = actual_weights_hash
        instance.tokenizer_sha256 = actual_tokenizer_hash
        instance.runtime = {"python": __import__("sys").version.split()[0],
                            "transformers": __import__("transformers").__version__,
                            "unsloth": __import__("importlib.metadata", fromlist=["version"]).version("unsloth")}
        return instance

    def __call__(self, prompt: str, schema: dict):
        from lmformatenforcer import JsonSchemaParser
        from lmformatenforcer.characterlevelparser import UnionParser
        from lmformatenforcer.integrations.transformers import build_transformers_prefix_allowed_tokens_fn
        parser = UnionParser([JsonSchemaParser(branch) for branch in schema["oneOf"]])
        grammar = build_transformers_prefix_allowed_tokens_fn(self.tokenizer, parser)
        encoded = self.tokenizer(prompt, return_tensors="pt", truncation=False).to(self.model.device)
        prompt_tokens = int(encoded["input_ids"].shape[1])
        if prompt_tokens > self.max_context_tokens:
            raise RuntimeError(f"prompt uses {prompt_tokens} tokens; context limit is {self.max_context_tokens}")
        started = time.time()
        output = self.model.generate(
            **encoded, max_new_tokens=self.max_new_tokens, max_length=None,
            do_sample=False,
            pad_token_id=self.tokenizer.pad_token_id or self.tokenizer.eos_token_id,
            prefix_allowed_tokens_fn=grammar)
        generated = output[0, prompt_tokens:]
        raw = self.tokenizer.decode(generated, skip_special_tokens=True)
        metadata = {"backend": "unsloth_qwen25_0_5b_4bit",
                    "weights_sha256": self.weights_sha256,
                    "tokenizer_json_sha256": self.tokenizer_sha256,
                    "prompt_token_count": prompt_tokens,
                    "generated_token_ids": generated.tolist(),
                    "generated_token_count": int(generated.numel()),
                    "eos_terminated": bool(generated.numel() and int(generated[-1]) == self.tokenizer.eos_token_id),
                    "elapsed_seconds": round(time.time() - started, 4),
                    "settings": {"do_sample": False, "max_new_tokens": self.max_new_tokens,
                                 "max_length": None, "grammar_constrained": True}}
        return raw, metadata
