# What this programme has contributed to Epistemic CI, and what it has not

`Silentpartnercoding/epistemic-ci` is a vendor-neutral meta-validation gate: a
test for the tests. Its v0 has **four** checks — **Vacuous Test** (planted defects
must make verification fail), **Executable Pass Condition** (corrupted outputs
must make the checker fail), **Observation Surface** (a positive population
count, a population fingerprint and a result fingerprint bound to one run id),
and **Final Artifact Binding** (a detached receipt naming and hashing every
declared final artifact, with the verifier rejecting each alteration).

An earlier version of this file said three. Final Artifact Binding was already
shipped when it was written, so the omission was in this summary, not in the
tool.

This programme's failure modes are the obvious source of candidate checks, so
this file records which have been logged there, which are already covered, and
which are deliberately not proposed. Its purpose is to stop the same defect being
proposed twice and to stop local findings quietly failing to travel.

## Logged as proposals

| issue | failure mode | why v0 misses it |
|---|---|---|
| [#2](https://github.com/Silentpartnercoding/epistemic-ci/issues/2) **Effect Reachability** | a population that cannot exhibit the effect its endpoint measures | Observation Surface requires `count > 0`; a positive, fingerprinted population can still contain zero instances of the condition the claim is about |
| [#3](https://github.com/Silentpartnercoding/epistemic-ci/issues/3) **Control Discrimination** | a must-be-nonzero control firing on every eligible input | Vacuous asks whether a defect causes failure, never whether correctness differs from incorrectness |
| [#4](https://github.com/Silentpartnercoding/epistemic-ci/issues/4) **Evidential Independence** | a test that is a corollary of another, cited as separate evidence | implication is invisible to plant-a-defect checks: the implied test *does* fail when the implying one fails, and that correlation reads as health |

Each carries the worked instance that produced it, the expected failure
condition, and a minimal fixture, per CONTRIBUTING.

## Merged upstream

| change | failure mode | how it was found |
|---|---|---|
| [#11](https://github.com/Silentpartnercoding/epistemic-ci/pull/11) **assurance bound** | a green run whose verifier never reads the verdict it verifies | RUN-20260810-1, internal adversarial review: a verifier checking only that its input is non-empty passes all four checks, then accepts a flipped verdict |

Reported rather than enforced. Whether a declared mutation set is representative
cannot be decided without knowing which defects matter, which is the thing under
study — so every result now states its own bound in machine-readable form instead
of a check pretending to close it.

**The recurrence matters more than the finding.** This programme found the same
blind spot in its own immunity ablation on the same day (`FINDING-BL058B.md`): two
grossly broken implementations pass, because mutation selection determines what is
learned. Two separately written codebases, one shared weakness.

## Already covered by v0 — deliberately not proposed

- **A checker that accepts corrupted output.** Executable Pass Condition.
- **A checker red on correct output.** Executable Pass Condition confirms the
  checker accepts fresh output before corrupting anything. The local variant of
  this defect — a registration's *invalidation clause* firing at p ≈ 3.7 × 10⁻⁹,
  red on a correct run — is a registration concern rather than a verification-path
  one, and is handled locally by the mutation harness.
- **Unverifiable claims about what was measured.** Observation Surface.

## Found here, not proposed, and why

- **Pass conditions incorporated by reference to unshipped documents** — real, and
  it cost a commission its regression arm, but it is a packaging property rather
  than a property of the verification path. Handled locally by the pre-flight's
  closure trap.
- **Withheld values published before a blind commission is answered** — specific
  to preregistered commissioning, not general research CI.
- **A control that silently stops covering something** — a sidecar naming pattern
  that skipped a real registration, a collision floor that quietly dropped values.
  Generalises poorly into a config-driven check; the discipline is to report
  reduced coverage rather than to detect it automatically.

## Rule

A defect found here that is a property of the **verification path** belongs
upstream. One that is a property of **this programme's registration discipline**
stays local. When in doubt it is logged upstream with the scope stated, because
an unlogged finding travels nowhere.
