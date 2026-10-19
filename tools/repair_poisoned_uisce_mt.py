#!/usr/bin/env python3
"""Replace known-bad Argos MT phrase in irish_map JSON files and scrub the shared MT cache."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from item_irish_translate import translate_item

_REPO = Path(__file__).resolve().parents[1]
_EXTRACT = _REPO / "plugins" / "irish-mod" / "extracted"
_TOOLS = _REPO / "tools"
_BAD = "Uisce agus Séarachas"
_MT_CACHE = _TOOLS / "item-names_mt_cache.json"

_GA_REBUILDS: list[tuple[str, Path, Path, Path]] = [
    (
        "item-names",
        _EXTRACT / "item-names.json",
        _TOOLS / "item-names_irish_map.json",
        _REPO / "plugins" / "irish-mod" / "Translations" / "item-names.ga.json",
    ),
    (
        "piece-names",
        _EXTRACT / "piece-names.json",
        _TOOLS / "piece-names_irish_map.json",
        _REPO / "plugins" / "irish-mod" / "Translations" / "piece-names.ga.json",
    ),
    (
        "captions",
        _EXTRACT / "captions.json",
        _TOOLS / "captions_irish_map.json",
        _REPO / "plugins" / "irish-mod" / "Translations" / "captions.ga.json",
    ),
    (
        "remainder",
        _EXTRACT / "remainder.json",
        _TOOLS / "remainder_irish_map.json",
        _REPO / "plugins" / "irish-mod" / "Translations" / "remainder.ga.json",
    ),
    (
        "npc-dialogue",
        _EXTRACT / "npc-dialogue.json",
        _TOOLS / "npc-dialogue_irish_map.json",
        _REPO / "plugins" / "irish-mod" / "Translations" / "npc-dialogue.ga.json",
    ),
    (
        "status-effects",
        _EXTRACT / "status-effects.json",
        _TOOLS / "status-effects_irish_map.json",
        _REPO / "plugins" / "irish-mod" / "Translations" / "status-effects.ga.json",
    ),
]


def _english_by_key(extract_path: Path) -> dict[str, str]:
    data = json.loads(extract_path.read_text(encoding="utf-8"))
    return {row["key"]: row["english"] for row in data.get("entries", [])}


def repair_irish_map(map_path: Path, english_by_key: dict[str, str]) -> int:
    irish_map: dict[str, str] = json.loads(map_path.read_text(encoding="utf-8"))
    fixed = 0
    for key, irish in list(irish_map.items()):
        if irish != _BAD:
            continue
        english = english_by_key.get(key, "")
        irish_map[key] = translate_item(key, english) if english.strip() else ""
        fixed += 1
    if fixed:
        map_path.write_text(json.dumps(irish_map, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return fixed


def scrub_mt_cache() -> int:
    if not _MT_CACHE.is_file():
        return 0
    cache: dict[str, str] = json.loads(_MT_CACHE.read_text(encoding="utf-8"))
    removed = 0
    for eng, ga in list(cache.items()):
        if ga == _BAD:
            del cache[eng]
            removed += 1
    if removed:
        _MT_CACHE.write_text(json.dumps(cache, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return removed


def fix_item_weight(map_path: Path) -> bool:
    if not map_path.is_file():
        return False
    irish_map: dict[str, str] = json.loads(map_path.read_text(encoding="utf-8"))
    if irish_map.get("item_weight") != "Meáchan Meáchan":
        return False
    irish_map["item_weight"] = "Meáchan"
    map_path.write_text(json.dumps(irish_map, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return True


def rebuild_ga(screen_id: str, extract: Path, irish_map: Path, ga_out: Path) -> None:
    import subprocess

    subprocess.run(
        [
            sys.executable,
            str(_TOOLS / "build_ga_from_extract.py"),
            "--extract",
            str(extract),
            "--irish-map",
            str(irish_map),
            "--out",
            str(ga_out),
            "--screen-id",
            screen_id,
        ],
        check=True,
        cwd=_REPO,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-rebuild-ga", action="store_true")
    parser.add_argument(
        "--rebuild-ga",
        action="store_true",
        help="Rebuild all scope ga.json files from irish maps (even if no repairs)",
    )
    args = parser.parse_args()

    total_fixed = 0
    for map_path in sorted(_TOOLS.glob("*_irish_map.json")):
        scope = map_path.name.replace("_irish_map.json", "")
        extract = _EXTRACT / f"{scope}.json"
        if not extract.is_file():
            continue
        n = repair_irish_map(map_path, _english_by_key(extract))
        if n:
            print(f"Fixed {n} keys in {map_path.name}")
            total_fixed += n

    if fix_item_weight(_TOOLS / "item-names_irish_map.json"):
        print("Fixed item_weight (duplicate Meachan -> Meachan)")
        total_fixed += 1

    removed = scrub_mt_cache()
    if removed:
        print(f"Removed {removed} poisoned entries from {_MT_CACHE.name}")

    print(f"Total irish_map repairs: {total_fixed}")

    if not args.no_rebuild_ga and (total_fixed or args.rebuild_ga):
        for screen_id, extract, irish_map, ga_out in _GA_REBUILDS:
            if irish_map.exists() and extract.exists():
                rebuild_ga(screen_id, extract, irish_map, ga_out)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
