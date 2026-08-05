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
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
