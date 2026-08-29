from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


def load_api_config(api_file: Path) -> dict[str, Any]:
    text = api_file.read_text(encoding="utf-8")
    models: list[str] = []
    in_models = False
    base_url = ""
    api_key = ""
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("1."):
            in_models = True
            continue
        if line.startswith("2."):
            in_models = False
            continue
        if line.startswith("3."):
            in_models = False
            continue
        if in_models and not line.startswith("Model price") and not line.startswith("Input Price") and not line.startswith("Completion Price"):
            models.append(line)
        if re.match(r"https?://", line):
            base_url = line.rstrip("/")
        if line.startswith("sk-"):
            api_key = line
    if not base_url or not api_key:
        raise ValueError(f"Could not parse base_url/api key from {api_file}")
    return {"base_url": base_url, "api_key": api_key, "models": models}


class ChatClient:
    def __init__(
        self,
        api_file: Path,
        model: str,
        temperature: float = 0.0,
        max_tokens: int = 2048,
        max_retries: int = 6,
    ):
        config = load_api_config(api_file)
        self.base_url = config["base_url"]
        self.api_key = config["api_key"]
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.max_retries = max_retries

    def complete(self, messages: list[dict[str, str]]) -> str:
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            self.base_url + "/v1/chat/completions",
            data=data,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        for attempt in range(self.max_retries + 1):
            try:
                with urllib.request.urlopen(request, timeout=120) as response:
                    body = json.loads(response.read().decode("utf-8"))
                return body["choices"][0]["message"]["content"]
            except urllib.error.HTTPError as exc:
                detail = exc.read().decode("utf-8", errors="replace")
                retryable = exc.code in {429, 500, 502, 503, 504} or _is_nested_transient(detail)
                if not retryable or attempt >= self.max_retries:
                    raise RuntimeError(f"LLM HTTP {exc.code}: {detail}") from exc
                time.sleep(_retry_delay(exc, attempt))
            except (urllib.error.URLError, TimeoutError) as exc:
                if attempt >= self.max_retries:
                    raise RuntimeError(f"LLM URL error: {exc}") from exc
                time.sleep(_retry_delay(None, attempt))
        raise RuntimeError("LLM request failed after retries")


def _retry_delay(exc: urllib.error.HTTPError | None, attempt: int) -> float:
    if exc is not None:
        retry_after = exc.headers.get("Retry-After")
        if retry_after:
            try:
                return min(float(retry_after), 120.0)
            except ValueError:
                pass
    return min(2.0 * (2**attempt), 120.0)


def _is_nested_transient(detail: str) -> bool:
    lowered = detail.lower()
    return any(
        marker in lowered
        for marker in ("model_not_provisioned", "no available channel", "rate limit", "temporarily unavailable")
    )
