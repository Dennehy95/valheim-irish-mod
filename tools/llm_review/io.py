"""Load slim exports and write audit artifacts."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from .models import AuditLine, Checkpoint, SlimEntry, Status


def load_slim_entries(path: Path) -> list[SlimEntry]:
    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        return []
    if path.suffix.lower() == ".jsonl":
        rows = [json.loads(line) for line in raw.splitlines() if line.strip()]
    else:
        data = json.loads(raw)
        if not isinstance(data, list):
            raise ValueError(f"{path}: expected JSON array")
        rows = data
    entries: list[SlimEntry] = []
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("Each slim row must be an object")
        entries.append(
            SlimEntry(
                key=str(row.get("key", "")),
                english=str(row.get("english", "")),
                irish=str(row.get("irish", "")),
            )
        )
    return entries


def append_audit_line(audit_path: Path, line: AuditLine) -> None:
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    with audit_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(line.to_json(), ensure_ascii=False) + "\n")


def load_audit_lines(audit_path: Path) -> list[AuditLine]:
    if not audit_path.is_file():
        return []
    lines: list[AuditLine] = []
    for raw in audit_path.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        d = json.loads(raw)
        lines.append(
            AuditLine(
                key=d["key"],
                english=d["english"],
                irish_original=d["irish_original"],
                status=d["status"],
                irish_suggested=d.get("irish_suggested"),
                reason=d.get("reason", ""),
                batch_id=int(d["batch_id"]),
            )
        )
    return lines


def write_summary(audit_lines: list[AuditLine], path: Path) -> None:
    counts = Counter(line.status for line in audit_lines)
    payload = {
        "total": len(audit_lines),
        "by_status": {s: counts.get(s, 0) for s in ("good", "needs_improvement", "wrong")},
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_checkpoint(path: Path, checkpoint: Checkpoint) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(checkpoint.to_json(), indent=2) + "\n", encoding="utf-8")


def load_checkpoint(path: Path) -> Checkpoint | None:
    if not path.is_file():
        return None
    return Checkpoint.from_json(json.loads(path.read_text(encoding="utf-8")))


def build_corrected_slim(
    entries: list[SlimEntry],
    audit_by_key: dict[str, AuditLine],
    include_needs_improvement: bool,
) -> list[dict[str, str]]:
    corrected: list[dict[str, str]] = []
    for entry in entries:
        audit = audit_by_key.get(entry.key)
        if not audit:
            continue
        if audit.status == "good":
            continue
        if audit.status == "needs_improvement" and not include_needs_improvement:
            continue
        irish = entry.irish
        if audit.irish_suggested:
            irish = audit.irish_suggested
        corrected.append({"key": entry.key, "english": entry.english, "irish": irish})
    return corrected


def write_json_array(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
