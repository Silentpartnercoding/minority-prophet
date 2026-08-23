# DRI-1A — decision-relative independence policy benchmark

**Status:** protocol, generator, baselines, metrics, thresholds, and adverse-result
path frozen before the confirmatory worlds are generated or scored.

## Question

When the same evidence record contains roots at several lineage cuts, does using
the cut relevant to the declared failure domain reduce false settlement relative
to agent headcount or any one fixed global cut? Can an explicit deterministic
policy execute that choice without model inference or material latency?

This first arm tests the value and executable plumbing of a declared policy. It
does **not** test whether a model can infer the right causal boundary from vague
natural language. A positive rules-engine result is policy conformance, not
learned causal intelligence.

## Frozen synthetic world generator

Generate the complete Cartesian product below in lexicographic order, then use
an independent `random.Random` stream seeded from SHA-256 of
`minority-prophet-dri1a-v1|<cell>|<replicate>` for every world:

- failure-domain families: `machine_local`, `shared_controller`,
  `copied_source`, `shared_upstream_component`;
- independent-root accuracy: `0.65`, `0.75`, `0.85`, `0.95`;
- erroneous-root amplification: `1`, `3`, `7`, `15` observations;
- decision class: `low_reversible`, `high_irreversible`;
- 64 replicates per cell.

This yields 8,192 worlds. Each world has a uniformly sampled Boolean truth and
five causally independent roots at the registered relevant cut. Each root
reports truth with the cell accuracy. A correct root emits one observation. An
incorrect root emits the registered amplification count, representing correlated
repetition of the same wrong observation. All emitted records retain identities
at all five candidate cuts.

The relevant cut and the deliberately finer/coarser alternatives are frozen as:

| Failure domain | Relevant cut | Finer cuts | Coarser cuts |
|---|---|---|---|
| `machine_local` | `machine` | `agent`, `evidence_origin` | `controller`, `upstream_component` |
| `shared_controller` | `controller` | `agent`, `machine` | `evidence_origin`, `upstream_component` |
| `copied_source` | `evidence_origin` | `agent`, `machine`, `controller` | `upstream_component` |
| `shared_upstream_component` | `upstream_component` | `agent`, `machine`, `controller`, `evidence_origin` | none |

At the relevant cut, every observation from one causal root shares that root ID.
At a finer cut, every repeated observation has a distinct ID. At a coarser cut,
causal roots `0/1`, `2/3`, and `4` are merged. A coarse root carrying conflicting
values is handled by the existing fail-closed root-vote kernel; it is not repaired
by the experiment.

`low_reversible` requires two winning roots. `high_irreversible` requires three.
This consequence label changes only the common evidence-sufficiency threshold;
it does not change truth, lineage, or the relevant causal cut.

## Frozen methods

1. **Agent headcount:** always select `agent`.
2. **Fixed machine:** always select `machine`.
3. **Fixed controller:** always select `controller`.
4. **Fixed evidence origin:** always select `evidence_origin`.
5. **Fixed upstream component:** always select `upstream_component`.
6. **Oracle policy:** select the registered relevant cut for the world family.
7. **Explicit rules engine:** apply the frozen family-to-cut table above to the
   declared `failure_domain`. No evidence values, truth labels, or model calls are
   available to the selector.
8. **Most-common-cut selector:** always select the lexicographically first cut
   among equally frequent oracle cuts (`controller` here). This is the cut-selection
   baseline; it is separate from the five aggregation baselines.

All aggregation methods use `provenance.decision_relative.assess_decision` and
the same per-world sufficiency threshold. No result-specific rescue, weighting,
or confidence score is permitted.

## Frozen metrics

Report overall and per-stratum:

- false-settlement rate: settled on the side opposite hidden truth, over all worlds;
- abstention rate;
- correct-settlement rate;
- unsupported-settlement rate: method settles where the oracle is unsettled;
- unnecessary-abstention rate: method abstains where the oracle settles correctly;
- exact disposition agreement with oracle;
- minority-reversal recovery: on worlds where agent observation majority and
  causal-root majority are both decisive and disagree, the fraction settling on
  the causal-root side;
- selected-cut accuracy for oracle, rules engine, and most-common selector;
- fraction of worlds with at least one decision-material alternative cut;
- evaluator latency in milliseconds at p50, p95, and p99; and
- deterministic result SHA-256 from two independent executions.

The primary false-settlement comparison uses the registered threshold directly.
As a conservative sensitivity analysis, also compare at approximately matched
abstention. For each fixed-cut baseline choose the threshold in `1..5` minimizing
absolute abstention-rate distance from the oracle. Ties favor the baseline by
lower false settlement, then lower threshold. Report the remaining abstention
difference; do not call rates matched when the absolute difference exceeds 0.01.

## Frozen success criterion

The joint DRI-1A policy-value claim is supported only if all conditions hold:

1. oracle false settlement is at least 0.15 lower than **every** fixed-cut
   baseline at the registered thresholds;
2. the same 0.15 minimum reduction holds against every approximately
   abstention-matched fixed-cut baseline whose abstention difference is at most
   0.01;
3. if no threshold for a baseline reaches the 0.01 matching tolerance, that
   comparison is marked unmatched and the joint criterion fails rather than
   dropping the baseline;
4. rules-engine selected-cut accuracy is `1.0` and its false-settlement,
   abstention, and disposition outputs equal the oracle byte-for-byte;
5. the most-common-cut selector accuracy is no greater than `0.25`;
6. rules-engine unnecessary abstention exceeds oracle by no more than 0.10;
7. at least 20% of worlds have a decision-material alternative cut; and
8. two complete executions produce identical semantic results, excluding only
   measured wall-clock latency fields.

These thresholds are intentionally difficult. Failure is a result, not grounds
to change the generator or scoring rule.

## Null, adverse outcomes, and kill implications

The null is that the oracle policy has no lower false-settlement rate than the
best fixed cut at comparable abstention. The strongest adverse outcomes are:

- one fixed cut matches the oracle, making decision relativity unnecessary in
  this threat model;
- oracle gains disappear once abstention is matched;
- the method gains safety only through prohibitive abstention;
- material cut changes are rare;
- the rules engine cannot reproduce the declared policy deterministically; or
- latency is large enough to undermine a tactical graph/ledger path.

A positive result remains evidence only for this frozen synthetic common-cause
model. It does not validate the supplied lineage, demonstrate real-world
frequency, establish joint multi-cut independence, calibrate confidence, infer
failure domains, authorize action, or show that customers will provide the
metadata. DRI-1B must separately test blinded human/model cut selection on
externally authored cases; a field study must test whether the required lineage
exists without self-reporting.

