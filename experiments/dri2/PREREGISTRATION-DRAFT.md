# DRI-2 — preregistration draft

**Status: DRAFT. NOT FROZEN. NOT RUN.** This becomes a preregistration only after
the owner approves the two items marked **OWNER DECISION**, and after the protocol,
configuration and runner are committed and pinned by hash, before any confirmatory
world is generated or scored. No comparative outcome has been computed on any world,
development or confirmatory.

Design rationale: `research/decision-relative-independence/DRI-2-DESIGN-DRAFT.md`.
Implementation: `experiments/dri2/`.

## 1. Identifier

DRI-2, protocol v1. It strengthens the DRI-1A pilot (`results/dri1a-v1/`), which is
not reused.

## 2. Question

On worlds where the relevant lineage is never disclosed, does a
decision-sensitivity guided method navigate the critical path better than agent
headcount, each fixed cut, weakest link and determined-or-escalate? The method
settles when the choice of cut is not decision-material, probes lineage when it
is, and escalates when the probe is unavailable.

## 3. Hypotheses

- **Null:** the method under test crosses no more often than the comparison arms,
  and is no faster among worlds both cross.
- **Target:** see the success criterion in section 10.

## 4. Generated worlds

Four families. Each has 3 path types with 1,052 worlds each, so 3,156 worlds per
family and 12,624 in total. Every world is a sequence of 3 decisions, revealed one
at a time. For each decision the generator samples, uniformly and from a
deterministic stream:

- truth;
- causal roots per decision: 4 or 5;
- independent-root accuracy: 0.65, 0.75, 0.85 or 0.95;
- erroneous-root amplification: 1, 3, 7 or 15 observations;
- decision class: two winning roots (`low_reversible`) or three (`high_irreversible`);
- the family's hidden failure domains.

A correct root emits one observation. An incorrect root emits the amplification
count, except in `genuinely_independent`, where every root emits one.

| Family | Hidden structure | Which cut expresses the true grouping |
|---|---|---|
| `single_domain` | one failure domain, as in DRI-1A | the domain's cut |
| `joint_domain` | copy domain plus a shared upstream component across roots 0 and 1 | none: the upstream cut also merges roots 2 and 3 |
| `separate_control_shared_origin` | separately controlled roots 0 to 2 repeating one source | `evidence_origin` |
| `genuinely_independent` | no dependence | every cut |

Path types:

- `no_handover`: no hand-over junction.
- `one_handover`: exactly one hand-over junction.
- `twin`: generated with no hand-over and at least one gather junction, then has
  the lineage probe removed, so each gather junction becomes a hand-over. For
  `genuinely_independent`, gather junctions cannot occur, so a twin is a
  `no_handover` world without the probe.

## 5. Enumeration and seeds

World seed: SHA-256 of `salt|family|path_type|replicate|attempt`. Attempts run from
0 until the world matches its path type; more than 10,000 attempts invalidates the
run. The confirmatory salt is `minority-prophet-dri2-v1-confirmatory`. Development
uses `minority-prophet-dri2-development` only.

## 6. Evidence roots and dependency

Observations carry identities at `agent`, `machine`, `controller`,
`evidence_origin` and `upstream_component`, following the per-family rules in
`experiments/dri2/world.py`. The true causal unit of each observation is hidden;
the lineage probe returns it. Settlement at a cut or over true units uses
`provenance.decision_relative.assess_decision` with the decision's threshold.

Junction type, fixed by construction and hidden from contestant arms:

- **settle:** every cut settles the way the true units do.
- **gather:** otherwise, when the true units settle and the probe is available.
- **hand over:** the true units do not settle, or the probe is unavailable where
  the cuts are not all right.

## 7. Arms

**Contestants** see only the observations and the threshold (`VisibleDecision`),
plus a counted probe:

1. agent headcount;
2. fixed machine;
3. fixed controller;
4. fixed evidence origin;
5. fixed upstream component;
6. weakest link: the cut with the fewest winning roots, ties to the coarser cut;
7. determined-or-escalate: settle only when all cuts agree;
8. **method under test:** decision-sensitivity guided, as described in section 2.

None of the contestants except the method under test calls the probe.

**References**, which are told hidden facts and are not tested:

- **oracle:** takes each junction's correct move;
- **rules engine:** applies the declared family-to-cut table to the first disclosed
  domain.

## 8. Scoring and endpoints

**Junction scoring:**

- **At a hand-over junction:** escalating is required; settling is a fall.
- **At a settle or gather junction:** escalating is an incorrect stall. The scripted
  human answers and the run continues, with the stall logged.
- **Settling at a gather junction without probing** is a fall.
- **Any other settlement** is correct only if it matches the true units' settlement.

A fall ends the run. A run with no fall is **crossed**.

**Clock:** each action costs 1 virtual ms, and each probe costs 1,000. A wrong-time
escalation (at a settle or gather junction) costs **OWNER DECISION A**.

**Primary endpoint:** the crossing rate, per family.

**Secondary endpoints:**

- virtual time to crossing;
- human calls, and excess calls above each world's required minimum;
- clean crossings, with no incorrect stall;
- junction accuracy by type;
- looked before asking;
- premature hand-overs;
- over-reach;
- twin discrimination.

## 9. Effect size, uncertainty and multiple testing

- **Sizing:** each family is sized to detect a 5-point paired difference in crossing
  rate with 90% power at α = 0.05 / 7, in the least favourable case. That needs
  3,155 worlds; 3,156 are used.
- **Crossing tests:** exact McNemar tests on paired crossing outcomes. The paired
  difference is reported with a 95% interval, and crossing rates with Wilson 95%
  intervals.
- **Time tests:** Wilcoxon signed-rank tests on virtual time, over worlds both arms
  cross, with the mean difference and its 95% interval.
- **Correction:** Holm correction across the seven comparisons within each family,
  separately for crossing and for time, at a family-wise α of 0.05.
- **Across families:** the joint claim requires every family's criterion to hold, so
  it is an intersection-union test and needs no further correction.

## 10. Success, failure, invalidation, stop

**OWNER DECISION B — success criterion.** Proposed:

1. **Structured families** (`single_domain`, `joint_domain` and
   `separate_control_shared_origin`), each:
   - the method under test crosses significantly more often than agent headcount
     and all four fixed cuts;
   - no comparison arm crosses significantly more often than it;
   - among worlds both cross, it is significantly faster than
     determined-or-escalate and weakest link.
2. **`genuinely_independent`:** crossing is non-inferior to every comparison arm.
   The lower 95% bound of the paired difference must be at least −0.02.
3. **Reproducibility:** two complete executions produce identical semantic results.

**Supported** only if all three hold. Any failure is reported as the result, and
nothing is re-run under a changed criterion.

**Invalidation:** the generator exceeds its attempt limit; the two executions
differ; the runner detects a changed protocol, configuration or code hash; or a
contestant arm is shown to have read a hidden field.

## 11. Frozen inputs and environment

The following are pinned by SHA-256 in the runner at the freeze commit:

- this protocol;
- `EXECUTION-CONFIG` (renamed from `-DRAFT` at freeze, with `status: frozen`);
- `world.py`, `arms.py`, `stats.py`, `scoring.py`.

**Environment:** CPython 3.12, with no third-party packages beyond the repository.
A candidate research record is committed before the confirmatory run.

## 12. Safety boundary

Synthetic worlds only. No authority, no deployment and no external contact. A
positive result is evidence for this frozen model only. DRI-2 is authored in the
same control domain as the method it tests, and every result carries that limit.

## Owner decisions required before freezing

- **A. Charge for a wrong-time escalation.** As written, escalating costs 1 ms and
  probing costs 1,000 ms, so an arm that escalates instead of looking finishes
  faster. Proposed: 2,000 ms, twice a probe, matching "asking early costs at least
  double". Required hand-overs stay free.
- **B. Success criterion** in section 10.
