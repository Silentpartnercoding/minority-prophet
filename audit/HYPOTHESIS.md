# Pre-work hypothesis (written before any code change)

Author: formal-methods / falsification lead
Date: 2026-08-05
Base commit: e1403a7
This hypothesis record was frozen before the remediation changes were applied.

Written after reading, and **before** modifying, the following:
`formal/PROOFS.md`, `formal/MinorityProphetV2.lean`, `FOUNDATIONS.md`,
`PROVENANCE-REQUIREMENTS.md`, `GLOSSARY.md`, `provenance/graph.py`,
`aggregation/{__init__,baselines,semantic}.py`,
`verification/independent_check_2026-08.py`.

---

## H0 — the primary hypothesis

**The theorems are arithmetically sound but are stated about a structure that
is not the structure the project actually uses, and the gap is load-bearing
in exactly the direction the project cares about.**

Three separable sub-claims, each independently testable:

### H0a — Forest vs. DAG (structural mismatch)

`PROOFS.md`, `MinorityProphetV2.lean` and `verification/independent_check_2026-08.py`
all model lineage as a **partial function** `parent : C → Option C`. That is a
**forest**: every claim has at most one parent, and `root(c)` is a *single*
claim.

`provenance/graph.py` models lineage as `copied_from : tuple[str, ...]` and
`EvidenceGraph.roots()` returns a `frozenset` — every claim has **arbitrarily
many** parents and **arbitrarily many** roots. `FOUNDATIONS.md` and the
assignment brief both say "directed acyclic evidence graph" / "directed acyclic
parent relation", i.e. a DAG.

Prediction: the forest proofs do **not** transfer verbatim; at minimum `T5`
("one edge edit moves one side's root count by exactly one") is *false* in the
DAG model, because in a DAG an edge deletion may orphan a claim that carries a
whole sub-DAG, or may not orphan it at all.

### H0b — T2 is false in its plain-English form

`PROOFS.md` T2 proves: adding `d` with `parent(d) = c` and `assert(d) =
assert(c)` changes nothing. The brief restates this as "**Adding copied claims
cannot change the verdict**."

Those are not the same statement. The proved version quantifies over copies
**whose parent edge is recorded**. A copy whose provenance is *not* recorded is
a parentless claim — i.e. a **root** — and it changes the verdict by exactly the
mechanism T4/T5 describe. Since undetected copying is the entire threat model
the project exists to address, the plain-English form is not merely loose, it
inverts the security reading.

Prediction: a two-line witness falsifies the plain-English form; the proved
form survives untouched.

### H0c — T5's security doctrine over-reaches its lemma

T5's *lemma* ("a single side-consistent edge edit that disturbs the root set
changes exactly one side's root count by exactly 1") is plausibly true in the
forest model. Its attached *doctrine* — "min_flip_budget >= 2 confers proved
immunity to any single key compromise or ops error" — silently assumes a
bijection between "real-world error" and "one edge edit". That bijection fails
for at least three ordinary events:

- deleting/losing **one claim record** orphans all of its children at once
  (unbounded root gain from a single ops error);
- compromising **one root-signing key** mints unboundedly many roots;
- one **identity merge/split** (duplicate or canonicalised IDs) changes a side
  count by more than one under set semantics.

Prediction: each is a counterexample to the *doctrine*, none to the *lemma*.
The repair is a definition change (define the error unit), not a proof change.

---

## H1 — secondary hypotheses

- **H1a (no aggregator in the product).** The verdict `F` that every theorem is
  about does not exist in `aggregation/`. The nearest artefact,
  `evidence_root_vote`, uses a *single* `root_id: str | None` per claim, silently
  drops `root_id is None` claims, and resolves duplicate root IDs by
  `setdefault` (first-writer-wins). So "implementation tests" for T1/T2/T4/T5
  is likely to be the empty set, and `evidence_root_vote` is likely
  **order-dependent** when side-consistency fails.
- **H1b (side-consistency is unenforced).** `EvidenceGraph.add` validates
  ancestry existence and ID uniqueness but never checks `value` agreement across
  an edge. R2 is a *hard requirement* in `PROVENANCE-REQUIREMENTS.md` with no
  enforcement point in code.
- **H1c (T4' is a finite check presented as a theorem).** "Theorem 4'" is
  labelled a theorem but its evidence is "exhaustive: 4,638/4,638 decisive
  worlds". Its *arithmetic* content is a one-line corollary of T4; the finite
  count adds nothing and blurs the evidence class.
- **H1d (everything factors through a 2-tuple).** Under side-consistency, `F`
  depends only on `(#true-asserting parentless claims, #false-asserting
  parentless claims)`. If so, T1/T2/T4/T4'/T5 are all corollaries of one
  factorisation lemma plus integer arithmetic, and the real content of the
  system is entirely in the *assumptions*, not the theorems.

---

## Test plan (executed before any repository change)

1. Run the existing Python suite and `independent_check_2026-08.py` verbatim;
   record exact counts and exit codes.
2. Write a standalone falsifier that (a) re-derives the forest results, (b)
   re-runs the same theorem statements in the **multi-parent DAG** model, and
   (c) brute-forces the adversarial list in the brief. Confirm or refute H0a.
3. Construct minimal witnesses for H0b and H0c by hand and check them
   mechanically.
4. Probe `evidence_root_vote` for order dependence (H1a) and `EvidenceGraph`
   for unenforced side-consistency (H1b).
5. Only then write Lean, formalising whichever model survives step 2.

Falsification of this hypothesis is a valid and reportable outcome.
