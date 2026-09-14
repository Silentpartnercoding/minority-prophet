"""The ontology-perturbation test — hold the phenomenon fixed, change the words.

Recorded in `canon/ORIGINS.md` as one of three ideas that never landed, and the
one with the clearest missing slot: every robustness check in this corpus
perturbs the *data*. This perturbs the *vocabulary*, and asks whether the
conclusion survives.

It is representation invariance applied to a vocabulary rather than to
coordinates, and it is a different probe from the social-pressure one in
`canon/susceptibility.py`. That one asks whether a conclusion survives other
people disagreeing. This one asks whether it survives being describable in other
words -- a conclusion that evaporates when two categories merge was a fact about
the category scheme, not about the world.

The tea wheel is the worked case. Its defect was not wrong answers. It was that a
tea departing from the expected trajectory produced no evidence rather than
contrary evidence, because there was no cell for it. Deleting a category and
finding the conclusion unchanged tells you the category was carrying nothing.
Deleting one and finding the conclusion gone tells you exactly what it was
resting on -- and that is the useful output, so results are reported
perturbation by perturbation.

**No survival score.** "Survived 6 of 8" is precisely the scalar this corpus
refuses to emit, and it is worse than useless here: the identity of the
perturbation that broke the conclusion is the finding. Two conclusions that each
survive six of eight, one failing under a merge and one failing under
translation, have nothing in common.

`INEXPRESSIBLE` is kept distinct from `OVERTURNED` throughout, for the reason
`canon/bounded_truth.py` gives: a vocabulary that cannot state the conclusion has
not disagreed with it.

The caller supplies the conclusion function. This module does not know what any
conclusion means and deliberately cannot -- it compares returned values for
equality and nothing more.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Callable, Hashable


class Kind(StrEnum):
    """Ways a vocabulary can be perturbed while the phenomenon stays fixed."""

    DROP = "drop"                 # remove a category entirely
    MERGE = "merge"               # collapse two categories into one
    SPLIT = "split"               # divide one category into two
    RENAME = "rename"             # same partition, different labels
    ADD_INSTRUMENT = "add_instrument"  # add a dimension an instrument supplies
    FREE = "free"                 # discard the scheme; let subjects invent terms
    TRANSLATE = "translate"       # express the same partition in another language


class Outcome(StrEnum):
    SURVIVED = "survived"
    OVERTURNED = "overturned"
    #: The perturbed vocabulary cannot state the conclusion. Not disagreement.
    INEXPRESSIBLE = "inexpressible"
    #: The conclusion function refused or failed. Recorded rather than swallowed,
    #: because a silently dropped perturbation reads as coverage that never ran.
    ERRORED = "errored"


#: Raised by a conclusion function to say "this vocabulary has no cell for it".
class Inexpressible(Exception):
    """The perturbed vocabulary cannot express the conclusion."""


@dataclass(frozen=True)
class Perturbation:
    """One change to the vocabulary, and the vocabulary it produces."""

    kind: Kind
    description: str
    vocabulary: frozenset[str]

    def __post_init__(self) -> None:
        if not self.description:
            raise ValueError("a perturbation must say what it changed")


@dataclass(frozen=True)
class Result:
    perturbation: Perturbation
    outcome: Outcome
    baseline: Hashable = None
    perturbed: Hashable = None
    detail: str = ""

    def report(self) -> str:
        head = f"  {self.perturbation.kind:<15} {self.outcome:<14} {self.perturbation.description}"
        if self.outcome is Outcome.OVERTURNED:
            return f"{head}\n      {self.baseline!r} -> {self.perturbed!r}"
        if self.detail:
            return f"{head}\n      {self.detail}"
        return head


@dataclass(frozen=True)
class Probe:
    """Per-perturbation results. No aggregate, by construction."""

    conclusion: str
    baseline: Hashable
    results: tuple[Result, ...]

    @property
    def overturned_by(self) -> tuple[Perturbation, ...]:
        """The finding. What the conclusion was actually resting on."""
        return tuple(r.perturbation for r in self.results
                     if r.outcome is Outcome.OVERTURNED)

    @property
    def inexpressible_under(self) -> tuple[Perturbation, ...]:
        return tuple(r.perturbation for r in self.results
                     if r.outcome is Outcome.INEXPRESSIBLE)

    @property
    def not_run(self) -> tuple[Perturbation, ...]:
        """Perturbations that errored. Surfaced so silence is never read as a pass."""
        return tuple(r.perturbation for r in self.results
                     if r.outcome is Outcome.ERRORED)

    def report(self) -> str:
        lines = [f"{self.conclusion!r}",
                 f"  baseline: {self.baseline!r}",
                 f"  {len(self.results)} perturbations run"]
        lines.extend(r.report() for r in self.results)
        if self.overturned_by:
            lines.append("  RESTING ON: " + ", ".join(
                p.description for p in self.overturned_by))
        else:
            lines.append("  no perturbation overturned it; this is not a survival "
                         "score and says nothing about perturbations not run")
        if self.not_run:
            lines.append("  NOT RUN (errored): " + ", ".join(
                p.description for p in self.not_run))
        return "\n".join(lines)


def probe(
    conclusion: str,
    conclude: Callable[[frozenset[str]], Hashable],
    vocabulary: frozenset[str],
    perturbations: list[Perturbation] | tuple[Perturbation, ...],
) -> Probe:
    """Run `conclude` under the original vocabulary and under each perturbation.

    `conclude` maps a vocabulary to a comparable conclusion value; it may raise
    `Inexpressible` to say the perturbed vocabulary has no cell for the question.
    Any other exception is recorded as ERRORED rather than swallowed.
    """
    if not perturbations:
        raise ValueError(
            "a perturbation probe with no perturbations reports nothing and "
            "would read as a pass; supply at least one"
        )
    baseline = conclude(vocabulary)

    results = []
    for p in perturbations:
        try:
            got = conclude(p.vocabulary)
        except Inexpressible as exc:
            results.append(Result(p, Outcome.INEXPRESSIBLE, baseline,
                                  detail=str(exc) or "no cell for the conclusion"))
            continue
        except Exception as exc:  # recorded, never silently dropped
            results.append(Result(p, Outcome.ERRORED, baseline,
                                  detail=f"{type(exc).__name__}: {exc}"))
            continue
        outcome = Outcome.SURVIVED if got == baseline else Outcome.OVERTURNED
        results.append(Result(p, outcome, baseline, got))

    return Probe(conclusion=conclusion, baseline=baseline, results=tuple(results))


def drop(vocabulary: frozenset[str], term: str) -> Perturbation:
    if term not in vocabulary:
        raise ValueError(f"cannot drop {term!r}: not in the vocabulary")
    return Perturbation(Kind.DROP, f"dropped {term!r}", vocabulary - {term})


def merge(vocabulary: frozenset[str], a: str, b: str, into: str) -> Perturbation:
    missing = {a, b} - vocabulary
    if missing:
        raise ValueError(f"cannot merge: {sorted(missing)} not in the vocabulary")
    return Perturbation(Kind.MERGE, f"merged {a!r} and {b!r} into {into!r}",
                        (vocabulary - {a, b}) | {into})


def split(vocabulary: frozenset[str], term: str, into: tuple[str, ...]) -> Perturbation:
    if term not in vocabulary:
        raise ValueError(f"cannot split {term!r}: not in the vocabulary")
    if len(into) < 2:
        raise ValueError("a split produces at least two terms")
    return Perturbation(Kind.SPLIT, f"split {term!r} into {', '.join(into)}",
                        (vocabulary - {term}) | set(into))


def rename(vocabulary: frozenset[str], mapping: dict[str, str]) -> Perturbation:
    """Same partition, different labels. A conclusion that does not survive this
    was about the words themselves, which is the starkest possible result."""
    missing = set(mapping) - vocabulary
    if missing:
        raise ValueError(f"cannot rename: {sorted(missing)} not in the vocabulary")
    return Perturbation(Kind.RENAME, f"relabelled {len(mapping)} terms",
                        frozenset(mapping.get(t, t) for t in vocabulary))


def add_instrument_dimension(vocabulary: frozenset[str], term: str) -> Perturbation:
    return Perturbation(Kind.ADD_INSTRUMENT, f"added instrument dimension {term!r}",
                        vocabulary | {term})


__all__ = [
    "Kind", "Outcome", "Inexpressible", "Perturbation", "Result", "Probe",
    "probe", "drop", "merge", "split", "rename", "add_instrument_dimension",
]
