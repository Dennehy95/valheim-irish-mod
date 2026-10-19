#!/usr/bin/env python3
"""Build plugins/irish-mod/Translations/*.ga.json from extracted/*.json + Irish map."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--extract", type=Path, required=True)
    parser.add_argument("--irish-map", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--screen-id", required=True)
    args = parser.parse_args()

    extract = json.loads(args.extract.read_text(encoding="utf-8"))
    irish_map: dict[str, str] = json.loads(args.irish_map.read_text(encoding="utf-8"))

    entries = []
    missing = []
    for row in extract["entries"]:
        key = row["key"]
        irish = irish_map.get(key)
        if not irish:
            missing.append(key)
            continue
        entries.append(
            {
                "key": key,
                "english": row["english"],
                "irish": irish,
                "translationMethod": "manual",
            }
        )

    if missing:
        print(f"Missing {len(missing)} Irish strings: {', '.join(missing[:20])}...", file=sys.stderr)
        return 1

    payload = {
        "screen_id": args.screen_id,
        "locale": "ga",
        "pendingApiKey": True,
        "machineAssisted": False,
        "source_extract": f"extracted/{args.extract.name}",
        "entries": entries,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(entries)} entries to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
