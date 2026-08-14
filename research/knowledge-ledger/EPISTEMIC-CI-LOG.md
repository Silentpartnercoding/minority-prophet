# What this programme has contributed to Epistemic CI, and what it has not

`Silentpartnercoding/epistemic-ci` is a vendor-neutral meta-validation gate: a
test for the tests. Its v0 has **eight** checks — **Vacuous Test**, **Executable
Pass Condition**, **Observation Surface**, **Final Artifact Binding**, **Pinned
Input Binding**, **Control Discrimination**, **Evidential Independence** and
**Effect Reachability**.

This file has now stated the wrong number three times — three, four, and five —
each after checks had already shipped. Twice the cause was this programme's own
contribution landing upstream without the summary following it.

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

## Merged upstream — checks 5 to 8

| change | failure mode | how it was found |
|---|---|---|
| [#13](https://github.com/Silentpartnercoding/epistemic-ci/pull/13) **Pinned Input Binding** | a runner that declares its results came from specific bytes while reading whatever is in the workspace | `evaluations/multi-model-v1/canonical-capability-runner.py` pinned two files at commit `41911af`, recorded their digests in `CAPABILITY-TOURNAMENT-V1-SUMMARY.json`, and then hashed and executed the **working-tree** copies |

**Why v0 missed it.** All four existing checks share one polarity: mutate
something, verification must fail. They establish that checking is *sensitive* to
corruption. This defect is the other half — a pinned input must be *insensitive*
to workspace corruption, because the run should never read it. Sensitivity in the
wrong place is a defect, and a silent one: every recorded digest still matches,
since the digest is taken of the same copy that was executed.

**Reconciliation, since the two rules appear to contradict.** They partition the
inputs rather than ranking the checks: a *live* input is read from the workspace
and Vacuous Test is correct for it; a *pinned* input is read from an immutable
reference and check 5 is correct for it. A path declared as both is rejected as a
configuration contradiction, because either behaviour would be wrong for one of
the two checks. Without that rule a correctly-pinned runner is reported defective
by check 1.

**The recurrence matters more than the finding, again.** The same class of
binding — a file whose bytes are bound by a published record — had already been
found in this programme the same day, in `aggregation/semantic.py` under
`results/los-inspired-v0.1.manifest.json`. That one was checked for and
respected; this one was not checked for and was broken. One codebase, one day,
two instances, one of them missed by the person who had just handled the other.

**Merged 2026-08-14, after failing this project's CI first.** The initial commit
wrote the tests with pytest, which broke self-test on all four supported Python
versions: `epistemic-ci` declares `dependencies = []` and runs
`python -m unittest discover`. Adding a dependency to a deliberately
dependency-free meta-validation tool, in order to test a check about not trusting
what you did not verify, was caught by the tool's own CI and rewritten.

**The local control was too weak, twice, and is now replaced.** The count test
added in PR #86 compared the stated number against the names in the same
sentence. It cannot catch the failure that actually recurs: when *both* go stale
together they stay internally consistent and the test passes. It missed the
"awaiting review" staleness after #13 merged, and it missed the count reading
five while upstream had eight.

The reasoning that produced it was also wrong. A cross-repository check was
rejected as catching "a strictly rarer case at strictly higher cost". That case
is not rarer — it is the only one that has ever occurred here. The test now
queries epistemic-ci for its actual check count, and skips rather than fails when
the network is unavailable, so an offline run is not a false red.

**Checks 6, 7 and 8 followed** ([#14](https://github.com/Silentpartnercoding/epistemic-ci/pull/14),
[#15](https://github.com/Silentpartnercoding/epistemic-ci/pull/15)), closing the
three remaining proposals. Control Discrimination and Evidential Independence are
both questions about the shape of one outcome matrix — whether a row varies at
all, and whether two rows are identical. Effect Reachability departs from its
issue deliberately: the proposal was a single population predicate returning more
than zero, which *passes the worked instance*, since 208 searched is greater than
zero. Requiring every declared stratum to be non-empty catches it.

**Scope, stated rather than assumed.** Check 5 establishes *insensitivity*
generically. *Sensitivity* — that corrupting what the pin resolves to makes the
run fail — depends on the pin mechanism and is checked only where a
`tamper_command` is supplied; otherwise it is reported not established. Pins are
counted separately from mutations so they cannot inflate the assurance bound.

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
- **"The verification system committed the error the project exists to prevent."**
  True as a description of #13, and deliberately not recorded as a finding. It is
  an interpretation of two facts rather than a third: that the runner read the
  workspace, and that this programme's thesis is that a copy is not an original.
  The claim that these are *the same* error is a claim about resemblance, and no
  observation makes it come out false. A statement that cannot fail is not
  evidence — the same objection this programme raised against its own
  `check_t4_tightness`, which reported 4,638/4,638 from a computation that never
  constructed a second world. The recurrence above is logged instead because it is
  countable, predicts that more instances exist, and could be refuted by showing
  the two cases are structurally unalike.

## Rule

A defect found here that is a property of the **verification path** belongs
upstream. One that is a property of **this programme's registration discipline**
stays local. When in doubt it is logged upstream with the scope stated, because
an unlogged finding travels nowhere.
