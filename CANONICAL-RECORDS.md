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
