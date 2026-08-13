"""KL-014 step 2 — instrument sensitivity check.

THIS IS NOT A FINDING. It reports nothing about the world and must never be
cited as evidence for or against HRI-1. It answers one narrow question about the
measuring device, asked before the device is pointed at anything:

    can mp-root-v1 exhibit a split at all?

If the answer were no -- if the identity function collapsed everything to one
value -- then the real run would return a split factor of 1.0 for a reason that
has nothing to do with reporting behaviour, and the benign result would be an
artefact of a broken instrument rather than evidence of anything.

Per PROTOCOL.md, this runs BEFORE the corpus is declared. It uses constructed
cases whose observation count is known by construction, so no labelling is
involved and no human judgement enters.

Run:  python research/knowledge-ledger/experiments/KL-014/src/sensitivity_check.py
Exit: 0 if the instrument recovers every constructed value exactly, 1 otherwise.
"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[5]))

from provenance.root_registry import RootRegistry, RootRequest  # noqa: E402


def request(issuer: str, observation: str, proposition: str, value: bool,
            evidence: str) -> RootRequest:
    """A request carrying only the fields root_identity actually digests.

    key_id, observed_at, nonce and signature are deliberately varied nowhere:
    they are not part of the identity material, and holding them constant makes
    that visible rather than assumed.
    """
    return RootRequest(
        issuer_id=issuer,
        key_id="k1",
        observation_id=observation,
        proposition_id=proposition,
        value=value,
        evidence_digest=evidence,
        observed_at=1_000_000,
        nonce="n",
    )


def distinct_roots(requests: list[RootRequest]) -> int:
    return len({RootRegistry.root_identity(r) for r in requests})


# ---------------------------------------------------------------------------
# Constructed cases. `observations` is ground truth BY CONSTRUCTION, not by
# judgement. `expect_roots` is what the instrument must report.
# ---------------------------------------------------------------------------

CASES: list[tuple[str, list[RootRequest], int, int, str]] = [
    (
        "A. one observation, one issuer",
        [request("alice", "obs-1", "p", True, "ev-1")],
        1, 1,
        "the trivial baseline; a split factor of 1.0 that means what it says",
    ),
    (
        "B. one observation, five issuers report it",
        [request(f"outlet-{i}", f"obs-{i}", "p", True, "ev-wire")
         for i in range(5)],
        1, 5,
        "THE CASE THAT MATTERS. Five outlets, one wire report, identical "
        "evidence digest. If the instrument cannot show 5 here it cannot show "
        "a split anywhere, and a benign real-world result would be worthless.",
    ),
    (
        "C. five observations, five issuers",
        [request(f"outlet-{i}", f"obs-{i}", "p", True, f"ev-{i}")
         for i in range(5)],
        5, 5,
        "genuine independence; split factor 1.0 for the right reason",
    ),
    (
        "D. two observations, one issuer reusing an observation id",
        [request("alice", "obs-1", "p", True, "ev-1"),
         request("alice", "obs-1", "p", True, "ev-1")],
        2, 1,
        "the MERGE direction: distinct observations collapsed to one identity. "
        "Destroys margin rather than inflating it, and is reported separately.",
    ),
    (
        "E. one observation, one issuer, two evidence renderings",
        [request("alice", "obs-1", "p", True, "ev-1"),
         request("alice", "obs-1", "p", True, "ev-1-reformatted")],
        1, 2,
        "split caused purely by evidence digest instability, with no second "
        "observation anywhere. Distinct from case B in cause, identical in "
        "effect on the count.",
    ),
    (
        "F. one observation, one issuer, opposing values",
        [request("alice", "obs-1", "p", True, "ev-1"),
         request("alice", "obs-1", "p", False, "ev-1")],
        1, 2,
        "value is in the digest, so one observation reported both ways yields "
        "two roots -- one per side. Recorded because it interacts with "
        "side-consistency, not because it is expected in a clean corpus.",
    ),
]


def main() -> int:
    print("KL-014 step 2 — instrument sensitivity check")
    print("NOT A FINDING. Constructed cases only; no corpus, no labels.\n")
    print(f"{'case':<52}{'O':>3}{'R exp':>7}{'R got':>7}{'split':>8}  result")
    print("-" * 92)

    failures = 0
    for name, requests, observations, expected, _why in CASES:
        got = distinct_roots(requests)
        ok = got == expected
        failures += not ok
        split = got / observations
        print(f"{name:<52}{observations:>3}{expected:>7}{got:>7}{split:>8.2f}  "
              f"{'ok' if ok else 'MISMATCH'}")

    print("-" * 92)
    if failures:
        print(f"\nFAIL: {failures} constructed case(s) not recovered exactly.")
        print("The instrument is wrong. Per PROTOCOL.md the real run does not start.")
        return 1

    sensitive = next(got for name, reqs, _o, _e, _w in CASES
                     if name.startswith("B.")
                     for got in [distinct_roots(reqs)])
    print("\nPASS: every constructed value recovered exactly.")
    print(f"  Case B reports {sensitive} roots for 1 observation, so the "
          "instrument CAN exhibit a split.")
    print("  A split factor of 1.0 on the real corpus would therefore be a "
          "statement about\n  reporting behaviour, not an artefact of the "
          "measure.")
    print("\nThis unblocks step 3 (declare the corpus). It is not evidence "
          "about HRI-1.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
