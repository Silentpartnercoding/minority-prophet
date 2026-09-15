# DRI-4 — when the record is incomplete, and when the trap is real

Status: **DRAFT. NOT FROZEN. NOT RUN.** It becomes a preregistration only after the
owner settles section 6, and the protocol, generator and runner are committed and
pinned before any world is generated.

## 1. Why this exists

DRI-3 (`results/dri3-v1/`) had two limits.

1. **Guaranteed by construction.** With every real dependence recorded and truthful
   lookups, the tiered rule cannot settle silently and wrongly. DRI-3 therefore
   confirmed the code and measured the cost, but discovered nothing about the rule.
   The guarantee is now a theorem: `robust_settlement_is_true` in
   `formal/lean/MinorityProphetCore/DependenceRobustness.lean`. It needs no further
   experiment. DRI-4 tests what the theorem assumes: that the record carries every
   real dependence. When it does not, the outcome is not known in advance.
2. **A trap family that did not trap.** `side_asymmetric` never produced a decision
   on which all five cuts agreed while the true grouping differed (0 of 3,350
   agreeing decisions). Each cut that recorded one side's dependence undercounted
   that side, so the cuts disagreed instead.

## 2. Questions

1. **Incomplete record.** As real shared identities go missing from the record, and
   spurious ones are added, how fast do silent false settlements and irreversible
   false settlements appear under the tiered rule? Are they still fewer than under
   the agreement rule?
2. **Side-asymmetric trap.** Can dependence split across the two sides, recorded at
   different cuts, produce a decision on which every cut agrees wrongly? If it can,
   does the tiered rule avoid silent false settlements there?

Lookups stay truthful. Imperfect lookups remain their own follow-up (owner
decision). No human; time is measured, not a criterion.

## 3. Worlds

**Record degradation.** DRI-3's recorded families (joint, shared origin, three
stacked, decoy, and the repaired side-asymmetric family below) are generated as in
DRI-3, then their record is degraded at stated rates:

- **missing rate m:** each true shared identity is independently replaced by
  distinct identities with probability m. Examples: the origin two copies of one
  source share, or the component two roots share.
- **spurious rate s:** each pair of independent roots independently receives a
  shared identity at a random cut with probability s.
- **grid:** m ∈ {0, 0.1, 0.25, 0.5} × s ∈ {0, 0.1}. At m = 0 and s = 0 the theorem
  guarantees zero silent false settlements, so that cell is a check of the
  implementation, not a finding.

The true grouping and the lookup are unchanged by degradation. Only what the record
shows changes.

**Repaired side-asymmetric family.** Generated structurally, then accepted only when
all of these hold:

- the two sides carry different hidden dependencies;
- those dependencies are recorded at different cuts;
- all five cuts settle the same way;
- the true grouping settles otherwise, or does not settle.

This is a property of the world checked at generation time. It is not a look at any
arm's behaviour.

- **Feasibility.** Checked on development worlds before freezing. If no world can
  meet the condition under this identity model, that is reported as the finding:
  dependence recorded on opposite sides at different cuts cannot produce the
  agreement trap. The family is then dropped, not forced. A proof of that statement
  would be attempted before the finding is claimed.

## 4. Arms

As in DRI-3:

- agreement rule;
- robustness everywhere;
- tiered rule (method under test);
- always look;
- oracle reference.

## 5. Endpoints

Per (m, s) cell and family, reported apart and never pooled:

- **primary:** silent false settlements and irreversible false settlements, for the
  tiered rule and the agreement rule, with exact 95% bounds;
- **secondary:**
  - flagged false settlements;
  - unneeded and required abstentions;
  - looks;
  - the reversible scorecard;
  - the dose-response slope of false settlements against m.

## 6. Decisions required before freezing

1. **Success criterion.** Proposed:
   - at every m > 0 cell, the tiered rule's silent false settlements are no more
     than the agreement rule's;
   - at m ≤ 0.25, they are significantly fewer, wherever the agreement rule has
     enough failures to test;
   - irreversible false settlements under the tiered rule are reported with bounds
     at each cell, with no pass mark, because they are expected to rise with m.
2. **The rate grid:** the missing and spurious rates in section 3, or others.
3. **Size:** worlds per cell. The rule-of-three bound at m = 0 needs 2,995 decisions
   per family. Higher-m cells need enough agreement-rule failures to test a
   difference.
4. **If the repaired trap proves infeasible:** drop it and report the infeasibility,
   as proposed, or redesign the identity model.
5. **Authorship:** the same limit as DRI-2 and DRI-3, stated.

## 7. Not claimed

This draft claims nothing. A future result would describe how the rule degrades in
a synthetic model of incomplete records. It would not give real-world rates of
missing or spurious identities, behaviour under imperfect lookups, or any authority
to act.
