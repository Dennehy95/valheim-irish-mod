#!/usr/bin/env bash
# Full-corpus LLM batch review (resume-safe). Set OPENROUTER_API_KEY before running.
set -euo pipefail
cd "$(dirname "$0")/.."

if [[ -z "${OPENROUTER_API_KEY:-}" ]]; then
  echo "Set OPENROUTER_API_KEY (see docs/llm-batch-review-blueprint.md)" >&2
  exit 1
fi

CONFIG="tools/llm_review_config.json"
if [[ ! -f "$CONFIG" ]]; then
  cp tools/llm_review_config.example.json "$CONFIG"
  echo "Created $CONFIG from example — verify model slug before long runs."
fi

python tools/llm_review_pipeline.py \
  exports/translations-slim.json \
  --batch-size 25 \
  --resume \
  --include-needs-improvement

echo ""
echo "After human review of exports/llm-review/audit.jsonl:"
echo "  python tools/merge_slim_translations.py exports/llm-review/translations-slim-corrected.json --dry-run"
echo "  python tools/merge_slim_translations.py exports/llm-review/translations-slim-corrected.json --mark-reviewed"
