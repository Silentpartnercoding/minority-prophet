"""Root assignment by declared ancestry, fail-closed on unattributable input.

Shared by KL-002 (source laundering) and KL-005 (syndication), which reached the
same mechanism independently from different domains.

The repair this module is, stated against the two rules it replaces:

`byte_identity` reads the document. Twenty paraphrases of one source are twenty
distinct byte strings, so it MINTS twenty roots from one origin. Measured, not
argued: KL-002's probe records 20 roots for 1 true origin, and the resulting
false claim outscores a genuinely triple-sourced true one.

`declared_origin` reads a field the document supplies. It collapses the twenty
correctly, and relocates the trust rather than removing it: a document that lies
about its origin is believed, and ADV-001's under-declaration is untouched.

What is actually different here is not the walk -- KL-005 already walked
`derivedFrom` -- it is the treatment of a document that declares NO ancestry.
Both prior rules treat "says nothing" as "is an original", which is precisely
how laundering works: strip the provenance and every copy is promoted to a
witness. This module refuses. A document with no declared ancestry is
`unattributable`; it is not a root, it does not count toward independence, and
it cannot be aggregated. Refusing to mint an origin that has not been shown is
the same choice KL-005 already made for citation cycles, applied to the much
commoner case of silence.

That is fail-closed, and it has a real cost: a genuine original that simply never
recorded its provenance is discarded along with the laundered copies. The cost is
the point. An origin claim that costs nothing to make is worth nothing, and a
system that accepts silence as originality cannot distinguish the two.
"""

from __future__ import annotations

UNATTRIBUTABLE = None


def resolve_root(doc_id: str, documents: dict, require_origin_claim: bool = True) -> str | None:
    """Walk `derivedFrom` to a declared original.

    Returns the origin's id, or None when the chain cannot establish one:

      * a cycle -- every member's originality rests on another's, so none is an
        original;
      * a dangling ancestor -- the chain leaves the known set and cannot be
        followed;
      * no declared ancestry AND no explicit origin claim -- silence, which this
        module refuses to read as originality.

    An original declares itself with `isOriginal: True`. That is still a claim
    the document makes about itself, and this module does not verify it; what it
    removes is the DEFAULT. Claiming originality is now an act, not an omission,
    which is what makes it auditable.
    """
    seen: set[str] = set()
    current = doc_id
    while True:
        if current in seen:
            return UNATTRIBUTABLE                      # cycle
        seen.add(current)
        doc = documents.get(current)
        if doc is None:
            return UNATTRIBUTABLE                      # dangling ancestor
        parent = doc.get("derivedFrom")
        if parent is None:
            # `require_origin_claim` is the domain's default, and it is a real
            # choice rather than a knob. In news (KL-005) a report with no
            # antecedent IS first-hand reporting, so silence is originality. In
            # source laundering (KL-002) an undeclared paraphrase is exactly what
            # an adversary produces, so silence must not be. Same walk; the
            # default belongs to the domain, and each caller states its own.
            if not require_origin_claim:
                return current
            return current if doc.get("isOriginal") else UNATTRIBUTABLE
        current = parent


def independent_roots(doc_ids, documents, require_origin_claim: bool = True) -> set[str]:
    """Distinct origins among the given documents. Unattributable ones vanish."""
    roots = set()
    for doc_id in doc_ids:
        root = resolve_root(doc_id, documents, require_origin_claim)
        if root is not UNATTRIBUTABLE:
            roots.add(root)
    return roots


def partition(doc_ids, documents) -> dict:
    """Roots plus what was refused, so a caller can see the cost it is paying."""
    roots, refused = set(), []
    for doc_id in doc_ids:
        root = resolve_root(doc_id, documents)
        if root is UNATTRIBUTABLE:
            refused.append(doc_id)
        else:
            roots.add(root)
    return {"roots": sorted(roots), "unattributable": sorted(refused)}
