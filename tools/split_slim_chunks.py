#!/usr/bin/env python3
"""Split a slim translation export into fixed-size chunk files for AI review."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent
_REPO = _TOOLS.parent
_DEFAULT_SLIM = _REPO / "exports" / "translations-slim.json"
_DEFAULT_OUT = _REPO / "exports" / "chunks"


def load_slim_array(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"{path}: expected a JSON array")
    return data


def write_chunk(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slim", type=Path, default=_DEFAULT_SLIM, help="Slim JSON array to split")
    parser.add_argument("--out-dir", type=Path, default=_DEFAULT_OUT, help="Output directory for chunks")
    parser.add_argument("--size", type=int, default=200, help="Entries per chunk (default: 200)")
    args = parser.parse_args()

    if args.size < 1:
        print("--size must be at least 1", file=sys.stderr)
        return 1
    if not args.slim.is_file():
        print(f"Missing slim file: {args.slim}", file=sys.stderr)
        return 1

    rows = load_slim_array(args.slim)
    if not rows:
        print("No entries to split", file=sys.stderr)
        return 1

    chunk_count = (len(rows) + args.size - 1) // args.size
    width = max(3, len(str(chunk_count)))

    for i in range(chunk_count):
        start = i * args.size
        end = min(start + args.size, len(rows))
        chunk_path = args.out_dir / f"chunk-{i + 1:0{width}d}.json"
        write_chunk(chunk_path, rows[start:end])
        print(f"Wrote {end - start} entries to {chunk_path}")

    print(f"Split {len(rows)} entries into {chunk_count} chunk(s) under {args.out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
