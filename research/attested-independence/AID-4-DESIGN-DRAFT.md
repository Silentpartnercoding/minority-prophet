# AID-4 — the two roads that are left

**Status: SPECIFICATION ONLY. No world, no run, no verdict.** Criteria for both
policies are fixed here before any world exists. The world is to be written by
someone other than the author of these policies.

## 1. Where this starts

Three experiments closed one road. Requiring witnesses to prove how deep they
went — and discounting those who cannot — was rejected by AID-1, by AID-2 after
repair, and by AID-3 on the adversarial review's own world. The failure is not a
bug to fix: **discounting witnesses who cannot prove themselves is the mechanism
and the harm at once.** AID-3 measured it as total and rate-independent, 4,800 of
4,800 decisions settled against a true contrary claim.

Two roads were named at that junction and neither has been tested. This tests
both, against the same worlds, including the construction that killed the first.

## 2. The two policies, named before the world

**Policy B — collapse-robust margin.** Count every witness, discount nobody.
Settle only when the settlement **survives the worst case the record cannot rule
out**: if `j` witnesses on the winning side are unattested, they might all be one
source, so the winning count could be as low as `n − j + 1`. Settle only if the
side still wins at that floor. It asks "would this answer hold if the silence
were hiding the worst?" rather than "who can prove themselves?".

The critical structural difference from the rejected policy: B is conservative
about **the decision**, not about **particular witnesses**. It never deflates one
side for lacking credentials. In a tie it abstains, as the baseline does.

**Policy C — priced exposure.** Count every witness and settle exactly as the
baseline settles. C changes no decision. It attaches to each settlement a
published figure — how much of it rests on witnesses who stated nothing —
reusing `unattested_exposure`, already shipped.

## 3. Why the two need different criteria

B is a decision rule and faces the axes that killed policy A: prevention, cost,
suppression, degeneration.

**C is not a decision rule.** It loses no settlements and prevents no errors by
construction, so scoring it on prevention would be meaningless. The only
question that matters about C is whether the number it publishes is worth
anything: **do settlements resting on silence actually fail more often than
settlements that do not?** If exposure does not separate the silently false from
the correct, then publishing it is ceremony, and the honest answer at this
junction is that we have nothing left to offer but the proof of ignorance.

## 4. Arms

1. `ladder` — `canon.proximity` unchanged. Baseline.
2. `margin` — **policy B. Primary for the decision criteria.**
3. `priced` — **policy C.** Settles identically to `ladder`; carries an exposure
   figure per decision.
4. `attested` — the rejected policy, as a known-bad reference point.
5. `refuse_all_unrecorded` — refuse on any unrecorded pair. Cost ceiling.

## 5. Criteria for policy B, fixed before the world

Scored on reversible decisions. Powered cells only, Holm-corrected, fail closed
when underpowered. Two executions semantically identical.

**B is supported only if all hold:**

1. **Prevention.** In every powered hidden-source cell, prevents at least 40% of
   the baseline's margin-critical silent false settlements. The same floor used
   since DRI-9; not chosen for this run.
2. **Cost is bounded by benefit, where benefit is possible.** Correct
   settlements lost do not exceed silent false settlements prevented, in every
   family where the baseline makes at least one margin-critical silent false
   settlement. Where it makes none, cost is reported and is not a pass mark.
3. **It is not worse than refusing.** Strictly more correct settlements than
   `refuse_all_unrecorded`, with prevention no more than 10 points below it.
4. **It does not suppress.** In every minority-suppression cell, the true
   contrary claim survives **at least as often** as under the baseline. Any loss
   fails the experiment outright. This is the criterion that killed policy A and
   it is not relaxed.
5. **It is not refusal with extra steps.** Where the baseline is already right
   and nothing is hidden, B settles at least half of what the baseline settles.

## 6. Criteria for policy C, fixed before the world

C is scored on discrimination, not on decisions.

1. **It discriminates.** Among the baseline's settlements in every powered cell,
   exposure must rank silent false settlements above correct ones with
   **AUC ≥ 0.70**. A coin flip is 0.50; a number that cannot beat 0.70 is not
   worth publishing as a warning.
2. **It is not constant.** At least 20% of settlements must carry an exposure
   figure different from the modal value. A figure that never varies has not
   discriminated anything, whatever its AUC computes to.
3. **It changes nothing.** C's settlements must be identical to the baseline's
   in every cell. Any divergence is a construction error, not a result — C is a
   disclosure rule and must not become a decision rule by accident.

## 7. What the world must contain

The families that have earned their place, carried forward:

- **A minority-suppression construction**, with a backed false side and a true
  side that cannot attest. This killed policy A. B must face it unchanged.
- **DR3's hidden source**, where nothing recorded connects the copies.
- **Honest witnesses who cannot attest at any rate**, so cost is real.
- **A baseline that is already right**, so reflexive caution is punished.
- **Mixed populations in one decision.**

And what B and C specifically need, which no previous world supplied:

- **Decisions whose margin is wide and whose witnesses are unattested**, so B can
  settle rather than refuse. A world where every margin is thin makes B
  indistinguishable from refusal and tests nothing.
- **Settlements that rest on silence and are nonetheless correct**, so C's
  exposure figure can be wrong in the direction that matters. If every
  high-exposure settlement is false, discrimination is trivial.

## 8. Kill criteria

- If **B suppresses**, the margin road closes and B is not rescued by any other
  number.
- If **C fails to discriminate**, the pricing road closes as a warning mechanism.
  It would remain honest bookkeeping, and honest bookkeeping that predicts
  nothing is not a safeguard.
- **If both fail**, the programme has no remaining constructive proposal, and the
  defensible position is the one the DRI series proved: settle only on recorded
  dependence, and state plainly that unrecorded dependence is outside what any
  reading rule can reach.

## 9. Disclosure

- Written by the author of both policies, after three rejections. Only a world
  written by someone else makes these criteria bite.
- Same control domain. Author separation, not independent validation.
- Every rate will be synthetic. Nothing here measures real adoption, and the
  census in `experiments/aid1/` found zero records in this estate stating a
  witness depth.
- No authority claim.
