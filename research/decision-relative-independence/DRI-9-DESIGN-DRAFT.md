# DRI-9 — running the traps

Status: **DRAFT.** It becomes a preregistration only when the protocol, generator
and runner are committed and pinned before any confirmatory campaign is
generated.

## 1. Why this exists

DRI-8 shook the tree and reached what DR3 proves reading cannot: dependence
recorded at no cut. It also showed how little that bought — 0.3% to 3.5% of the
baseline's silent false settlements, at 16 to 468 probes each — and why. Opening
the result up gave three separate piles:

1. **Decisions the merge cannot fix.** Strike one echo off four witnesses and
   three still outvote two. The dependence is real and the answer is unchanged.
2. **Decisions the truth does not settle.** In the pair family the true grouping
   fails to settle on 3,560 of 6,000 decisions while the record settles anyway.
   The rule is wrong because it answered, not because it miscounted.
3. **Echoes the tracer missed.** Detection is imperfect and the budget is finite.

Pile 2 is the biggest and needs no detection at all. Piles 1 and 3 need a better
instrument or none. DRI-9 runs the remaining ways to reach what you cannot touch.

## 2. The traps

- **Refuse when fragile (free).** Before answering, ask whether the answer
  survives any two witnesses on the winning side turning out to be one. If not,
  do not answer. No probing, no budget: it attacks pile 2 directly, and it pays
  in abstentions.
- **Bait.** Plant a distinctive harmless marker where a source will pick it up.
  Anything downstream carries it whether or not the notebook says so. The cost
  lands before the decision, not during it, which is the opposite of DRI-8's
  tracer.
- **Ablation.** Cut a source's upstream and see whose report changes with it.
  The strongest causal test there is, and the most violent: the decision it is
  spent on loses testimony.
- **Reflection.** Echoes have a timing signature even when they share no words:
  who speaks second, and in what order, decision after decision. Every earlier
  experiment threw the clock away.
- **The ladder.** Each signal alone is weak. Combined — bait, timing and a
  co-error record — they are a case. **This is the method under test**, named
  here so that "the best of six arms" cannot be chosen after the outcomes are
  visible.

## 3. Worlds

DRI-8's campaigns, unchanged in structure: persistent sources, a component with a
per-decision fault state, dependence recorded at no cut, and a decoy family whose
sources merely look correlated. Missing lineage is fixed at zero so the hidden
case is isolated.

New observables, all of them outside the notebook:

- **markers:** a bait token a source carries when it draws on a marked component,
  at the cell's pickup rate; unrelated sources carry one only by coincidence.
- **arrival order:** each report has a position, with sources sharing a component
  ordered consistently and jitter set by the cell.
- **cut response:** when a source's upstream is cut, sources sharing it change
  together at a stated rate; others rarely.

**Cells.** Bait pickup ∈ {0.5, 0.9} × timing jitter ∈ {low, high}. Ablation
budget and feedback are fixed, so the cells vary exactly what the two cheap
instruments can see.

## 4. Criterion, with a floor this time

DRI-8's criterion asked whether the effect was significant and never whether it
was worth having. This one states the size first.

Supported only if all hold:

1. **Effect floor.** In both hidden families, the ladder prevents **at least 25%**
   of the baseline's silent false settlements **on margin-critical decisions** —
   the ones where knowing the dependence could change the answer — and does so
   significantly, Holm-corrected.
2. **No harm.** In the decoy family, no arm makes significantly more silent false
   settlements than the baseline, and the ladder's false merges do not exceed its
   true merges.
3. **Cost ceiling.** The ladder keeps at least 95% of the baseline's correct
   settlements, and spends at most 100 interventions per prevented error.
4. **Reproducibility.** Two executions give identical semantic results.

The free arm, refusing when fragile, is reported against the same endpoints with
its abstention cost stated. It is not the method under test, because a rule that
answers less is not obviously better and the trade is the finding.

## 5. Fixed from DRI-8

The margin-critical test merges **any subset** of the true hidden group, not the
whole group at once. DRI-8's endpoint read zero for the trio family because
merging all three never flipped a decision while merging a pair sometimes did.
That defect is disclosed in `results/dri8-v1/README.md` and corrected here.

## 6. Limits

- Every trap is a new assumption about the world, not a better rule: bait assumes
  something to plant, ablation assumes something you may break, reflection
  assumes a clock you trust.
- Pickup, jitter and cut-response rates are stated, not measured on anything real.
- Families, instruments and arms are authored in the same control domain as the
  engine.
- No authority claim.
