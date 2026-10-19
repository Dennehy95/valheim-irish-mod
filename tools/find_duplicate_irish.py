#!/usr/bin/env python3
"""Group translation rows by identical Irish; flag groups whose English texts differ."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
_DEFAULT_TRANS = _REPO / "plugins" / "irish-mod" / "Translations"
_DEFAULT_OUT = _REPO / "exports" / "duplicate-irish-report.csv"

_WS = re.compile(r"\s+")


def _norm_english(text: str) -> str:
    return _WS.sub(" ", text.strip().lower())


def load_entries(trans_dir: Path) -> list[dict]:
    rows: list[dict] = []
    for ga_path in sorted(trans_dir.glob("*.ga.json")):
        data = json.loads(ga_path.read_text(encoding="utf-8"))
        source_file = ga_path.name
        for entry in data.get("entries", []):
            irish = (entry.get("irish") or "").strip()
            if not irish:
                continue
            rows.append(
                {
                    "key": entry["key"],
                    "english": entry.get("english", ""),
                    "irish": irish,
                    "sourceFile": source_file,
                }
            )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trans-dir", type=Path, default=_DEFAULT_TRANS)
    parser.add_argument("--out", type=Path, default=_DEFAULT_OUT)
    parser.add_argument(
        "--min-keys",
        type=int,
        default=2,
        help="Minimum keys sharing the same Irish to include (default: 2)",
    )
    args = parser.parse_args()

    rows = load_entries(args.trans_dir)
    by_irish: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_irish[row["irish"]].append(row)

    report_rows: list[dict] = []
    for irish, group in sorted(by_irish.items(), key=lambda x: -len(x[1])):
        if len(group) < args.min_keys:
            continue
        norms = {_norm_english(r["english"]) for r in group}
        if len(norms) <= 1:
            continue
        keys = ";".join(sorted(r["key"] for r in group))
        english_samples = " | ".join(sorted({r["english"] for r in group})[:8])
        if len({r["english"] for r in group}) > 8:
            english_samples += " | …"
        report_rows.append(
            {
                "irish": irish,
                "key_count": len(group),
                "distinct_english_count": len(norms),
                "keys": keys,
                "english_samples": english_samples,
            }
        )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "irish",
                "key_count",
                "distinct_english_count",
                "keys",
                "english_samples",
            ],
        )
        writer.writeheader()
        writer.writerows(report_rows)

    print(f"Wrote {len(report_rows)} suspicious groups to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
