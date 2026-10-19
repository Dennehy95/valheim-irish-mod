"""Data models for LLM batch review responses."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

Status = Literal["good", "needs_improvement", "wrong"]
VALID_STATUSES = frozenset({"good", "needs_improvement", "wrong"})


@dataclass
class SlimEntry:
    key: str
    english: str
    irish: str


@dataclass
class ReviewResult:
    key: str
    status: Status
    irish_suggested: str | None = None
    reason: str = ""


@dataclass
class AuditLine:
    key: str
    english: str
    irish_original: str
    status: Status
    irish_suggested: str | None
    reason: str
    batch_id: int

    def to_json(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "english": self.english,
            "irish_original": self.irish_original,
            "status": self.status,
            "irish_suggested": self.irish_suggested,
            "reason": self.reason,
            "batch_id": self.batch_id,
        }


@dataclass
class Checkpoint:
    input_path: str
    batch_size: int
    model: str
    provider: str
    completed_batch_ids: list[int] = field(default_factory=list)
    total_batches: int = 0
    total_entries: int = 0

    def to_json(self) -> dict[str, Any]:
        return {
            "input_path": self.input_path,
            "batch_size": self.batch_size,
            "model": self.model,
            "provider": self.provider,
            "completed_batch_ids": sorted(self.completed_batch_ids),
            "total_batches": self.total_batches,
            "total_entries": self.total_entries,
        }

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> Checkpoint:
        return cls(
            input_path=data["input_path"],
            batch_size=int(data["batch_size"]),
            model=data["model"],
            provider=data.get("provider", "openrouter"),
            completed_batch_ids=list(data.get("completed_batch_ids", [])),
            total_batches=int(data.get("total_batches", 0)),
            total_entries=int(data.get("total_entries", 0)),
        )


def parse_batch_response(payload: dict[str, Any], expected_keys: set[str]) -> list[ReviewResult]:
    reviews = payload.get("reviews")
    if not isinstance(reviews, list):
        raise ValueError("Response JSON must contain a 'reviews' array")

    seen: set[str] = set()
    results: list[ReviewResult] = []
    for idx, item in enumerate(reviews):
        if not isinstance(item, dict):
            raise ValueError(f"reviews[{idx}] must be an object")
        key = item.get("key")
        if not key or not isinstance(key, str):
            raise ValueError(f"reviews[{idx}] missing string 'key'")
        status = item.get("status")
        if status not in VALID_STATUSES:
            raise ValueError(f"reviews[{idx}] invalid status: {status!r}")
        irish_suggested = item.get("irish_suggested")
        if irish_suggested is not None and not isinstance(irish_suggested, str):
            raise ValueError(f"reviews[{idx}] irish_suggested must be string or null")
        reason = item.get("reason", "")
        if not isinstance(reason, str):
            raise ValueError(f"reviews[{idx}] reason must be a string")
        if status == "good" and irish_suggested:
            irish_suggested = None
        seen.add(key)
        results.append(
            ReviewResult(
                key=key,
                status=status,
                irish_suggested=irish_suggested,
                reason=reason.strip(),
            )
        )

    missing = expected_keys - seen
    extra = seen - expected_keys
    if missing or extra:
        parts = []
        if missing:
            parts.append(f"missing keys: {sorted(missing)[:5]}{'...' if len(missing) > 5 else ''}")
        if extra:
            parts.append(f"unexpected keys: {sorted(extra)[:5]}{'...' if len(extra) > 5 else ''}")
        raise ValueError("; ".join(parts))

    return results
