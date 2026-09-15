# DRI-3 v1 confirmatory result

**Outcome:** the preregistered criterion was **supported**. All 27 registered checks
passed. One registered comparison, `side_asymmetric`, was underpowered under the
preregistered rule and was not a check.

**Records:**

| What | Where |
|---|---|
| Protocol | `experiments/dri3/PREREGISTRATION.md`, frozen at commit `1875bd70c8540b7e989c44e2a633a2c9372e3b8a` |
| Pinned runner | commit `1ee4ff230c639cb263cfadb774bede0a32f8ebc2` |
| Candidate record `DRI-3-V1` | commit `28d3a4c80030a33151da1b877629f58381833fc6` |

All three were pushed before any confirmatory world was generated.

**Commit history note:** an earlier commit, `e947226`, carries the title "Freeze DRI-3
protocol v1" but holds the unfrozen draft files. Its freeze script failed at the
rename step. The protocol commit above records this. No world was generated between
the two commits.

## Run

- **Worlds:** 14,000 confirmatory worlds (7 families × 2,000), 42,000 decisions.
- **Executions:** two full executions, with identical semantic results. The semantic
  SHA-256 was
  `508282040f5e22760c6bf86e7e53becdb477abedb814643daeef67b2d0d4709e`.
- **Output:** `result.json`, SHA-256
  `e41245b961137de97b1e9b272de9370c467b9f362f2ca9248c7b830850e81ab1`.
- **When:** 2026-09-15, from 16:58:46 to 17:00:08 UTC.
- **Environment:** CPython 3.12.13 on macOS arm64, at commit `28d3a4c`, with a clean
  worktree. Logs are `run-stdout.txt` and `run-stderr.txt`.

## Primary results

Every recorded family has 6,000 decisions, 3,000 of them irreversible. With zero
events, the exact 95% upper bound on the rate is 0.000499 over 6,000 decisions and
0.000998 over 3,000. Both are below the preregistered 0.001.

Columns 2 and 3 are for the tiered rule, the method under test; the last column
compares it with the agreement rule.

| Family | Silent false settlements | False settlements on irreversible decisions | Agreement rule, silent false settlements |
|---|---:|---:|---|
| single domain | 0 | 0 | 0 |
| joint domain | 0 | 0 | 23, all flagged by the tiered rule; exact McNemar p = 2.4×10⁻⁷ |
| separate control, shared origin | 0 | 0 | 0 |
| three stacked | 0 | 0 | 757, all on irreversible decisions; p ≈ 10⁻²²⁸ |
| side asymmetric | 0 | 0 | 0; underpowered, not a check |
| decoy shared identity | 0 | 0 | 0 |

- **Joint domain.** The tiered rule made the same 23 false reversible settlements as
  the agreement rule, because on reversible decisions it settles on agreement. But it
  stamped all 23 "not robust", so none was silent.
- **Three stacked.** On irreversible decisions it abstained or looked where the
  agreement rule settled falsely 757 times.

## The stacked-dependence mistake under each rule

| Family | Agreement rule, false settlements | Robustness everywhere | Tiered rule | Always look |
|---|---:|---:|---:|---:|
| joint domain | 23 | 0 | 23, all flagged | 0 |
| three stacked | 757 | 0 | 0 | 0 |

## Cost scorecard (selects a policy; not a pass or fail)

These figures cover reversible decisions in the six recorded families. They compare
robustness everywhere with the agreement rule.

- **Extra looks:** 1,102.
- **False settlements prevented:** 23, all in joint domain.
- **Extra looks per prevented false settlement:** **47.9**, within the preregistered
  ceiling of 100.
- **Policy selected:** **force looks on reversible decisions.**
- **Extra abstentions** where the agreement rule would have settled correctly: 465.

The ratio rests on one family. In joint domain it was 3.6 extra looks per prevented
false settlement. In the other five recorded families, forced looks on reversible
decisions prevented nothing. They cost 51, 797, 124, 16 and 31 extra looks, in the
order single domain, shared origin, side asymmetric, decoy and three stacked. So the
selected policy is right for the family mix this protocol generated. It is not a
general finding about how often stacked dependence occurs.

## What the robustness check cost

**Separate control, shared origin**, correct settlements:

| Condition | Agreement rule | Tiered rule | Robustness everywhere |
|---|---:|---:|---:|
| lookup available | 1,072 | 1,072 | 1,072 |
| lookup unavailable | 953 | 658 | 291 |

- **With a lookup,** no rule lost a correct settlement. The robustness check cost
  looks: the agreement rule made 1,964, the tiered rule 2,255 and robustness
  everywhere 2,667.
- **Without a lookup,** the check turned settlements the agreement rule got right by
  luck into required abstentions. The record alone could not justify them. That is
  the price of immunity where lineage cannot be checked, and it falls mostly on
  families with shared identities.
- **Decoy shared identity** cost little. Robustness everywhere made 16 more looks than
  the agreement rule, with no loss of correct settlements. Most decoy identities
  already made the cuts disagree, and the agreement rule looked anyway.

## Expected failure: unrecorded dependence

This family was reported apart, as declared.

- **Every rule that reads the record** (agreement rule, robustness everywhere, tiered
  rule) made 817 silent false settlements, 460 of them irreversible.
- **Always look** made 429, all in lookup-unavailable worlds.
- **The oracle** made 0.

Dependence that no recorded identity carries cannot be detected from the record.
Only lineage finds it.

## A family that did not test what it was built to test

`side_asymmetric` was meant to produce the stacked-dependence mistake with
different dependencies on each side. It never did.

- **The numbers:** all five cuts agreed and settled on 3,350 of its 6,000 decisions,
  and in none of them did the true grouping differ.
- **Why:** each cut that merges one side's pair undercounts that side, so the cuts
  disagree with each other rather than overcount the same side together.
- **Consequence:** the agreement rule made no false settlement there. The
  preregistered comparison was underpowered, and it is reported, not counted. The
  family still exercised the rules, with no false settlements under any of them, but
  it is not evidence about side-asymmetric stacking.

## What this establishes

Within this frozen synthetic model, with truthful lookups:

- **Silent false settlements:** settling only on a settlement robust over every
  combination of recorded possible dependence, under the owner's tiered cost rule,
  made none in six families of recorded dependence. That includes 780 decisions
  where the old agreement rule settled falsely.
- **Irreversible decisions:** it made no false settlement on any of them.
- **Bounds:** both rates are bounded below 1 in 1,000 at 95% confidence.
- **Cost:** extra looks where lookups exist, and lost settlements where they do not.

## What it does not establish

- **By construction:** with recorded dependence and truthful lookups, the tiered rule
  cannot settle silently and wrongly, as the protocol states. The run confirms the
  implementation, the generator and the cost; it is not an independent discovery
  that the rule works.
- **Imperfect lookups:** deferred by owner decision.
- **Unrecorded dependence:** it provides no immunity to it. Family 7 shows this
  directly.
- **Side-asymmetric stacking:** that family did not produce the case.
- **The real world:** real-world frequency of stacked dependence, or whether the
  selected reversible policy suits real deployments.
- **Independence of authorship:** the families were authored in the same control
  domain as the engine. This is internal replication.
- **Authority:** permission for anything to act.
