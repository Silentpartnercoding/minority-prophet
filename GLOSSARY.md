# Glossary

**Belief** — A versioned claim about a proposition, held with stated confidence.

**Claim lineage** — Directed ancestry describing copying, derivation, and transformation.

**Civilization** — The complete system of agents, protocols, memory, identity, evidence, and aggregation rules.

**Competence** — Empirically estimated reliability scoped to a task or domain; not general reputation.

**Evidence root** — A lineage node grounded in an observation rather than copied from another claim.

**Independence** — Absence of relevant shared causal ancestry under a stated model; never inferred solely from different agent names.

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
