#!/usr/bin/env python3
"""Batch LLM QA for slim Valheim Irish translations (audit + corrected slim export)."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent
_REPO = _TOOLS.parent
_DEFAULT_SLIM = _REPO / "exports" / "translations-slim.json"
_DEFAULT_OUT = _REPO / "exports" / "llm-review"

if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

from llm_review.client import chat_completion_json
from llm_review.config import DEFAULT_CONFIG_PATH, load_config
from llm_review.io import (
    append_audit_line,
    build_corrected_slim,
    load_audit_lines,
    load_checkpoint,
    load_slim_entries,
    write_checkpoint,
    write_json_array,
    write_summary,
)
from llm_review.models import AuditLine, Checkpoint, parse_batch_response
from llm_review.prompts import build_messages


def chunk_batches(entries: list, batch_size: int) -> list[list]:
    return [entries[i : i + batch_size] for i in range(0, len(entries), batch_size)]


def slim_dicts(batch: list) -> list[dict[str, str]]:
    return [{"key": e.key, "english": e.english, "irish": e.irish} for e in batch]


def finalize_outputs(
    out_dir: Path,
    entries: list,
    include_needs_improvement: bool,
) -> None:
    audit_path = out_dir / "audit.jsonl"
    audit_lines = load_audit_lines(audit_path)
    write_summary(audit_lines, out_dir / "audit-summary.json")
    audit_by_key = {line.key: line for line in audit_lines}
    corrected = build_corrected_slim(entries, audit_by_key, include_needs_improvement)
    write_json_array(out_dir / "translations-slim-corrected.json", corrected)
    print(f"Wrote {out_dir / 'audit-summary.json'}")
    print(f"Wrote {len(corrected)} rows to {out_dir / 'translations-slim-corrected.json'}")


def run_pipeline(args: argparse.Namespace) -> int:
    input_path = args.input.resolve()
    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    config = load_config(args.config, model_override=args.model)
    entries = load_slim_entries(input_path)
    if not entries:
        print(f"No entries in {input_path}", file=sys.stderr)
        return 1

    batches = chunk_batches(entries, args.batch_size)
    total_batches = len(batches)
    checkpoint_path = out_dir / "checkpoint.json"
    audit_path = out_dir / "audit.jsonl"

    checkpoint = load_checkpoint(checkpoint_path) if args.resume else None
    completed: set[int] = set()
    if checkpoint:
        if (
            checkpoint.input_path != str(input_path)
            or checkpoint.batch_size != args.batch_size
            or checkpoint.model != config.active_model
        ):
            print(
                "WARNING: checkpoint does not match current input/batch/model; "
                "delete checkpoint.json or omit --resume to start fresh",
                file=sys.stderr,
            )
        completed = set(checkpoint.completed_batch_ids)

    if args.dry_run:
        batch = batches[0]
        messages = build_messages(slim_dicts(batch))
        print("=== DRY RUN: batch 0 ===")
        print(f"Provider: {config.provider}  Model: {config.active_model}")
        print(f"Entries in batch: {len(batch)}")
        print("--- system ---")
        print(messages[0]["content"][:800] + ("..." if len(messages[0]["content"]) > 800 else ""))
        print("--- user (truncated) ---")
        user = messages[1]["content"]
        print(user[:2000] + ("..." if len(user) > 2000 else ""))
        return 0

    if args.resume and not checkpoint and audit_path.is_file():
        existing = load_audit_lines(audit_path)
        completed = {line.batch_id for line in existing}

    max_batch = total_batches
    if args.max_batches is not None:
        max_batch = min(total_batches, args.max_batches)

    processed = 0
    for batch_id, batch in enumerate(batches):
        if batch_id >= max_batch:
            break
        if batch_id in completed:
            continue

        batch_payload = slim_dicts(batch)
        messages = build_messages(batch_payload)
        expected_keys = {e.key for e in batch}

        print(f"Batch {batch_id + 1}/{total_batches} ({len(batch)} entries)...", flush=True)
        payload = chat_completion_json(config, messages)
        reviews = parse_batch_response(payload, expected_keys)

        by_key = {r.key: r for r in reviews}
        for entry in batch:
            r = by_key[entry.key]
            append_audit_line(
                audit_path,
                AuditLine(
                    key=entry.key,
                    english=entry.english,
                    irish_original=entry.irish,
                    status=r.status,
                    irish_suggested=r.irish_suggested,
                    reason=r.reason,
                    batch_id=batch_id,
                ),
            )

        completed.add(batch_id)
        cp = Checkpoint(
            input_path=str(input_path),
            batch_size=args.batch_size,
            model=config.active_model,
            provider=config.provider,
            completed_batch_ids=sorted(completed),
            total_batches=total_batches,
            total_entries=len(entries),
        )
        write_checkpoint(checkpoint_path, cp)
        processed += 1

        if config.request_delay_seconds > 0 and batch_id + 1 < max_batch:
            time.sleep(config.request_delay_seconds)

    if processed == 0 and not completed:
        print("No batches processed.", file=sys.stderr)
        return 1

    finalize_outputs(out_dir, entries, args.include_needs_improvement)
    print(f"Completed batches: {len(completed)}/{total_batches}")
    return 0


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "input",
        nargs="?",
        type=Path,
        default=_DEFAULT_SLIM,
        help="Slim JSON array or chunk file (default: exports/translations-slim.json)",
    )
    parser.add_argument("--batch-size", type=int, default=25, help="Entries per LLM request (default: 25)")
    parser.add_argument("--out-dir", type=Path, default=_DEFAULT_OUT, help="Output directory")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH, help="Path to llm_review_config.json")
    parser.add_argument("--model", type=str, default=None, help="Override model slug from config/env")
    parser.add_argument("--max-batches", type=int, default=None, help="Process at most N batches (testing)")
    parser.add_argument("--resume", action="store_true", help="Resume from exports/llm-review/checkpoint.json")
    parser.add_argument(
        "--include-needs-improvement",
        action="store_true",
        help="Include needs_improvement rows in translations-slim-corrected.json (default: wrong only)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print first batch prompt; no API call")
    args = parser.parse_args()

    if not args.input.is_file():
        print(f"Missing input: {args.input}", file=sys.stderr)
        return 1
    if args.batch_size < 1:
        print("--batch-size must be >= 1", file=sys.stderr)
        return 1

    return run_pipeline(args)


if __name__ == "__main__":
    raise SystemExit(main())
