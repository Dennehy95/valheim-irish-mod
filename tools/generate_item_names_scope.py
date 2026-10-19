#!/usr/bin/env python3
"""Write tools/scopes/item-names.keys.txt — all vanilla item_* keys not already wired."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

from discover_scope_keys import load_tables
from scope_io import is_scope_header_comment

_REPO = Path(__file__).resolve().parents[1]


def load_wired_keys(repo: Path) -> set[str]:
    wired: set[str] = set()
    for path in (repo / "tools" / "scopes").glob("*.keys.txt"):
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not is_scope_header_comment(line):
                wired.add(line)
    trans = repo / "plugins" / "irish-mod" / "Translations"
    for ga in trans.glob("*.ga.json"):
        import json

        data = json.loads(ga.read_text(encoding="utf-8"))
        for entry in data.get("entries", []):
            wired.add(entry["key"])
    return wired


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--game-path",
        type=Path,
        default=Path(r"A:\Steam\steamapps\common\Valheim"),
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=_REPO / "tools" / "scopes" / "item-names.keys.txt",
    )
    parser.add_argument("--repo", type=Path, default=_REPO)
    args = parser.parse_args()

    resources = args.game_path / "valheim_Data" / "resources.assets"
    if not resources.is_file():
        print(f"Missing {resources}", file=sys.stderr)
        return 1

    tables = load_tables(resources)
    wired = load_wired_keys(args.repo)
    keys = sorted(k for k in tables if k.startswith("item_") and k not in wired)

    header = (
        f"# All localization keys with prefix item_ not already wired ({len(keys)} keys).\n"
        "# Includes display names, descriptions, and lore; no UI-length filter.\n"
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(header + "\n".join(keys) + "\n", encoding="utf-8")
    print(f"Wrote {len(keys)} keys to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
