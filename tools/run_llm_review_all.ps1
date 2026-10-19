# Full-corpus LLM batch review (resume-safe). Set OPENROUTER_API_KEY before running.
$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)

if (-not $env:OPENROUTER_API_KEY) {
    Write-Error "Set OPENROUTER_API_KEY (see docs/llm-batch-review-blueprint.md)"
}

$config = "tools\llm_review_config.json"
if (-not (Test-Path $config)) {
    Copy-Item "tools\llm_review_config.example.json" $config
    Write-Host "Created $config from example — verify model slug before long runs."
}

python tools/llm_review_pipeline.py `
    exports/translations-slim.json `
    --batch-size 25 `
    --resume `
    --include-needs-improvement

Write-Host ""
Write-Host "After human review of exports/llm-review/audit.jsonl:"
Write-Host "  python tools/merge_slim_translations.py exports/llm-review/translations-slim-corrected.json --dry-run"
Write-Host "  python tools/merge_slim_translations.py exports/llm-review/translations-slim-corrected.json --mark-reviewed"
