"""Anthropic Messages API backend for the V4 model run (docs/V3_CONSULTAS.md §15). No training, no state access.

- The key is read only from the environment variable ANTHROPIC_API_KEY; it is never written, logged or returned.
- Fixed before the first call (§15.6): temperature 0, max_tokens 1024, no system-prompt changes, no tools.
- Every call returns the raw text plus metadata (model actually served, stop reason, token usage, request id).
- Transport failures (HTTP 429/5xx/overloaded, timeouts) are retried with backoff and logged as EXECUTION failures;
  they never become model answers. A 4xx other than 429 stops the run (configuration problem, not the model's fault).
"""
from __future__ import annotations

import json
import os
import time

from pilot_harness import Backend

API = "https://api.anthropic.com/v1/messages"
VERSION = "2023-06-01"


class ExecutionError(RuntimeError):
    """The call could not be completed for reasons outside the model (network, quota, configuration)."""


class AnthropicBackend(Backend):
    def __init__(self, model: str, temperature: float = 0.0, max_tokens: int = 1024, timeout: float = 120.0,
                 max_retries: int = 6, session=None, sleep=time.sleep):
        import requests
        self.requests = requests
        self.session = session or requests.Session()
        ca = "/root/.ccr/ca-bundle.crt"
        self.verify = ca if os.path.exists(ca) else True
        self.model, self.temperature, self.max_tokens = model, temperature, max_tokens
        self.timeout, self.max_retries, self.sleep = timeout, max_retries, sleep
        self.name = f"anthropic:{model}"
        self.last_meta: dict = {}
        self.execution_log: list[dict] = []

    def _key(self) -> str:
        k = os.environ.get("ANTHROPIC_API_KEY", "")
        if not k:
            raise ExecutionError("ANTHROPIC_API_KEY is not set in the environment")
        return k

    def generate(self, system: str, user: str, schema: dict) -> str:
        body = {"model": self.model, "max_tokens": self.max_tokens, "temperature": self.temperature,
                "system": system, "messages": [{"role": "user", "content": user}]}
        headers = {"x-api-key": self._key(), "anthropic-version": VERSION, "content-type": "application/json"}
        for attempt in range(self.max_retries + 1):
            try:
                r = self.session.post(API, headers=headers, data=json.dumps(body), timeout=self.timeout, verify=self.verify)
            except self.requests.RequestException as e:   # network-level failure
                self.execution_log.append({"attempt": attempt, "kind": "network", "error": type(e).__name__})
                self.sleep(min(60, 2 ** attempt))
                continue
            if r.status_code == 200:
                d = r.json()
                text = "".join(b.get("text", "") for b in d.get("content", []) if b.get("type") == "text")
                self.last_meta = {"model_served": d.get("model"), "stop_reason": d.get("stop_reason"),
                                  "usage": d.get("usage"), "request_id": r.headers.get("request-id"), "attempts": attempt + 1}
                return text
            kind = "retryable" if r.status_code in (429, 500, 502, 503, 504, 529) else "fatal"
            self.execution_log.append({"attempt": attempt, "kind": kind, "status": r.status_code})
            if kind == "fatal":
                raise ExecutionError(f"HTTP {r.status_code} (configuration or request problem); run stopped")
            self.sleep(min(60, 2 ** attempt))
        raise ExecutionError("retries exhausted")
