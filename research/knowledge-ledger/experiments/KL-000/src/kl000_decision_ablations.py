"""The registered v1.3.0 decision ablations, ABL-R1 and ABL-R52.

Each is B5 with exactly one owner decision inverted and nothing else. They
are the positive controls for I12: the checker that clears B5 must catch
each of them at its exact registered surface (22,440 and 38,760 exhaustive
worlds), with no fixture consulted anywhere in the phase. Receipts are
re-signed after the inversion so the catch is I12's and not I6's -- these
model a *different evaluator*, not a tampered receipt.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from knowledge_ledger.transaction import canonical_bytes, evaluate_transaction  # noqa: E402


def _resign(receipt: dict) -> dict:
    unsigned = {k: v for k, v in receipt.items() if k != "contentDigest"}
    receipt["contentDigest"] = (
        "sha256:" + hashlib.sha256(canonical_bytes(unsigned)).hexdigest()
    )
    return receipt


def ablation_r1_inverted(payload: dict) -> dict:
    """R1 inverted: presence is existential -- ties and strict minorities
    conclude `supported` (the IND-20260807-1 reading)."""
    receipt = evaluate_transaction(payload)
    if receipt["claim"]["type"] == "presence":
        want = (
            "supported"
            if receipt["evidence"]["supportingRoots"]
            else "not_established"
        )
        if receipt["conclusion"] != want:
            receipt = dict(receipt)
            receipt["conclusion"] = want
            return _resign(receipt)
    return receipt


def ablation_r52_signed(payload: dict) -> dict:
    """R5.2 inverted: margin is signed, count(S) - count(O) (the
    IND-20260807-1/-2 reading)."""
    receipt = evaluate_transaction(payload)
    evidence = receipt["evidence"]
    signed = len(evidence["supportingRoots"]) - len(evidence["opposingRoots"])
    if signed != evidence["margin"]:
        receipt = dict(receipt)
        receipt["evidence"] = dict(evidence)
        receipt["evidence"]["margin"] = signed
        return _resign(receipt)
    return receipt


ABLATIONS = {
    "ABL-R1": ablation_r1_inverted,
    "ABL-R52": ablation_r52_signed,
}
