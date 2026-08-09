"""Deterministic missingness, collision, and white-box misbinding attacks."""

from __future__ import annotations

import hashlib
from collections import defaultdict
from dataclasses import replace
from typing import Iterable

from experiments.lir1.infer import timestamp_seconds
from experiments.lir1.model import ClaimInstance
from experiments.lir1.synthetic_fixture import hide_edges
from experiments.lir3.provenance_parent import provenance_score


ATTACK_SALT = "minority-prophet-lir4-identity-attack-v1"


def visible_edges(claims: list[ClaimInstance]) -> list[ClaimInstance]:
    return hide_edges(claims, 0.40)


def _selected(claim: ClaimInstance, attack: str, fraction: float) -> bool:
    if fraction <= 0:
        return False
    if fraction >= 1:
        return True
    cutoff = int(fraction * (2**256 - 1))
    digest = hashlib.sha256(
        f"{ATTACK_SALT}|{attack}|{claim.dataset}|{claim.case_id}|{claim.claim_id}".encode()
    ).hexdigest()
    return int(digest, 16) <= cutoff


def _is_hidden_edge(original: ClaimInstance, visible: ClaimInstance) -> bool:
    return bool(original.observed_parents) and not visible.observed_parents


def remove_reply_identity(
    original: list[ClaimInstance], visible: list[ClaimInstance], *, fraction: float
) -> list[ClaimInstance]:
    originals = {claim.claim_id: claim for claim in original}
    attacked: list[ClaimInstance] = []
    for claim in visible:
        source = originals[claim.claim_id]
        metadata = dict(claim.channel_metadata)
        if _is_hidden_edge(source, claim) and _selected(source, "missing", fraction):
            metadata["reply_target_author_id"] = None
        attacked.append(replace(claim, channel_metadata=metadata))
    return attacked


def _collision_id(case_id: str, author_id: str | None, buckets: int) -> str | None:
    if author_id is None:
        return None
    digest = hashlib.sha256(f"{ATTACK_SALT}|collision|{case_id}|{author_id}".encode()).digest()
    return f"collision:{int.from_bytes(digest[:8], 'big') % buckets}"


def collide_identities(
    original: list[ClaimInstance], visible: list[ClaimInstance], *, buckets: int
) -> list[ClaimInstance]:
    if buckets < 1:
        raise ValueError("buckets must be positive")
    originals = {claim.claim_id: claim for claim in original}
    attacked: list[ClaimInstance] = []
    for claim in visible:
        source = originals[claim.claim_id]
        metadata = dict(claim.channel_metadata)
        metadata["reply_target_author_id"] = _collision_id(
            claim.case_id, metadata.get("reply_target_author_id"), buckets
        )
        attacked.append(
            replace(
                claim,
                author_id=_collision_id(claim.case_id, claim.author_id, buckets),
                channel_metadata=metadata,
            )
        )
    return attacked


def adversarially_misbind(
    original: list[ClaimInstance], visible: list[ClaimInstance]
) -> tuple[list[ClaimInstance], int]:
    """Point hidden edges at the best earlier author from a different true root."""
    originals = {claim.claim_id: claim for claim in original}
    grouped: dict[str, list[ClaimInstance]] = defaultdict(list)
    for claim in visible:
        grouped[claim.case_id].append(claim)
    attacked: list[ClaimInstance] = []
    eligible = 0
    for rows in grouped.values():
        rows.sort(
            key=lambda row: (
                timestamp_seconds(row.timestamp) or float("-inf"),
                row.claim_id,
            )
        )
        seen: list[ClaimInstance] = []
        for claim in rows:
            source = originals[claim.claim_id]
            cross_root = [
                candidate
                for candidate in seen
                if originals[candidate.claim_id].true_root_id != source.true_root_id
                and candidate.author_id is not None
            ]
            if _is_hidden_edge(source, claim) and cross_root:
                best = max(
                    cross_root,
                    key=lambda candidate: (
                        provenance_score(claim.feature_view(), candidate.feature_view()),
                        candidate.claim_id,
                    ),
                )
                metadata = dict(claim.channel_metadata)
                metadata["reply_target_author_id"] = best.author_id
                claim = replace(claim, channel_metadata=metadata)
                eligible += 1
            attacked.append(claim)
            seen.append(claim)
    return attacked, eligible


def count_hidden_edges(
    original: Iterable[ClaimInstance], visible: Iterable[ClaimInstance]
) -> int:
    originals = {claim.claim_id: claim for claim in original}
    return sum(_is_hidden_edge(originals[claim.claim_id], claim) for claim in visible)
