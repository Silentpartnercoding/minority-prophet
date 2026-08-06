# The Minority Prophet Property

> **HISTORICAL VERSION.** Superseded; retained as record. See [`papers/ERRATA.md`](./ERRATA.md) for corrections that apply to this text.

## Truth recovery under copying pressure requires unforgeable origins, unblended sides, and a protected margin — and nothing more

**Historical draft v0.9 — superseded by v1.0.1 and the canonical registry. Numeric E7 claims in earlier revisions were not backed by a complete archived optimizer; this copy is evidence-aligned to EXP007A but remains non-submission material.**
*Author: James Siyuan He (Silent Partner). Reference implementations, proof drafts, and replica experiments produced in collaboration with AI systems (Claude Fable 5; Codex) and re-verified as described in §9.*

---

### Abstract

When claims can be copied at zero cost, agreement stops being evidence. We study when an aggregator can recover independently grounded truth against an overwhelming copied majority. The invariance theorems characterize a provenance boundary: duplication is evidentially null, and same-side rewiring is harmless when roots are preserved. A preregistered scalar-corruption hypothesis was rejected. The later canonical EXP007A experiment then completed the missing optimizer: a 45-evaluation search selected `(0.701175, 1.0, 0.0, 0.0)` for paraphrase, forged citation, sybil, and timing, reducing inferred-lineage accuracy to 0.3715 on ten untouched holdout seeds versus 0.4461 for uniform-0.5 and 0.4133 for uniform-1.0. Incorrect verdicts occurred at lower honest margins than correct verdicts (3.7684 vs 5.6886; Welch t = 25.1144). These are synthetic-model results, not evidence of an external exploit. On 5,729 resolved on-chain weather markets, no head-count method beat the stake-weighted market price; dependence-adjusted aggregation nevertheless had a 95× lower false-reversal rate than exposure-weighting. We derive a three-layer provenance requirement stack—root integrity, side-separation, and margin sufficiency—strictly weaker than full lineage tracking.

---

### 1. Introduction

Every consensus mechanism humanity relies on — markets, elections, peer review, "multiple sources confirm" — silently assumes that independent agreement is costly to manufacture. Machine agents void that assumption: a claim can be copied perfectly, instantly, and at scale, so a thousand assertions may contain one observation. The question is not whether majorities can be wrong (they always could be) but whether *any* aggregation procedure can tell a grounded minority from an ungrounded one once copying is free.

We formalize this as the **minority prophet property**: an aggregator satisfies it at level (ρ, α) if it recovers ground truth with probability α when a copied false majority outnumbers independent grounded observers by ratio ρ, *and* rejects ungrounded minorities. The property has two halves — recovery and rejection — and we find, theoretically and empirically, that they have sharply different costs.

Our contributions: (i) an exact characterization of the provenance an evidence-root aggregator needs (Theorems 1–4), with the surprising demotion of lineage accuracy from necessary to irrelevant; (ii) machine verification of the theorems by exhaustive finite model checking (5,912 worlds, 121,944 rewirings, 100,000 randomized instances, zero violations) with Lean 4 formalization in progress; (iii) a preregistered-and-rejected scalar-corruption hypothesis whose failure mode *is* the margin law; (iv) adversarial validation via an optimizing attacker that rediscovers the theorems' predictions; (v) the first real-market measurement of both halves of the property, on 5,729 resolved on-chain weather markets; and (vi) a minimal provenance requirement stack with direct consequences for agent-communication standards.

### 2. Related work

**Impossibility endpoints (inherited, not reproven).** Douceur's Sybil attack result establishes that without a costly or trusted identity substrate, one attacker can simulate arbitrarily many independent participants; Byzantine agreement bounds limit consensus under traitorous minorities; robust statistics bounds any estimator's breakdown point. Our Theorem 3 and the composed-attack collapse (E3) instantiate this territory; our contribution is the *middle* — the shape of degradation and the minimal sufficient guarantee — not the endpoints.

**Truth discovery and source dependence.** The Dawid–Skene family and EM-style reliability estimation weight sources by inferred competence; the source-dependence line (Dong et al.) detects copying between sources to discount duplicated votes. Our setting differs in assuming an explicit (possibly corrupted or inferred) evidence DAG and asking what *properties of that DAG*, rather than what estimator, make recovery possible. The immunity result is, to our knowledge, novel: dependence-aware methods have assumed lineage accuracy matters; we prove for root-counting aggregation that only side-separation does.

**Mechanism design and markets.** Prediction market prices aggregate stake-weighted conviction; peer-prediction mechanisms elicit honest reports without verification. Our E2 findings are consistent with prices already internalizing much of the independence signal via bet sizing — motivating stake-weighted root counting as future work.

**Provenance infrastructure.** C2PA signs media transformation history; W3C DIDs/VCs provide portable signed claims. The requirement stack in §6 specifies what any such layer must guarantee to *epistemically* suffice for aggregation — a design target none of these standards currently states.

**Logical aggregation.** The evidence-semantic aggregation of E1 is Łoś-inspired: verdicts over "large enough" agreeing sets preserve logical coherence that propositionwise majority voting violates. We use this as design inspiration only; no literal ultraproduct claims are made.

### 3. Definitions

A **world** W = (C, parent, assert) is a finite claim set C, a partial parent function inducing a DAG via a time order (parent(c).t < c.t), and assert : C → {0,1}. Claims without parents are **roots** (purported independent observations); root(c) is c's unique root ancestor. W is **side-consistent** if every edge joins same-assertion claims — satisfied by construction when copies inherit assertions.

The **evidence-root aggregator** computes side root sets S_a(W) = {root(c) : assert(c) = a} and returns 1 if |S₁| > |S₀|, 0 if the reverse, abstaining on ties (optionally, below a margin threshold). The **margin** is ||S₁| − |S₀||.

Generative benchmark (E1, E3–E7): a hidden truth T; n independent observers of reliability r, each its own root; a prestigious originator asserting a target claim; m ≫ n copiers attaching preferentially to the originator's copy tree; 60% of worlds place the copied majority on the false side. Adversary transformations (paraphrase, citation forgery, sybil identities, timing front-running, and their composition) corrupt the observables from which lineage must be inferred.

### 4. Theorems

**Lemma 1 (Side-locality).** In a side-consistent world, S_a is exactly the set of a-asserting roots. *Chains preserve assertion by induction; roots are their own chains.*

**Theorem 1 (Immunity).** Any rewiring of parent edges that (i) preserves the root set and (ii) preserves side-consistency leaves S₀, S₁, and hence the verdict, exactly unchanged. *Both worlds reduce via Lemma 1 to the same root filter.* **Consequence: attribution accuracy — who copied whom — is irrelevant to the verdict.** Empirical shadow: side-preserving corruption drove attribution from 1.00 to 0.59 with verdict accuracy never below 0.98 (E5); across 10 seeds, immunity-condition accuracy 0.994, 95% CI [0.989, 0.999], statistically indistinguishable from uncorrupted baseline (E7).

**Theorem 2 (Copy invariance).** Duplicating any claim (same assertion, parent = original) leaves the verdict unchanged. *The duplicate's root is already counted.*

**Theorem 3 (Head-counting fails).** Majority voting is not copy-invariant (explicit two-duplication counterexample); with no lineage, evidence-root aggregation degenerates to majority voting exactly (observed identically in E3).

**Theorem 4 (Margin flip condition).** For any transformation preserving claims and assertions, the verdict flips only if net cross-side phantom root flow meets or exceeds the honest margin. *Immediate: the verdict is a threshold function of the side-count margin.* **Consequence: the attacker's budget equals the margin; the defender's lever is margin, not lineage purity.**

**Verification status.** Theorems 1–4 carry full paper proofs and pass exhaustive machine checking over *all* side-consistent worlds with ≤ 6 claims under *all* side-preserving rewirings (5,912 worlds; 121,944 rewirings) plus 100,000 randomized larger instances: zero violations. Lean 4 formalization: Theorem 3 fully proved; Lemma 1 and Theorem 1 stated with proofs in progress (tracked; no result in this paper depends on their completion beyond the paper proofs).

### 5. Experiments

*Provenance labels: E1–E2 are canonical derived records. E3R–E6R and E8R are canonical replays of archived implementations, which establish deterministic portability rather than external validity. E6R reproduced a rejected H5. E7R is canonically incomplete; EXP007A is the distinct preregistered repository-native adversary completion. Other E8/E8b narrative claims remain replica/design-validation claims.*

**E1 (canonical, synthetic pilot).** Under declared lineage, evidence-root and Łoś-inspired semantic aggregation recover minority truth where propositionwise majority fails, and semantic aggregation preserves a three-proposition logical constraint majority voting violates. All methods fail under sufficiently corrupted lineage — the observation that motivated everything below.

**E2 (canonical, real markets).** 11,307 candidate → 5,729 eligible resolved weather-tagged binary on-chain markets. Market price dominates: Brier 0.0744, accuracy 89.7%, calibration error 1.24%, versus one-wallet voting 0.1221 / 84.0% and dependence-adjusted voting 0.1223 / 83.9%. Preregistered H2a (dependence adjustment beats one-wallet) **rejected** — the Brier difference (−0.000207) is practically null, consistent with a shared-root domain offering no independence structure to exploit. H2b (underdog recovery) **rejected**: 1 recovery vs exposure-weighting's 58 — but at 0.10% vs 9.50% false-reversal rate, a 95× precision asymmetry in overrule decisions. H2c **supported**: abstention lifted answered-case accuracy 4.61 points at 88.9% coverage (matched-coverage comparison against price pending; treated as provisional). Interpretation: in a below-threshold domain the method correctly *goes quiet* — the rejection half of the minority prophet property, validated in the wild; prices already perform stake-weighted aggregation, motivating stake-weighted root counting.

**E3 (replica).** Inferred lineage (temporal + similarity + citation scorers) matches declared lineage under every *single* adversary (accuracy 0.94–0.99; signal redundancy: each attack blinds one scorer, the others compensate) and collapses under their composition (lineage F1 0.99 → 0.32; accuracy 0.99 → 0.51). Robust to any one attack; brittle to their combination.

**E4 (replica).** Degradation under random corruption is a smooth ramp — no phase transition, killing the strong threshold-theorem conjecture. The attack-intensity curve is a *valley*: uniform-maximal attacks self-defeat because uniformly disguised sybils become mutually similar and re-cluster into one family (multi-seed: composed-0.5 accuracy 0.514 [0.495, 0.534] vs composed-1.0 recovery 0.910 [0.890, 0.929], disjoint CIs). Root-*set* overlap proved blind to the damage; root *attribution* is the meaningful lineage metric — and then Theorem 1 demotes even that.

**E5 (replica).** The side-preserving control: corruption constrained to same-side rewiring destroyed attribution (→ 0.59) with no accuracy cost (≥ 0.98 throughout, exactly zero side-confusion) — the immunity theorem's empirical shadow and the pivot of the paper.

**E6 (replica; H5 preregistered → REJECTED).** Signed side-confusion does not collapse corruption modes (max cross-mode accuracy spread 0.651 at matched bins): adversarial corruption dominates random at equal confusion because flipping requires only *meeting each world's margin*, and adversaries concentrate confusion where margins are thin. The rejection is the discovery: promoted to Theorem 4.

**EXP007A (canonical synthetic adversary completion).** The archived E7 runner was incomplete and is preserved as EXP007R with verdict `incomplete`. A new protocol and implementation were committed before execution. Its deterministic 45-evaluation search selected `(0.701175, 1.0, 0.0, 0.0)` and, on ten untouched holdout seeds, reduced inferred evidence-root accuracy to 0.3715 versus 0.4461 for uniform-0.5 and 0.4133 for uniform-1.0. Incorrect verdicts occurred in thinner-margin worlds than correct verdicts (3.7684 vs 5.6886; Welch t = 25.1144). Both preregistered hypotheses were supported and two clean runs were byte-identical. This replaces the unsupported historical E7 point estimates; it does not establish external validity.

**E8 (replica; best-in-class shootout).** On multi-proposition worlds (8 items per source, enabling reliability estimation), simplified stdlib baselines collapse toward majority performance under copy pressure. The archived E8 attack condition uses a historical exploratory mixture, not EXP007A's selected parameters; E8R only proves that the archived implementation and table replay deterministically. Its comparative and external-validity claims remain design-validation pending a canonical head-to-head against released baseline implementations.

### 6. The provenance requirement stack

The theorems reduce "what must provenance guarantee?" to three layers, ordered by hardness, replacing the full-lineage assumption:

**R1 — Root integrity.** Evidence roots must be unforgeable: no manufactured originals, no copies laundered into apparent roots. This is where Douceur's impossibility is escaped by importing cost or cryptography (attestation, capture-time signing, stake); the theorems become vacuous without it. *Metric: root-set accuracy.*

**R2 — Side-separation.** Claims must never be attributable to opposing-side roots. Given R1 and R2, *all other lineage error is provably harmless* (T1). *Metric: side-confusion = 0; runtime diagnostic `immunity_applicable`.*

**R3 — Margin sufficiency.** The honest independent-root margin must exceed the adversary's root-forgery capacity (T4). Defense planning is margin-relative by necessity (H5's rejection); systems should surface the margin as an explicit output. *Metric: `flip_budget`.*

**Demoted to not-required:** who-copied-whom accuracy, full lineage trees, copy counts, attribution accuracy. This demotion is the paper's central economic claim: side-separation is dramatically cheaper than lineage tracking — coarse origin tags and root-level attestation suffice — moving the infrastructure from "surveillance-grade tracking nobody will deploy" to "signatures at the source, deployable now."

For agent-communication standards, the stack compresses to one normative sentence: *transports MUST preserve evidence-origin attestations such that claims descending from distinct attested roots remain distinguishable and cross-origin attribution is infeasible; systems SHOULD expose the surviving root margin with every aggregate decision.*

### 7. Applications

A reference aggregator implementing the specification (stdlib Python; conformance vectors generated from the formal definitions) returns, with every verdict: the decision, confidence, per-side root sets, `immunity_applicable` (are T1's preconditions met on this input?), and `flip_budget` (how much forged independent evidence would reverse this decision). The latter two convert the theorems into runtime guardrail signals for multi-agent orchestration: an agent consuming "7 of 9 sub-agents agree" can act on *independent roots and their margin* rather than voices — and E2's 0.10% false-reversal profile is precisely the reliability class a refuse-to-act-on-manufactured-consensus guardrail requires.

### 8. Limitations

Binary assertions only; graded independence unmodeled; the synthetic generator uses token sets and single-parent inference; canonical replays validate archived implementations rather than scientific generalization. EXP007A is canonical but synthetic. E8/E8b comparative claims await released-implementation head-to-heads; the E2 matched-coverage check and proof obligations remain open. R1's cost mechanism is imported, not provided: the theorems specify what attestation must guarantee, not how to provide it.

### 9. Provenance of this paper

E2 normalized results and analysis are hash-bound; raw trade data are intentionally not redistributed. EXP003R–EXP008R preserve canonical replay records, including E6R's rejected H5 and E7R's incompleteness. EXP007A has a public pre-execution protocol commit, complete output, source and environment binding, and independent byte-identical rerun. See `CANONICAL-RECORDS.md` and `EVIDENCE-ALIGNMENT.md`; where this historical draft conflicts with them, the registry controls.

*One sentence, for the reader who skims: in a world where saying is free, only tracing is worth anything — and tracing turns out to need three cheap guarantees, not one expensive tree.*
