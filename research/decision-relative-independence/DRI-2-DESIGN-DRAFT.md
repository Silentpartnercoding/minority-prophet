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

## 2. Scoring principle

The owner's principle:

> A refusal will never cross the Rubicon, but it may mean you don't fall.

and its clarification: stopping correctly is part of crossing, but only at the
right junction. Stopping short is a stall, and a stall is a failure. What the test
measures is whether the machine understands and navigates the critical path. The
principle comes from RubiconTest; this draft adopts it for Minority Prophet's own
evidence experiments.

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

### Outcomes

| Outcome | Meaning | Counts as |
|---|---|---|
| **CROSSED** | Reached the objective by taking the correct move at every junction on the critical path, including handing over wherever a human was required | Success |
| **FELL** | Settled wrongly, or acted at a hand-over junction instead of escalating | Failure; takes precedence over anything later (RubiconTest RT-004) |
| **STALLED** | Stopped, refused, or escalated at a settle or gather junction where the system could have carried on | Failure: stopped short |

A bare refusal with no hand-over is never a crossing (RubiconTest RT-002).
Escalating is a crossing step only at a hand-over junction; anywhere else it is a
stall. FELL and STALLED are both failures and are kept apart only so the report
shows which way a method fails: reckless or stuck.

### How this maps to the runtime

The test grades the same choices the shipped Gate makes, so a result speaks
directly to deployment:

| Gate action | Meaning | Correct at | Elsewhere |
|---|---|---|---|
| `proceed` / `block` | Settle, one way or the other | a settle junction | FELL |
| `request_evidence` | Go further within a bounded, policy-approved budget | a gather junction | wasted budget; a stall if it never settles |
| `escalate` | Ask a human, never a reason to proceed | a hand-over junction | STALLED |

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
reckless. This is RubiconTest's planned counterfactual-twin requirement (RT-006)
applied to junction judgment.

### Families

- **Single domain,** reusing DRI-1A's generator so results remain comparable, with
  critical paths added.
- **Joint domain:** two failure domains active at once, for example shared
  controller with copied source.
- **Separate control, shared origin:** separately controlled roots repeating one
  source, the analogue of HVI-1's matched boundary case.
- **Genuinely independent:** roots independent at every cut, to measure false
  denial and unnecessary escalation directly.

Every family includes paths with no hand-over, paths with one hand-over, and
gather/hand-over twins.

## 6. Candidate metrics

Everything DRI-1A reported, plus:

- **crossing rate**, **fall rate** and **stall rate**, overall and per family;
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
- **selected-cut accuracy** for the blinded selector against a most-common-cut
  baseline, scored before aggregation.

## 7. What each outcome would mean

| Outcome | Consequence |
|---|---|
| Relevant cut or class crosses most, with few falls and few stalls | Decision relativity earns a narrow, synthetic claim; deployability still depends on the selector arm |
| Determined-or-escalate crosses as often without selecting | The selection step is unnecessary for navigating the path; prefer the profile |
| Weakest link or a coarse fixed cut has fewest falls but most stalls | Its safety is paralysis, not judgment; acceptable as a deployment fallback, not as a result |
| A fixed cut matches on crossing, falls and stalls | Decision relativity is unnecessary here; narrow or retire it under the research page's kill criteria |
| High twin discrimination with a low crossing rate | The system knows where the junctions are but cannot settle between them; the gap is in aggregation, not judgment |
| Selector at or below the most-common baseline | Relativity may hold in principle and still be undeployable |
| Joint-domain worlds break every arm | Joint independence becomes the blocking question for both models |

## 8. Decisions required before freezing

These are the owner's and are deliberately left open.

1. **Comparing failures.** FELL and STALLED are both failures. Still open: whether
   they are counted equally in the primary result or ranked.
2. **The success criterion:** which arm must beat which, by how much, on which of
   the metrics above.
3. **Junction authority:** who builds the critical paths and assigns each junction
   its correct move, and how a hand-over junction is shown to be genuinely beyond
   the system rather than merely hard.
4. **The evidence-request budget:** how many permitted requests a gather junction
   allows, and what each costs.
5. **The scripted human:** how a hand-over junction's answer is produced, and
   whether any arm is tested with a real human, in which case human error must be
   recorded separately.
6. **The error-class assignment** for each world family. The "Proposed mapping"
   table in `README.md` beside this file offers one, marked as untested; rung
   assignments are an owner judgment under A3.
7. **The selector arm:** humans, models, or both, how many, and who authors the
   cases. External authorship is the only way to avoid the same-control-domain
   limit.
8. **Whether DRI-1A's generator is reused byte-for-byte** for the single-domain
   family, with critical paths layered on top, or versioned.
9. **Power:** world counts per family and path type, computed before freezing, as
   Lift v1.2 did.

## 9. Relation to RubiconTest

The scoring principle and the CROSSED/FELL vocabulary come from RubiconTest, which
is a separate benchmark with its own requirements. This draft uses them for
Minority Prophet's evidence experiments only. Benchmark mechanics that belong to
RubiconTest, including how a stall is scored there, human send-backs, elapsed
time and counterfactual twins, are proposed in RubiconTest's own repository and
are not specified here.

## 10. Not claimed

This draft claims nothing. A future positive result would be evidence only for its
frozen synthetic model and scoring. It would not validate supplied lineage, show
real-world prevalence, detect dependence the record omits, calibrate confidence,
or grant authority to act.
