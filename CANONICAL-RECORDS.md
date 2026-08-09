# Canonical research records

Canonical means the repository can identify the exact protocol, executable
implementation, inputs or source boundary, derived output, interpretation, and
content hashes that belong to one record. It does not mean that the result is
true outside its stated experiment.

## Current registry

| Experiment | Status | Canonical record | Boundary |
| --- | --- | --- | --- |
| EXP001 | Canonical derived record | `results/los-inspired-v0.1.manifest.json` | Fixed-seed constructed worlds; no real-world generalization. |
| EXP002 | Canonical derived record | `results/resolved-weather-v0.1.manifest.json` | Public derived data is bound; mutable upstream API bytes and raw pseudonymous trades are intentionally not retained. |
| EXP003 | Replica/design validation | Archived evidence packet only | Requires a repository-native runner and a preregistered replication identifier before a new canonical run. |
| EXP004 | Replica/design validation | Archived evidence packet only | Requires portable corruption-sweep code, frozen configuration, and a new replication run. |
| EXP005 | Replica/design validation | Archived evidence packet only | Requires public preregistration and a repository-native rerun; an archived claim of preregistration is not substituted for public commit order. |
| EXP006 | Replica/design validation | Archived evidence packet only | Requires a versioned H5 replication protocol, portable runner, and fresh content-bound output. |
| EXP007 | Exploratory artifact | Archived runner only | Requires a stated hypothesis, frozen seeds/budget, output schema, and canonical rerun. |
| EXP008 | Portable reference runner | `experiments/exp008_shootout.py` | Runner is public and archive-identical, but no canonical output is claimed until a new protocol is preregistered and rerun. |
| EXP003R | Canonical archived-implementation replication: reproduced | `results/canonical-replications-v1/run-a/receipt.json` | Two isolated runs were byte-identical; this validates the archived implementation, not external validity. |
| EXP004R | Canonical archived-implementation replication: reproduced | `results/canonical-replications-v1/run-a/receipt.json` | Both the original root-set sweep and corrected attribution-axis sweep reproduced. |
| EXP005R | Canonical archived-implementation replication: reproduced | `results/canonical-replications-v1/run-a/receipt.json` | The side-confusion sweep reproduced; theoretical generalization remains outside scope. |
| EXP006R | Canonical archived-implementation replication: reproduced; H5 rejected | `results/canonical-replications-v1/run-a/receipt.json` | Program and output reproduced, while its stated collapse hypothesis failed its own threshold. |
| EXP007R | Canonical attempted replication: incomplete | `results/canonical-replications-v1/run-a/receipt.json` | Multi-seed section ran; the archived optimizer contains placeholders and produced no result. |
| EXP008R | Canonical archived-implementation replication: reproduced | `results/canonical-replications-v1/run-a/receipt.json` | Complete shootout output was byte-identical across two isolated runs. |
| EXP007A | Canonical repository-native adversary completion: supported | `results/exp007a-v1/result.json` | New preregistered search; it completes but does not rewrite EXP007R or validate the paper's previously reported optimum. |
| EXP009 | Canonical selective-hybrid confirmation: supported | `results/exp009-v1/result.json` | Frozen synthetic policy preserved the preregistered tradeoff; inferred lineage remained weak and declared lineage is an oracle ceiling. |
| HVI-1 | Canonical shared-control confirmation: supported | `results/hvi1-v1/result.json` | Supported control provenance blocks representation laundering; it does not prove causal independence, hidden ownership, truth, or authority. |
| HEO-1 | Canonical evidence-origin confirmation: supported | `results/heo1-v1/result.json` | Supported derivation lineage blocks transformation laundering; it does not discover hidden sources, prove truth, or grant authority. |
| HGD-1 | Canonical graded-dependence experiment: rejected | `results/hgd1-v1/result.json` | Six of seven hypotheses passed, but the primary absolute-effect threshold failed; collocation does not prove causal dependence, truth, or authority. |
| HGD-2 | Canonical graded-dependence replication: rejected | `results/hgd2-v1/result.json` | Safety improved, but control coverage and attacked usefulness failed; much of the gain came through abstention. |
| HES-1 | Canonical evidence-seeking experiment: supported with material subgroup limitation | `results/hes1-v1/result.json` | Blind acquisition restored substantial coverage, but software false-negative accuracy was inadequate; independence alone does not establish claim-specific competence. |
| EAA-P5 | Imported out-of-tree unified-auditor validation: rejected | `results/eaa-p5-out-of-tree-v1/manifest.json` | The frozen candidate did not improve forged-root collapse tolerance or disjoint-software selective risk. This is a content-bound imported packet, not a repository-native rerun or third-party validation. |
| LIR-1/PHEME-R2 | Canonical recorded-lineage recovery experiment: rejected | `results/lir1-pheme-r2-v0.1/canonical-manifest.json` | Hidden-parent recovery failed on a disjoint PHEME holdout; reply-tree roots are recorded platform lineage, not causal evidence independence. |
| LIR-1E | Canonical constructed record-root recovery experiment: supported with material abstention | `results/lir1e-confirmatory-v0.1/canonical-manifest.json` | The frozen method recovered useful constructed roots and truth advantage, answering 25 of 36 cases; it does not establish causal evidence independence or uncontrolled real-world performance. |
| LIR-2 | Canonical precision-constrained root-coverage experiment: supported | `results/lir2-confirmatory-v0.1/canonical-manifest.json` | Direct root grouping answered 34 of 36 constructed cases correctly with zero false root merges; the synthetic generator and model pair remain a narrow boundary. |
| LIR-2/PHEME | Canonical fixed-method recorded-lineage transfer: rejected | `results/lir2-pheme-transfer-v0.1/canonical-manifest.json` | The constructed-corpus root grouper did not transfer to PHEME reply-tree coverage; precision remained 1.0 but recall was 0.2020. |
| LIR-3/PHEME | Canonical observable-provenance bridge: supported | `results/lir3-confirmatory-v0.1/canonical-manifest.json` | Reply-target author identity recovered recorded PHEME reply components when exact parent IDs were hidden; this does not establish causal evidence ancestry, independence, authentication, or truth. |
| LIR-4/PHEME | Canonical provenance graceful-degradation experiment: rejected | `results/lir4-confirmatory-v0.1/canonical-manifest.json` | Substantial reply-identity missingness fragmented recorded roots; the false-identity safety diagnostic was underpowered because only one holdout case had multiple roots. |

## Promotion rule

An old replica is never promoted merely by adding hashes after the fact.
Promotion creates a new, versioned replication record and requires:

1. protocol and hypotheses committed before the run;
2. repository-native offline runner with fixed seeds and configuration;
3. environment and dependency declaration;
4. append-only derived output with no selective deletion;
5. SHA-256 manifest covering protocol, code, input boundary, output, and write-up;
6. automated manifest verification;
7. an honest verdict including null or adverse results; and
8. independent rerun evidence when the claim depends on portability.

The original archives remain immutable chain-of-custody evidence. They are
inputs to designing replications, not substitutes for them.
