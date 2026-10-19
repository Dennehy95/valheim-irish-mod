"""Load LLM review configuration and API keys from env + JSON file."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_TOOLS = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG_PATH = _TOOLS / "llm_review_config.json"
EXAMPLE_CONFIG_PATH = _TOOLS / "llm_review_config.example.json"


@dataclass
class ReviewConfig:
    provider: str
    model: str
    reasoning_effort: str | None
    temperature: float
    max_retries: int
    retry_backoff_seconds: float
    request_delay_seconds: float
    timeout_seconds: float
    openrouter_base_url: str
    groq_base_url: str
    groq_model: str

    @property
    def active_model(self) -> str:
        if self.provider == "groq":
            return self.groq_model
        return self.model


def load_config(path: Path | None = None, model_override: str | None = None) -> ReviewConfig:
    cfg_path = path or DEFAULT_CONFIG_PATH
    data: dict[str, Any] = {}
    if cfg_path.is_file():
        data = json.loads(cfg_path.read_text(encoding="utf-8"))
    elif EXAMPLE_CONFIG_PATH.is_file():
        data = json.loads(EXAMPLE_CONFIG_PATH.read_text(encoding="utf-8"))

    env_model = os.environ.get("LLM_REVIEW_MODEL")
    provider = os.environ.get("LLM_REVIEW_PROVIDER", data.get("provider", "openrouter")).lower()
    model = model_override or env_model or data.get("model", "x-ai/grok-4.7")

    return ReviewConfig(
        provider=provider,
        model=model,
        reasoning_effort=data.get("reasoning_effort"),
        temperature=float(data.get("temperature", 0.2)),
        max_retries=int(data.get("max_retries", 4)),
        retry_backoff_seconds=float(data.get("retry_backoff_seconds", 2.0)),
        request_delay_seconds=float(data.get("request_delay_seconds", 0.5)),
        timeout_seconds=float(data.get("timeout_seconds", 180)),
        openrouter_base_url=data.get("openrouter_base_url", "https://openrouter.ai/api/v1/chat/completions"),
        groq_base_url=data.get("groq_base_url", "https://api.groq.com/openai/v1/chat/completions"),
        groq_model=data.get("groq_model", "llama-3.3-70b-versatile"),
    )


def api_key_for_provider(provider: str) -> str | None:
    if provider == "groq":
        return os.environ.get("GROQ_API_KEY")
    return os.environ.get("OPENROUTER_API_KEY")
