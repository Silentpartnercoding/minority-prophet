# DRI-3 — preregistration draft

**Status: DRAFT. NOT FROZEN. NOT RUN.** It becomes the preregistration when it is
renamed, committed and pinned by hash in the runner, before any confirmatory world
is generated or scored. No comparative outcome has been computed on any DRI-3
world.

Design rationale: `research/decision-relative-independence/DRI-3-DESIGN-DRAFT.md`.
Implementation: `experiments/dri3/`. Engine under test:
`provenance/dependence_robustness.py`.

## 1. Identifier

DRI-3, protocol v1.

## 2. Question

When dependence stacks in ways no single independence cut expresses, does settling
only on a settlement that is robust over every combination of recorded possible
dependence eliminate silent false settlements? What does that cost?

The rule is applied under the owner's tiered cost rule: robust-only on irreversible
decisions, and stamped "not robust" on reversible ones.

## 3. Hypotheses

- **Null:** the tiered rule makes silent false settlements, or false settlements on
  irreversible decisions, in families whose dependence is recorded.
- **Target:** section 10.

## 4. Generated worlds

- **Size.** Seven families, 2,000 worlds each. Every world holds 3 independent
  decisions: 6,000 decisions per family and 42,000 in total.
- **Lookup condition.** Even-numbered worlds allow a lineage lookup and
  odd-numbered worlds do not. That is 1,000 worlds in each condition. The lookup
  returns the true grouping exactly, or nothing. Imperfect lookups are deferred to a
  follow-up (owner decision).
- **Decision class.** Fixed by world number, so that exactly half of every family's
  decisions (3,000) are irreversible, split evenly across the two lookup
  conditions:
  - irreversible decisions need 3 winning roots;
  - reversible decisions need 2.
- **Sampled for each decision:** truth, 4 or 5 causal roots, independent-root
  accuracy (0.65, 0.75, 0.85 or 0.95) and erroneous-root amplification (1, 3, 7 or
  15 observations). A correct root emits one observation; an incorrect root emits
  the amplification count.

**Families.** Identities are recorded at `agent`, `machine`, `controller`,
`evidence_origin` and `upstream_component`. Below each family's copy cut, every
copy of a root is distinct.

| # | Family | True dependence | Recorded where |
|---|---|---|---|
| 1 | `single_domain` | copies of each root | the copy cut; coarser cuts also merge roots 0/1 and 2/3 |
| 2 | `joint_domain` | copies; roots 0 and 1 share a component | upstream, which also merges 2 and 3 |
| 3 | `separate_control_shared_origin` | copies; roots 0 to 2 repeat one source | evidence origin; upstream merges 0/1 and 2/3 |
| 4 | `three_stacked` | copies; roots 0 and 1 share an origin; roots 2 and 3 share a component | origin (0/1) and upstream (2/3) separately |
| 5 | `side_asymmetric` | copies; the first two true-valued roots share an origin; the first two false-valued roots share a controller | at different cuts, by side |
| 6 | `decoy_shared_identity` | copies only | upstream groups roots by parity with no effect on their errors |
| 7 | `unrecorded_dependence` | copies; roots 0 and 1 are one source | **nowhere**: the declared expected failure |

In families 1 to 6 the true grouping is always a reading of the recorded identities.
Integrity tests assert this on development worlds.

**Seeds.** A world's seed is SHA-256 of `salt|family|replicate`. The confirmatory
salt is `minority-prophet-dri3-v1-confirmatory`. Development uses
`minority-prophet-dri3-development` only.

## 5. Arms

No human. An abstention supplies no answer. Contestants see only the observations,
the threshold and the decision class; they are never told the truth, the grouping or
the family.

1. **Agreement rule:** the DRI-2 method. It settles when all five cuts settle alike,
   and otherwise looks, abstaining if nothing comes back.
2. **Robustness everywhere:** settles only on a robust settlement from
   `assess_dependence_robustness`. Otherwise it looks, and abstains if nothing comes
   back.
3. **Tiered rule (method under test):**
   - irreversible decisions are handled as by robustness everywhere;
   - reversible decisions are handled as by the agreement rule, and a settlement
     made without looking that is not robust is stamped "not robust".
4. **Always look:** looks at every decision. Without a lookup, it settles only if the
   record is robust.
5. **Oracle (reference):** settles as the true grouping does.

## 6. Scoring

**Decisions** (every decision is scored, and a false settlement does not end a
world):

| Outcome | Definition |
|---|---|
| correct settlement | settles the way the true grouping does |
| false settlement | any other settlement; **flagged** if stamped "not robust", **silent** otherwise |
| unneeded abstention | abstains although the true grouping settles and either a lookup was available or the record alone robustly settles it that way |
| required abstention | abstains where nothing available could settle it |

**Worlds:**

- **falsely settled:** any false settlement;
- **complete:** no false settlement and no unneeded abstention;
- **incomplete:** no false settlement, but at least one unneeded abstention.

**Time.** Each look costs 1,000 virtual ms and each decision 1 ms. It is measured,
not a criterion.

## 7. Cost scorecard (owner decision)

The scorecard is worked out over the recorded families, on reversible decisions
only:

- **extra looks:** looks by robustness everywhere beyond the agreement rule's, per
  decision;
- **prevented false settlements:** decisions where the agreement rule falsely
  settles and robustness everywhere does not;
- **ratio:** extra looks per prevented false settlement, per family and overall.

If the overall ratio is at most 100, forcing looks on reversible decisions is
justified. Otherwise the engine's reversible policy is to stamp non-robust
settlements. The scorecard selects a policy; it is not a pass or fail.
Irreversible decisions carry no ceiling.

## 8. Endpoints

- **Primary:**
  - silent false settlements by the tiered rule, per recorded family;
  - false settlements by the tiered rule on irreversible decisions, per recorded
    family;
  - silent false settlements by the tiered rule against the agreement rule, per
    family.
- **Secondary, never pooled:**
  - every outcome count, per arm, family, condition and class;
  - looks, stamped settlements and virtual time;
  - world outcomes;
  - the scorecard;
  - family 7, reported apart.

## 9. Uncertainty and multiple testing

- **Bounds.** With zero events in n decisions, the exact one-sided 95% upper bound
  on the rate is 1 − 0.05^(1/n). That is 0.000499 for 6,000 decisions and 0.000998
  for 3,000.
- **Comparison with the agreement rule.** An exact McNemar test on paired
  per-decision silent-false-settlement indicators, in `joint_domain`,
  `three_stacked` and `side_asymmetric`, with Holm correction at a family-wise α
  of 0.05.
- **When a comparison is run.** A family is tested only when the agreement rule makes
  at least 7 silent false settlements there. Seven is the smallest count at which an
  exact two-sided test with no discordance on the other side can reach significance
  at the first Holm step with three tests. Otherwise the comparison is reported as
  underpowered and is not a check. This was fixed before any DRI-3 world was
  generated, because DRI-2 v2 showed the joint-domain trap is rare (4 in 9,468
  decisions).

## 10. Success criterion

Supported only if all of the following hold:

1. **Every recorded family (1 to 6):**
   - the tiered rule makes zero silent false settlements, with the 95% upper bound
     below 0.001;
   - it makes zero false settlements on irreversible decisions, with the 95% upper
     bound below 0.001.
2. **Powered comparisons:** in each comparison family with enough agreement-rule
   failures to test (section 9), the tiered rule makes significantly fewer silent
   false settlements than the agreement rule.
3. **Reproducibility:** two complete executions give identical semantic results.

Family 7 never counts toward support or failure.

**Invalidation:**

- the runner detects a changed protocol, configuration or code hash;
- the two executions differ;
- a contestant arm is shown to have read a hidden field;
- an integrity test shows that a recorded family's true grouping is not a reading
  of its record.

## 11. Frozen inputs and environment

- **Pinned by SHA-256 in the runner at the freeze commit:**
  - this protocol;
  - `EXECUTION-CONFIG.json`;
  - `world.py`, `arms.py`, `scoring.py`;
  - `experiments/dri2/stats.py`;
  - `provenance/dependence_robustness.py`;
  - `provenance/decision_relative.py`.
- **Environment:** CPython 3.12, with no third-party packages beyond the repository.
- **Candidate record:** committed before the run.

## 12. Boundary and disclosure

- **Where the engine came from.** The engine change was designed from DRI-2's false
  settlements. A diagnostic of it on already-scored DRI-2 v2 worlds was seen before
  this protocol. It flagged all four known traps, with no robust-but-wrong result,
  about 700 extra reversible looks per prevented false settlement, and 70% extra
  flags in shared-origin worlds.
- **What the protocol reuses.** It reuses none of those worlds, and families 4 to 7
  are new.
- **What is guaranteed by construction.** With recorded dependence and truthful
  lookups, the tiered rule cannot settle silently and wrongly; that is a property
  of the rule. This run therefore mainly tests the implementation, the generator and
  the cost. Family 7 shows the boundary.
- **Authorship.** Everything is authored by the same control domain as the engine,
  so the adversarial families are not independent.
- **Scope.** Synthetic worlds only. No real-world lineage, cost, or authority claim.
