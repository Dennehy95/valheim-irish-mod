#!/usr/bin/env python3
"""Merge slim translation edits (key, english, irish) back into *.ga.json bundles."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent
_REPO = _TOOLS.parent
_DEFAULT_TRANS = _REPO / "plugins" / "irish-mod" / "Translations"

SLIM_FIELDS = frozenset({"key", "english", "irish"})


def load_slim(path: Path) -> list[dict]:
    raw = path.read_text(encoding="utf-8")
    stripped = raw.strip()
    if not stripped:
        return []

    if path.suffix.lower() == ".jsonl":
        rows: list[dict] = []
        for line_no, line in enumerate(raw.splitlines(), start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_no}: invalid JSONL: {exc}") from exc
        return rows

    try:
        data = json.loads(stripped)
    except json.JSONDecodeError:
        rows = []
        for line_no, line in enumerate(raw.splitlines(), start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}: not a JSON array or JSONL: {exc}") from exc
        return rows

    if not isinstance(data, list):
        raise ValueError(f"{path}: expected a JSON array of slim entries")
    return data


def slim_to_map(rows: list[dict]) -> dict[str, str]:
    by_key: dict[str, str] = {}
    duplicates: list[str] = []
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("Each slim entry must be a JSON object")
        extra = set(row) - SLIM_FIELDS
        if extra:
            print(f"WARNING: ignoring extra fields on {row.get('key', '?')}: {sorted(extra)}", file=sys.stderr)
        key = row.get("key")
        if not key:
            raise ValueError("Slim entry missing required field: key")
        if key in by_key:
            duplicates.append(key)
        by_key[key] = row.get("irish", "")
    if duplicates:
        print(f"WARNING: duplicate keys in slim file; last value wins ({len(duplicates)})", file=sys.stderr)
    return by_key


def build_key_locations(trans_dir: Path) -> dict[str, list[tuple[Path, int]]]:
    locs: dict[str, list[tuple[Path, int]]] = defaultdict(list)
    for ga_path in sorted(trans_dir.glob("*.ga.json")):
        data = json.loads(ga_path.read_text(encoding="utf-8"))
        for idx, entry in enumerate(data.get("entries", [])):
            locs[entry["key"]].append((ga_path, idx))
    return locs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("slim", type=Path, help="Slim JSON array or JSONL file")
    parser.add_argument("--trans-dir", type=Path, default=_DEFAULT_TRANS)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report changes without writing *.ga.json files",
    )
    parser.add_argument(
        "--mark-reviewed",
        action="store_true",
        help="Set translationMethod to ai-reviewed on updated entries; set file machineAssisted true",
    )
    args = parser.parse_args()

    if not args.slim.is_file():
        print(f"Missing slim file: {args.slim}", file=sys.stderr)
        return 1
    if not args.trans_dir.is_dir():
        print(f"Missing translations directory: {args.trans_dir}", file=sys.stderr)
        return 1

    slim_map = slim_to_map(load_slim(args.slim))
    locs = build_key_locations(args.trans_dir)

    keys_updated: list[str] = []
    keys_unchanged: list[str] = []
    keys_not_found: list[str] = []

    files_data: dict[Path, dict] = {}
    dirty_files: set[Path] = set()

    for key, new_irish in slim_map.items():
        places = locs.get(key)
        if not places:
            keys_not_found.append(key)
            continue

        key_changed = False
        for ga_path, idx in places:
            if ga_path not in files_data:
                files_data[ga_path] = json.loads(ga_path.read_text(encoding="utf-8"))
            entry = files_data[ga_path]["entries"][idx]
            old_irish = entry.get("irish", "")
            if old_irish == new_irish:
                continue
            key_changed = True
            entry["irish"] = new_irish
            if args.mark_reviewed:
                entry["translationMethod"] = "ai-reviewed"
            dirty_files.add(ga_path)

        if key_changed:
            keys_updated.append(key)
        else:
            keys_unchanged.append(key)

    if args.mark_reviewed:
        for ga_path in dirty_files:
            files_data[ga_path]["machineAssisted"] = True

    if not args.dry_run:
        for ga_path in sorted(dirty_files):
            ga_path.write_text(
                json.dumps(files_data[ga_path], indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

    keys_updated.sort()
    keys_unchanged.sort()
    keys_not_found.sort()

    mode = "DRY RUN — no files written" if args.dry_run else "Applied"
    print(f"{mode}")
    print(f"Keys updated: {len(keys_updated)}")
    print(f"Keys unchanged (irish already matched): {len(keys_unchanged)}")
    print(f"Keys in slim not found in translations: {len(keys_not_found)}")
    if keys_not_found[:10]:
        print("  Not found (first 10): " + ", ".join(keys_not_found[:10]))
        if len(keys_not_found) > 10:
            print(f"  ... and {len(keys_not_found) - 10} more")
    if dirty_files:
        print(f"Files touched: {len(dirty_files)}")
        for ga_path in sorted(dirty_files):
            print(f"  {ga_path.relative_to(_REPO)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
