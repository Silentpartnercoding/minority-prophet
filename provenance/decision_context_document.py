"""Read the decision-context document form, which nothing ever parsed.

`provenance/decision-context.schema.json` has existed since v0.1 and had no
reader. Every decision this corpus has scored was scored on a `DecisionContext`
built in Python by an experiment harness — `experiments/dri1`, `dri2`, `dri3`,
`dri8`, `dri9`. The declared document form, the one an outside caller would
actually send, could not be relied on by anyone because nothing consumed it.

WHY THIS IS A SEPARATE MODULE, and not a function added to `decision_relative`:

`provenance/decision_relative.py` is a pinned frozen input of nine preregistered
experiments — DRI-3, 4, 5, 6, 8, 9, 10, 11 and AID-2. Each runner records that
file's SHA-256 in its `PINNED` map, and `verify_pins()` refuses to run if the
digest has moved. Those digests are the evidence that each experiment ran
against exactly that code.

Adding even a purely additive function to that file changes its digest and
breaks all nine. Re-deriving the pins to make the failure go away would be
worse than the failure: it would make the record assert that experiments frozen
weeks ago ran against code written afterwards. The pins are not a build
inconvenience to be routed around; they are the thing that makes a frozen result
mean anything.

So the loader lives here and imports what it needs. `DecisionContext` is
unchanged, unmoved, and still pinned at the digest those nine experiments were
frozen against.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping

from provenance.decision_relative import DecisionContext, DecisionContextError

#: The document form this module consumes, from
#: `provenance/decision-context.schema.json`.
DECISION_CONTEXT_SCHEMA = "minority-prophet.decision-context.v0.1"

#: Keys the schema permits. It sets `additionalProperties: false`, so an unknown
#: key is a malformed document rather than a tolerated extension — and silently
#: ignoring one would mean discarding a policy fact the caller believed it had
#: declared.
CONTEXT_KEYS = frozenset({
    "schema", "decision_id", "proposition_id", "failure_domain",
    "independence_cut", "minimum_winning_roots", "consequence", "reversibility",
    "cut_selection_basis", "candidate_cuts",
})

#: Required by the document, which is stricter than the dataclass. `consequence`
#: and `reversibility` carry defaults in Python so an in-process caller can
#: construct a context without ceremony; a document that omits them has failed to
#: declare policy facts the schema demands, and defaulting them here would invent
#: the declaration rather than read it.
CONTEXT_REQUIRED = (
    "schema", "decision_id", "proposition_id", "failure_domain",
    "independence_cut", "minimum_winning_roots", "consequence", "reversibility",
    "cut_selection_basis",
)

_TEXT_FIELDS = (
    "decision_id", "proposition_id", "failure_domain", "independence_cut",
    "consequence", "reversibility", "cut_selection_basis",
)


def decision_context_from_document(document: Mapping[str, object]) -> DecisionContext:
    """Read a decision-context document into a `DecisionContext`.

    Fails closed on anything it cannot read as written. A decision context states
    which independence cut a decision turns on; guessing at a malformed one would
    substitute this module's judgement for the caller's declaration, which is the
    single thing `decision_relative`'s own docstring promises never to do.
    """
    if not isinstance(document, Mapping):
        raise DecisionContextError("decision context document must be an object")

    unknown = sorted(set(document) - CONTEXT_KEYS)
    if unknown:
        raise DecisionContextError(
            "unpermitted decision context keys: " + ", ".join(unknown)
        )
    missing = [key for key in CONTEXT_REQUIRED if key not in document]
    if missing:
        raise DecisionContextError(
            "decision context document requires " + ", ".join(missing)
        )
    if document["schema"] != DECISION_CONTEXT_SCHEMA:
        raise DecisionContextError(
            f"unsupported decision context schema {document['schema']!r}"
        )

    minimum = document["minimum_winning_roots"]
    # `isinstance(True, int)` is True, and a bool here would silently become a
    # threshold of one. The schema says integer.
    if isinstance(minimum, bool) or not isinstance(minimum, int):
        raise DecisionContextError("minimum_winning_roots must be an integer")

    candidates = document.get("candidate_cuts", ())
    if isinstance(candidates, (str, bytes)) or not isinstance(candidates, Iterable):
        raise DecisionContextError("candidate_cuts must be an array of strings")
    candidate_cuts = tuple(str(cut) for cut in candidates)
    if len(set(candidate_cuts)) != len(candidate_cuts):
        raise DecisionContextError("candidate_cuts must be unique")

    for key in _TEXT_FIELDS:
        if not isinstance(document[key], str):
            raise DecisionContextError(f"{key} must be a string")

    try:
        return DecisionContext(
            decision_id=str(document["decision_id"]),
            proposition_id=str(document["proposition_id"]),
            failure_domain=str(document["failure_domain"]),
            independence_cut=str(document["independence_cut"]),
            minimum_winning_roots=minimum,
            consequence=str(document["consequence"]),
            reversibility=str(document["reversibility"]),
            cut_selection_basis=str(document["cut_selection_basis"]),
            candidate_cuts=candidate_cuts,
        )
    except ValueError as exc:
        # The dataclass already enforces the semantic rules. Re-raised as the
        # adapter's own error so a caller reading a document catches one type.
        raise DecisionContextError(str(exc)) from exc
