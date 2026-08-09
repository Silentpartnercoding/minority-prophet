# What is claimed, and what would break it

A target for adversarial review. Every claim below is numbered, stated as
narrowly as the evidence supports, and paired with what would falsify it. If you
are here to attack this work, attack these — not the impressions the surrounding
prose might leave.

Where a claim is **not** made, that is said explicitly. Several things this
programme has measured do not support the claim a reader would expect them to,
and those are listed in §B.

---

## A. Claims

### A1. Theorem 1 (immunity) — machine-checked, and stated with all its hypotheses

If two worlds are side-consistent, **have the same assertion function**, and have
the same root set, the verdict is identical. No constraint at all is placed on how
the non-root lineage differs.

**Evidence.** `proof_status: proved_compiled` — a Lean proof at
`formal/lean/MinorityProphetCore/Immunity.lean`, theorem
`MinorityProphet.immunity`. Finite verification recorded in
`formal/THEOREM-LEDGER.json`: 116,032 root-preserving forest rewirings and 1,992
root-preserving DAG rewirings, zero violations.
`lineage/reference_mutant_audit.py` **reproduces** the 116,032 figure; it does not
add to it.

**Drift is tracked, not hidden.** The ledger flags T1 `generalized_from_repository:
true` — it is broader than the paper's statement, which restricted which rewirings
counted. Two of the six theorems are flagged narrowed and two generalized, each
with its reason. T5 was narrowed by *adding* the same-assertion hypothesis, which a
counterexample proves necessary.

**A correction to an earlier draft of this file, kept visible.** A1 previously
omitted the same-assertion hypothesis and cited only the finite verification. Our
rewirings preserve sides by construction, so no measurement was affected — but
dropping a hypothesis from a claim statement is exactly the defect the ledger
records against the repository's original T5. The document meant to prevent that
error committed it.

**Not verified here.** No Lean toolchain was available in this session, so
`proved_compiled` is taken from the ledger rather than rebuilt. Rebuilding it is a
cheap and worthwhile attack.

**Breaks if.** The Lean proof does not compile, or you exhibit two worlds meeting
all three hypotheses with different verdicts.

### A2. The immunity ablation is not a test of `root_of`

Firing counts from the immunity ablation measure invariance under rewiring, not
the correctness of `root_of`, and must not be cited as evidence of the latter.

**Evidence.** `depth0` and `alwaysZero` change `root_of`'s output — they are
classified `BEHAVIOUR_CHANGING`, not equivalent — and fire **zero** under both
readings. Both collapse the verdict to a function of the multiset of sides, which
rewiring preserves by construction. `FINDING-BL058B.md`.

**Breaks if.** You show either mutant is in fact equivalent (making the zero
forced and the finding vacuous), or that some eligible pair does catch them.

### A3. The side-consistency reading is not free under mutation

v0.4 registered parent-local and root-based as interchangeable. They agree
exactly for a correct implementation and diverge under mutation, including in the
eligible population.

**Evidence.** Three mutants diverge in population; `offByOneStop` diverges in
firing too — 1,720 against 118,968. Reproduced independently of the audit that
raised it. `AMENDMENT-BL058.md`, `FINDING-BL058B.md`.

**Breaks if.** You show the divergence is an artefact of our eligibility rule
rather than of the readings.

### A4. KL-001's absence verdict is a total function of two bits

The verdict is determined by (opposing evidence present, coverage complete) and
nothing else.

**Evidence.** `knowledge_ledger/transaction.py` — three branches, two inputs, no
fallthrough. All four cells enumerated and verified, and each input shown
load-bearing: a rule reading only the findings bit is caught by exactly one cell,
one reading only the coverage bit by two.
`experiments/KL-001/conformance/verify_absence_rule.py`.

**Breaks if.** You find an input that changes the verdict and is not one of those
two, or a fifth reachable outcome.

### A5. Two attack prices, and the parity gap

`flip_budget` is the forgery price; `conversions_to_reverse` is the compromise
price and is roughly **half** of it. Abstention is unreachable by conversion from
an odd margin, because conversions move the margin in steps of two and preserve
its parity.

**Evidence.** Stated identically in Gate's `README.md` and Border's
`SECURITY.md`; both suites pass (72 and 50 tests). Quoting `flip_budget` alone
overstates the cost of the relevant attack, which is the defect this corrected.

**Breaks if.** You construct a conversion sequence reaching abstention from an
odd margin, or show the half-ratio is wrong.

### A6. Preregistrations are byte-identical to their pinned commits

Six bindings verified: each pinned commit exists, is an ancestor of the published
branch, and the preregistration blob at HEAD matches the blob at the pin.

**Evidence.** `scripts/check_registration_chain.py`, run in CI on every commit.
It deliberately does **not** use "last-touching commit equals the pin", which is
wrong in both directions — red on merged duplicate history, green on tampering
that preserves commit identity.

**Breaks if.** You alter a preregistration in a way the check passes, or show a
pin that is not a genuine ancestor.

---

## B. Things measured that do **not** support the obvious claim

### B1. The dual ledger is *not* claimed to reduce false cleans in practice

v0.3 met its registered primary endpoint — 0.0213 against a bar of
strictly-below-0.0426. That result is **not** evidence of practical benefit, and
`STATUS.json`'s `claimAllowed` forbids the claim.

Because the verdict is a total function of two bits (A4), on any synthetic corpus
both rates reduce to generator settings:

    cleanRefusalRate = |clean repos with an unreadable file| / |clean repos|
    rescues          = |defective repos, no findings, unreadable file|

Every term is something we chose. The rates were not measured; they were chosen
and read back. The effect is **one repository** — two false cleans became one.
And of four repositories moved to `not_established`, one was defective and
**three were clean**, a cost the registered endpoint counts nothing of.

`frozen-v3` is cancelled, not deferred: there is no corpus size that fixes this.

### B2. The 95% recall target could not fail

Both arms run the identical scanner, so recall is equal by construction —
measured equal to the digit on both corpora. Retired as an endpoint and re-scoped
to an invariant that *can* fail: if the arms ever stop sharing a scanner, the
comparison silently stops being a comparison.

### B3. LIN-000's T1-POS carried no independent load

Established earlier and unretracted: it is reachable only via L1-POS, so it is a
corollary rather than independent evidence.

---

## C. Known weaknesses — start here

These are the places I would attack, listed because finding them again is a waste
of your time.

**C1. The independent mutant audit cannot be interpreted, and I could not fix
it.** `IND-v4-RESULTS.json` records mutants by name and firing count with no
implementation, no fingerprint, no equivalence classification, and no stated unit
of counting. Two of its entries fire zero and nothing determines whether that
means "harmless" or "blind spot". I reconstructed both from their *names* and
found my reconstructions equivalent — a fact about my reconstructions, not proof
the originals were harmless. The independent implementation is not in this
repository. A2 and A3 are established from **our** audit, which publishes
everything; the independent one remains uninterpretable.

**C2. A real-repository run needs defect ground truth for real repositories.**
Unsolved, and nothing in this programme solves it. This is why KL-001 stops at
`fixture-passed` and why the 15% `cleanRefusalRate` ceiling (owner decision, fixed
before any population it will be tested against exists) has nothing to test
against yet.

**C3. Earlier findings are superseded in framing, not withdrawn.** A reader who
stops at `FINDING-KL001-v0.3.md` comes away with "reduces false cleans by half".
Banners now point forward, but the documents remain persuasive in the wrong
direction, and every number in them is accurate — which makes the misreading
easier, not harder.

**C4. The tooling catches mechanical error and is blind to design error.** Every
mistake made while building this was caught by a check — a vacuous boundary run, an
invented ladder rung, a stale status file, a probe that would have passed by
printing a constant. **Not one design error was caught by tooling.** The deepest
problem here — that both KL-001 endpoints were generator settings read back — was
found by a human asking one question. `scripts/check_effect_reachability.py`
now catches one narrow form of it. I have no account of the rest, and no reason
to think that form is the only one.

**C5. CI has an input you cannot audit.** `MP_BOUNDARY_DIGESTS` supplies blocked
vocabulary as hashes from a repository secret, so a fork can pass where main
fails. The success line discloses how many runtime rules were active and says the
result is not reproducible without them. It discloses none of their contents. No
finding depends on this check — it is a publication guard, not an instrument —
but the divergence is real.

**C6. Dropped hypotheses are this programme's characteristic defect — three
instances, all found rather than prevented.** A theorem is restated somewhere
other than where it is proved, one hypothesis is left out, and the restatement is
strictly stronger than the thing that was proved.

1. The research repository's original **T5** omitted the same-assertion
   hypothesis. A counterexample proves it necessary. Found by the formal audit;
   the ledger records the narrowing.
2. **Gate's README** stated T1 as invariance under *"arbitrary corruption of
   who-copied-whom"*, omitting root-set preservation. Orphaning a claim creates a
   new origin and T1 says nothing about the result. The implementation was
   correct throughout — `aggregator.py` says "side-preserving, root-preserving" —
   so only the public headline claim was wrong. Fixed in
   minority-prophet-gate#12, which also adds the `FORMAL.md` that the package
   docstring had cited without it existing.
3. **This file**, section A1, omitted the same-assertion hypothesis of T1. The
   document written to prevent the defect committed it.

Three for three, in a programme whose central discipline is not overclaiming. The
common cause is restating a theorem away from its proof, so `FORMAL.md` now
refuses to restate and points at the ledger instead. That is a mitigation, not a
fix: nothing prevents the next restatement, and no check detects one. **If you
find a fourth, the interesting question is not the instance but why three rounds
of review did not make the pattern visible before the third.**

**C7. Redaction did not remove anything from history.** Three items redacted on
2026-08-09 remain fetchable from earlier commits on the public branch. Removing
them means rewriting 292 of 333 commits and breaking all six registration pins,
which was judged a worse trade than the exposure (owner decision). The `--sweep`
mode scans the tree at a ref, **not history**, so it would not catch this class
either.
