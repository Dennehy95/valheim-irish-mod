#!/usr/bin/env python3
"""Fill tools/item-names_mt_cache.json (unique English -> Gaeilge via Argos offline MT)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]


def _ensure_argos_en_ga() -> object:
    import argostranslate.package
    import argostranslate.translate

    argostranslate.package.update_package_index()
    available = argostranslate.package.get_available_packages()
    pkg = next((p for p in available if p.from_code == "en" and p.to_code == "ga"), None)
    if pkg is None:
        raise RuntimeError("No Argos en->ga package in index")
    installed = argostranslate.translate.get_installed_languages()
    has_pair = any(
        getattr(i, "code", None) == "en" for i in installed
    ) and any(getattr(i, "code", None) == "ga" for i in installed)
    if not has_pair:
        download_path = pkg.download()
        argostranslate.package.install_from_path(download_path)

    from argostranslate import translate

    return translate


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--extract",
        type=Path,
        default=_REPO / "plugins" / "irish-mod" / "extracted" / "item-names.json",
    )
    parser.add_argument(
        "--cache",
        type=Path,
        default=_REPO / "tools" / "item-names_mt_cache.json",
    )
    args = parser.parse_args()

    translate = _ensure_argos_en_ga()
    extract = json.loads(args.extract.read_text(encoding="utf-8"))
    unique = sorted({e["english"] for e in extract["entries"] if e["english"].strip()})

    cache: dict[str, str] = {}
    if args.cache.is_file():
        cache = json.loads(args.cache.read_text(encoding="utf-8"))

    todo = [u for u in unique if u not in cache]
    print(f"{len(unique)} unique English; {len(cache)} cached; {len(todo)} to translate")

    for i, text in enumerate(todo, 1):
        cache[text] = translate.translate(text, "en", "ga")
        if i % 100 == 0 or i == len(todo):
            args.cache.write_text(json.dumps(cache, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            print(f"Saved cache ({len(cache)} entries) after {i}/{len(todo)}")

    args.cache.write_text(json.dumps(cache, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Done. {len(cache)} entries in {args.cache}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
