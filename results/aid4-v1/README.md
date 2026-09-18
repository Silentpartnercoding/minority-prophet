# AID-4 v1 confirmatory result

**Outcome: both policies rejected.** Policy B fails 25 of 41 checks; policy C
fails 23 of 56. Two executions semantically identical. 7,200 campaigns, all ten
pinned inputs verified unchanged.

This tested the two roads left after three experiments closed the first. Criteria
for both were frozen before the world existed; the world was written by an author
who designed neither policy.

**Both kill criteria fire.** By the frozen draft's own section 8: if B suppresses
the margin road closes, if C fails to discriminate the pricing road closes, and
if both fail the programme has no remaining constructive proposal of this kind.

## 1. Policy B: it never says the minority is wrong, and never says they are right

Criterion 4 — the anti-suppression check, the reason this experiment exists —
**passes in all six cells**. It passes vacuously, and the vacuity was disclosed
in the protocol before any salt was read.

| `minority_wins`, true claim vindicated | α = 0.0 | α = 0.5 | α = 1.0 |
|---|---:|---:|---:|
| `ladder` (baseline) | 3,600 | 3,600 | 3,600 |
| `priced` | 3,600 | 3,600 | 3,600 |
| **`margin`** | **0** | **0** | **0** |
| `attested` | 0 | 0 | 0 |
| `refuse_all_unrecorded` | 0 | 0 | 0 |

The baseline vindicates the true minority claim every time. B vindicates it
never. Criterion 4 records **no loss**, because it asks only whether a claim was
settled *against*, and B — whose floor gates the baseline's answer rather than
holding a second election — only ever converts settlements into abstentions.

That is a defect in the criterion I wrote, not a property of the world. I had
conflated *not being convicted* with *being believed*. `settlesForTruth` is
reported so the gap is on the record; repairing the criterion belongs to a
successor registration, not to a retroactive edit.

## 2. Policy B's other failures

| Criterion | Where it fails |
|---|---|
| 1. Prevention | `backed_hidden_source` at every rate; `hidden_source` at α = 1.0 |
| 2. Cost bounded by benefit | `hidden_source` and `backed_hidden_source` at α ≤ 0.5; `mixed_populations` at every rate |
| 3. Not worse than refusing | every powered cell of both dependence families |
| 5. Not refusal with extra steps | `honest_unattestable` at every rate; `wide_margin_unattested` at α = 0.0 |

`backed_hidden_source` is the decisive one: three copies of one hidden parent,
each holding a device key and a verified identity, attesting at every rate. B's
floor never fires against them, so it prevents nothing — the AID-2 finding
reproduced against a different policy. **A credential earns depth and says
nothing about shared origin.**

Cost where no benefit was possible, reported rather than scored because
criterion 2 scopes itself out there:

| Family | correct settlements lost, α = 0.0 / 0.5 / 1.0 |
|---|---|
| `honest_unattestable` | 3,600 / 3,600 / 3,600 |
| `minority_wins` | 3,600 / 3,600 / 3,600 |
| `silent_but_correct` | 3,600 / 3,144 / 1,728 |
| `wide_margin_unattested` | 3,600 / 486 / 0 |

`wide_margin_unattested` is the one family where B recovers fully at full
adoption, and it is the construction built so B *could* settle. Where nobody can
attest, B discards every correct settlement at every rate.

## 3. Policy C: the warning light is wired to nothing

Exposure must rank silently false settlements above correct ones with AUC ≥ 0.70.

| Family | α = 0.0 | α = 0.5 | α = 1.0 |
|---|---:|---:|---:|
| `hidden_source` | 0.500 | 0.513 | 0.500 |
| `backed_hidden_source` | 0.500 | 0.506 | 0.500 |
| `mixed_populations` | 0.500 | 0.506 | 0.500 |

A coin flip in every powered cell. At α = 0.0 and α = 1.0 the figure is
constant — variation share 0.0 — so it separates nothing at all, and the
non-constancy criterion fails alongside.

The pooled figure, **reported and deliberately not scored** because pooling lets
the author's choice of families set the number, is worse than useless:

| α | 0.0 | 0.5 | 1.0 |
|---|---:|---:|---:|
| pooled AUC | 0.306 | 0.249 | 0.193 |

Below 0.5 means **anti-correlated**: settlements resting on silence were, if
anything, slightly *more* likely to be right. Publishing that number as a
warning would point readers away from the errors.

C's one clean pass is structural: `identicalToLadder` holds in every cell.
C changed no decision anywhere, which is what a disclosure rule must do, and is
why it is scored on discrimination alone.

## 4. Why all three roads failed, in one line

Each tried to convert *we do not know* into a decision rule — discount them,
abstain, or print a number. Ignorance does not convert. It relocates.

## Run

- **Scope:** criteria on reversible decisions; adoption curve reported, not a
  pass mark.
- **Size:** 7,200 campaigns, 12 decisions each; 8 families, 3 adoption rates,
  `FABRICATION`.
- **Reproducibility:** two executions identical, SHA-256
  `8b145002384e2322a63de00f5b0f281dfaf2cc0b7863d497f54e0e2c5eb68b05`.
- **Output:** `result.json`, SHA-256
  `52986a906a84b4add8ffc57fec54a1c903e5710c02000358466cd6fbdb807b86`.
- **Campaign manifest:** SHA-256
  `359f0858762a9ee8a66b991f07ba25c3cb34afc5d38bf39cfb823ac3a4e61e4b`.
- **When:** 2026-09-18, 16:56:04 to 16:56:37 UTC.
- **Environment:** CPython 3.12.13 on macOS arm64, commit
  `c4fa1bef11ed96748eddc5eec252ef4ea495b1be`. `dirtyWorktree: true` because the
  shell redirect created this directory's `run-stdout.txt` before the run sampled
  git status; the guarantee that matters is the pin check, which verified all ten
  inputs including the policy at `116d290f…`.
- **The confirmatory salt** was reachable only through the runner's explicit
  opt-in. The world's author shipped no runner deliberately, so that turning the
  key would be a separate recorded act; the runner is the operator's and the
  world is not.

## What this does not establish

- **Not that B's criterion 4 is unfixable.** The repair is known and already
  measured — score vindication alongside survival. It was frozen unrepaired
  because editing criteria after seeing them fail is the error this methodology
  exists to prevent. Repairing it would not rescue B: it would only move B's
  failure from a reported counter into the scoreboard.
- **Not a real-world rate.** Adoption is a dial in a generator, and the census in
  `experiments/aid1/` found zero records in this estate stating a witness depth.
- **Not independent validation.** Author separation within one control domain.
- **Not a verdict on recorded dependence.** Where lineage *is* recorded, the
  proved robustness rule is untouched by any of this and remains the method.
