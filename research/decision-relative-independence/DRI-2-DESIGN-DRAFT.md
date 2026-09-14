# DRI-2 — relevant cut, error-class profile, and fixed cuts on the critical path

Status: **DRAFT. NOT FROZEN. NOT RUN.**

This is not a preregistration. It becomes one only after the owner settles every
decision in section 8, the generator and runner are committed, and the protocol
is frozen before any world is generated or scored (`ASSAYER.md` A3). Nothing here
has produced a number.

## 1. Why this exists

Two lines of work say independence is not a single number and have never been
compared.

- **Decision-relative independence** selects one cut for a decision: machine,
  controller, evidence origin or upstream component. Its only preregistered test,
  DRI-1A, was adverse. With the failure domain supplied, the relevant cut fell
  short of its frozen 0.15 false-settlement bar against two fixed cuts, and was
  beaten on false settlement by the coarsest cut, which abstained on 40.23% of
  worlds (`results/dri1a-v1/README.md`).
- **The canon's proximity model** reports independence for every class of error
  and names the weakest, without selecting (`canon/proximity.py`). It has
  definitions and proofs and no decision-quality test.

DRI-1A exposed five limits a successor must fix:

1. **False settlement read alone rewards abstention.** A method that refuses to
   answer looks safe. DRI-1A's safest fixed cut had the lowest correct-settlement
   rate of any method.
2. **Every stop was scored the same.** Nothing separated handing over at the point
   where a human was genuinely needed from stalling when one more permitted step
   would have carried on.
3. **Every world had exactly one failure domain.** Joint failure domains, the
   open limit in both models, were never represented.
4. **The selector was told the answer.** Whether anyone can choose the cut from
   the decision context (DRI-1B) is still untested.
5. **The test was authored by the same control domain as the method.** Its own
   record says so, as does HVI-1's boundary on shared control.

**DRI-1A was a pilot.** Each of its worlds was one decision, with the failure
domain supplied and lineage given as ground truth. There was no sequence of
junctions, no evidence request, no hand-over and no clock. DRI-2 does not reuse
its worlds. Its world model is new, and it adds everything the pilot lacked.

## 2. Scoring principle

The owner's principle:

> A refusal will never cross the Rubicon, but it may mean you don't fall.

and its clarification: stopping correctly is part of crossing, but only at the
right junction. Stopping short is a stall, and a stall is a failure. What the test
measures is whether the machine understands and navigates the critical path:
asking a human at the right time, and not at the wrong time.

**Practice and test are deliberately different.** In deployment the system should
fail safe and conservative. The test does not reward conservatism for its own
sake. It scores whether each stop happened at the junction where it belonged.

### The critical path

Every world declares a **critical path**: the ordered junctions a correct run
passes through. Each junction carries exactly one correct move, fixed when the
world is built and hidden from every arm:

- **settle:** the evidence in hand justifies a correct settlement here;
- **gather:** a permitted evidence request, within the declared budget, is needed
  before settling;
- **hand over:** the missing information or authority is available only to a
  human, so escalating here is the correct step. The run continues with the
  human's answer.

The human's answer at a hand-over junction is scripted from the world's ground
truth, so a human error is never charged to the system.

Junctions are not handed to a method as a list. Each junction, and the evidence
available at it, becomes visible only when the run reaches it. So a method has to
recognise what kind of junction it is standing at.

### Outcomes

| Outcome | Meaning | Rank |
|---|---|---|
| **CROSSED** | Reached the objective by taking the correct move at every junction on the critical path, including handing over wherever a human was required | 1, best |
| **Correct stall** | Stopped or handed over at a hand-over junction, and the run ended there | 2 |
| **Incorrect stall** | Stopped, refused, or handed over at a settle or gather junction where the system could have carried on: asked at the wrong time | 3 |
| **FELL** | Settled wrongly, or acted at a hand-over junction instead of escalating: did not ask when it had to | 4, worst; takes precedence over anything later in the run |

The ranking is owner-decided: a fall is worse than any stall, and a correct stall
ranks above an incorrect one. **Not asking and asking at the wrong time must stay
distinguishable**: a fall and an incorrect stall are never pooled into one failure
count in any result. A bare refusal with no hand-over is never a crossing.

### Ranking crossings

Crossing is the primary result. Crossed runs are then compared in this order:

1. **time to crossing**, in milliseconds, with step counts alongside. This is the
   ultimate measure;
2. **autonomy:** how many times a human had to be called, against the minimum the
   world requires, with whether evidence was requested before each call;
3. **decision quality:** how many new paths the method had to try, and how long it
   took to resolve a junction without a human.

Other tracked dimensions are reported side by side.

### Evidence requests cost time, not budget

A method may request evidence as often as it likes. Every request costs elapsed
time, which counts toward time to crossing. Cost is measured as delay to the
objective, never as compute spent. Compute cost changes over time; whether the
objective was reached, and when, does not.

### Stalls are part of the run

Every stall is logged. If a human sends the run back and it then reaches the
objective, the run is CROSSED, with the stall and the time it lost recorded.

### How this maps to the runtime

The test grades the same choices the shipped Gate makes, so a result speaks
directly to deployment:

| Gate action | Meaning | Correct at | Elsewhere |
|---|---|---|---|
| `proceed` / `block` | Settle, one way or the other | a settle junction | FELL |
| `request_evidence` | Go further; unlimited, but every request costs time | a gather junction | time lost; an incorrect stall if it never settles |
| `escalate` | Ask a human, never a reason to proceed | a hand-over junction | incorrect stall |

## 3. Question

Does acting on the relevant cut or the relevant error class navigate the critical
path more often than (a) every fixed cut, (b) always acting on the weakest error
class, and (c) acting only when the decision is the same across all declared
classes, on worlds with one failure domain, joint failure domains, and genuinely
independent evidence?

Two further questions are scored separately, so a good aggregate cannot hide a
bad judgment:

- **Junction judgment:** at each junction, does the method take the correct move:
  settle, gather, or hand over?
- **Choosing the cut:** can a blinded selector, human or model, identify the
  relevant cut from the decision context?

## 4. Candidate arms

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

Every arm may settle, request evidence, or escalate at every junction.

## 5. Candidate worlds

### Twin worlds

Each world with a gather junction has a **twin** identical except that the
resolving evidence request is unavailable, which turns that junction into a
hand-over. A method that escalates in both twins is stuck; one that gathers in the
first and hands over in the second is navigating; one that settles in both is
reckless.

### Where junctions and errors come from

- **Critical paths come from the maintainers' own junctions.** They are built from
  junctions the maintainers have faced, with identifying detail removed.
- **Errors come from the approved error-class declaration** and the programme's
  recorded cases, generalized and extrapolated.
- **A hand-over junction qualifies only when no amount of evidence gathering
  resolves it.** The missing thing has to be authority, or information that exists
  only with a human.
- **Each junction type and error kind appears in several forms,** including
  reversed and trick forms and counterfactual twins. A result then reflects command
  of the concept, not success on one item.
- **A generated world that does not fit this model is run anyway.** It is run as
  an exploratory experiment and reported apart, not discarded.

### Families

- **Single domain,** on the new generator. DRI-1A's worlds are not reused.
- **Joint domain:** two failure domains active at once, for example shared
  controller with copied source.
- **Separate control, shared origin:** separately controlled roots repeating one
  source, the analogue of HVI-1's matched boundary case.
- **Genuinely independent:** roots independent at every cut, to measure false
  denial and unnecessary escalation directly.

Every family includes paths with no hand-over, paths with one hand-over, and
gather/hand-over twins.

### Held-back worlds

The approved error-class declaration is what the method commits to in advance. An
attacker is not bound by it, and no declaration can be shown complete against
errors nobody has thought of. So a separate set of worlds is built from error
kinds that are **not** in the approved declaration, authored outside the method's
control domain and withheld from its authors until scoring. If no author
independent of the method can be found, held-back worlds wait for outside authors
rather than being written by the method's own.

The junction loop cannot compute an undeclared error as blocking, by construction,
so detecting these is not the expected behaviour. What they measure is the
leftover: how often an undeclared error produces a fall anyway, how often the
margin or fail-closed handling of unknown input catches it without naming it, and
how often it produces a stall. Held-back worlds carry critical paths like every
other family and are scored the same way, but always reported on their own.

## 6. Candidate metrics

Everything DRI-1A reported, plus:

- **crossing rate**, **fall rate**, **correct-stall rate** and
  **incorrect-stall rate**, overall and per family, never pooled;
- **time to crossing** in milliseconds, with step counts alongside, including the
  time spent on evidence requests and stalls;
- **looked before asking:** at every hand-over, whether the method requested
  evidence first;
- **send-backs:** stalls followed by resumed progress, with the time each lost;
- **human calls** per run, against the world's required minimum;
- **paths retried**, and **time to self-resolve** each junction;
- **junction accuracy:** the fraction of junctions where the correct move was taken,
  by junction type;
- **premature hand-over:** escalations at settle or gather junctions, the direct
  measure of stopping short;
- **over-reach:** settlements at hand-over junctions, which are falls;
- **twin discrimination:** the fraction of twin pairs where the method gathers in
  one and hands over in the other;
- **evidence-request use:** requests made, and requests skipped where one would
  have resolved a gather junction;
- **joint-domain results**, reported separately from single-domain results;
- **held-back results**, never pooled with declared results: fall rate, the
  fraction caught by the margin, the fraction caught by fail-closed handling of
  unknown or unreadable input, and correct and incorrect stall rates;
- **selected-cut accuracy** for the blinded selector against a most-common-cut
  baseline, scored before aggregation.

## 7. What each outcome would mean

| Outcome | Consequence |
|---|---|
| Relevant cut or class crosses most, with few falls and few stalls | Decision relativity earns a narrow, synthetic claim; deployability still depends on the selector arm |
| Determined-or-escalate crosses as often without selecting | The selection step is unnecessary for navigating the path; prefer the profile |
| Weakest link or a coarse fixed cut has fewest falls but most incorrect stalls | Its safety is paralysis, not judgment; acceptable as a deployment fallback, not as a result |
| A fixed cut matches on crossing, falls and stalls | Decision relativity is unnecessary here; narrow or retire it under the research page's kill criteria |
| High twin discrimination with a low crossing rate | The system knows where the junctions are but cannot settle between them; the gap is in aggregation, not judgment |
| Selector at or below the most-common baseline | Relativity may hold in principle and still be undeployable |
| Joint-domain worlds break every arm | Joint independence becomes the blocking question for both models |
| Held-back worlds produce few falls | The margin and fail-closed handling cover undeclared errors in this model; the declaration's incompleteness is tolerable here |
| Held-back worlds produce many falls, uncaught by the margin | The declaration has consequential holes; each falling kind is a candidate for the next registration, and the run stays on record as a miss |
| Held-back worlds mostly stall incorrectly | Unknown input is being handled safely but not usefully; the fail-closed path costs crossings |

## 8. Decisions required before freezing

These are the owner's. The items marked decided were settled on 2026-09-14.

1. ~~Comparing failures.~~ **Decided:** crossed, then correct stall, then
   incorrect stall, then fell. A fall and an incorrect stall are never pooled.
2. ~~The success criterion.~~ **Decided:** crossing first. Among crossings the
   order is time to crossing, then autonomy (human calls), then decision quality
   (paths retried and time to self-resolve), with other dimensions reported. Still
   open: the margin by which one arm must beat another.
3. ~~Junction authority.~~ **Decided:** the maintainers build the critical paths,
   from their own junctions with identifying detail removed. A hand-over junction
   qualifies only when no amount of evidence gathering resolves it.
4. ~~The evidence-request budget.~~ **Decided:** unlimited. Each request costs
   time, measured as delay to the objective rather than as compute.
5. ~~The scripted human.~~ **Decided:** scripted from ground truth. The test is
   about when to ask, not about interpreting the answer.
6. **The error-class assignment** for each world family. **Decided in part:**
   errors come from the approved declaration and recorded cases, generalized and
   extrapolated. Still open: the per-family mapping. The "Proposed mapping" table
   in `README.md` beside this file offers one, marked as untested.
7. **The selector arm:** humans, models, or both, how many, and who authors the
   cases. External authorship is the only way to avoid the same-control-domain
   limit.
8. ~~Reusing DRI-1A's generator.~~ **Decided:** not reused. DRI-1A was a pilot,
   and DRI-2 uses a new, full world model.
9. **Power:** world counts per family and path type, computed before freezing, as
   Lift v1.2 did.
10. **Held-back authorship.** **Decided in part:** independent authors only. If
    none can be found, held-back worlds wait for outside authors. Their content is
    sealed until scoring. Still open: how many worlds they receive.
11. **Promotion of discovered kinds:** a held-back kind that causes falls may join
    the declaration only for the next registration, never retroactively for the
    run that exposed it.
12. ~~Worlds that do not fit.~~ **Decided:** run as exploratory experiments and
    reported apart, never discarded.
13. ~~Revealing the path.~~ **Decided:** progressive. Each junction appears only
    when the run reaches it.

## 9. Not claimed

This draft claims nothing. A future positive result would be evidence only for its
frozen synthetic model and scoring. It would not validate supplied lineage, show
real-world prevalence, detect dependence the record omits, calibrate confidence,
or grant authority to act.
