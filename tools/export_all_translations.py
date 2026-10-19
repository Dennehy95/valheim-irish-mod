#!/usr/bin/env python3
"""Export all Irish translation entries from plugins/irish-mod/Translations/*.ga.json."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent
_REPO = _TOOLS.parent
_DEFAULT_TRANS = _REPO / "plugins" / "irish-mod" / "Translations"
_DEFAULT_EXPORT = _REPO / "exports"

FILE_META_KEYS = ("screen_id", "locale", "pendingApiKey", "machineAssisted", "source_extract")

CSV_COLUMNS = [
    "key",
    "english",
    "irish",
    "sourceFile",
    "screen_id",
    "locale",
    "pendingApiKey",
    "machineAssisted",
    "source_extract",
    "translationMethod",
]


def load_all_entries(trans_dir: Path) -> tuple[list[dict], list[str]]:
    """Merge entries from all *.ga.json; dedupe by key (first file wins, sorted by name)."""
    by_key: dict[str, dict] = {}
    duplicates: list[str] = []

    for ga_path in sorted(trans_dir.glob("*.ga.json")):
        data = json.loads(ga_path.read_text(encoding="utf-8"))
        file_meta = {k: data.get(k) for k in FILE_META_KEYS}
        source_file = ga_path.name

        for entry in data.get("entries", []):
            key = entry["key"]
            row = {
                "key": key,
                "english": entry.get("english", ""),
                "irish": entry.get("irish", ""),
                "sourceFile": source_file,
                **file_meta,
                "translationMethod": entry.get("translationMethod", ""),
            }
            if key in by_key:
                prev = by_key[key]["sourceFile"]
                duplicates.append(f"{key} ({prev} + {source_file})")
                continue
            by_key[key] = row

    rows = sorted(by_key.values(), key=lambda r: r["key"])
    return rows, duplicates


def write_json(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_readme(path: Path, row_count: int, ga_file_count: int, generated_at: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = f"""# Translation exports

Full export of Irish (`ga`) strings from `plugins/irish-mod/Translations/*.ga.json`.

| Artifact | Description |
|----------|-------------|
| `translations-full.json` | All entries as a JSON array, sorted by `key` |
| `translations-full.csv` | Same fields for Excel/Google Sheets (UTF-8 with BOM) |

## Snapshot

- **Rows (unique keys):** {row_count:,}
- **Source files:** {ga_file_count} `*.ga.json` translation bundles
- **Generated (UTC):** {generated_at}

## Regenerate

From the repository root:

```bash
python tools/export_all_translations.py
```

Optional paths:

```bash
python tools/export_all_translations.py --trans-dir plugins/irish-mod/Translations --export-dir exports
```

Each row includes `key`, `english`, `irish`, `sourceFile`, file-level metadata (`pendingApiKey`, `machineAssisted`, `screen_id`, …), and per-entry `translationMethod`. Keys are deduplicated across files (first file in sorted filename order wins).
"""
    path.write_text(body, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trans-dir", type=Path, default=_DEFAULT_TRANS)
    parser.add_argument("--export-dir", type=Path, default=_DEFAULT_EXPORT)
    args = parser.parse_args()

    if not args.trans_dir.is_dir():
        print(f"Missing translations directory: {args.trans_dir}", file=sys.stderr)
        return 1

    ga_files = sorted(args.trans_dir.glob("*.ga.json"))
    if not ga_files:
        print(f"No *.ga.json files in {args.trans_dir}", file=sys.stderr)
        return 1

    rows, duplicates = load_all_entries(args.trans_dir)
    if duplicates:
        print(f"WARNING: skipped {len(duplicates)} duplicate keys", file=sys.stderr)
        for line in duplicates[:20]:
            print(f"  {line}", file=sys.stderr)
        if len(duplicates) > 20:
            print(f"  ... and {len(duplicates) - 20} more", file=sys.stderr)

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    export_dir = args.export_dir
    write_json(export_dir / "translations-full.json", rows)
    write_csv(export_dir / "translations-full.csv", rows)
    write_readme(export_dir / "README.md", len(rows), len(ga_files), generated_at)

    print(f"Exported {len(rows)} keys from {len(ga_files)} files to {export_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
