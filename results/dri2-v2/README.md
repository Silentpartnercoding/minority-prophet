# DRI-2 v2 confirmatory result

**Outcome:** the preregistered joint criterion was **supported**. All 44 registered
checks passed.

DRI-2 v2 is the final version of DRI-2. It reuses the frozen DRI-2 v1 method code
byte for byte, runs on fresh worlds, removes the human (an escalation is an
abstention and no answer is supplied), and measures speed without making it a
criterion. The protocol is `experiments/dri2v2/PREREGISTRATION.md`, frozen at commit
`7e4e7f501a6180b488caeb893c479930e771b8eb`. The runner is commit
`abd3a1631d4116e4f10bcc6597f5fab1853ca68a`, and the candidate record `DRI-2-V2` was
committed at `fd79b1f4f999636844ea34a7207c7bf01309ebaa`. All three were pushed before
any v2 world was generated.

**Disclosure, from the preregistration:** v2 was specified after the v1 result was
known. Its criterion is v1's registered criterion without the speed checks. Nothing
was added, and the method code is unchanged. This is not a blind test of a newly
conceived criterion.

## Run

- **Worlds:** 12,624 on the v2 confirmatory salt, 3,156 per family.
- **Executions:** two full executions, with identical semantic results. The semantic
  SHA-256 was
  `982792192e6b6ecde3f89f7fc889d51e87d9299e65cc56460c12dadf94be8f0c`.
- **Output:** `result.json`, SHA-256
  `a5342fc55b0491479a951e3e7c8bb8c9e3de63ae360d5e529d19d6225f32c5e3`.
- **When:** 2026-09-15, from 14:50:47 to 14:58:17 UTC.
- **Environment:** CPython 3.12.13 on macOS arm64, at commit `fd79b1f`, with a clean
  worktree. Logs are `run-stdout.txt` and `run-stderr.txt`.

## Crossing rate (primary)

| Arm | single domain | joint domain | separate control, shared origin | genuinely independent |
|---|---:|---:|---:|---:|
| **method under test** | **1.000** | **0.999** | **1.000** | 1.000 |
| agent headcount | 0.062 | 0.083 | 0.279 | 1.000 |
| fixed machine | 0.068 | 0.084 | 0.284 | 1.000 |
| fixed controller | 0.212 | 0.082 | 0.283 | 1.000 |
| fixed evidence origin | 0.446 | 0.084 | 0.529 | 1.000 |
| fixed upstream component | 0.773 | 0.936 | 0.862 | 1.000 |
| weakest link | 0.799 | 0.936 | 0.867 | 1.000 |
| determined-or-escalate | 1.000 | 0.999 | 1.000 | 1.000 |
| *oracle (reference)* | *1.000* | *1.000* | *1.000* | *1.000* |
| *rules engine (reference)* | *0.667* | *0.385* | *0.350* | *1.000* |

- **Structured families:** in each one, the method crossed significantly more often
  than headcount and all four fixed cuts (exact McNemar, Holm-adjusted p < 10⁻⁵⁹).
  No arm crossed significantly more often than it.
- **Genuinely independent:** no decision was material, every arm behaved identically,
  and non-inferiority held.
- **Falls:** the method fell in 4 joint-domain worlds, the same count as
  determined-or-escalate. Every cut agreed there while the true grouping differed.

## Unneeded abstentions (secondary, not a criterion)

An unneeded abstention is giving up at a decision the evidence could have settled,
by looking if necessary.

| Arm | single domain | joint domain | separate control, shared origin | genuinely independent |
|---|---:|---:|---:|---:|
| **method under test** | **0** | **41** | **0** | 0 |
| determined-or-escalate | 2,945 | 2,399 | 463 | 0 |
| weakest link | 2,417 | 2,237 | 324 | 0 |
| fixed upstream component | 2,318 | 2,237 | 320 | 0 |
| fixed evidence origin | 1,361 | 59 | 0 | 0 |

**Clean crossings,** with no fall and no unneeded abstention:

| Family | Method | Determined-or-escalate |
|---|---:|---:|
| single domain | 3,156 | 1,328 |
| joint domain | 3,111 | 1,519 |
| separate control, shared origin | 3,156 | 2,723 |

Determined-or-escalate crossed as often as the method only because abstaining does not
end a run.

**Twin discrimination** measures whether the method probed and settled where lineage
existed, and abstained where it was withheld:

| Family | Discriminating twins |
|---|---|
| single domain | 1,925 of 1,925 |
| joint domain | 1,714 of 1,736 (98.7%) |
| separate control, shared origin | 1,146 of 1,146 |

## Speed (measured, not a criterion)

With no human and no charge for abstaining, every action costs 1 virtual ms and a
probe 1,000 ms. The speed data now measures only the cost of looking.

- **Every other arm** averaged 3 ms per crossed world, because none of them looks.
- **The method** averaged 1,794 ms (single domain), 1,618 ms (joint domain), 836 ms
  (separate control, shared origin) and 3 ms (genuinely independent). That is about
  one probe per material decision: 5,651, 5,092, 2,628 and 0 probes in total.
- **Paired comparisons:** on worlds both arms crossed, the method was significantly
  slower than every non-looking arm, by roughly the time of its probes. That is
  expected by construction.
- **What the time bought:** the difference between unneeded abstentions and clean
  crossings above.

## What this establishes

Within this frozen synthetic model, where the relevant lineage is never disclosed, a
method that settles when the choice of cut is not decision-material and looks when it
is:

- crossed as often as always abstaining when uncertain, and far more often than
  headcount, any fixed cut or weakest link;
- almost never gave up on a decision the evidence could settle: 0 to 41 unneeded
  abstentions, against 324 to 2,945 for the abstaining arms;
- looked where lineage was available and abstained where it was not.

The v1 finding reproduced on fresh worlds without a human.

## What it does not establish

- **Beyond the model:** real-world lineage availability, prevalence of these
  failure domains, or the real cost of looking.
- **The criterion:** a blind test of it. It was fixed after v1.
- **Hidden error kinds:** DRI-2 has no held-back worlds.
- **Independence of authorship:** the test was authored, built, run and reviewed in
  the same control domain as the method. This is internal replication.
- **Authority:** permission for anything to act.
