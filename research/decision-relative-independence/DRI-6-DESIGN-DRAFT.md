# DRI-6 — imperfect lookups

Status: **DRAFT.** It becomes a preregistration only when the protocol, generator
and runner are committed and pinned before any confirmatory world is generated.

## 1. Why this exists

Every DRI experiment so far assumed a truthful lookup. When the tiered rule cannot
settle robustly it looks, then settles on whatever the lookup reports. Imperfect
lookups were deferred at DRI-3 by owner decision. On 2026-09-15 the owner asked
whether imperfect lookups do anything other than cost time.

They can change correctness, not only time. A lookup that misses a dependence
counts copies as independent, and the rule then settles on a false majority.

## 2. Questions

1. **Harm:** how many silent false settlements do lookup errors cause under the
   tiered rule?
2. **Record check:** does checking a reported grouping against the record catch
   them? A grouping passes when every reported unit is joined by recorded shared
   identities inside it.
3. **Confirmation:** does looking twice and settling only when both reports agree
   catch them, and at what cost in looks and unneeded abstentions?

## 3. Worlds

- **Base:** DRI-4's five families with a complete lineage record, on a new salt,
  2,000 base worlds each, which is 6,000 decisions per family.
- **Lookup errors:** each call independently reports a grouping with errors.
  - **split rate e_s:** a true unit with several observations is reported as one
    unit per observation. A dependence is missed.
  - **merge rate e_m:** a pair of true units is reported as one unit. A dependence
    is invented.
- **Cells:** (e_s, e_m) ∈ {(0, 0), (0.05, 0), (0.2, 0), (0, 0.2), (0.2, 0.2)}.
- **Common random numbers:** shared across arms and cells.

## 4. Arms

- **Frozen DRI-3 arms, which settle on whatever the lookup reports:**
  - agreement rule;
  - tiered rule;
  - always look.
- **Checked tiered rule:** the tiered rule, abstaining when the report fails the
  record check.
- **Confirmed tiered rule (method under test):** the tiered rule, looking twice and
  settling only when both reports pass the check and give the same settlement.
- **Oracle reference.**

## 5. What is guaranteed, and what is not

**Guaranteed.** These are checked as implementation checks, not claimed as
findings.

- Both new arms make their first lookup exactly where the tiered rule looks, with
  the same report. So neither is ever silently wrong where the tiered rule is not.
- With truthful lookups and a complete record, none of the three makes a silent
  false settlement (DR2).

**Not guaranteed, and what DRI-6 measures.**

- **The check:** with a complete record, a truthful report always passes. A missed
  dependence usually passes too, so the check mainly catches invented dependence
  that has no recorded link. Ledger DR3 is the same argument: the record cannot tell
  copies from independent sources.
- **Confirmation:** catches an error only when the second report differs in its
  settlement, and costs a second look everywhere.

## 6. Proposed criterion

Supported only if all hold:

1. **Truthful cell:** in every family, the confirmed tiered rule makes zero silent
   false settlements, with the 95% bound below 0.001.
2. **Every family and cell:** neither new arm is silently wrong where the tiered rule
   is not.
3. **Erring cells:** in every family and cell where the tiered rule makes at least 12
   silent false settlements, the confirmed tiered rule makes significantly fewer.
   The test is exact McNemar, Holm-corrected over up to 20 comparisons.
4. **Reproducibility:** two executions are identical.

## 7. Reported with no pass mark

- **Checked against tiered:** the paired comparison.
- **Harm from lookups:** false settlements made after a look, per arm.
- **Cost of confirmation:**
  - extra looks per prevented false settlement;
  - extra unneeded abstentions.

A decision with a lookup counts as decidable even when the lookup errs, so an
abstention there is unneeded.

## 8. Limits

- **Error model:** synthetic and independent across calls. Correlated errors, such
  as a lookup that is wrong the same way every time, would defeat confirmation. They
  are not modelled.
- **Record:** complete lineage only. With missing lineage, a truthful report can fail
  the record check.
- **Content:** DRI-5's content fingerprint is not combined here.
- **Authorship:** everything is authored in the same control domain as the engine.
- **No authority claim.**
