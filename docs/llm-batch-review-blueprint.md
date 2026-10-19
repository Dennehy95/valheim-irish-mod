# LLM batch review blueprint (hands-off QA)

Automated QA for `exports/translations-slim.json`: batch 20–30 rows per LLM call, grade each key, emit an audit trail and a **corrected slim** file for [`merge_slim_translations.py`](../tools/merge_slim_translations.py). Human review the audit before merging into `*.ga.json`.

Related: [ai-review-workflow.md](ai-review-workflow.md) (slim export / merge round-trip).

---

## Architecture

```
  export_slim_translations.py
           |
           v
  translations-slim.json  (~6058 rows: key, english, irish)
           |
           v
  llm_review_pipeline.py  (--batch-size 25, --resume)
           |
     +-----+-----+
     v           v
  OpenRouter     Groq (optional)
  (primary)      (fallback / experiments)
     |
     v
  exports/llm-review/
    audit.jsonl              one JSON object per key
    audit-summary.json       counts by status
    checkpoint.json          idempotent resume
    translations-slim-corrected.json
           |
           v  (human reads audit.jsonl)
  merge_slim_translations.py [--dry-run] [--mark-reviewed]
           |
           v
  plugins/irish-mod/Translations/*.ga.json  -->  game
```

---

## Status enum

| Value | Meaning |
|--------|---------|
| `good` | Fluent Caighdeán, placeholders OK, game-appropriate |
| `needs_improvement` | Understandable but awkward / minor issues; optional fix |
| `wrong` | Incorrect meaning, broken placeholders, or unusable |

Corrected slim (default): only `wrong` rows, with `irish` set to `irish_suggested` when present. Pass `--include-needs-improvement` to also export `needs_improvement` rows.

---

## Prompt design

Implemented in `tools/llm_review/prompts.py`.

**System** (summary):

- Valheim survival RPG UI context (items, crafting, dialogue, tutorials).
- Caighdeán Oifigiúl; terse labels vs fuller descriptions.
- Item names: Irish noun-modifier order where appropriate.
- Keep `{0}`, `{1}`, `<color=...>`, `\n`, URLs unless already consistently localized.
- Never change `key` or `english`.
- Structured JSON output with `reviews[]`: `key`, `status`, `irish_suggested`, `reason`.

**User** (per batch):

- Embeds the batch as a JSON array (`key`, `english`, `irish` only).
- Requires exactly one review per input key.
- JSON object only (no markdown fences).

Use `python tools/llm_review_pipeline.py --dry-run` to print the first batch prompt locally.

---

## Model routing and secrets

| Provider | Env var | Config keys |
|----------|---------|-------------|
| **OpenRouter** (primary) | `OPENROUTER_API_KEY` | `provider: "openrouter"`, `model`, `reasoning_effort` |
| **Groq** (optional) | `GROQ_API_KEY` | `LLM_REVIEW_PROVIDER=groq`, `groq_model` |

Copy `tools/llm_review_config.example.json` → `tools/llm_review_config.json` (gitignored). Optional overrides:

- `LLM_REVIEW_MODEL` — slug override without editing JSON
- `LLM_REVIEW_PROVIDER` — `openrouter` or `groq`

**Recommended Grok 4.7 high (OpenRouter):**

- Slug: `x-ai/grok-4.7` (verify on [OpenRouter Grok 4.7](https://openrouter.ai/x-ai/grok-4.7) before a long run).
- Dated canonical slug (if needed): `x-ai/grok-4.7-20260916`.
- Set `"reasoning_effort": "high"` in config for high reasoning (OpenRouter/xAI parameter).

Never commit API keys or `llm_review_config.json`.

---

## Cost / token estimate (~6058 strings @ 25/batch)

| Metric | Estimate |
|--------|----------|
| Batches | ⌈6058 / 25⌉ = **243** API calls |
| Input tokens / batch | ~2.5–4k (25 rows + system prompt) |
| Output tokens / batch | ~1–2.5k (reviews + reasons) |
| **Total input** | ~0.6–1.0M tokens |
| **Total output** | ~0.25–0.6M tokens |

**OpenRouter `x-ai/grok-4.7` list pricing (check live):** ~$2 / 1M input, ~$6 / 1M output → **roughly $2–4** for the full corpus, plus variance from reasoning length. Run `--max-batches 1` and check OpenRouter usage dashboard before committing to 6k.

---

## Safety and operations

1. **No auto-merge** — Inspect `exports/llm-review/audit.jsonl` and spot-check `wrong` / `needs_improvement` before merge.
2. **`merge_slim_translations.py --dry-run`** first; apply without `--dry-run` only after approval.
3. **`--mark-reviewed`** after merge to set `translationMethod: ai-reviewed` on changed entries.
4. **Checkpoints** — `exports/llm-review/checkpoint.json` + append-only `audit.jsonl`; re-run with `--resume` after interruption.
5. **Idempotent resume** — Completed `batch_id`s are skipped; delete `checkpoint.json` and `audit.jsonl` to restart clean.
6. **Gitignore** — Runtime output under `exports/llm-review/` stays local.

---

## Commands

**Setup (once per machine):**

```powershell
copy tools\llm_review_config.example.json tools\llm_review_config.json
$env:OPENROUTER_API_KEY = "<your-key>"
```

**Dry-run (no API):**

```powershell
python tools/llm_review_pipeline.py --dry-run
```

**Test batch (1 × 25 rows):**

```powershell
python tools/llm_review_pipeline.py --max-batches 1 --batch-size 25
```

**Full corpus (Grok 4.7 high via OpenRouter, resumable):**

```powershell
.\tools\run_llm_review_all.ps1
```

Or explicitly:

```powershell
python tools/llm_review_pipeline.py exports/translations-slim.json `
  --batch-size 25 `
  --model x-ai/grok-4.7 `
  --resume `
  --include-needs-improvement
```

**Merge after human review:**

```powershell
python tools/merge_slim_translations.py exports/llm-review/translations-slim-corrected.json --dry-run
python tools/merge_slim_translations.py exports/llm-review/translations-slim-corrected.json --mark-reviewed
```

**Single chunk file** (e.g. chunk from `split_slim_chunks.py`):

```powershell
python tools/llm_review_pipeline.py exports/chunks/chunk-001.json --out-dir exports/llm-review/chunk-001
```

---

## Files

| Path | Role |
|------|------|
| `tools/llm_review_pipeline.py` | CLI entry |
| `tools/llm_review/` | Config, prompts, HTTP client, I/O |
| `tools/llm_review_config.example.json` | Committed template |
| `tools/llm_review_config.json` | Local overrides (gitignored) |
| `tools/run_llm_review_all.ps1` / `.sh` | Full-corpus wrapper |
| `exports/llm-review/*` | Audit, checkpoint, corrected slim (gitignored) |
