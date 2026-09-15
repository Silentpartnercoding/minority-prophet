# DRI-6 v1 confirmatory result

**Outcome:** the preregistered joint criterion was **supported**. All 77 registered
checks passed.

**The four comparisons that were not checks.** In the merge-only cell (0, 0.2) the
tiered rule made fewer than 12 silent false settlements in joint domain, shared
origin, three stacked and the trap. Those comparisons were underpowered under the
preregistered rule, so they were not checks. The other 16 comparisons were powered,
and every one was significant.

**Commits.** All three were pushed before any confirmatory world was generated. The
draft was committed first, at `a3d225f`.

| What | Commit |
|---|---|
| Protocol, `experiments/dri6/PREREGISTRATION.md` | `0ecd84704f2c7147e4b7e3effcbbb1fea2373b9e` |
| Pinned runner | `401746aa4802595ef6064aa8be652869c8d40e96` |
| Candidate record `DRI-6-V1` | `8d3df18e5b46ce73cb33984b3f698014cfdd99b9` |

## Run

- **Scope:** 10,000 base worlds, each scored under 5 lookup-error cells, with 6,000
  decisions per family per cell.
- **Reproducibility:** two full executions gave identical semantic results. The
  semantic SHA-256 was
  `f4d20fcf277541953c476935b53fe1ec8c0b25e99c0aa8df4ee5dd6254c37783`.
- **Output:** `result.json`, SHA-256
  `8cef26f1502fa8e80f72c8e45dfb8a226e3aed951b7dbb459f4e7c8cfe3e1734`.
- **When:** 2026-09-15, 19:18:17 to 19:24:14 UTC.
- **Environment:** CPython 3.12.13 on macOS arm64, at commit `8d3df18`, with a clean
  worktree. Logs are `run-stdout.txt` and `run-stderr.txt`.
- **Concurrency:** the DRI-5 confirmatory run was executing in a separate worktree at
  the same time. The two runs share no state.

## 1. Imperfect lookups do more than cost time

With truthful lookups, the tiered rule made zero silent false settlements in every
family. Once lookups erred, it made many, and every one of them, in every family and
cell, was made after a look. The robustness stamp still covered the decisions it
settled without looking.

## 2. Looking twice removes most of them

Silent false settlements, as tiered rule / checked tiered rule / confirmed tiered
rule, with the share the confirmed rule prevented:

| Family | split 0.05 | split 0.2 | merge 0.2 | split 0.2 + merge 0.2 |
|---|---|---|---|---|
| side asymmetric trap | 214 / 214 / 18 (92%) | 749 / 749 / 230 (69%) | 0 / 0 / 0 | 262 / 206 / 9 (97%) |
| three stacked | 114 / 114 / 8 (93%) | 408 / 408 / 102 (75%) | 0 / 0 / 0 | 316 / 302 / 58 (82%) |
| joint domain | 100 / 100 / 3 (97%) | 322 / 322 / 71 (78%) | 6 / 1 / 0 (100%) | 171 / 141 / 13 (92%) |
| separate control, shared origin | 104 / 104 / 8 (92%) | 412 / 412 / 89 (78%) | 0 / 0 / 0 | 264 / 249 / 42 (84%) |
| decoy shared identity | 53 / 53 / 0 (100%) | 217 / 217 / 69 (68%) | 14 / 2 / 1 (93%) | 104 / 57 / 10 (90%) |

- **Confirmation works, but not completely.** The errors that remain are the ones
  where both lookups erred the same way. At a 20% split rate that is 22–32% of the
  tiered rule's errors. Independence across calls is what makes confirmation work;
  a lookup that is wrong the same way every time would defeat it.
- **The record check catches no missed dependence.** In every split-only cell the
  checked tiered rule made exactly as many silent false settlements as the tiered
  rule. That is ledger DR3 again: the record cannot tell copies from independent
  sources. The check caught only invented dependence, in the cells with merges.
- **Guarantees held in the implementation.** Neither new arm was silently wrong where
  the tiered rule was not, in any of the 25 family-cell pairs.

## 3. Cost

Confirmed tiered rule against tiered rule, as extra looks per prevented false
settlement; extra unneeded abstentions; and correct settlements before and after:

| Family | split 0.05 | split 0.2 | merge 0.2 | split 0.2 + merge 0.2 |
|---|---|---|---|---|
| side asymmetric trap | 7.7; 0; 0 → 0 | 2.9; 0; 0 → 0 | –; 0; 0 → 0 | 1.7; 0; 0 → 0 |
| three stacked | 18.7; 2; 1,983 → 1,981 | 6.5; 6; 1,977 → 1,971 | –; 8; 1,961 → 1,953 | 5.3; 10; 1,957 → 1,947 |
| joint domain | 20.3; 12; 2,737 → 2,725 | 7.8; 50; 2,687 → 2,637 | 163.3; 233; 2,313 → 2,080 | 6.2; 218; 2,290 → 2,072 |
| separate control, shared origin | 23.9; 4; 1,726 → 1,722 | 7.1; 12; 1,714 → 1,702 | –; 87; 1,523 → 1,436 | 8.2; 98; 1,528 → 1,430 |
| decoy shared identity | 42.6; 55; 3,397 → 3,342 | 15.3; 146; 3,258 → 3,112 | 59.5; 716; 2,195 → 1,479 | 8.2; 683; 2,154 → 1,471 |

The trap family's true grouping never settles, so no arm can settle it correctly
there.

- **Missed dependence is cheap to guard against.** Against split errors the
  confirmed rule cost 2.9–42.6 extra looks per prevented false settlement. That is
  under the owner's reversible-decision ceiling of 100, and it lost few correct
  settlements.
- **Invented dependence is expensive.** When lookups merge units, the two reports
  often disagree, and the confirmed rule abstains where the tiered rule would have
  settled correctly. In decoy shared identity at a 20% merge rate, correct
  settlements fell from 2,195 to 1,479. In joint domain the cost was 163 extra looks
  per prevented false settlement, above the ceiling.

## 4. Irreversible decisions

False settlements on irreversible decisions, tiered rule against confirmed tiered
rule:

| Family | truthful | split 0.05 | split 0.2 | merge 0.2 | split 0.2 + merge 0.2 |
|---|---|---|---|---|---|
| side asymmetric trap | 0 vs 0 | 214 vs 18 | 749 vs 230 | 0 vs 0 | 262 vs 9 |
| three stacked | 0 vs 0 | 81 vs 8 | 273 vs 79 | 0 vs 0 | 212 vs 47 |
| joint domain | 0 vs 0 | 53 vs 3 | 184 vs 36 | 0 vs 0 | 92 vs 8 |
| separate control, shared origin | 0 vs 0 | 66 vs 8 | 259 vs 54 | 0 vs 0 | 171 vs 24 |
| decoy shared identity | 0 vs 0 | 30 vs 0 | 116 vs 35 | 0 vs 0 | 48 vs 6 |

## What this establishes

Within this frozen synthetic model, with a complete lineage record:

- **Correctness, not only time.** Imperfect lookups change correctness. An erring
  lookup is the main source of silent false settlements once the record cannot
  settle a decision.
- **Confirmation.** A second, independent look, settling only when the two reports
  agree, removed 68–100% of those errors in every powered comparison. Against missed
  dependence it did so at modest cost.
- **The record check.** Checking a report against the record cannot catch missed
  dependence, and catches invented dependence only partly.

## What it does not establish

- **Correlated lookup errors.** A source that is wrong the same way every time was
  not modelled, and would defeat confirmation.
- **Real-world rates.** It does not give real lookup-error rates.
- **Missing lineage or content.** It does not cover behaviour with missing lineage or
  with DRI-5's content fingerprint. A truthful report can fail the record check when
  lineage is missing.
- **Independent authorship.** The families, error model and arms were authored in
  the same control domain as the engine. This is internal replication.
- **Authority.** It grants no permission for anything to act.
