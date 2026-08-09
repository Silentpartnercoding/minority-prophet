"""Transparent parent recovery from incomplete edges plus weak provenance."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Iterable

from experiments.lir1.infer import jaccard, roots_from_parents, temporal_score, timestamp_seconds


@dataclass(frozen=True)
class Configuration:
    author_min_score: float
    author_margin: float
    fallback: str

    @property
    def identifier(self) -> str:
        return (
            f"author-{self.author_min_score:.2f}-margin-{self.author_margin:.2f}"
            f"-fallback-{self.fallback}"
        )


CONFIGURATIONS = tuple(
    Configuration(author_score, margin, fallback)
    for author_score in (0.00, 0.25, 0.45, 0.65)
    for margin in (0.00, 0.10, 0.20)
    for fallback in ("none", "mention", "mention-text")
)
TEXT_FALLBACK_THRESHOLD = 0.75
MENTION_FALLBACK_THRESHOLD = 0.45


def _metadata(row: dict[str, Any]) -> dict[str, Any]:
    value = row.get("channel_metadata")
    return value if isinstance(value, dict) else {}


def provenance_score(child: dict[str, Any], candidate: dict[str, Any]) -> float:
    child_meta, candidate_meta = _metadata(child), _metadata(candidate)
    url_overlap = bool(
        set(child_meta.get("url_domains") or [])
        & set(candidate_meta.get("url_domains") or [])
    )
    hashtag_overlap = bool(
        set(child_meta.get("hashtags") or [])
        & set(candidate_meta.get("hashtags") or [])
    )
    return (
        0.70 * jaccard(child.get("text"), candidate.get("text"))
        + 0.20 * temporal_score(child, candidate)
        + 0.06 * url_overlap
        + 0.04 * hashtag_overlap
    )


def _ranked(
    child: dict[str, Any], candidates: list[dict[str, Any]]
) -> list[tuple[float, str]]:
    return sorted(
        ((provenance_score(child, row), row["claim_id"]) for row in candidates),
        key=lambda item: (-item[0], item[1]),
    )


def _confident(
    ranked: list[tuple[float, str]], *, minimum: float, margin: float
) -> str | None:
    if not ranked or ranked[0][0] < minimum:
        return None
    runner_up = ranked[1][0] if len(ranked) > 1 else 0.0
    if ranked[0][0] - runner_up < margin:
        return None
    return ranked[0][1]


def infer_parents(
    features: Iterable[dict[str, Any]], *, configuration: Configuration
) -> dict[str, str | None]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in features:
        grouped[(row["dataset"], row["case_id"])].append(row)
    predictions: dict[str, str | None] = {}
    for rows in grouped.values():
        rows.sort(
            key=lambda row: (
                timestamp_seconds(row["timestamp"]) or float("-inf"),
                row["claim_id"],
            )
        )
        seen: dict[str, dict[str, Any]] = {}
        for child in rows:
            exposed = [parent for parent in child["observed_parents"] if parent in seen]
            if exposed:
                predictions[child["claim_id"]] = sorted(exposed)[0]
                seen[child["claim_id"]] = child
                continue
            metadata = _metadata(child)
            reply_author = metadata.get("reply_target_author_id")
            candidates = [
                row
                for row in seen.values()
                if row["proposition_id"] == child["proposition_id"]
            ]
            author_candidates = [row for row in candidates if row.get("author_id") == reply_author]
            predicted = _confident(
                _ranked(child, author_candidates),
                minimum=configuration.author_min_score,
                margin=configuration.author_margin,
            )
            if predicted is None and reply_author and configuration.fallback != "none":
                mentions = set(metadata.get("mentioned_author_ids") or [])
                mention_candidates = [row for row in candidates if row.get("author_id") in mentions]
                predicted = _confident(
                    _ranked(child, mention_candidates),
                    minimum=MENTION_FALLBACK_THRESHOLD,
                    margin=configuration.author_margin,
                )
            if predicted is None and reply_author and configuration.fallback == "mention-text":
                predicted = _confident(
                    _ranked(child, candidates),
                    minimum=TEXT_FALLBACK_THRESHOLD,
                    margin=configuration.author_margin,
                )
            predictions[child["claim_id"]] = predicted
            seen[child["claim_id"]] = child
    return predictions


def infer_roots(
    features: Iterable[dict[str, Any]], *, configuration: Configuration
) -> dict[str, str]:
    return roots_from_parents(infer_parents(features, configuration=configuration))
