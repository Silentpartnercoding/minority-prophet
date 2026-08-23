# DRI-1B v1 — blinded proximal-root identifiability

**Record ID:** `DRI-1B`

**Version:** `1.0.0`

**Lane:** candidate

**Phase:** specification and externally authored fixture

**Status:** frozen protocol only; no case acquisition, reviewer response,
confirmatory execution, model call, runtime effect, or authority effect is
authorized by this record.

## 1. Why this experiment exists

DRI-1A asked what happens when a correct decision-relative independence cut is
given to the evaluator. Its noncanonical synthetic candidate run showed a large
descriptive accuracy and minority-recovery advantage, but failed its joint
preregistered criterion. It also handed the rules engine the failure-domain
label, so it did not test whether anyone can identify the right cut.

DRI-1B tests the missing prerequisite: whether the proximal root relevant to a
decision is a stable, externally adjudicable target. If blinded humans cannot
identify it consistently from a complete case packet, training or prompting an
AI to emit that label would automate ambiguity rather than solve it.

This protocol was written after the DRI-1A result was known. No DRI-1A world may
enter DRI-1B, and no DRI-1A effect estimate is treated as confirmatory evidence
for this study.

## 2. Research question, null, and target hypothesis

**Question:** Given the same multi-resolution evidence graph and decision
context—but not the author/adjudicator label—can blinded reviewers identify the
single proximal independence cut, or correctly declare that no single available
cut is sufficient, often enough to improve the resulting evidence disposition
over every fixed-cut policy without indiscriminate minority rescue or excessive
abstention?

**Null:** Reviewer consensus has no higher exact-label accuracy than the best
fixed-cut policy, and any apparent reduction in incorrect disposition can be
explained by increased abstention or unconditional minority preservation.

**Target:** The reviewer-consensus selector is reproducibly identifiable,
outperforms every fixed cut by the registered margin, retains most of the oracle
recovery of materially independent minority evidence, rarely rescues an
ungrounded minority, and does not obtain its advantage by refusing too many
otherwise settled cases.

## 3. Unit, label space, and terminology

The unit is one decision case containing one proposition, one proposed action,
one consequence/reversibility class, and one unchanged set of observations with
root identity at every available cut.

The mutually exclusive target labels are:

1. `agent`
2. `machine`
3. `controller`
4. `evidence_origin`
5. `upstream_component`
6. `joint_or_insufficient`

The first five name the nearest recorded causal boundary whose collapse removes
the shared failure that is material to the stated decision. The sixth means no
single available cut safely represents the material dependency: multiple cuts
are jointly required, lineage is missing, or the supplied graph cannot settle
the question.

The **ultimate root** remains preserved. Selecting a proximal root never erases
deeper lineage or claims that the selected cut is universally independent.

## 4. Population and fixed sample

The study requires 276 eligible externally authored cases:

- 60 development cases, 10 for each target label; and
- 216 untouched confirmatory cases, 36 for each target label.

At least six case authors are required. No author may contribute more than 20%
of eligible cases. The experiment builder, scorer implementer, and test
reviewers may not author confirmatory cases. Author identities are represented
publicly by opaque IDs; control relationships and consent records remain in the
private run manifest.

Authorship diversity is an anti-overfitting control, not a claim of independent
verification. Unless a content-bound external-control witness exists, the
research record continues to declare the work same-control-domain or unknown.

Cases must be operational decision scenarios, sanitized historical incidents,
or simulations whose causal/dependency structure can be explicitly stated.
Fictional names and non-sensitive values are required. No private customer
information, credentials, vulnerabilities, or live safety decision may enter.

### Fixed consequence balance

Within every label stratum, 18 confirmatory cases are `low_reversible` and 18
are `high_irreversible`.

Within each label-and-consequence cell, six confirmatory cases are
`material_reversal`, six are `false_rescue_trap`, and six are
`no_headcount_minority`. The confirmatory set therefore contains exactly 72
cases of each minority class. Development uses five cases of each consequence
class per target label; its minority-class mix is reported but not constrained.

- `low_reversible` requires at least two winning roots at the selected cut.
- `high_irreversible` requires at least three winning roots.

These thresholds affect settlement only. They do not alter the correct causal
cut. An author may not choose another threshold.

### Eligibility

A case is eligible only when:

- every public and withheld field validates against `case.schema.json`;
- the public packet contains roots at all five cuts for every observation;
- the author supplies a complete withheld materiality table showing the
  disposition at every cut;
- the target label follows from that table and the decision context;
- the evidence graph contains at least one alternative cut whose root partition
  differs from another cut;
- no public field directly contains the target label, answer key, stratum name,
  or an instruction to choose a particular cut; and
- both pre-review adjudicators accept the target label and rationale.

Cases failing eligibility are rejected before development/confirmation
splitting. Reasons and counts remain in the manifest. They are never replaced
because of reviewer or aggregation outcomes.

## 5. Authorship and adjudication before the holdout exists

Authors use `AUTHORING-GUIDE.md` and `case.schema.json`. Each author creates:

1. a public decision/evidence packet;
2. a withheld target label;
3. a causal rationale naming the material shared failure;
4. the expected disposition at every candidate cut; and
5. a counterexample explaining why the nearest finer and coarser cuts are wrong
   or why no single cut is sufficient.

Two adjudicators who are neither authors nor test reviewers independently
evaluate every proposed case before it is split. They see the full author packet
but no test-reviewer response. Both must agree with the target label and certify
that it is entailed by the recorded graph and decision context. There is no
majority rescue or third-adjudicator substitution. A disagreement makes the case
ineligible.

Report author/adjudicator proposed-case agreement, rejection rate, and reasons.
If more than 25% of submitted cases are rejected, or fewer than 276 eligible
cases remain, the study stops as `incomplete`. Additional cases may be solicited
only before any test-reviewer response is collected and without seeing method
outcomes.

## 6. Development/confirmation split and sealing

After eligibility is closed, cases are grouped by target label and consequence
class. Within each group, sort by:

```text
SHA256("minority-prophet-dri1b-v1|" + case_id)
```

The first registered quota becomes development; the remainder becomes
confirmatory. If more than the exact quota exists, excess cases are retained in
the acquisition manifest but not substituted after responses.

Before any selector implementation is tuned or any test reviewer sees a packet,
commit:

- a normalized public-development manifest and its content hashes;
- a normalized public-confirmatory manifest and its content hashes;
- a separately access-controlled withheld-label commitment;
- the case-set IDs and split digest;
- authorship/adjudication counts and control-relationship declarations; and
- a statement that no confirmatory response exists.

The withheld labels must not be accessible to selector implementers or test
reviewers. A signature, repository boundary, or separate machine is a transport
control, not proof of external independence.

## 7. Frozen review procedure

Three test reviewers evaluate every confirmatory public packet independently.
They may inspect only the public packet and the frozen neutral instruction in
`AUTHORING-GUIDE.md`. They may not communicate, use author/adjudicator labels,
see another response, search for the case, or use an AI assistant.

Each response validates against `selector-response.schema.json` and contains:

- exactly one target label;
- confidence from 0 through 100;
- one cited material failure from the public packet;
- one reason the nearest rejected alternative is not sufficient; and
- no proposed action authority.

All three reviewers answer all 216 cases. Missing or malformed responses are
`joint_or_insufficient` with confidence zero for disposition metrics and are
incorrect for exact-label accuracy. They are not retried after labels are
unsealed.

Reviewer consensus is the modal label. A three-way tie becomes
`joint_or_insufficient`; ties are never broken using confidence or the withheld
label.

Compensation, reviewer consent, recruitment criteria, and conflicts of interest
must be frozen in the private run manifest before review. This protocol does not
authorize recruitment, payment, or collection of personal data.

## 8. Frozen methods and controls

Every method receives the same evidence values, roots, decision class, and
sufficiency threshold.

1. each individual blinded reviewer;
2. reviewer consensus (primary practical selector);
3. fixed `agent` cut / headcount;
4. fixed `machine` cut;
5. fixed `controller` cut;
6. fixed `evidence_origin` cut;
7. fixed `upstream_component` cut;
8. fixed `joint_or_insufficient` / always abstain;
9. uniform random label with frozen seed `20260823`;
10. author/adjudicator target label (oracle ceiling).

No model selector is part of DRI-1B. An AI/model study receives a new identifier
and preregistration only if the human-identifiability gate passes. This prevents
model selection, prompting, or provider availability from changing the present
hypothesis after data are seen.

For labels 1–5, use the existing
`provenance.decision_relative.assess_decision` adapter and the case's fixed
threshold. `joint_or_insufficient` produces `unsettled` without discarding the
lineage. The oracle is a ceiling, not a deployable method.

## 9. Endpoints

### Co-primary identifiability endpoints

- exact reviewer-consensus target-label accuracy over all confirmatory cases;
- Fleiss' kappa among the three test reviewers;
- reviewer-consensus accuracy difference from the best fixed label; and
- accuracy on `joint_or_insufficient` cases.

### Co-primary decision endpoints

- **incorrect disposition:** opposite to the oracle disposition, or settled
  when the oracle is unsettled;
- **unnecessary abstention:** unsettled when the oracle is correctly settled;
- **exact disposition agreement** with the oracle;
- **material minority recovery:** among cases where observation headcount and
  the oracle are both settled on opposite sides, settlement on the oracle side;
- **false minority rescue:** settlement on the observation-minority side when
  that side is not the oracle disposition, divided by all registered
  `false_rescue_trap` cases; and
- answered coverage.

The definition deliberately rejects a no-child-left-behind policy. Preserving a
minority record is always required; promoting it is correct only when its
decision-relative independent support warrants the oracle disposition.

### Secondary diagnostics

- accuracy and disposition metrics by label, consequence class, author, and
  reviewer;
- confidence calibration and risk/coverage curves at 50%, 70%, and 90%
  coverage, with confidence thresholds selected on development cases only;
- decision-material alternative-cut prevalence;
- scorer p50, p95, and p99 latency separated from human review time; and
- missing/malformed response counts.

No scalar utility that hides abstention behind an arbitrary cost is a primary
endpoint. False settlement, false rescue, abstention, and coverage remain
separate.

## 10. Statistical analysis and multiplicity

The natural cluster is the case. Use exactly 10,000 paired case bootstrap
resamples with seed `20260823` for 95% percentile intervals on method
differences, recovery, rescue, disposition error, and kappa. Report Wilson 95%
intervals for standalone proportions. Do not bootstrap observations within a
case.

The primary claim is an intersection-union gate: every registered condition in
Section 11 must pass, so no multiplicity correction is used to rescue individual
primary clauses. All pairwise secondary method comparisons use Holm-Bonferroni
family-wise correction at alpha `0.05`, with the complete adjusted and
unadjusted table published. Subgroup results are descriptive and cannot rescue
a failed primary gate.

With 216 balanced confirmatory cases, a standalone proportion has a worst-case
Wilson 95% half-width of approximately 6.6 percentage points. This does not
guarantee power for every paired comparison. If fewer than 216 eligible cases or
complete reviewer rows exist, the run is incomplete rather than silently
re-powered.

## 11. Frozen joint success gate

The DRI-1B human-identifiability thesis is supported only if all conditions hold:

1. the lower 95% bootstrap bound for reviewer-consensus exact-label accuracy is
   at least `0.70`;
2. the lower 95% bootstrap bound for Fleiss' kappa is at least `0.60`;
3. the lower 95% paired-bootstrap bound for consensus accuracy minus the best
   fixed-label accuracy is at least `0.15`;
4. consensus accuracy on `joint_or_insufficient` is at least `0.70`;
5. consensus material-minority recovery is at least `0.80` of oracle recovery;
6. the upper 95% Wilson bound for false minority rescue is at most `0.05`;
7. the upper 95% paired-bootstrap bound for consensus incorrect disposition
   minus oracle incorrect disposition is at most `0.10`;
8. the upper 95% paired-bootstrap bound for consensus unnecessary abstention
   minus oracle unnecessary abstention is at most `0.10`; and
9. all acquisition, blinding, completeness, integrity, and reproducibility gates
   in Sections 12–14 pass.

The best fixed label is selected only by its confirmatory aggregate accuracy for
the purpose of a conservative baseline comparison; all fixed-label results are
published. Because label strata are exactly balanced, every fixed label has a
nominal exact-label accuracy of one sixth before missingness.

## 12. Failure, invalidation, and stopping rules

The thesis is rejected if any joint success clause fails on a valid complete
run. The run is `incomplete` rather than rejected when recruitment, case count,
review count, or approved execution resources are unavailable.

The run is invalidated and preserved if any of the following occurs:

- a confirmatory label is exposed to a selector implementer or test reviewer
  before responses are content-bound;
- confirmatory cases or reviewers are replaced based on outcomes;
- protocol, case, split, prompt/instruction, scorer, or environment bytes do not
  match their commitments;
- reviewer communication or AI assistance is discovered;
- an unregistered retry, prompt repair, exclusion, threshold, or label change is
  used;
- result files are selectively deleted; or
- authority or a live action is inferred from an evidence assessment.

Stop without execution if author/adjudicator rejection exceeds 25%, exact quotas
cannot be filled, conflicts/consent are not recorded, privacy review fails, or
the required owner authorization is absent. Once confirmatory review begins,
stop only for safety/privacy or integrity breach; preserve all completed rows.

## 13. Environment, implementation, and execution commitment

This protocol alone is intentionally not executable. Before any confirmatory
review or scoring, a separate committed `EXECUTION-COMMITMENT.json` must bind:

- this protocol path, SHA-256, and commit;
- case schema and authoring-guide hashes;
- public development and confirmatory case-set hashes;
- access-controlled label-commitment digest;
- reviewer-instruction digest and response-schema hash;
- exact scorer commit and source hashes;
- Python version, OS/platform, dependency lock digest, and command line;
- bootstrap implementation and seed;
- repository clean/dirty state;
- private consent/conflict/compensation manifest digest;
- owner authorization reference;
- output, stdout/stderr, timing, and intervention-log paths; and
- explicit confirmation that no confirmatory response existed when the
  commitment was made.

The scorer must be implemented and tested on development cases only, then
committed before review. A clean detached worktree must reproduce byte-identical
semantic JSON twice. Timing and machine metadata are stored separately. Builder,
runner, and reviewer control relationships are reported; same-operator reruns
are internal reproduction, not independent verification.

No amendment may change a target, endpoint, threshold, eligibility rule, or
method after any confirmatory response exists. A necessary pre-response change
creates a versioned protocol and lifecycle record; it never edits this one.

## 14. Evidence package and artifact paths

The eventual run, if separately authorized, must preserve:

- `experiments/dri1b/PREREGISTRATION.md`
- `experiments/dri1b/AUTHORING-GUIDE.md`
- `experiments/dri1b/case.schema.json`
- `experiments/dri1b/selector-response.schema.json`
- `experiments/dri1b/EXECUTION-COMMITMENT.json`
- `experiments/dri1b/HOLDOUT-COMMITMENT.json`
- immutable normalized public packets;
- access-controlled withheld-label commitments, never private labels in a
  public repository when they would compromise a future run;
- scorer source and tests;
- raw responses and validation failures;
- result JSON, manifest, logs, timings, environment, and interventions; and
- the lifecycle record `research/records/DRI-1B.json`.

The canonical manifest must hash protocol, schemas, instructions, scorer,
inputs, output, logs, environment, and write-up, and must name their commits.
Adverse, incomplete, or invalidated output remains visible.

## 15. Interpretation and architectural boundary

A supported result would show that decision-relative proximal roots are
human-identifiable in this authored case population and that the label improves
the registered disposition tradeoff. It would not show that an AI can select the
cut, that WEX can obtain trustworthy field lineage, that the correct cut is
unique in all domains, that evidence is true, or that an action is authorized.

A rejected identifiability result is a serious kill signal: do not build a model
selector or runtime gate around a target that reviewers cannot reproduce. An
incomplete result says the authoring/adjudication apparatus was not feasible; it
does not support the thesis.

If DRI-1B passes, the next separately registered study may test model selection.
Only after that may a WEX shadow study examine real metadata availability and
latency. Runtime intervention remains a later authority-sensitive phase.
