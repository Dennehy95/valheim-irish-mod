#!/usr/bin/env python3
"""Count unique Valheim localization keys in resources.assets (all localization* TextAssets)."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import sys
from collections import Counter
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


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_all_keys(resources_assets: Path) -> tuple[dict[str, str], list[str], int]:
    """Return key -> english (first seen), asset names touched, raw row count."""
    env = UnityPy.load(str(resources_assets))
    found: dict[str, str] = {}
    assets: list[str] = []
    raw_rows = 0

    for obj in env.objects:
        if obj.type.name != "TextAsset":
            continue
        data = obj.read()
        name = data.m_Name or ""
        if not name.startswith("localization"):
            continue
        assets.append(name)
        script = data.m_Script
        if isinstance(script, bytes):
            script = script.decode("utf-8")
        reader = csv.reader(io.StringIO(script))
        try:
            header = next(reader)
        except StopIteration:
            continue
        eng_idx = header.index("English") if "English" in header else None
        for row in reader:
            if not row or row[0].startswith("//"):
                continue
            key = row[0].strip()
            if not key:
                continue
            raw_rows += 1
            if key in found:
                continue
            english = ""
            if eng_idx is not None and eng_idx < len(row):
                english = row[eng_idx]
            found[key] = english
    return found, sorted(set(assets)), raw_rows


def key_prefix(key: str) -> str:
    if key.startswith("$"):
        rest = key[1:]
        m = re.match(r"^([a-z0-9]+_)", rest, re.I)
        return ("$" + m.group(1)) if m else "$other"
    m = re.match(r"^([a-z0-9]+_)", key, re.I)
    return m.group(1) if m else "(no_prefix)"


def load_wired_keys(repo: Path) -> set[str]:
    wired: set[str] = set()
    for path in (repo / "tools" / "scopes").glob("*.keys.txt"):
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not is_scope_header_comment(line):
                wired.add(line)
    trans = repo / "plugins" / "irish-mod" / "Translations"
    for ga in trans.glob("*.ga.json"):
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
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--json-out", type=Path, help="Write full census JSON")
    args = parser.parse_args()

    resources = args.game_path / "valheim_Data" / "resources.assets"
    if not resources.is_file():
        print(f"Missing {resources}", file=sys.stderr)
        return 1

    keys, assets, raw_rows = load_all_keys(resources)
    wired = load_wired_keys(args.repo)
    uncovered = set(keys) - wired
    sha = sha256_file(resources)

    prefix_all = Counter(key_prefix(k) for k in keys)
    prefix_uncovered = Counter(key_prefix(k) for k in uncovered)

    report = {
        "resources_assets_sha256": sha,
        "localization_assets": assets,
        "raw_csv_rows_seen": raw_rows,
        "unique_vanilla_keys": len(keys),
        "wired_keys": len(wired),
        "covered_in_vanilla": len(set(keys) & wired),
        "uncovered_vanilla_keys": len(uncovered),
        "coverage_pct": round(100.0 * len(set(keys) & wired) / len(keys), 2) if keys else 0,
        "top_prefixes_all": prefix_all.most_common(25),
        "top_prefixes_uncovered": prefix_uncovered.most_common(25),
    }

    print(json.dumps(report, indent=2))
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
