# Glossary

<!-- mp-status: {"id":"glossary","class":"current","asOf":"2026-09-19","replacement":null,"immutable":false,"theorems":["DR1","DR2","DR3","U1"],"researchRecords":["AID-1-V1","AID-2-V1","AID-3-V1","AID-4-V1"],"describesMechanisms":["recorded_graph_roots","bounded_root_issuance","proximate_mis_count","recorded_dependence_robust_settlement"],"recommendedMechanisms":["recorded_graph_roots","bounded_root_issuance","recorded_dependence_robust_settlement"]} -->

**Belief** — A versioned claim about a proposition, held with stated confidence.

**Claim lineage** — Directed ancestry describing copying, derivation, and transformation.

**Civilization** — The complete system of agents, protocols, memory, identity, evidence, and aggregation rules.

**Competence** — Empirically estimated reliability scoped to a task or domain; not general reputation.

**Observation** — A world-level event or measurement. A repository record may
claim to describe one, but record shape alone does not establish that it was
independently observed.

**Independence** — Absence of relevant shared causal ancestry under a stated model; never inferred solely from different agent names.

**Decision-relative independence** — Independence evaluated at an explicit lineage cut selected for a stated decision and failure domain. The underlying lineage does not change; only the root identity relevant to the assessment changes. This is an adapter-level research primitive, not part of the proved aggregation kernel.

**Independence cut** — The declared causal boundary at which observations are collapsed for one decision, such as evidence origin, machine, controller, or upstream component. Every reported independent count must name its cut.

**Proximal root** — An observation's root at the independence cut relevant to the current decision. It can settle an operational question without being the observation's ultimate human, organizational, or causal ancestor.

**Decision materiality** — A counterfactual property: an alternative independence cut is material when it changes the decision disposition among settled true, settled false, and unsettled under the declared sufficiency standard.

**Minority-truth recovery** — Accuracy restricted to worlds where the true-belief coalition is numerically smaller than the false-belief coalition.

**Mimetic pressure** — Tendency to adopt beliefs, desires, goals, trust, status, or curiosity from others.

**Provenance** — Attributable history of a claim, source, evidence, time, transformations, and signatures.

**Truth aggregation** — Mapping claims and evidence into a belief distribution or abstention.

**Recorded root** — A claim record with no usable ancestry in the named record.
This means “no ancestry recorded,” not “independently observed.” An unrecorded
copy is indistinguishable from a recorded root to that graph and is governed by
the margin theorems, not by copy invariance. See `formal/CLAIM-SCOPE.md`.

**Issued root identity** — An authenticated, quota-bounded identity minted by
`provenance.RootRegistry`. It can preserve a declared copy relationship and
limit issuance. Distinct issued identities do not prove distinct observations,
issuer honesty, truth, or deployment adoption.

**Effective witness** — One unit in an exact maximum independent set relative
to a named possible-dependence graph and error class. It is a model-relative
counting unit, not a claim that the world contains that many independent
observations. Exact counting is used or the implementation refuses.

**Root identity** — The criterion by which two roots count as the same root. `S_a` is a *set*, so every verdict is a function of this criterion. Defined in `canon/U1-PROXIMATE-ROOTS.md`: dependence is not an equivalence, so the count is a **maximum independent set** rather than a quotient, and shared ancestry is cause-in-fact rather than dependence. Any de-duplication or canonicalisation step is still inside the trusted base. Ledger `U1`, `proved_compiled`; worked in `canon/U1-WORKED-EXAMPLE.md`.

**Flip budget** — `|margin|`, in units of **net per-side root gain** (`p₀ − p₁`). Not a count of adversary actions: one action that *converts* a root from one side to the other is worth two units. Always report `conversions_to_reverse` alongside it.

**Three distinct things are measured by asking "would the verdict flip?", and only the first is a margin.** They differ in what is varied, so they are not interchangeable and no two of them should be summed into a single score. Recorded here so the distinction is not derived a fourth time.

| term | measures | what is varied |
|---|---|---|
| **Flip budget** (above) | how many counted support units must be converted to reverse a verdict | the named evidence model |
| **False-reversal rate** and **copied-minority recovery** | how often an aggregator overturns wrongly, and how often rightly | the world, against known ground truth |
| **Pressure susceptibility** | how easily a judge moves when nothing evidential has changed | prestige, consensus, framing, source repetition, who is speaking |

**False-reversal rate** — Fraction of all propositions where the majority is right and the aggregator overturns it. A behavioural error rate measured against ground truth, not a property of an evidence graph. Preregistered with a ceiling in `experiments/EXP009-HYBRID-PREREGISTRATION.md`. Its partner is copied-minority recovery, and neither is meaningful without the other: refusing to overrule anything drives false reversals to zero.

**Copied-minority recovery** — Accuracy on the cases where a copied majority is wrong. The benefit term whose price is the false-reversal rate. Reported as a pair with it, never alone.

**Pressure susceptibility** — How far a judge's output moves when the evidence is held fixed and only social variables change. Deliberately **not** called a flip anything and not expressed in margin units, because it is not a distance in root gain and cannot be compared to one. Currently **unbuilt**; the design constraint recorded in advance is that it must be reported decomposed rather than as one number, and that **belief change and action change are reported separately**, since a belief may move harmlessly while the action holds, and a small move may cross a threshold and turn proceed into abstain. A single headline number here would rebuild the black box that confidence scores were, under a new name.

**Root conversion** — Moving one root (and its descendant subtree, to preserve side-consistency) from one side to the other. Costs two units of flip budget. Reversal by conversion costs `⌊margin/2⌋ + 1` actions.

**Unattributed claim** — A claim with no recorded root. The repository formerly treated this two contradictory ways: promoted to a root (maximum influence) in the formal model, silently discarded (zero influence) in `evidence_root_vote`. It is now an explicit named policy on `aggregation.root_vote.verdict`, defaulting to fail-closed. Ledger `U2`.

**Side consistency (R2)** — Every derivation edge joins claims asserting the same value. Enforced at ingest by `provenance.EvidenceGraph`. Without it the aggregator does not degrade gracefully; it double-counts, placing a single root on both sides.
