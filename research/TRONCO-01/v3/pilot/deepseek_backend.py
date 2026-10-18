"""DeepSeek chat-completions backend for the V4 model run (deviation §16 of docs/V3_CONSULTAS.md). No training, no state.

Same contract as anthropic_backend: key only from the environment (DEEPSEEK_API_KEY), never written or logged; temperature 0,
max_tokens 1024, no response_format and no post-processing (parity with the Claude run); only `content` is used as the answer
(any separate reasoning field is recorded as present/absent, never as the answer). Transport failures are execution failures.
"""
from __future__ import annotations

import json
import os
import time

from anthropic_backend import ExecutionError
from pilot_harness import Backend

API = "https://api.deepseek.com/chat/completions"


class DeepSeekBackend(Backend):
    def __init__(self, model: str, temperature: float = 0.0, max_tokens: int = 1024, timeout: float = 180.0,
                 max_retries: int = 6, session=None, sleep=time.sleep):
        import requests
        self.requests = requests
        self.session = session or requests.Session()
        ca = "/root/.ccr/ca-bundle.crt"
        self.verify = ca if os.path.exists(ca) else True
        self.model, self.temperature, self.max_tokens = model, temperature, max_tokens
        self.timeout, self.max_retries, self.sleep = timeout, max_retries, sleep
        self.name = f"deepseek:{model}"
        self.last_meta: dict = {}
        self.execution_log: list[dict] = []

    def _key(self) -> str:
        k = os.environ.get("DEEPSEEK_API_KEY", "")
        if not k:
            raise ExecutionError("DEEPSEEK_API_KEY is not set in the environment")
        return k

    def generate(self, system: str, user: str, schema: dict) -> str:
        body = {"model": self.model, "temperature": self.temperature, "max_tokens": self.max_tokens, "stream": False,
                "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
        headers = {"Authorization": "Bearer " + self._key(), "Content-Type": "application/json"}
        for attempt in range(self.max_retries + 1):
            try:
                r = self.session.post(API, headers=headers, data=json.dumps(body), timeout=self.timeout, verify=self.verify)
            except self.requests.RequestException as e:
                self.execution_log.append({"attempt": attempt, "kind": "network", "error": type(e).__name__})
                self.sleep(min(60, 2 ** attempt))
                continue
            if r.status_code == 200:
                d = r.json()
                msg = (d.get("choices") or [{}])[0].get("message", {})
                self.last_meta = {"model_served": d.get("model"), "finish_reason": (d.get("choices") or [{}])[0].get("finish_reason"),
                                  "usage": d.get("usage"), "request_id": d.get("id"), "attempts": attempt + 1,
                                  "reasoning_present": bool(msg.get("reasoning_content"))}
                return msg.get("content") or ""
            kind = "retryable" if r.status_code in (429, 500, 502, 503, 504) else "fatal"
            self.execution_log.append({"attempt": attempt, "kind": kind, "status": r.status_code})
            if kind == "fatal":
                raise ExecutionError(f"HTTP {r.status_code} (configuration or request problem); run stopped")
            self.sleep(min(60, 2 ** attempt))
        raise ExecutionError("retries exhausted")
