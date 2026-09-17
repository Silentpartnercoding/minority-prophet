# AID-2 — does the range do what the number could not

**Status: SPECIFICATION ONLY. No world, no run, no verdict.** The arms and the
criteria are named here before any world exists, and the world is to be written
by someone other than the author of the policy.

## 1. What AID-1 left open

AID-1 rejected the attestation policy, 61 of 111 checks. The failure that
mattered was suppression: 720 of 720 decisions settled against a true contrary
claim carried by unattestable witnesses, while every other arm abstained and the
claim survived. The scope clause written to prevent exactly that did not hold,
and cannot, because the use is caller-declared: a caller deciding whether to act
says `PERMIT_ACTION` truthfully while the same deflated count deletes the claim.

The diagnosis is that **a single number cannot serve two decisions that need
opposite conservatism.** Deflating a count is prudent when it decides whether to
act and is an attack when it decides whether a claim survives.

The repair is `witness_bounds`: a lower bound counting only independence that
was *earned*, an upper bound counting independence wherever the record cannot
*rule it out*. Evaluate the decision at both ends; settle only when the answer is
the same at both; otherwise refuse.

AID-1 could not test that, because its arms asked for a point estimate. This
experiment exists for that one question.

## 2. The primary method, named before the world

`attested_bounds`: for each decision, compute each side's `witness_bounds`,
evaluate the settlement at the lower end and at the upper end, and settle only
if both ends give the same disposition. Otherwise refuse and escalate.

## 3. Arms

1. `ladder` — `canon.proximity.independent_for`, unchanged. Baseline.
2. `attested_bounds` — **primary**, above.
3. `attested_point` — the repaired policy through `effective_witnesses_for`, a
   single count. Isolates what the range buys over a number.
4. `attested_declared_only` — backing neutralised, declared depth at face value.
   The theatre check.
5. `refuse_all_unrecorded` — refuse on any pair lacking recorded ancestry. The
   trivially safe upper bound on cost.

## 4. Questions

1. Does the range stop the suppression the number caused?
2. What does it cost against the number, in correct settlements?
3. Does it still prevent what the policy exists to prevent?
4. Does it degenerate into refusal once ranges are wide?

## 5. What the world must contain

The six families of AID-1, unchanged in intent: `nobody_can_attest`,
`adversary_attests_freely`, `hidden_shared_source` (aware and unaware),
`baseline_already_right`, `minority_suppression`, `mixed_attestation`.

**The failure mode this world exists to expose:** a bounds rule can collapse
into refusing everything, because any unattested witness widens the range and a
wide range never agrees at both ends. That must be visible and punished, not
mistaken for safety. Criterion 6 is there for it.

## 6. Criteria, fixed before any world exists

Scored on reversible decisions. Powered cells only, Holm-corrected across arms,
fail closed when underpowered. Two executions must be semantically identical.

**The primary is supported only if all hold:**

1. **It prevents what it exists to prevent.** In every powered cell of the
   hidden-source family, at least 40% of the baseline's margin-critical silent
   false settlements are prevented.
2. **Cost is bounded by benefit, where benefit is possible.** At `α = 1.0`,
   correct settlements lost do not exceed silent false settlements prevented, in
   every family where the baseline makes at least one margin-critical silent
   false settlement. Where it makes none, cost is reported and is not a pass
   mark.
3. **It is not theatre.** `attested_declared_only` does materially worse than
   the primary in the freely-attesting family, in cells where the arms can
   differ at all.
4. **It is not worse than refusing.** Strictly more correct settlements than
   `refuse_all_unrecorded`, with margin-critical prevention no more than 10
   percentage points below refusal's, in every powered cell.
5. **It does not suppress.** In the minority-suppression family, the true
   contrary claim survives at least as often as under the baseline, in every
   cell. Any loss fails the experiment outright, whatever else holds.
6. **It is not refusal with extra steps.** In `baseline_already_right` at
   `α = 1.0`, the primary settles at least half of what the baseline settles. A
   rule that refuses whenever the range is wide fails here, and should.

**Reported, not criteria:** the adoption curve; the gap between
`attested_bounds` and `attested_point`; and the share of decisions where the two
ends of the range disagreed.

## 7. Two criteria repaired, before this world exists

AID-1 exposed two of its own criteria as untestable. Both are repaired here, in
advance and with the reason, because a criterion that **no possible arm** can
satisfy measures nothing:

- **Criterion 2** was stated "in every family and cell". The specification's own
  required family `nobody_can_attest` guarantees zero prevention by
  construction, so the bound was unsatisfiable regardless of the policy. It now
  applies where prevention is possible, and cost elsewhere is reported.
- **Criterion 4** required "at no worse prevention" than `refuse_all_unrecorded`,
  which refuses essentially everything and therefore trivially prevents
  everything. No arm that answers anything could satisfy it; it failed 30 of 30
  cells for that reason alone. The repaired form keeps the intent — do not be
  worse than the trivially safe rule — while being satisfiable.

Criterion 3 is additionally restricted to cells where the arms can differ, since
at the `TRANSCRIPTION` class every admissible depth clears the divergence test
and all arms are identical by construction.

## 8. Kill criterion

If the range prevents the suppression only by refusing everything, the bounds
approach is dead and the honest remaining option is policy C: count the
unattested, and publish the exposure as a number.

## 9. Disclosure

- Written by the author of the policy it tests, after AID-1's results were
  known. Only the world, written by someone else, makes the criteria bite.
- **This is a re-test on a world family whose earlier results are known.** A pass
  here is weaker evidence than AID-1's failure was, and must be reported as such.
- Same control domain. Not independent validation.
- Every rate will be synthetic. Adoption is a dial in a generator.
- No authority claim.
