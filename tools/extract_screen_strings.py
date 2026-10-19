#!/usr/bin/env python3
"""Extract scoped English strings from Valheim localization TextAssets (static spike)."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

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


def load_scope_keys(scope_file: Path) -> list[str]:
    keys: list[str] = []
    for line in scope_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        keys.append(line)
    return keys


def load_localization_tables(resources_assets: Path) -> dict[str, dict[str, str]]:
    """Map localization key -> {asset_name, english}. First asset wins per key."""
    env = UnityPy.load(str(resources_assets))
    found: dict[str, dict[str, str]] = {}
    asset_names: list[str] = []

    for obj in env.objects:
        if obj.type.name != "TextAsset":
            continue
        data = obj.read()
        name = data.m_Name or ""
        if not name.startswith("localization"):
            continue
        asset_names.append(name)
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
            english = row[eng_idx] if eng_idx < len(row) else ""
            found[key] = {"source_asset": name, "english": english}
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--game-path",
        type=Path,
        default=Path(r"A:\Steam\steamapps\common\Valheim"),
        help="Steam Valheim install (contains valheim_Data)",
    )
    parser.add_argument(
        "--scope",
        type=Path,
        required=True,
        help="Newline-separated localization keys (see tools/scopes/)",
    )
    parser.add_argument(
        "--screen-id",
        required=True,
        help="Output screen slug, e.g. fejd-root-main-menu",
    )
    parser.add_argument(
        "--out",
        type=Path,
        required=True,
        help="Output JSON path",
    )
    args = parser.parse_args()

    resources = args.game_path / "valheim_Data" / "resources.assets"
    if not resources.is_file():
        print(f"Missing {resources}", file=sys.stderr)
        return 1

    scope_keys = load_scope_keys(args.scope)
    tables = load_localization_tables(resources)

    entries = []
    missing = []
    for key in scope_keys:
        row = tables.get(key)
        if row is None:
            missing.append(key)
            continue
        entries.append(
            {
                "key": key,
                "english": row["english"],
                "source_asset": row["source_asset"],
            }
        )

    payload = {
        "screen_id": args.screen_id,
        "screen_title": "FejdStartup root main menu",
        "scope_notes": (
            "Primary title-screen button row and same-view footer links "
            "(changelog, feedback, mod notice, etc.). Excludes character/world "
            "select, settings panels, and loading health-warning overlays."
        ),
        "scope_keys_file": str(args.scope.as_posix()),
        "extracted_at_utc": datetime.now(timezone.utc).isoformat(),
        "method": "static",
        "game_path": str(args.game_path),
        "resources_assets_sha256": sha256_file(resources),
        "key_count": len(entries),
        "entries": entries,
        "missing_keys": missing,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if missing:
        print(f"Warning: {len(missing)} scope keys not found: {', '.join(missing)}", file=sys.stderr)
    print(f"Wrote {len(entries)} keys to {args.out}")
    return 0 if not missing else 2


if __name__ == "__main__":
    raise SystemExit(main())
