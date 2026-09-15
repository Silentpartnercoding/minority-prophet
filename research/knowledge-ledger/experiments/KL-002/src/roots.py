"""KL-002 first gate — root assignment under two competing rules.

No inference, no network, no randomness. Every function here is a total
function of its input, which is why this file reports an enumerated table and
never a rate: a rate over an authored population is a generator setting read
back (the finding KL-001's DESIGN-v0.4 already acted on).
"""

from __future__ import annotations

import hashlib
import re


def normalize(text: str) -> str:
    """Lowercase, strip punctuation, collapse whitespace.

    Deliberately generous. A stricter normalizer would split these documents
    into *more* roots, never fewer, so the gate's outcome below is the
    best case for byte identity rather than a straw man.
    """
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", "", text.lower())).strip()


def root_by_byte_identity(doc: dict) -> str:
    """ADV-004's rule: root identity IS byte identity."""
    return "sha256:" + hashlib.sha256(normalize(doc["text"]).encode()).hexdigest()[:16]


def root_by_declared_origin(doc: dict) -> str:
    """The dual ledger's rule: a document carries the origin it descends from."""
    return doc["declaredOrigin"]


RULES = {
    "byte_identity": root_by_byte_identity,
    "declared_origin": root_by_declared_origin,
}


def distinct_roots(documents: list[dict], rule: str) -> set[str]:
    assign = RULES[rule]
    return {assign(d) for d in documents if d.get("assertsClaim")}
