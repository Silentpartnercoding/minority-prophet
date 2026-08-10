# Internal adversarial review — first pass

> **THIS IS NOT AN INDEPENDENT AUDIT.** It was performed by an agent directed by
> the repository owner. Under `AGENTS.md` rule 2, that is **one control domain**,
> and under rule 3 the result is **internal replication, not independent
> validation**. Agreement between this review and the repositories' own tests is
> not evidence of correctness. This label may not be dropped in summarisation.

**Audited commits**

    minority-prophet          427f27846e2c
    minority-prophet-gate     88a9f471f79e
    minority-prophet-border   41c1c070473f
    epistemic-ci              6870233b5e0d

**Coverage.** Stage 1 baselines across all four repositories; Stage 2 (Epistemic
CI composition); part of Stage 4 (Gate boundaries). **Border, the cross-repository
composition harness, KL-011 readiness and the claim/adoption audit are not
done.** This is a first pass, and its silence about those areas is silence, not a
clean result.

## Baselines

    minority-prophet   353 passed, 8 skipped        chain verified; sweep clean (1.41M lines)
    gate                82 passed, 177 subtests
    border              57 passed, 1 skipped
    epistemic-ci        33 passed, 7 skipped        skips are github-app extras; a
                                                    dedicated CI job installs them and runs them

No baseline failures. No target code was modified to obtain a green baseline.

## Findings

**ECI-01 — ASSURANCE WEAKNESS.** All four Epistemic CI checks report PASS on a
verification path that never reads the verdict it exists to verify. The verifier
checks only that its input file is non-empty; the declared mutations are the ones
it happens to catch. Demonstrated: after a green run, flipping `PASS` to `FAIL` in
both the source fixture and the generated result leaves both verifiers exiting 0.
Mutation selection is author-controlled and unconstrained, and nothing measures
whether the declared set is representative. No documented claim is falsified —
the README does say *"every **declared** defect"* — but a green "test for the
tests" is compatible with a vacuous verifier.

**GATE-01 — DOCUMENTATION GAP.** `attest.origin` is documented as *"root id this
claim descends from"* and as causing collapse *"into that family"*. Every
executable use of `origin` in the package is freshness-policy classification;
`aggregator.py` never mentions it. Collapse works only through
`attest.derived_from`. Fifty claims sharing one `origin` count as fifty
independent roots and convert a correctly-escalating tie into a proceed — the
manufactured independence `SECURITY.md` names as the central threat.

## No counterexample within the declared search

- **Deterministic deny is never overridden by evidence.** 486 combinations
  enumerated (0–8 supporting × 0–8 opposing roots × evidence-sensitive on/off ×
  three flip-budget thresholds). Zero escapes.
- **T2 copy invariance holds.** Fifty properly derived copies leave a tie at
  `escalate`.
- **Wrong-subject evidence escalates** rather than proceeding.
- **Epistemic CI's advisor security tests do run**, in a dedicated CI job that
  installs the optional dependencies. The local skip is local only.

## Two errors of my own, recorded rather than deleted

1. I tested lineage with a top-level `parent` key I invented; the real field is
   `attest.derived_from`. The "counterexample to T2" that produced was my error.
   T2 holds.
2. I ran the first Gate pass entirely under `TrustAllVerifier` without
   registering that its own docstring says it *"Provides NO security"*. Results
   from a test double cannot establish a library weakness on their own.

Both were caught by reading the source rather than by any check. Neither would
have been caught by re-running.

## Required closing statements

**1. Strongest supported positive statement.**
Gate's deterministic-deny boundary and T2 copy invariance survived every attack
attempted, including exhaustive enumeration of 486 evidence shapes against the
deny path. Within that declared space there is no counterexample.

**2. Strongest supported negative statement.**
A fully green Epistemic CI run does not exclude a verification path that ignores
the meaning of what it verifies, and the same blind spot — mutation selection
determining what is learned — was independently found in the research
repository's own immunity ablation on the same day (`FINDING-BL058B.md`). Two
separately written codebases, one shared weakness. That recurrence is stronger
evidence than either instance and suggests it is a property of mutation-based
assurance as practised here.

**3. Highest-impact reproducible counterexample.**
None against a documented claim. The closest is GATE-01: `reproductions/gate-01.py`
turns a tie into a proceed using fifty claims that share one declared origin,
contradicting the adapter's own docstring but not any theorem.

**4. Most important unresolved uncertainty.**
Whether the seams hold. Border and the end-to-end composition — identity →
admission → evidence → policy → effect — were not tested at all. Every component
result above is a component result, and the programme's own findings are mostly
about composition failures, which is exactly where nothing has been looked at yet.

**5. The single next experiment.**
Build the out-of-tree end-to-end harness and test invariant 1 alone: *allow
executes the exact bound action at most once*, under retry, reorder and
duplicate injection. It is the cheapest seam test and the one whose failure would
invalidate the most downstream claims.
