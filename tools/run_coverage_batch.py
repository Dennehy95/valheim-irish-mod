#!/usr/bin/env python3
"""Extract → MT cache → Irish map → ga.json for one coverage batch (same as item_*)."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
_TOOLS = _REPO / "tools"
_MT_CACHE = _TOOLS / "item-names_mt_cache.json"


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True, cwd=_REPO)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope", type=Path, required=True)
    parser.add_argument("--screen-id", required=True)
    parser.add_argument("--screen-title", required=True)
    parser.add_argument("--extract", type=Path, required=True)
    parser.add_argument("--irish-map", type=Path, required=True)
    parser.add_argument("--ga-out", type=Path, required=True)
    args = parser.parse_args()

    py = sys.executable

    run(
        [
            py,
            str(_TOOLS / "extract_screen_strings.py"),
            "--scope",
            str(args.scope),
            "--screen-id",
            args.screen_id,
            "--screen-title",
            args.screen_title,
            "--out",
            str(args.extract),
        ]
    )
    run(
        [
            py,
            str(_TOOLS / "build_item_mt_cache.py"),
            "--extract",
            str(args.extract),
            "--cache",
            str(_MT_CACHE),
        ]
    )
    run(
        [
            py,
            str(_TOOLS / "generate_item_names_irish_map.py"),
            "--extract",
            str(args.extract),
            "--out",
            str(args.irish_map),
        ]
    )
    run(
        [
            py,
            str(_TOOLS / "build_ga_from_extract.py"),
            "--extract",
            str(args.extract),
            "--irish-map",
            str(args.irish_map),
            "--out",
            str(args.ga_out),
            "--screen-id",
            args.screen_id,
        ]
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
