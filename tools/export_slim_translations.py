#!/usr/bin/env python3
"""Export slim Irish translation rows (key, english, irish only) for AI review."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent
_REPO = _TOOLS.parent
_DEFAULT_TRANS = _REPO / "plugins" / "irish-mod" / "Translations"
_DEFAULT_EXPORT = _REPO / "exports"

from export_all_translations import load_all_entries  # noqa: E402

SLIM_FIELDS = ("key", "english", "irish")


def to_slim_rows(rows: list[dict]) -> list[dict]:
    return [{k: row.get(k, "") for k in SLIM_FIELDS} for row in rows]


def write_json(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trans-dir", type=Path, default=_DEFAULT_TRANS)
    parser.add_argument("--export-dir", type=Path, default=_DEFAULT_EXPORT)
    parser.add_argument(
        "--jsonl",
        action="store_true",
        help="Also write translations-slim.jsonl (one slim object per line)",
    )
    args = parser.parse_args()

    if not args.trans_dir.is_dir():
        print(f"Missing translations directory: {args.trans_dir}", file=sys.stderr)
        return 1

    rows, duplicates = load_all_entries(args.trans_dir)
    if duplicates:
        print(f"WARNING: skipped {len(duplicates)} duplicate keys in export", file=sys.stderr)

    slim = to_slim_rows(rows)
    export_dir = args.export_dir
    json_path = export_dir / "translations-slim.json"
    write_json(json_path, slim)
    print(f"Wrote {len(slim)} entries to {json_path}")

    if args.jsonl:
        jsonl_path = export_dir / "translations-slim.jsonl"
        write_jsonl(jsonl_path, slim)
        print(f"Wrote {len(slim)} lines to {jsonl_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
