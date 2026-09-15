# DRI-2 v1 confirmatory result

**Outcome:** the preregistered joint criterion was **not supported**. 45 of the 50
registered checks passed. All five failures are on time to crossing.

The protocol is `experiments/dri2/PREREGISTRATION.md`, frozen at commit
`574a6a626845215244f03fa85a5cd689f0ed350c`. The pinned runner is commit
`a7e2970422df5d12d713a53909e543106a1d60b3`, and the candidate record `DRI-2-V1` was
committed at `1e6b07c87e609627cbb393f9fec1435302ac3264`. All three were pushed
before any confirmatory world was generated.

## Run

- **Worlds:** 12,624 on the confirmatory salt, 3,156 per family.
- **Executions:** two full executions, with identical semantic results. The semantic
  SHA-256 was
  `ade282044427a4d584c23fa272cdfb030a2416da0ba3c8f6b77b0906cc98aa02`.
- **Output:** `result.json`, SHA-256
  `7a8203aa384074748b51521e9898c2d39ab1538e3a9ffcd11b6e0828ad5d7f01`.
- **When:** 2026-09-15, from 00:23:07 to 00:30:36 UTC.
- **Environment:** CPython 3.12.13 on macOS arm64, at commit `1e6b07c`, with a clean
  worktree. Standard output and error are kept as `run-stdout.txt` and
  `run-stderr.txt`.

## Crossing rate

The method under test is the decision-sensitivity guided method: it settles when
the choice of cut does not change the settlement, probes lineage when it does, and
escalates when the probe is unavailable.

| Arm | single domain | joint domain | separate control, shared origin | genuinely independent |
|---|---:|---:|---:|---:|
| **method under test** | **1.000** | **0.997** | **1.000** | 1.000 |
| agent headcount | 0.065 | 0.077 | 0.279 | 1.000 |
| fixed machine | 0.076 | 0.082 | 0.279 | 1.000 |
| fixed controller | 0.212 | 0.085 | 0.283 | 1.000 |
| fixed evidence origin | 0.441 | 0.083 | 0.529 | 1.000 |
| fixed upstream component | 0.772 | 0.945 | 0.855 | 1.000 |
| weakest link | 0.802 | 0.945 | 0.860 | 1.000 |
| determined-or-escalate | 1.000 | 0.997 | 1.000 | 1.000 |
| *oracle (reference)* | *1.000* | *1.000* | *1.000* | *1.000* |
| *rules engine (reference)* | *0.667* | *0.394* | *0.358* | *1.000* |

In every structured family, the method under test crossed significantly more often
than headcount, all four fixed cuts and weakest link (exact McNemar, Holm-adjusted
p < 0.001). No arm crossed more often than it. Determined-or-escalate crossed exactly
as often, because stalls do not end a run and it crosses by asking.

## Why the joint criterion failed

The criterion also required the method to be significantly faster than
determined-or-escalate and weakest link, on worlds both arms crossed, in each
structured family.

| Family | vs determined-or-escalate | vs weakest link |
|---|---|---|
| single domain | faster: −93.8 ms mean, Holm p 0.041 — **passed** | −57.3 ms, Holm p 0.449 — **failed** (not significant) |
| joint domain | **slower**: +92.8 ms, Holm p 0.0015 — **failed** | **slower**: +100.9 ms, Holm p 0.0015 — **failed** |
| separate control, shared origin | **slower**: +539.0 ms, Holm p < 10⁻²⁰⁰ — **failed** | **slower**: +526.0 ms, Holm p < 10⁻²⁰⁰ — **failed** |

The source is the clock. The breakdown below is descriptive, computed from the
frozen output after the verdict; it is not a preregistered analysis.

- **A probe costs 1,000 ms, and the method probes whenever the cuts disagree.**
  That includes decisions that turn out to need a human. There it pays for the probe
  and then makes a required hand-over, which costs nothing. It escalated after
  probing 2,701 times in single domain, 2,683 in joint domain and 2,158 in separate
  control, shared origin.
- **Asking arms pay only for asking at the wrong time.** Determined-or-escalate and
  weakest link never probe. They pay 2,000 ms for each wrong-time escalation, and
  nothing at a required hand-over.
- **Per world, probe time against wrong-time escalation time was:**
  - single domain: 1,805 ms against 1,899 ms (determined-or-escalate) and 1,528 ms
    (weakest link);
  - joint domain: 1,609 ms against 1,537 ms and 1,447 ms;
  - separate control, shared origin: 829 ms against 290 ms and 205 ms. This family
    has 457 gather junctions but 2,202 hand-over junctions, so looking first
    mostly buys nothing.

Under the frozen clock, looking before a hand-over that looking cannot resolve
costs time, while asking there is free. That makes the method slower wherever
hand-overs outnumber gather junctions.

## Secondary results

| Family | Excess human calls: method / determined-or-escalate / weakest link | Clean crossings (no incorrect stall): method / determined-or-escalate | Twin discrimination, method |
|---|---|---|---|
| single domain | 0 / 2,997 / 2,412 | 3,156 / 1,343 | 1,895 of 1,895 |
| joint domain | 29 / 2,421 / 2,277 | 3,117 / 1,541 | 1,674 of 1,700 |
| separate control, shared origin | 0 / 457 / 323 | 3,156 / 2,722 | 1,150 of 1,150 |
| genuinely independent | 0 / 0 / 0 | 3,156 / 3,156 | none eligible |

- **Falls.** The method fell in 10 joint-domain worlds, the same count as
  determined-or-escalate. Every cut settled the same way there while the true
  grouping did not, so settling when all cuts agree is wrong in those worlds.
- **Genuinely independent.** No decision was material, and every arm behaved
  identically. The non-inferiority checks passed trivially.

## What this establishes

Within this frozen synthetic model:

- **Crossing and wrong-time asks.** Settling when the cut is not decision-material
  and looking when it is crossed as often as always escalating when uncertain, with
  almost no human calls beyond those required. It crossed far more often than
  headcount, any fixed cut, or weakest link.
- **Twin discrimination.** In twin pairs, the method looked where lineage existed and
  handed over where it did not.
- **Time.** It was not faster than the arms that ask, and in two families it was
  slower. The registered criterion therefore fails. This is reported as the result,
  and nothing is re-run under a changed criterion or clock.

## What it does not establish

- **Beyond the model:** real-world lineage availability, the prevalence of these
  failure domains, or any real cost of probing or of human attention.
- **The clock:** that the result is insensitive to the frozen charges of 1,000 ms per
  probe and 2,000 ms per wrong-time escalation. A different clock is a new registered
  version, not this one.
- **Hidden error kinds:** DRI-2 has no held-back worlds.
- **Independence of authorship:** it was authored, built, run and reviewed in the
  same control domain as the method. This is internal replication, not independent
  validation.
- **Authority:** permission for anything to act.
