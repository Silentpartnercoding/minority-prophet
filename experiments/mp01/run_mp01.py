"""Run the canonical six-agent false-consensus demonstration.

This is a deterministic teaching fixture, not a real-world finding and not a
truth oracle. It demonstrates one narrow property: when recorded ancestry says
that five claims descend from one root, five claims must not be presented as
five independent observations.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from aggregation.root_vote import Verdict, verdict
from provenance.graph import EvidenceGraph, EvidenceNode


WORLD_ID = "MP.01-CANONICAL-6A"
FIXED_TIME = "2026-08-15T00:00:00+00:00"


@dataclass(frozen=True)
class CollapsedClaim:
    """The proposition value associated with one reconstructed evidence root."""

    value: bool
    root_id: str
    independence_basis: str


def _node(
    node_id: str,
    *,
    answer_b: bool,
    source_id: str,
    copied_from: tuple[str, ...] = (),
    transformation: str | None = None,
) -> EvidenceNode:
    return EvidenceNode(
        node_id=node_id,
        proposition_id="candidate-answer-b",
        value=answer_b,
        observer_id=node_id.replace("claim-", "agent-"),
        source_id=source_id,
        confidence=0.8,
        evidence={"uri": f"urn:mp:synthetic:{source_id}"},
        copied_from=copied_from,
        transformations=(transformation,) if transformation else (),
        timestamp=FIXED_TIME,
    )


def build_graph() -> EvidenceGraph:
    """Build the same declared ancestry shown in the public demonstration."""

    graph = EvidenceGraph()
    for node in (
        _node("claim-a1", answer_b=False, source_id="source-x"),
        _node(
            "claim-a2",
            answer_b=False,
            source_id="source-x",
            copied_from=("claim-a1",),
            transformation="agent-transfer",
        ),
        _node(
            "claim-a3",
            answer_b=False,
            source_id="source-x",
            copied_from=("claim-a1",),
            transformation="source-summary",
        ),
        _node(
            "claim-a4",
            answer_b=False,
            source_id="source-x",
            copied_from=("claim-a2",),
            transformation="agent-summary",
        ),
        _node(
            "claim-a5",
            answer_b=False,
            source_id="source-x",
            copied_from=("claim-a3",),
            transformation="publication-paraphrase",
        ),
        _node("claim-b1", answer_b=True, source_id="source-y"),
    ):
        graph.add(node)
    return graph


def run() -> dict[str, Any]:
    graph = build_graph()
    nodes = graph.nodes()
    naive_a = sum(not node.value for node in nodes)
    naive_b = sum(node.value for node in nodes)

    collapsed: list[CollapsedClaim] = []
    seen: set[str] = set()
    for node in nodes:
        for root_id in graph.roots(node.node_id):
            if root_id in seen:
                continue
            seen.add(root_id)
            collapsed.append(
                CollapsedClaim(
                    value=next(item.value for item in nodes if item.node_id == root_id),
                    root_id=root_id,
                    independence_basis="declared",
                )
            )

    root_result = verdict(collapsed)
    if root_result.verdict is not Verdict.ABSTAIN:
        raise AssertionError("the canonical 1:1 evidence-root fixture must abstain")

    result: dict[str, Any] = {
        "schema_version": "mp.demo.v1",
        "status": "SYNTHETIC_DEMONSTRATION",
        "world_id": WORLD_ID,
        "question": "Which answer has more independent recorded support?",
        "agent_votes": {
            "answer_a": naive_a,
            "answer_b": naive_b,
            "naive_result": "answer_a",
        },
        "recorded_lineage": [
            {
                "claim_id": node.node_id,
                "agent_id": node.observer_id,
                "asserted_answer": "answer_b" if node.value else "answer_a",
                "derived_from": list(node.copied_from),
                "evidence_roots": sorted(graph.roots(node.node_id)),
            }
            for node in nodes
        ],
        "independent_evidence": {
            "answer_a": sorted(root_result.support_false),
            "answer_b": sorted(root_result.support_true),
            "effective_ratio": "1:1",
        },
        "epistemic_assessment": {
            "verdict": root_result.verdict.value,
            "reason": "The recorded 5:1 agent majority collapses to a 1:1 evidence-root tie.",
            "interventions": ["PRESERVE_MINORITY", "REQUIRE_INDEPENDENT_SOURCE"],
        },
        "claim_boundary": (
            "This fixture shows dependence collapse under declared ancestry. "
            "It does not prove either answer true or infer hidden real-world copying."
        ),
    }
    canonical = json.dumps(result, sort_keys=True, separators=(",", ":")).encode()
    result["result_hash"] = "sha256:" + hashlib.sha256(canonical).hexdigest()
    return result


def main() -> None:
    print(json.dumps(run(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

