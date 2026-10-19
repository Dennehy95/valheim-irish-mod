"""HTTP clients for OpenRouter and Groq chat completions."""

from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.request
from typing import Any

from .config import ReviewConfig, api_key_for_provider

_JSON_FENCE = re.compile(r"^```(?:json)?\s*|\s*```$", re.MULTILINE)


def _strip_fences(text: str) -> str:
    t = text.strip()
    if t.startswith("```"):
        t = _JSON_FENCE.sub("", t).strip()
    return t


def _parse_json_content(content: str) -> dict[str, Any]:
    cleaned = _strip_fences(content)
    data = json.loads(cleaned)
    if not isinstance(data, dict):
        raise ValueError("LLM response must be a JSON object")
    return data


def _post_json(url: str, headers: dict[str, str], body: dict[str, Any], timeout: float) -> dict[str, Any]:
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8")
    return json.loads(raw)


def chat_completion_json(
    config: ReviewConfig,
    messages: list[dict[str, str]],
) -> dict[str, Any]:
    api_key = api_key_for_provider(config.provider)
    if not api_key:
        env_name = "GROQ_API_KEY" if config.provider == "groq" else "OPENROUTER_API_KEY"
        raise RuntimeError(f"Missing {env_name} for provider {config.provider}")

    if config.provider == "groq":
        url = config.groq_base_url
        model = config.groq_model
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        body: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": config.temperature,
            "response_format": {"type": "json_object"},
        }
    else:
        url = config.openrouter_base_url
        model = config.model
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/Dennehy95/valheim-irish-mod",
            "X-Title": "valheim-irish-mod llm-review",
        }
        body = {
            "model": model,
            "messages": messages,
            "temperature": config.temperature,
            "response_format": {"type": "json_object"},
        }
        if config.reasoning_effort:
            body["reasoning_effort"] = config.reasoning_effort

    last_err: Exception | None = None
    for attempt in range(config.max_retries):
        try:
            if attempt > 0:
                time.sleep(config.retry_backoff_seconds * (2 ** (attempt - 1)))
            response = _post_json(url, headers, body, config.timeout_seconds)
            choices = response.get("choices")
            if not choices:
                raise ValueError("API response missing choices")
            content = choices[0].get("message", {}).get("content", "")
            if not content:
                raise ValueError("API response missing message content")
            return _parse_json_content(content)
        except urllib.error.HTTPError as exc:
            last_err = exc
            if exc.code in (429, 500, 502, 503, 504):
                continue
            raise
        except (urllib.error.URLError, json.JSONDecodeError, ValueError, TimeoutError) as exc:
            last_err = exc
            continue

    raise RuntimeError(f"LLM request failed after {config.max_retries} attempts: {last_err}")
