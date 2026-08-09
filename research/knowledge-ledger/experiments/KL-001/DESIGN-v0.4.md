# KL-001 v0.4 — design notes, resolving BL-061 and BL-062

Not a registration. It explains why v0.4's registration cannot be written against
the corpora we have, and why the corpus we were about to build would not have
helped either.

## Owner decision, recorded

`cleanRefusalRate` ceiling: **15%**. Fixed 2026-08-09, before the population it
will be tested against exists. v0.3 measured 23% and would fail it.

The ceiling is deliberately set where the current evidence fails, rather than
where it passes, so the endpoint can come out against the intervention.

## What changed after the ceiling was set

Sizing a corpus for a 15% ceiling produced an unexpected result, and following it
retired more of the experiment than it repaired.

**First: the ceiling is undecidable at the current scale.** With 13 clean
repositories, the 95% upper confidence bound on *zero* refusals is 24.7% — above
the ceiling. No result on this corpus can clear the bar, including a perfect one.
Reaching 80% power against a true rate of half the ceiling needs about **120 clean
repositories**, roughly nine times what we have.

**Then: building that corpus would have measured nothing.** The verdict is a total
function of two bits. From `knowledge_ledger/transaction.py` — three branches, two
inputs, no fallthrough, nothing else consulted:

| opposing evidence | coverage complete | verdict |
|---|---|---|
| yes | yes | `present` |
| yes | no  | `present` |
| no  | yes | `absent_within_declared_scope` |
| no  | no  | `not_established` |

So on any synthetic population:

    cleanRefusalRate = |clean repos with an unreadable file| / |clean repos|
    rescues          = |defective repos, no findings, unreadable file|

Every term is a generator setting. The rates were not measured; they were chosen
and read back. A larger corpus tightens a confidence interval around an authored
number, which is worse than an underpowered estimate because it looks like
evidence.

**`frozen-v3` is therefore cancelled.** Not deferred — cancelled. There is no size
at which a synthetic corpus answers the question those endpoints ask.

## BL-061 — resolved by splitting the claim, not by re-powering it

The original defect stands: the registered endpoint counts defective repositories
only, so a conversion to `not_established` books an improvement when the
repository was defective and records nothing when it was clean. A one-sided
endpoint cannot come out against the intervention.

The repair is not a second synthetic rate. It is separating two claims that were
tangled together:

**Claim 1 — what the rule does.** Deterministic, so it is settled by enumeration:
four cells, all four verified, no corpus and no confidence interval involved.
`conformance/verify_absence_rule.py` and `tests/test_absence_conformance.py`.
Each input is additionally shown load-bearing, because a rule ignoring one of its
inputs still yields four rows and three correct verdicts — "all cells pass" is not
by itself evidence the cells matter. Measured: a rule reading only the findings
bit is caught by exactly one cell, the incomplete-coverage one, and a rule reading
only the coverage bit is caught by two.

Also measured, and worth stating because it is the mechanism expressed as a
property rather than a percentage: **coverage decides exactly one of the two cell
pairs — the one where nothing was found.** If it decided both, the rule would be
downgrading positive findings. If it decided neither, the dual ledger would do
nothing at all.

**Claim 2 — how much it helps.** This is a question about how often each cell
occurs, which is a fact about real repositories and not about our generator. It is
**retired from synthetic evaluation**. The 15% ceiling is carried forward as the
registered bar for the first real-repository run, where the occurrence rate is
observed rather than configured.

## BL-062 — resolved as originally proposed

"Preserve 95% of true positives" is satisfied by the structure of the experiment:
both arms run the identical scanner, so recall is identical by construction.
Measured exactly equal to the digit on both corpora — 81.7/81.7 and 79.3/79.3.

Retired as an endpoint; re-scoped to an invariant assertion:

    recall(dual) == recall(baseline)      exactly, not within a tolerance

That can fail for a real reason: if the arms ever stop sharing a scanner, through
a refactor or a well-meant improvement to one of them, the comparison silently
stops being a comparison. The number does not change. The claim it supports does.

**An assertion that cannot fail is decoration; the same assertion re-scoped to
something that can fail is a regression test.**

## What v0.3's numbers may still be quoted for

Description of a specific corpus, labelled as such. They are not evidence about
the intervention's benefit, and `FINDING-KL001-v0.3.md` already reports the
headline as one repository rather than as a percentage. Nothing in that finding is
withdrawn — this document narrows what it can be *used* for.

## What a real-repository run needs, when it happens

- the 15% ceiling above, already fixed
- a clean denominator near 120, from the power calculation, or a stated decision
  to report the rate without a pass/fail verdict
- `scripts/check_effect_reachability.py` satisfied — BL-060, which v0.2 would
  have failed
- a defect ground truth for real repositories, which is the genuinely hard part
  and is not solved by anything in this experiment

That last item is the reason this is a design note and not a registration.

## Open, and deliberately unresolved

The defect-class taxonomy remains unregistered. The `(file, kind)` key is
injective on v1 and v2 — 0 of 135 planted defects collide — so recall is not
inflated today, but that is a property of those corpora rather than of the metric.
A population with two same-kind defects in one file would score 1/1 where the
truth is 1/2, silently. The choice belongs in a registration, not in a generator.
