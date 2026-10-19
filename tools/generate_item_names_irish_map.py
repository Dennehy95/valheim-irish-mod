#!/usr/bin/env python3
"""Build tools/item-names_irish_map.json from extracted item-names.json."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from item_irish_translate import translate_item

_REPO = Path(__file__).resolve().parents[1]
_CACHE = _REPO / "tools" / "item-names_mt_cache.json"

# Argos en→ga sometimes returns this garbage for unrelated English inputs.
_POISONED_MT: frozenset[str] = frozenset({"Uisce agus Séarachas"})


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--extract",
        type=Path,
        default=_REPO / "plugins" / "irish-mod" / "extracted" / "item-names.json",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=_REPO / "tools" / "item-names_irish_map.json",
    )
    args = parser.parse_args()

    extract = json.loads(args.extract.read_text(encoding="utf-8"))
    entries = extract.get("entries", [])
    cache: dict[str, str] = {}
    if _CACHE.is_file():
        cache = json.loads(_CACHE.read_text(encoding="utf-8"))

    irish_map: dict[str, str] = {}

    for i, row in enumerate(entries, 1):
        key = row["key"]
        english = row["english"]
        if not english.strip():
            irish_map[key] = ""
            continue
        cached = cache.get(english)
        if cached and cached not in _POISONED_MT:
            irish = cached
        else:
            irish = translate_item(key, english)
        irish_map[key] = irish
        if i % 50 == 0 or i == len(entries):
            print(f"Translated {i}/{len(entries)}", file=sys.stderr)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(irish_map, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(irish_map)} strings to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
