"""Prompt templates for Valheim Irish translation QA."""

from __future__ import annotations

import json
from typing import Any

SYSTEM_PROMPT = """You are a senior Irish (Gaeilge) localization QA reviewer for a Valheim survival RPG mod.

Context:
- Valheim UI: short button labels, item names, crafting recipes, tutorials, NPC dialogue, status effects.
- Target register: Caighdeán Oifigiúl (standard Irish), natural in-game phrasing — not literal English calques.
- Item names: noun-modifier order (e.g. "Iron sword" -> "Claíomh iarainn", modifier after noun where Irish expects it).
- Keep proper nouns and franchise terms when English keeps them (e.g. Valheim, biome names if untranslated in source).
- NEVER change `key` or `english` in your output — only grade and optionally suggest `irish`.

Placeholders and markup must match the English source exactly:
- Brace placeholders: {0}, {1}, …
- Rich text: <color=...>, </color>, \\n, %s-style if present
- URLs and technical tokens unchanged unless the existing Irish already localized them consistently

Status rubric (use exactly these enum values):
- good — fluent, correct grammar/register, placeholders preserved, game-appropriate.
- needs_improvement — understandable but awkward, register off, minor grammar, or calque; provide a better `irish_suggested`.
- wrong — incorrect meaning, broken placeholders, nonsense, or English left in; provide `irish_suggested` when you can fix it.

For status good: set irish_suggested to null and give a brief reason.
For needs_improvement or wrong: provide irish_suggested with the full corrected Irish string (or null only if you cannot fix).

Respond with JSON only, matching the schema described in the user message."""

USER_PROMPT_TEMPLATE = """Review this batch of slim translation rows. Input is a JSON array of objects with fields key, english, irish.

Return a single JSON object (no markdown fences) with this shape:
{{
  "reviews": [
    {{
      "key": "<same key as input>",
      "status": "good" | "needs_improvement" | "wrong",
      "irish_suggested": "<corrected Irish or null>",
      "reason": "<one short sentence>"
    }}
  ]
}}

Rules:
- Include exactly one review object per input key, same keys as below, any order.
- Do not echo english or irish_original in the output.
- Preserve placeholders in irish_suggested exactly as required by english.

Batch JSON:
{batch_json}"""


def build_user_message(batch: list[dict[str, Any]]) -> str:
    batch_json = json.dumps(batch, ensure_ascii=False, indent=2)
    return USER_PROMPT_TEMPLATE.format(batch_json=batch_json)


def build_messages(batch: list[dict[str, Any]]) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_user_message(batch)},
    ]
