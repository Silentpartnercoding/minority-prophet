# DRI-8 — shaking the tree: passive history against active probing

Status: **Frozen.** The preregistration is `experiments/dri8/PREREGISTRATION.md`,
protocol v1. This draft records the design rationale and is not itself pinned.

## 1. Why this exists

DR3 (`no_record_rule_is_immune`) proves that no rule reading only the record can
separate two independent sources from two that share an unrecorded origin. DRI-5
tested the one observable that comes free with the evidence, a content
fingerprint: it recovered the copying case completely, the shared-origin case
barely, and paraphrase defeated it. DRI-6 closed the lookup question and left two
holes: a lookup wrong the same way every time, and missing lineage combined with
lookup error.

What remains is the hard case: **two sources drawing on one hidden origin,
recorded nowhere, worded differently.** Nothing in the record and nothing in the
content distinguishes it from genuine independence.

DR3 is about reading. It says nothing about acting. Two ways to get evidence the
record does not contain:

- **Time, passively.** Sources that share a hidden origin are wrong together more
  often than chance. Learning that needs resolved outcomes and enough decisions.
- **A probe, actively.** Put a tracer through one source's upstream and see
  whether another source's next report carries it. A shared path carries it; an
  unrelated one only by coincidence.

The first is correlation, available to any observer. The second is an
intervention, which is why it can identify what observation cannot — and it costs
something, and it is not always possible.

## 2. Questions

1. **Does time work?** Does a co-error track record prevent silent false
   settlements from hidden shared dependence?
2. **Does shaking the tree work better**, and at what cost in probes?
3. **What does learning cost when it is wrong?** Merging two genuinely
   independent sources removes a root from their side and can hand the decision
   to the other one — a false settlement neither rule makes today.
4. **The DRI-6 leftovers.** Does either method survive a lookup that is wrong the
   same way every time, and missing lineage at the same time?

## 3. Worlds

A **campaign** is a population of six persistent sources answering twelve
decisions in order. Persistence is the point: a track record needs the same
sources to reappear, and a probe needs something to probe.

Each campaign carries both kinds of dependence:

- **hidden:** sources sharing an upstream component recorded at no cut, with
  independent content per source. This is the DR3 case.
- **recorded:** a pair sharing an identity at the upstream-component cut, truly
  one source. DRI-4's degradation can erase that link, which is how missing
  lineage and hidden dependence are tested together.

A component has a per-decision fault state; when faulty, every source drawing on
it errs together. Otherwise each source errs at its own rate.

- **Families.** `shared_upstream_pair` (two share a hidden component),
  `shared_upstream_trio` (three do), `coincident_independents` (none do, but two
  are inaccurate enough to look correlated — the decoy, where learning can harm).
- **Cells.** Missing lineage m ∈ {0, 0.25}, feedback rate r ∈ {1.0, 0.25}, probe
  budget b ∈ {2, 10} per campaign.
- **The lookup is the correlated error case.** It returns the grouping the
  lineage system knows: recorded dependence included, the hidden component never.
  It is therefore wrong the same way on every call, which is what DRI-6 declared
  out of scope. No separate knob is needed.

## 4. Arms

- **tiered rule** — DRI-3's, per decision, no memory. Baseline.
- **content tiered rule** — DRI-5's fingerprint as an extra cut. Content is
  independent per source here, so this is a control, not a contender.
- **track record** — merges a pair once it has been wrong together often enough
  over enough decisions whose outcome was revealed.
- **probe** — when merging a suspect pair *would change this decision's outcome*,
  spends a probe on that pair; enough positive tracers and the pair is merged
  from then on.
- **oracle reference.**

A learned merge is an identity at a `learned` cut that every source carries: a
merged group shares one, everyone else has their own. It therefore reaches both
the robustness engine and the across-cuts agreement check, exactly as a recorded
shared identity would.

## 5. The don't-care zone

A dependence that cannot move a decision does not matter to that decision. Before
spending a probe, the arm recomputes the settlement with the pair merged and
compares both the settlement and whether it would be stamped "not robust". No
change, no probe. This is the flip-budget idea applied per decision and decided
exactly rather than by a threshold, and the same test splits the results:
**margin-critical** decisions, where merging the true hidden group changes the
outcome, against the slack where it cannot.

## 6. What is not guaranteed

- **Learning can invent dependence**, and in the decoy family that can turn a
  correct settlement into a false one. Both learning arms can be worse than the
  baseline.
- **Probes cost and can mislead**: a tracer reaches an unrelated source by
  coincidence at a stated rate, and the budget is finite.
- **Time may be too slow**: a component that rarely misfires leaves little to
  learn from, especially at the low feedback rate.

## 7. Proposed criterion

Supported only if all hold:

1. **Prevention.** In both shared-upstream families, at the generous probe
   budget, the probe arm makes significantly fewer silent false settlements than
   the tiered rule in every powered cell. Exact McNemar, Holm-corrected.
2. **No harm.** In the decoy family, neither learning arm makes significantly
   more silent false settlements than the tiered rule.
3. **Cost ceiling.** In every cell, the probe arm keeps at least 90% of the
   tiered rule's correct settlements.
4. **Reproducibility.** Two executions give identical semantic results.

The track-record arm is measured on the same endpoints and reported, not required
to pass: whether time alone suffices is the finding, not the pass mark.

## 8. Reported with no pass mark

- probes spent per prevented false settlement;
- learned merges, split into true and false;
- margin-critical against slack, for every arm;
- every outcome count for every arm.

## 9. Limits

- **Probing must be possible.** A tracer through a source's upstream is an
  assumption about the world, not a property of the record. Where the upstream
  cannot be touched, this arm does not exist.
- **The tracer model is synthetic.** Detection and coincidence rates are stated,
  not measured.
- **Same control domain.** Families, probe model and arms are authored here.
- **No authority claim.**
