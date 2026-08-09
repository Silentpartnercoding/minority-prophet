"""Deterministic mechanics fixture. This is not the registered LLM corpus."""

from __future__ import annotations

import datetime as dt
import hashlib
from dataclasses import replace

from .model import ClaimInstance


def split_for(case_id: str, dataset: str = "lir1_fixture") -> str:
    bucket = int(hashlib.sha256(f"{dataset}|{case_id}".encode()).hexdigest(), 16) % 100
    return "development" if bucket < 20 else "confirmatory"


def build_fixture(cases: int = 40) -> list[ClaimInstance]:
    claims: list[ClaimInstance] = []
    base = dt.datetime(2026, 1, 1, tzinfo=dt.timezone.utc)
    for case_number in range(cases):
        case_id = f"fixture-{case_number:03d}"
        split = split_for(case_id)
        proposition = f"fixture-proposition-{case_number:03d}"
        root_false = f"{case_id}-false-root"
        timestamp = base + dt.timedelta(days=case_number)

        for observer in range(3):
            claim_id = f"{case_id}-true-{observer}"
            claims.append(ClaimInstance(
                dataset="lir1_mechanics_fixture", case_id=case_id, claim_id=claim_id,
                proposition_id=proposition,
                text=f"sensor{observer} positive{observer} datum{case_number} unique{observer}",
                timestamp=(timestamp + dt.timedelta(minutes=observer)).isoformat(),
                author_id=f"observer-{observer}", observed_parents=(), content_truth="true",
                independence_label="independent", true_root_id=claim_id,
                label_basis="constructed_exact", label_scope="record_root", split=split,
                channel_metadata={"asserted_value": True},
            ))

        claims.append(ClaimInstance(
            dataset="lir1_mechanics_fixture", case_id=case_id, claim_id=root_false,
            proposition_id=proposition,
            text=f"shared false report marker{case_number} says the proposition is false",
            timestamp=(timestamp + dt.timedelta(minutes=4)).isoformat(), author_id="false-origin",
            observed_parents=(), content_truth="true", independence_label="independent",
            true_root_id=root_false, label_basis="constructed_exact", label_scope="record_root",
            split=split, channel_metadata={"asserted_value": False},
        ))
        for copy_number in range(8):
            claim_id = f"{case_id}-copy-{copy_number}"
            claims.append(ClaimInstance(
                dataset="lir1_mechanics_fixture", case_id=case_id, claim_id=claim_id,
                proposition_id=proposition,
                text=(f"shared false report marker{case_number} says proposition false "
                      f"edition {copy_number}"),
                timestamp=(timestamp + dt.timedelta(minutes=5 + copy_number)).isoformat(),
                author_id=f"copier-{copy_number}", observed_parents=(root_false,),
                content_truth="true", independence_label="mutated_copy", true_root_id=root_false,
                label_basis="constructed_exact", label_scope="record_root", split=split,
                channel_metadata={"asserted_value": False},
            ))
    return claims


def hide_edges(claims: list[ClaimInstance], fraction: float) -> list[ClaimInstance]:
    result: list[ClaimInstance] = []
    cutoff = int(fraction * (2**256 - 1))
    for claim in claims:
        if not claim.observed_parents:
            result.append(claim)
            continue
        digest = hashlib.sha256(
            f"{claim.dataset}|{claim.case_id}|{claim.claim_id}|20260808".encode()
        ).hexdigest()
        result.append(replace(claim, observed_parents=() if int(digest, 16) <= cutoff else claim.observed_parents))
    return result
