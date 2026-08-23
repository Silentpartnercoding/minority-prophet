# Glossary

**Belief** — A versioned claim about a proposition, held with stated confidence.

**Claim lineage** — Directed ancestry describing copying, derivation, and transformation.

**Civilization** — The complete system of agents, protocols, memory, identity, evidence, and aggregation rules.

**Competence** — Empirically estimated reliability scoped to a task or domain; not general reputation.

**Evidence root** — A lineage node grounded in an observation rather than copied from another claim.

**Independence** — Absence of relevant shared causal ancestry under a stated model; never inferred solely from different agent names.

**Decision-relative independence** — Independence evaluated at an explicit lineage cut selected for a stated decision and failure domain. The underlying lineage does not change; only the root identity relevant to the assessment changes. This is an adapter-level research primitive, not part of the proved aggregation kernel.

**Independence cut** — The declared causal boundary at which observations are collapsed for one decision, such as evidence origin, machine, controller, or upstream component. Every reported independent count must name its cut.

**Proximal root** — An observation's root at the independence cut relevant to the current decision. It can settle an operational question without being the observation's ultimate human, organizational, or causal ancestor.

**Decision materiality** — A counterfactual property: an alternative independence cut is material when it changes the decision disposition among settled true, settled false, and unsettled under the declared sufficiency standard.

**Minority-truth recovery** — Accuracy restricted to worlds where the true-belief coalition is numerically smaller than the false-belief coalition.

**Mimetic pressure** — Tendency to adopt beliefs, desires, goals, trust, status, or curiosity from others.

**Provenance** — Attributable history of a claim, source, evidence, time, transformations, and signatures.

**Truth aggregation** — Mapping claims and evidence into a belief distribution or abstention.

**Evidence root (recorded)** — A lineage node with no recorded ancestry. NOTE: this means "no ancestry *recorded*", not "independently observed". An undetected copy is indistinguishable from an evidence root and is governed by the margin theorems, not by copy invariance. See `formal/CLAIM-SCOPE.md`.

**Root identity** — The criterion by which two roots count as the same root. `S_a` is a *set*, so every verdict is a function of this criterion — and no artifact in this repository defines it. Any de-duplication or canonicalisation step is therefore inside the trusted base. Ledger `U1`.

**Flip budget** — `|margin|`, in units of **net per-side root gain** (`p₀ − p₁`). Not a count of adversary actions: one action that *converts* a root from one side to the other is worth two units. Always report `conversions_to_reverse` alongside it.

**Root conversion** — Moving one root (and its descendant subtree, to preserve side-consistency) from one side to the other. Costs two units of flip budget. Reversal by conversion costs `⌊margin/2⌋ + 1` actions.

**Unattributed claim** — A claim with no recorded root. The repository formerly treated this two contradictory ways: promoted to a root (maximum influence) in the formal model, silently discarded (zero influence) in `evidence_root_vote`. It is now an explicit named policy on `aggregation.root_vote.verdict`, defaulting to fail-closed. Ledger `U2`.

**Side consistency (R2)** — Every derivation edge joins claims asserting the same value. Enforced at ingest by `provenance.EvidenceGraph`. Without it the aggregator does not degrade gracefully; it double-counts, placing a single root on both sides.
