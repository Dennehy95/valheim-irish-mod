"""Read tools/scopes/*.keys.txt — header comments only, not keys like #piece_foo."""

from __future__ import annotations

from pathlib import Path


def is_scope_header_comment(line: str) -> bool:
    """True for `# ...` scope headers, not localization keys that start with `#`."""
    if not line.startswith("#"):
        return False
    return len(line) == 1 or line[1] in " \t"


def load_scope_keys(scope_file: Path) -> list[str]:
    keys: list[str] = []
    for line in scope_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or is_scope_header_comment(line):
            continue
        keys.append(line)
    return keys


def load_scope_key_set(paths: list[Path]) -> set[str]:
    wired: set[str] = set()
    for path in paths:
        wired.update(load_scope_keys(path))
    return wired
