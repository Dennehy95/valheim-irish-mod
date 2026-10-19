#!/usr/bin/env python3
"""List localization keys from Valheim resources.assets by prefix with filters."""

from __future__ import annotations

import argparse
import csv
import io
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

from scope_io import is_scope_header_comment

try:
    import UnityPy
except ImportError:
    print("Install dependencies: pip install -r tools/requirements.txt", file=sys.stderr)
    raise


def load_tables(resources_assets: Path) -> dict[str, str]:
    env = UnityPy.load(str(resources_assets))
    found: dict[str, str] = {}
    for obj in env.objects:
        if obj.type.name != "TextAsset":
            continue
        data = obj.read()
        name = data.m_Name or ""
        if not name.startswith("localization"):
            continue
        script = data.m_Script
        if isinstance(script, bytes):
            script = script.decode("utf-8")
        reader = csv.reader(io.StringIO(script))
        try:
            header = next(reader)
        except StopIteration:
            continue
        if "English" not in header:
            continue
        eng_idx = header.index("English")
        for row in reader:
            if not row or row[0].startswith("//"):
                continue
            key = row[0].strip()
            if not key or key in found:
                continue
            found[key] = row[eng_idx] if eng_idx < len(row) else ""
    return found


def filter_key(key: str, english: str, max_english_len: int) -> bool:
    if not english or "\n" in english:
        return False
    if len(english) > max_english_len:
        return False
    lowered = key.lower()
    for skip in ("_description", "_lore", "_tooltip_long", "_flavor"):
        if skip in lowered:
            return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--game-path",
        type=Path,
        default=Path(r"A:\Steam\steamapps\common\Valheim"),
    )
    parser.add_argument("--prefix", action="append", default=[], help="Key prefix, e.g. hud_")
    parser.add_argument("--max-english-len", type=int, default=80)
    parser.add_argument("--exclude-file", type=Path, action="append", default=[])
    parser.add_argument("--out", type=Path, help="Write keys one per line")
    args = parser.parse_args()

    resources = args.game_path / "valheim_Data" / "resources.assets"
    if not resources.is_file():
        print(f"Missing {resources}", file=sys.stderr)
        return 1

    exclude: set[str] = set()
    for path in args.exclude_file:
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not is_scope_header_comment(line):
                exclude.add(line)

    tables = load_tables(resources)
    keys = sorted(
        k
        for k, eng in tables.items()
        if k not in exclude
        and any(k.startswith(p) for p in args.prefix)
        and filter_key(k, eng, args.max_english_len)
    )

    if args.out:
        header = (
            f"# Auto-discovered: prefixes {', '.join(args.prefix)}; "
            f"max English len {args.max_english_len}; excludes {len(exclude)} keys.\n"
        )
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(header + "\n".join(keys) + "\n", encoding="utf-8")
        print(f"Wrote {len(keys)} keys to {args.out}")
    else:
        for k in keys:
            print(k)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
