# DRI-4 v1 confirmatory result

**Outcome:** the preregistered joint criterion was **not supported**. 65 of 67
registered checks passed.

**What failed.** Both failures are the significance check in
`separate_control_shared_origin` at missing rate m = 0.1. The tiered rule made
fewer silent false settlements than the agreement rule there, but not significantly
fewer:

| Spurious rate | Tiered rule | Agreement rule | Exact McNemar p (raw) |
|---|---:|---:|---:|
| s = 0 | 10 | 15 | 0.062 |
| s = 0.1 | 14 | 17 | 0.25 |

Both raw p-values are already above 0.05, before correction.

**What else was not a check.** The four `decoy_shared_identity` comparisons were
underpowered under the preregistered rule, so they were not checks.

**Commits.** All three below were pushed before any confirmatory world was
generated. The draft was committed first, at `86e5028`, so the freeze is a clean
rename.

| What | Commit |
|---|---|
| Protocol, `experiments/dri4/PREREGISTRATION.md` | `dfe938da19f03b81e53520bb4e2dee33f889b2f4` |
| Pinned runner | `4f94db76a078d441fc4c9779324d2a2031043678` |
| Candidate record `DRI-4-V1` | `1c7c5e2c7f598ff3a330a36793fb0db9d8ede6f9` |

## Run

- **Scope:** 10,000 base worlds, each scored through 8 record cells: 80,000 scored
  worlds and 240,000 decisions.
- **Reproducibility:** two full executions gave identical semantic results. The
  semantic SHA-256 was
  `f3339a486b6098aeffcf8b6e780679221e2d91c9eef328a027f4bf6c0aecacbd`.
- **Output:** `result.json`, SHA-256
  `55f9006693b2fcb029260467351602aa3254e1ade9238d5531121475580847de`.
- **When:** 2026-09-15, from 18:04:33 to 18:14:02 UTC.
- **Environment:** CPython 3.12.13 on macOS arm64, at commit `1c7c5e2`, with a clean
  worktree. Logs are `run-stdout.txt` and `run-stderr.txt`.

## 1. With a complete record, the proven guarantee held

At m = 0 the tiered rule made **zero silent false settlements** in every family, at
both spurious rates. Each figure is over 6,000 decisions, with a 95% upper bound of
0.000499.

| Family | Agreement rule, silent false settlements (s = 0 / s = 0.1) | Tiered rule |
|---|---|---:|
| side asymmetric trap | 6,000 / 3,494 | 0 / 0 |
| three stacked | 768 / 671 | 0 / 0 |
| joint domain | 18 / 16 | 0 / 0 |
| separate control, shared origin | 0 / 0 | 0 / 0 |
| decoy shared identity | 0 / 0 | 0 / 0 |

This is the implementation check of the proven theorem (DR2), not a discovery.

The repaired trap family did what DRI-3's side-asymmetric family could not. At
m = 0 and s = 0, the agreement rule settled all 6,000 of its decisions falsely. The
tiered rule stamped every reversible one "not robust", 3,000 in all, and made no
false settlement on any irreversible one.

## 2. As the record loses shared identities, protection erodes

Silent false settlements at s = 0 (tiered rule against agreement rule), with the
share the tiered rule prevented:

| Family | m = 0.1 | m = 0.25 | m = 0.5 |
|---|---|---|---|
| side asymmetric trap | 713 vs 5,551 (87%) | 2,016 vs 5,399 (63%) | 4,123 vs 5,596 (26%) |
| three stacked | 212 vs 835 (75%) | 486 vs 1,003 (52%) | 1,178 vs 1,478 (20%) |
| joint domain | 30 vs 50 (40%) | 104 vs 134 (22%) | 252 vs 302 (17%) |
| separate control, shared origin | 10 vs 15 (33%) | 75 vs 91 (18%) | 322 vs 357 (10%) |
| decoy shared identity | 0 vs 0 | 0 vs 0 | 0 vs 0 |

- **Never worse.** In all 30 cells with m > 0, the tiered rule made no more silent
  false settlements than the agreement rule. It was significantly fewer in 14 of the
  16 powered comparisons.
- **But not immune.** Once real dependence is missing from the record, the true
  grouping is no longer a reading the record allows. The rule can then be robustly
  wrong, and at half the shared identities missing it prevented only 10–26% of the
  agreement rule's silent errors.
- **Where the errors come from.** In every cell, the tiered rule's silent false
  settlements equal those of robustness everywhere. The silent errors that return
  are robust-but-wrong settlements, the case the theorem's assumption excludes.
- **Spurious identities.** They made the rule more cautious, and so cut silent errors
  further. For example, in the trap family at m = 0.1 the tiered rule's count fell
  from 713 to 414.

## 3. Irreversible decisions

False settlements on irreversible decisions were reported with no pass mark, as
preregistered. They rise with m. Tiered rule against agreement rule, at s = 0:

| Family | m = 0 | m = 0.1 | m = 0.25 | m = 0.5 |
|---|---|---|---|---|
| side asymmetric trap | 0 vs 3,000 | 357 vs 2,766 | 1,015 vs 2,708 | 2,075 vs 2,785 |
| three stacked | 0 vs 768 | 181 vs 797 | 390 vs 883 | 879 vs 1,120 |
| joint domain | 0 vs 0 | 9 vs 10 | 25 vs 34 | 99 vs 122 |
| separate control, shared origin | 0 vs 0 | 7 vs 7 | 64 vs 68 | 232 vs 250 |

## 4. Cost

In `separate_control_shared_origin` the tiered rule settled correctly less often than
the agreement rule in every cell. At m = 0 and s = 0 it made 1,816 correct
settlements against 2,133, the same price of robustness DRI-3 measured. In the
other families, correct settlements were within a few percent.

## What this establishes

Within this frozen synthetic model with truthful lookups:

- **Complete record.** The proven guarantee held exactly in the implementation, on
  families built to break the agreement rule. That includes a trap on which the
  agreement rule settled every decision falsely.
- **Incomplete record.** The robustness rule's advantage shrinks steadily as true
  shared identities go missing. It never made more silent errors than the agreement
  rule. It was not significantly better in every powered comparison, so the frozen
  criterion is not met.

## What it does not establish

- **Real-world rates.** Real rates of missing or spurious identities, or which cell
  resembles any real system.
- **Imperfect lookups.** Behaviour with imperfect lookups remains the follow-up.
- **Rescue.** Any rescue of the failed checks. The verdict stands, and a different
  threshold or rate grid would be a new registered version.
- **Independence of authorship.** The families and degradation model are authored in
  the same control domain as the engine. This is internal replication.
- **Authority.** Permission for anything to act.
