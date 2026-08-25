# Repository map

This is a directory-level guide to the public repository. Existing paths remain
stable so external references and historical records do not break.

## Public entry points

| Path | Purpose |
|---|---|
| [`README.md`](../README.md) | Public front door |
| [`docs/`](./) | Navigation and reader guides |
| [`PUBLIC-CLAIMS.md`](../PUBLIC-CLAIMS.md) | Shortest supported claim set |
| [`SYSTEM-ARCHITECTURE.md`](../SYSTEM-ARCHITECTURE.md) | Component and trust boundaries |
| [`CANONICAL-RECORDS.md`](../CANONICAL-RECORDS.md) | Canonical/imported record registry |
| [`EVIDENCE-ALIGNMENT.md`](../EVIDENCE-ALIGNMENT.md) | Claim-to-record ledger |
| [`papers/00-CURRENT-PAPER.md`](../papers/00-CURRENT-PAPER.md) | Stable pointer to the current manuscript |

## Core research and implementation

| Directory | Contents |
|---|---|
| [`aggregation/`](../aggregation/) | Aggregation algorithms and experimental comparators |
| [`benchmark/`](../benchmark/) | Synthetic worlds, CLI, and metrics |
| [`provenance/`](../provenance/) | Evidence graph, ancestry, root, and schema primitives |
| [`formal/`](../formal/) | Mathematical model, Lean proofs, and theorem scope |
| [`knowledge_ledger/`](../knowledge_ledger/) | Reference ledger structures and validation |
| [`contracts/`](../contracts/) | Neutral schema/contract drafts |
| [`interop/`](../interop/) | Interoperability fixtures and adapters |
| [`evaluations/`](../evaluations/) | Model-evaluation harnesses and the reference runtime engine |

## Research lifecycle

| Directory | Contents |
|---|---|
| [`experiments/`](../experiments/) | Protocols, implementations, fixtures, and experiment notes |
| [`research/`](../research/) | Integrity rules, records, ledger work, field evidence, and focused tracks |
| [`results/`](../results/) | Preserved result packages, manifests, nulls, and adverse outcomes |
| [`verification/`](../verification/) | Verification scripts and noncanonical validation tracks |
| [`papers/`](../papers/) | Current and historical manuscripts and review packages |
| [`output/`](../output/) | Generated release artifacts such as rendered PDFs |
| [`public/research/`](../public/research/) | Research summaries prepared for the public website |

## Product and presentation surfaces

| Directory | Contents |
|---|---|
| [`website/`](../website/) | Public website source and deployment notes |
| [`app/`](../app/) | Dashboard/application implementation |
| [`public/`](../public/) | Static assets and publishable research summaries |
| [`worker/`](../worker/) | Edge/site worker implementation |

## Project operations

| Directory | Contents |
|---|---|
| [`tests/`](../tests/) | Python and repository-integrity tests |
| [`scripts/`](../scripts/) | Validation, lifecycle, paper, and maintenance tools |
| [`.github/`](../.github/) | CI workflows and repository templates |
| [`audit/`](../audit/) and [`AUDIT-BRIEF/`](../AUDIT-BRIEF/) | Audit material and review briefs |
| [`conformance/`](../conformance/) | Conformance fixtures and checks |
| [`build/`](../build/) | Build support files |

## Root documents by question

- **What is the idea?** [`FOUNDATIONS.md`](../FOUNDATIONS.md)
- **What can we say publicly?** [`PUBLIC-CLAIMS.md`](../PUBLIC-CLAIMS.md)
- **What is being researched next?** [`ROADMAP.md`](../ROADMAP.md) and
  [`RESEARCH-DIRECTION.md`](../RESEARCH-DIRECTION.md)
- **What would falsify it?** [`RESEARCH-HYPOTHESES.md`](../RESEARCH-HYPOTHESES.md)
- **How do the components relate?** [`SYSTEM-ARCHITECTURE.md`](../SYSTEM-ARCHITECTURE.md)
- **What does provenance require?** [`PROVENANCE-REQUIREMENTS.md`](../PROVENANCE-REQUIREMENTS.md)
- **What do project terms mean?** [`GLOSSARY.md`](../GLOSSARY.md)
- **How do I contribute?** [`CONTRIBUTOR-QUICKSTART.md`](../CONTRIBUTOR-QUICKSTART.md)
  and [`CONTRIBUTING.md`](../CONTRIBUTING.md)

If a file looks current but conflicts with a canonical record or evidence
ledger, follow the [documentation authority order](README.md#how-authority-works-here).
