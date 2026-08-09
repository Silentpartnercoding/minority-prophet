"""Strict claim model and leakage-safe feature projection for LIR-1."""

from __future__ import annotations

import datetime as dt
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable


LABEL_BASES = {
    "constructed_exact",
    "explicit_edge",
    "adjudicated_lineage",
    "heuristic_proxy",
    "unknown",
}
LABEL_SCOPES = {
    "content_truth",
    "direct_parent",
    "record_root",
    "evidence_independence",
    "none",
}


@dataclass(frozen=True)
class ClaimInstance:
    dataset: str
    case_id: str
    claim_id: str
    proposition_id: str
    text: str | None
    timestamp: str | None
    author_id: str | None
    observed_parents: tuple[str, ...]
    content_truth: str
    independence_label: str
    true_root_id: str | None
    label_basis: str
    label_scope: str
    split: str
    channel_metadata: dict[str, Any]
    schema: str = "minority-prophet.lir1-claim-instance.v1"

    def validate(self) -> None:
        if self.schema != "minority-prophet.lir1-claim-instance.v1":
            raise ValueError("unexpected claim schema")
        for field in (self.dataset, self.case_id, self.claim_id, self.proposition_id):
            if not field:
                raise ValueError("claim identity fields must be non-empty")
        if len(set(self.observed_parents)) != len(self.observed_parents):
            raise ValueError("observed parents must be unique")
        if self.claim_id in self.observed_parents:
            raise ValueError("a claim cannot parent itself")
        if self.content_truth not in {"true", "false", "unresolved", "not_applicable"}:
            raise ValueError("invalid content truth")
        if self.independence_label not in {"independent", "copy", "mutated_copy", "unknown"}:
            raise ValueError("invalid independence label")
        if self.label_basis not in LABEL_BASES or self.label_scope not in LABEL_SCOPES:
            raise ValueError("invalid label provenance")
        if self.split not in {"development", "confirmatory"}:
            raise ValueError("invalid split")
        if self.timestamp is not None:
            parsed = dt.datetime.fromisoformat(self.timestamp.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                raise ValueError("timestamp must include a timezone")
        if self.true_root_id is not None and self.label_basis in {"heuristic_proxy", "unknown"}:
            raise ValueError("proxy or unknown labels cannot assert a true root")

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["observed_parents"] = list(self.observed_parents)
        value["schema"] = self.schema
        return value

    def feature_view(self) -> dict[str, Any]:
        """Return only fields an inference method is allowed to observe."""
        return {
            "schema": self.schema,
            "dataset": self.dataset,
            "case_id": self.case_id,
            "claim_id": self.claim_id,
            "proposition_id": self.proposition_id,
            "text": self.text,
            "timestamp": self.timestamp,
            "author_id": self.author_id,
            "observed_parents": list(self.observed_parents),
            "channel_metadata": {
                key: value
                for key, value in self.channel_metadata.items()
                if not key.startswith("label_") and not key.startswith("true_")
            },
        }


def write_jsonl(path: Path, claims: Iterable[ClaimInstance]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for claim in claims:
            claim.validate()
            handle.write(json.dumps(claim.to_dict(), sort_keys=True, separators=(",", ":")))
            handle.write("\n")


def read_jsonl(path: Path) -> list[ClaimInstance]:
    claims: list[ClaimInstance] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            raw = json.loads(line)
            raw["observed_parents"] = tuple(raw["observed_parents"])
            claim = ClaimInstance(**raw)
            try:
                claim.validate()
            except ValueError as exc:
                raise ValueError(f"{path}:{line_number}: {exc}") from exc
            claims.append(claim)
    return claims
