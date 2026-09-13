"""Run Minority Prophet Test v0.1."""

from __future__ import annotations

import argparse
import json

from .evaluate import evaluate
from .world import generate_worlds


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Minority Prophet Test v0.1")
    parser.add_argument("--worlds", type=int, default=500)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--independent", type=int, default=3)
    parser.add_argument("--copied", type=int, default=95)
    args = parser.parse_args()
    worlds = generate_worlds(
        count=args.worlds,
        seed=args.seed,
        independent_truth_count=args.independent,
        copied_false_count=args.copied,
    )
    report = {
        "benchmark": "Minority Prophet Test",
        "version": "0.1",
        "seed": args.seed,
        "configuration": {
            "worlds": args.worlds,
            "independent_truth_agents": args.independent,
            "copied_false_agents": args.copied,
        },
        "results": evaluate(worlds),
        "reading": {
            "world_shape": (
                f"Each world holds {args.independent} independent observers and "
                f"{args.copied} agents repeating one rumour. The rumour is always false."
            ),
            "why_the_baselines_score_zero": (
                "Zero is the expected result, not a failure. Majority and weighted "
                "voting count agents, and the copies outnumber the observers in every "
                "world, so both are wrong every time. This is the failure the "
                "benchmark exists to exhibit."
            ),
            "what_dependence_aware_does": (
                "It resolves each claim to the evidence it ultimately rests on, so the "
                f"{args.copied} repeaters collapse to the single rumour they descend "
                "from and are outweighed by the independent observers. It abstains "
                "rather than guessing when the roots are tied."
            ),
            "scope": (
                "These worlds are generated, and lineage is given rather than inferred. "
                "This demonstrates the aggregator under known provenance. It is not "
                "evidence that provenance can be recovered from real systems; see the "
                "published external validation, which returned zero coverage."
            ),
        },
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
