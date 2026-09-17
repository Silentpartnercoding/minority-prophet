# DRI-11 — refusal named first, composite named second

Status: **SPECIFICATION ONLY. No world, no run.** Both methods are named here
before any world exists, and the world is to be written by someone else. That
separation is the point: DRI-9 was built by the author of the instrument and
flattered it; DRI-10, written by the review, rejected the same instrument on the
first honest test.

## 1. What DRI-10 measured

Per cell, reversible decisions, from the frozen result:

| Behaviour | Measured |
|---|---|
| Refusing when fragile prevents errors in **every** hidden family, with no instrument | 473–521 prevented, including where dependence carries no mark |
| Refusing costs answers | correct settlements 2,034 → 1,551 |
| Bait collapses a carrier that shares no error | 2,830–2,866 → 1,389–2,194 correct, zero true merges |
| Bait is blind to unmarked dependence | prevented 0 of 1,005 and 0 of 988 |
| Requiring two signals never collapsed the carrier | ladder false merges 0–55, all families |
| Requiring two signals often prevents nothing | ladder prevented 0–258, nothing at all in two cells |

Refusal is the only arm that worked everywhere. Its weakness is a single number:
what it throws away.

## 2. Primary method: fragile refusal

Refuse when believing any single winning-side pair would change the settlement or
its stamp. Otherwise answer. No marks, no probes, no memory, no budget.

**Named first because it is the simplest thing that could work.** If it passes,
every instrument in this programme is unnecessary complexity, and that is the
result. It is also the only arm whose cost is its sole failure mode, which makes
it falsifiable by one number.

## 3. Secondary method: corroborated belief with refusal fallback

Named in advance so it cannot be promoted after seeing outcomes, and justified
only if refusal fails on cost.

1. **Believe** a pair when at least two declared signals agree, acting by
   overriding the record's identities at every cut (`dri9/rule.believe`). This is
   the ladder's rule, which never collapsed the carrier in DRI-10.
2. **Otherwise, if the answer is fragile and no signal supports any winning-side
   pair**, refuse.
3. **Otherwise answer.**

The claim: belief recovers the answers refusal throws away, without collapsing
carriers.

## 4. Criteria, stated before any world exists

Scored on reversible decisions, Holm-corrected across both methods.

**Refusal (primary) is supported only if:**

1. **Prevention.** In every powered family where dependence is real, prevents at
   least 40% of the baseline's margin-critical silent false settlements —
   including where dependence carries no mark.
2. **Cost bound.** Unneeded abstentions do not exceed the silent false
   settlements it prevents. Refusing twice to prevent once is not protection.
3. **Correct settlements** stay within 80% of the baseline. This is deliberately
   looser than the 95% asked of instruments, because refusal's whole mechanism is
   declining to answer; if it cannot clear even this, the approach is dead.

**Composite (secondary) is supported only if, in addition:**

4. **It beats refusal on cost.** Strictly fewer unneeded abstentions, at no worse
   prevention, in every powered family.
5. **No collapse.** Where shared structure carries no shared error, false merges
   do not exceed true merges and correct settlements stay within 95% of baseline.

**Both:** fail closed when underpowered; two executions identical.

## 5. What the world must contain, requested of the adversarial author

Both methods must be able to lose:

- **A family where refusing is expensive** — fragile but correct decisions, so the
  cost bound can actually bite. DRI-10 had none, so refusal's weakness was never
  a failure condition.
- **A carrier that shares no error**, keeping the collapse check live.
- **Unmarked dependence**, where signals are silent and refusal must carry it.
- **Leaked marks**, so corroboration can be fooled.
- **Two weak signals that agree wrongly** — a world where the marker and the
  co-error record share a cause. No experiment so far contains this, and it is
  the case that kills the composite if it exists in reality.
- **A family where the baseline is already right**, so any method that refuses or
  merges reflexively is punished.

## 6. Disclosure

- Written after seeing DRI-9 and DRI-10, so both methods are fitted to their
  measured failures. Only a world written by someone else can say whether either
  generalises.
- Same control domain as the engine either way. Not independent validation.
- No authority claim.
