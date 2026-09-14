# DRI-2 — relevant cut, error-class profile, and fixed cuts under joint scoring

Status: **DRAFT. NOT FROZEN. NOT RUN.**

This is not a preregistration. It becomes one only after the owner settles every
decision in section 7, the generator and runner are committed, and the protocol
is frozen before any world is generated or scored (`ASSAYER.md` A3). Nothing here
has produced a number.

## 1. Why this exists

Two lines of work say independence is not a single number and have never been
compared.

- **Decision-relative independence** selects one cut for a decision: machine,
  controller, evidence origin or upstream component. Its only preregistered test,
  DRI-1A, was adverse: with the failure domain supplied, the relevant cut fell
  short of its frozen 0.15 false-settlement bar against two fixed cuts and was
  beaten on false settlement by the coarsest cut, which abstained on 40.23% of
  worlds (`results/dri1a-v1/README.md`).
- **The canon's proximity model** reports independence for every class of error
  and names the weakest, without selecting (`canon/proximity.py`). It has
  definitions and proofs and no decision-quality test.

DRI-1A exposed four limits a successor must fix:

1. **False settlement read alone rewards abstention.** A method that refuses to
   answer looks safe. Scoring must combine correct settlement, abstention and
   false settlement under costs fixed in advance.
2. **Every world had exactly one failure domain.** Joint failure domains, the
   open limit in both models, were never represented.
3. **The selector was told the answer.** Whether anyone can choose the cut from
   the decision context (DRI-1B) is still untested.
4. **The test was authored by the same control domain as the method.** Its own
   record says so, as does HVI-1's boundary on shared control.

## 2. Question

Under costs fixed in advance, does acting on the relevant cut or the relevant
error class produce better decisions than (a) every fixed cut, (b) always acting
on the weakest error class, and (c) acting only when the decision is the same
across all declared classes, on worlds with one failure domain, joint failure
domains, and genuinely independent evidence?

A second question is scored separately so a correct aggregate cannot hide a wrong
causal model: can a blinded selector, human or model, identify the relevant cut
from the decision context?

## 3. Candidate arms

1. **Agent headcount.**
2. **Each fixed cut:** machine, controller, evidence origin, upstream component.
3. **Weakest link:** act on the least-defended error class, the proposed
   counterpart of always taking the coarsest cut.
4. **Determined-or-escalate:** settle only when the disposition is the same for
   every declared error class, otherwise escalate. This mirrors the discipline in
   `aggregation/independence_axes.py::effective_witness_bounds`.
5. **Oracle relevant cut:** the preregistered cut for the world family, as in DRI-1A.
6. **Declared-policy rules engine:** the frozen family-to-cut table.
7. **Blinded selector:** humans and/or models choose the cut from externally
   authored case descriptions without outcome labels. This is DRI-1B's scope.

## 4. Candidate world families

- **Single domain,** reusing DRI-1A's generator unchanged so results remain
  comparable.
- **Joint domain:** two failure domains active at once, for example shared
  controller with copied source.
- **Separate control, shared origin:** separately controlled roots repeating one
  source, the analogue of HVI-1's matched boundary case.
- **Genuinely independent:** roots independent at every cut, to measure false
  denial and unnecessary escalation directly.

## 5. Candidate metrics

Everything DRI-1A reported, plus:

- **decision loss** under the cost weights fixed in section 7;
- **false-denial rate** on genuinely independent worlds;
- **escalation rate**, reported separately from abstention;
- **joint-domain error**, reported separately from single-domain error;
- **selected-cut accuracy** for the blinded selector against a most-common-cut
  baseline, scored before aggregation.

## 6. What each outcome would mean

| Outcome | Consequence |
|---|---|
| Relevant cut or class beats every comparator on decision loss | Decision relativity earns a narrow, synthetic claim; deployability still depends on the selector arm |
| Determined-or-escalate matches it without selecting | The selection step is unnecessary for decision quality; prefer the profile |
| Weakest link wins on loss | Conservatism is cheap in this threat model; record the costs that made it so |
| A fixed cut matches on loss | Decision relativity is unnecessary here; narrow or retire it under the research page's kill criteria |
| Selector at or below the most-common baseline | Relativity may hold in principle and still be undeployable |
| Joint-domain worlds break every arm | Joint independence becomes the blocking question for both models |

## 7. Decisions required before freezing

These are the owner's and are deliberately left open.

1. **Cost weights** for false settlement, abstention or escalation, and a missed
   correct action. The primary result depends entirely on them. They must be set
   without reference to any generated world.
2. **The success criterion:** which arm must beat which, by how much, and whether
   abstention matching is retained as a sensitivity analysis.
3. **The error-class assignment** for each world family. The "Proposed mapping"
   table in `README.md` beside this file offers one, marked as untested; rung
   assignments are an owner judgment under A3.
4. **The selector arm:** humans, models, or both, how many, and who authors the
   cases. External authorship is the only way to avoid the same-control-domain
   limit.
5. **Whether DRI-1A's generator is reused byte-for-byte** for the single-domain
   family, or versioned.
6. **Power:** world counts per family, computed before freezing, as Lift v1.2 did.

## 8. Not claimed

This draft claims nothing. A future positive result would be evidence only for its
frozen synthetic model and costs. It would not validate supplied lineage, show
real-world prevalence, detect dependence the record omits, calibrate confidence,
or grant authority to act.
