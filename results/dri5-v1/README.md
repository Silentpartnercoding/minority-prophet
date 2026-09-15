# DRI-5 v1 confirmatory result

**Outcome:** the preregistered joint criterion was **not supported**. 189 of the 193
registered checks passed.

**What failed.** All four failures are recovery checks at a missing rate of
m = 0.25. In each, the content tiered rule made fewer silent false settlements than
the tiered rule, but not significantly fewer:

| Family | Cell | Tiered rule | Content tiered rule | Exact McNemar p (raw) |
|---|---|---:|---:|---:|
| separate control, shared origin | p = 0, q = 0 | 57 | 50 | 0.016 |
| joint domain | p = 0.5, q = 0 | 93 | 87 | 0.031 |
| three stacked | p = 0.5, q = 0 | 472 | 471 | 1 |
| separate control, shared origin | p = 0.5, q = 0 | 57 | 56 | 1 |

The shared-origin cell at p = 0, q = 0 was below 0.05 before correction and failed
after Holm correction.

**Underpowered comparisons.** The tiered rule made no silent false settlement in any
`decoy_shared_identity` cell. Its 8 comparisons were therefore underpowered, and
32 were powered.

**Commits.** All three were pushed before any confirmatory world was generated. The
draft was committed first, at `c9cb99e`, together with the DR3 proof.

| What | Commit |
|---|---|
| Protocol, `experiments/dri5/PREREGISTRATION.md` | `f80c6a1b0085fed57352b95dec9e44e7c407e6e3` |
| Pinned runner | `87cf5b8756ceb6d1c1df2f5dc4edaa380701153f` |
| Candidate record `DRI-5-V1` | `d7c7de82fd95d0a42bf64e6989774e7b8798e407` |

One slip before the runner commit: the first generated runner pinned the DRI-4
generator's hash under the DRI-5 generator's name. Its own test caught this, the
runner was regenerated, and only the corrected runner was committed.

## Run

- **Scope:** 10,000 base worlds, each scored through 12 cells, which is 120,000 scored
  worlds with 6,000 decisions per family per cell.
- **Reproducibility:** two full executions gave identical semantic results. The
  semantic SHA-256 was
  `5c92a1c7eaaeaf6f4e977d7d52718f112ba3f9a325ca9b43987084b9e4b7d877`.
- **Output:** `result.json`, SHA-256
  `e6a2e80271ab7939b4f7389a96431cd0cc5c3a4f5d79bc46235a9dfb62004301`.
- **When:** 2026-09-15, from 19:12:17 to 19:27:38 UTC.
- **Environment:** CPython 3.12.13 on macOS arm64, at commit `d7c7de8`, with a clean
  worktree. Logs are `run-stdout.txt` and `run-stderr.txt`.
- **Concurrent run:** from 19:18 the DRI-6 confirmatory run executed at the same time
  in a separate worktree. The two runs share no state.

## 1. The guarantees held in the implementation

- **Complete lineage.** At m = 0 the content tiered rule made zero silent false
  settlements in every family and cell.
- **Never worse.** It was never silently wrong on a decision where the tiered rule
  was not.
- **Admissible decisions.** It was never silently wrong on a decision whose true
  grouping was admissible over lineage and content.

These results check the implementation of consequences of DR2 and of monotonicity.
They are not discoveries.

## 2. Content catches forgotten copies, and little else

The table shows silent false settlements, tiered rule against content tiered rule,
with the share content prevented. Here p is the paraphrase rate and q the collision
rate.

| Family | m | p 0, q 0 | p 0, q 0.2 | p 0.5, q 0 | p 0.5, q 0.2 |
|---|---|---|---|---|---|
| side asymmetric trap | 0.25 | 2,012 → 0 (100%) | 2,012 → 0 (100%) | 2,012 → 1,624 (19%) | 2,012 → 1,514 (25%) |
| side asymmetric trap | 0.5 | 4,065 → 0 (100%) | 4,065 → 0 (100%) | 4,065 → 3,477 (14%) | 4,065 → 3,314 (18%) |
| three stacked | 0.25 | 472 → 452 (4%) | 472 → 300 (36%) | 472 → 471 (0%) | 472 → 320 (32%) |
| three stacked | 0.5 | 1,166 → 974 (16%) | 1,166 → 711 (39%) | 1,166 → 1,116 (4%) | 1,166 → 860 (26%) |
| joint domain | 0.25 | 93 → 67 (28%) | 93 → 48 (48%) | 93 → 87 (6%) | 93 → 68 (27%) |
| joint domain | 0.5 | 242 → 119 (51%) | 242 → 87 (64%) | 242 → 207 (14%) | 242 → 179 (26%) |
| separate control, shared origin | 0.25 | 57 → 50 (12%) | 57 → 26 (54%) | 57 → 56 (2%) | 57 → 34 (40%) |
| separate control, shared origin | 0.5 | 334 → 252 (25%) | 334 → 157 (53%) | 334 → 319 (4%) | 334 → 226 (32%) |

- **Forgotten copies.** In the trap family, the lost dependence is copying. There,
  exact content removed every silent false settlement at both missing rates. It also
  removed every irreversible false settlement: 993 at m = 0.25 and 2,052 at m = 0.5,
  down to 0.
- **Shared components.** In three stacked, joint domain and shared origin, much of
  the lost dependence is roots that share a component or origin without being
  copies. Content carries no trace of that, and recovery was partial.
- **Paraphrase.** Rewording half of all copies cut recovery sharply everywhere: to
  14–25% in the trap family and to 0–14% elsewhere. It produced three of the four
  failed checks.
- **Collisions.** Chance shared wording (q = 0.2) prevented more errors, because it
  made the rule more cautious across the board. That caution is not detection, and it
  has a cost (section 3).
- **Admissibility undercounts recovery.** "Admissible over lineage and content"
  undercounts what content recovers. In the trap family at m = 0.25, p = 0, q = 0,
  content restored admissibility on only 844 of the decisions the tiered rule got
  wrong silently, yet the content rule prevented all 2,012. Robustness needs the root
  counts to be bounded correctly, not the full grouping to be recovered.

## 3. Cost of collisions

These figures use complete lineage (m = 0), tiered rule against content tiered rule:

| Family | Stamped correct settlements, q 0 → q 0.2 (content rule) | Correct settlements, q 0 → q 0.2 (content rule) |
|---|---|---|
| three stacked | 31 → 256 | 2,013 → 1,867 |
| joint domain | 44 → 294 | 2,681 → 2,547 |
| separate control, shared origin | 744 → 860 | 1,724 → 1,724 |
| decoy shared identity | 0 → 500 | 3,358 → 3,358 |

- **What collisions cost.** With no missing lineage there is nothing to recover, so
  collisions only cost. Correct reversible settlements get stamped "not robust", and
  some decisions without a lookup can no longer be settled at all.
- **Scoring rule.** Scoring counts a decision as decidable only when lineage and
  content together robustly settle it. Those lost settlements therefore appear as
  required abstentions, not unneeded ones, and the table shows them as the drop in
  correct settlements.

## What this establishes

Within this frozen synthetic model with truthful lookups:

- **Guarantees.** They held in the implementation.
- **Forgotten copies.** Where missing lineage hides copying, an exact content
  fingerprint restores full protection. It did so on the family built to trap the old
  rule.
- **Other dependence.** It does not restore protection where the missing dependence
  is a shared component or origin.
- **Paraphrase.** Rewording largely defeats it.
- **Verdict.** Recovery was not significant in 4 of 32 powered comparisons, so the
  frozen criterion is not met.

## What it does not establish

- **Real-world content.** Real content similarity and real paraphrase or collision
  rates were not measured. Fingerprints here are exact and synthetic.
- **Fuzzy matching.** How a fuzzy similarity measure would trade detection against
  collisions is untested.
- **Rescue.** The failed checks are not rescued. The verdict stands, and a narrower
  criterion would be a new registered version.
- **Imperfect lookups.** They are covered by DRI-6.
- **Independence of authorship.** The families, content model and arms were authored
  in the same control domain as the engine. This is internal replication.
- **Authority.** It grants no permission for anything to act.
