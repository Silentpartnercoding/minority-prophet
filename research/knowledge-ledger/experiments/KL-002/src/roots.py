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


def root_by_declared_origin(doc: dict) -> str | None:
    """The dual ledger's rule: a document carries the origin it descends from.

    A document declaring no origin yields None rather than a root. Counting a
    missing declaration as a distinct root would let stripping the field mint
    independence, which is the laundering this experiment is about.
    """
    return doc.get("declaredOrigin") or None


def root_by_ancestry(doc: dict, documents: dict | None = None) -> str | None:
    """The repair: walk declared ancestry, and refuse silence.

    Implemented in `knowledge_ledger.ancestry` and shared with KL-005, which
    reached the same mechanism from the syndication side. A document declaring
    no ancestry is UNATTRIBUTABLE rather than an origin, which is the difference
    between this rule and the two above.
    """
    from knowledge_ledger.ancestry import resolve_root
    return resolve_root(doc["docId"], documents or {})


RULES = {
    "byte_identity": root_by_byte_identity,
    "declared_origin": root_by_declared_origin,
    "ancestry": root_by_ancestry,
}


def distinct_roots(documents: list[dict], rule: str, index: dict | None = None) -> set[str]:
    """Distinct roots under `rule`. Unattributable documents contribute none."""
    assign = RULES[rule]
    asserting = [d for d in documents if d.get("assertsClaim")]
    if rule == "ancestry":
        return {r for r in (assign(d, index or {}) for d in asserting) if r is not None}
    return {r for r in (assign(d) for d in asserting) if r is not None}


def build_index(*groups) -> dict:
    """docId -> document, plus any declared origins, for ancestry resolution."""
    index = {}
    for group in groups:
        for doc in group.get("documents", []):
            index[doc["docId"]] = doc
        origin = group.get("origin")
        if origin:
            index[origin["docId"]] = origin
    return index
