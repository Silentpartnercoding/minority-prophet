# The Minority Prophet Property: Copy-Invariant Evidence Aggregation in Rooted Claim Graphs

**James Siyuan He**  
Preprint v1.2.0; not peer reviewed, 18 August 2026
Correspondence: https://github.com/Silentpartnercoding  
Archival DOI (all versions): https://doi.org/10.5281/zenodo.21965712 — resolves to the latest deposited version

## Abstract

When claims can be copied at negligible cost, a large apparent majority may contain only one underlying observation. This paper isolates a structural response to that problem. A finite binary claim graph records derivation edges from claims to earlier claims. Parentless claims are declared evidence roots, and an aggregator counts the distinct roots supporting each side rather than the number of claims. Under side consistency, the resulting verdict is invariant to every lineage change that preserves assertions and the root set. Adding a copy with a recorded parent also leaves the verdict unchanged, whereas ordinary majority voting is not copy-invariant. The signed root margin gives a tight decision-sensitivity law: a winning verdict can cease to win only when net opposing root flow reaches the margin, and reversal requires one additional unit. With assertions fixed, a root-set symmetric difference of at most k cannot change a verdict whose absolute margin exceeds k. The statements are compiler-checked in Lean 4.32.2 against a pinned Mathlib revision. A preregistered finite and randomized validation record covers 50,362 bounded forest worlds and 100,000 generated worlds; its positive checks report zero violations while its negative controls detect the intended failure modes. These results concern correct counting of declared provenance, not truth, authenticity, causal independence, discovery completeness, or authority. The paper therefore presents copy invariance as a conditional aggregation guarantee and makes root qualification an explicit external trust boundary.

**Keywords:** evidence aggregation; data provenance; correlated votes; copy invariance; source dependence; formal verification; Sybil resistance

## 1. Introduction

Repeated agreement is useful evidence only when the repetitions carry sufficiently distinct information. That premise becomes fragile in systems where one observation can be copied, paraphrased, syndicated, or reproduced by many agents at negligible cost. A voice-counting rule treats every descendant as new support. Under copying pressure, its apparent sample size can therefore grow while its informational base stays fixed.

This paper asks a narrower question than whether an aggregator can recover truth: if derivation provenance is declared, what aggregation rule makes recorded copying irrelevant to the verdict? The answer studied here is to count roots of derivation rather than claims. The resulting property is called the **minority prophet property** in its structural form: a grounded minority can defeat an arbitrarily large recorded-copy majority whenever it contains more distinct declared roots.

The contribution is deliberately conditional. The model does not infer whether two records are genuinely independent. It does not prove that a root is accurate, authentic, complete, or authorized. It proves what follows after a system supplies a finite acyclic claim graph, a binary assertion for every claim, and a root identity relation.

The paper makes four contributions:

1. It defines a root-counting aggregator over finite, side-consistent claim DAGs and identifies the minimal information used by the decision rule.
2. It proves lineage immunity, recorded-copy invariance, majority non-invariance, and tight root-margin sensitivity results in a compiler-checked Lean development.
3. It reports bounded validation from a preregistered lineage program, including positive checks and failure-sensitive ablations, without presenting those checks as additional proofs.
4. It separates the proved aggregation layer from the unresolved trust layer: root identity, root qualification, discovery coverage, graded dependence, revocation, and operational authority.

This focus distinguishes the paper from the broader v1.0.7 research synthesis, which also reports markets, behavioral comparators, lineage inference, and evidence-seeking systems. Those programs remain in the repository but are outside this manuscript's claim set.

## 2. Related work

### 2.1 Correlated votes and causal independence

The classical jury-theorem intuition relies on competence and independence conditions. Research on correlated votes shows that positive correlation can reduce collective competence and can make enlargement harmful over part of the parameter range [1]. Dietrich and Spiekermann distinguish probabilistic notions of opinion independence and relate them to the causal network through which evidence and influence produce beliefs [2]. Hong and Page separately distinguish generated signals from interpreted signals, showing that familiar independence assumptions do not transfer unchanged between the two [3].

The present model does not attempt to establish probabilistic independence from graph structure. A distinct root is only a structural unit declared by the provenance layer. The theorem is therefore about multiplicity control: recorded descendants of the same root cannot increase that root's weight.

### 2.2 Truth discovery and source dependence

Truth-discovery methods combine conflicting values while estimating source reliability [4]. Source-dependence models additionally infer copying relationships and discount dependent data [5] [6]. This paper shares their motivation but starts from a different input boundary. It assumes a declared derivation graph and asks what is guaranteed when roots and sides are preserved. It neither replaces statistical copying detection nor claims comparative superiority. When lineage is absent or incorrect at the root boundary, the structural guarantee may not apply.

### 2.3 Identity multiplication

The Sybil problem shows why redundant identities cannot be treated as independent evidence without an external constraint on identity creation [7]. Root counting changes the aggregation unit but does not itself solve root issuance. A deployment must bind roots to a suitable observation and control domain, constrain issuance, and specify revocation and compromise handling. Those are security requirements imported by the theorem, not consequences of it.

### 2.4 Formal verification

The formal development uses Lean [8] and Mathlib [9]. Compiler checking eliminates a large class of proof-transcription errors, but it establishes only the encoded statements. The model-to-world mapping and the trustworthiness of root metadata remain outside the proof assistant.

## 3. Model

### 3.1 Worlds and roots

A world W on n claims contains:

- a finite claim set C = {0, ..., n-1};
- a parent relation parents(c) contained in {0, ..., c-1}, so the time order makes the graph acyclic; and
- an assertion function a(c) in {0, 1}.

A claim r is a **root** when parents(r) is empty. The set roots_W(c) contains the parentless ancestors of c. Multiple parents are permitted.

The world is **side-consistent** when every parent edge connects claims with the same assertion:

> p in parents(c) implies a(p) = a(c).

Side consistency models copying or derivation that preserves the binary proposition. It excludes synthesis across opposing sides. This assumption is load-bearing: without it, one root can enter both side sets.

### 3.2 Aggregator and margin

For side b in {0, 1}, define the supporting root set

> S_b(W) = union { roots_W(c) : a(c) = b }.

The root aggregator F returns 1 when |S_1| > |S_0|, returns 0 when |S_0| > |S_1|, and abstains on equality. All reported results use the zero-threshold rule: abstention occurs only on an exact tie.

Define the signed root margin

> m(W) = |S_1(W)| - |S_0(W)|.

The verdict is a threshold function of m(W). The absolute margin |m(W)| is a sensitivity certificate measured in net per-side root units, not necessarily in attacker actions or real-world incidents.

### 3.3 Trust boundary

Root identity is primitive in the formal model. In a deployed system it must be supplied by a canonicalization and attestation layer. Different keys, processes, prompts, services, or machines do not by themselves establish independent control. A compromised issuer may create many apparently distinct roots unless issuance is bounded externally. Consequently, the words **root**, **independent evidence**, and **truth** are not interchangeable in this paper.

## 4. Formal results

The complete sources are in `formal/lean/MinorityProphetCore/`. They compile with Lean 4.32.2 and Mathlib revision `905b95818eb32af7874a58b427f50c1711a5e96c`, with zero `sorry`, zero `native_decide`, and no added axioms beyond the standard dependencies reported by Lean.

### 4.1 Side locality

**Lemma 1 (side locality).** In a side-consistent world, S_b(W) is exactly the set of parentless claims asserting b.

**Proof sketch.** Every ancestor of a b-asserting claim also asserts b by induction along the acyclic time order. Hence every root reached from that claim is a b-root. Conversely, each parentless b-claim is included in its own root set. The Lean theorem is `side_locality`.

This factorization is the bridge to the remaining results. Once side locality holds, the aggregator uses only the assertions on roots.

### 4.2 Lineage immunity

**Theorem 1 (root-preserving lineage immunity).** Let W and W' be side-consistent worlds on the same claims. If their assertion functions and root sets are equal, then F(W) = F(W').

**Proof.** By Lemma 1, each side-root set is the filter of the root set by the assertion function. Equal root sets and assertions therefore give equal S_0 and S_1, hence equal verdicts. The Lean theorem is `immunity`.

The result permits arbitrary changes among non-root edges, including additions, deletions, and retargeting, provided that assertions, side consistency, and the root set survive. It does not say that attribution is globally irrelevant: an edit that creates or removes a root is outside the theorem.

### 4.3 Recorded-copy invariance

**Theorem 2 (recorded-copy invariance).** Append a claim whose parent is an existing claim and whose assertion equals that parent's assertion. If W is side-consistent, the appended world has the same side-root counts, margin, and verdict as W.

**Proof sketch.** The new claim is not a root. Every old root remains a root, and the new claim reaches only roots already reachable from its parent. Therefore neither side-root set changes, up to the index embedding used by the formalization. The Lean theorems are `copy_invariance` and `margin_addCopy`.

The recorded-parent condition is essential. A copied claim with no recorded parent is represented as a new root and can change the verdict.

### 4.4 Head counting is not copy-invariant

**Theorem 3 (majority non-invariance).** Ordinary claim majority is not invariant to copying.

**Witness.** The list [1, 1, 0] has a 1-majority. Appending two copies of the dissenting value produces [1, 1, 0, 0, 0], which has a 0-majority. The Lean theorem `majority_not_copy_invariant` checks this witness.

This theorem concerns ordinary unweighted majority only. It does not establish an impossibility result for every conceivable voice-based mechanism.

### 4.5 Margin sensitivity

For two worlds define opposing flow as the decrease in signed margin:

> flow(W, W') = m(W) - m(W').

**Theorem 4 (loss-of-win condition).** If F(W) = 1 and F(W') is not 1, then flow(W, W') is at least m(W).

**Theorem 4a (tightness).** If flow(W, W') equals m(W), then F(W') abstains. If F(W') = 0, then flow(W, W') is at least m(W) + 1.

These are threshold-arithmetic results, compiled as `T4_flip_requires_margin`, `T4'_flow_eq_margin_abstains`, and `T4'_reversal_needs_margin_succ`.

The unit matters. Relabelling one existing root from side 1 to side 0 changes the signed margin by two. Thus an action count cannot be inferred from the flow bound without specifying the permitted action model.

### 4.6 Root-set error tolerance

Let d_R(W, W') be the cardinality of the symmetric difference between the two root sets.

**Theorem 5 (fixed-assertion root-error tolerance).** Let W and W' be side-consistent and have equal assertion functions. If d_R(W, W') <= k, then:

- a verdict with |m(W)| > k is unchanged; and
- a verdict with |m(W)| >= k cannot be reversed, although it may become an abstention.

The central Lean result `margin_diff_le_rootSet_diff` bounds the margin change by d_R. The verdict consequences are `root_error_tolerance` and `no_reversal_of_margin_ge`.

Equal assertions are essential. A side conversion can move the margin by two while leaving the root set unchanged. The theorem also measures root-set units, not key compromises, database incidents, or adversarial actions.

## 5. Validation evidence

Formal proof is the primary evidence for the general statements. The repository also contains a preregistered bounded validation program, LIN-000 v0.4, designed to test the implementation and to expose incorrect variants. Its result record is valid under its registered invalidation rules.

### 5.1 Design

The finite phase enumerates all single-parent worlds of sizes one through six, for 50,362 total worlds. The randomized phase generates 100,000 worlds of up to twenty claims from a counter-based, fully specified stream. The registration fixes the generator, enumeration order, canonical serialization, digests, populations, expected directions, and invalidation conditions before the v0.4 reference result.

The validation schema is a forest rather than the theorem's multi-parent DAG. A forest is a strict subcase of the DAG model, so the checks exercise implementation behavior in a bounded domain but do not extend the proofs.

### 5.2 Results

| Check | Population | Result | Evidence class |
|---|---:|---:|---|
| Exhaustive worlds generated | 50,362 | exact registered count | finite enumeration |
| Randomized worlds generated | 100,000 | exact registered count | randomized generation |
| Side-locality, exhaustive | 5,912 side-consistent worlds | 0 violations | bounded check |
| Side-locality, randomized | 54,747 side-consistent worlds | 0 violations | randomized check |
| Root-preserving rewiring | 116,032 eligible pairs | 0 verdict violations | bounded check |
| Side-consistency necessity arm | 194,112 eligible pairs | 47,224 verdict changes | negative control |
| Shallow-root ablation | both phases | detected in 35,416 exhaustive and 76,833 randomized worlds | power check |
| Claim-count ablation | both phases | detected in 21,440 exhaustive and 34,779 randomized worlds | power check |

The exhaustive and randomized streams regenerate identically and match their recorded SHA-256 digests. The result record reports no invalidation reasons. Zero observed violations in a finite or sampled domain are not a proof; the negative controls matter because they show that the checks distinguish at least the registered incorrect implementations from the reference behavior.

### 5.3 Reproducibility

The validation registration, traceability file, implementation, result JSON, formal sources, and exact toolchain pins are versioned in the repository. The repository-level command `make verify` runs the normal test, integrity, site, and evaluation gates. The Lean core is reproduced separately with `lake build` from `formal/lean/`.

## 6. Interpretation

The results support three precise interpretations.

First, recorded multiplicity is not evidence multiplicity. Once a copy retains a derivation edge, any number of such descendants contributes the same root set as the original claim.

Second, root-set integrity is more important to this verdict than precise attribution among non-roots. A lineage system may misidentify which same-side ancestor a descendant copied while preserving the decision, yet a single mistake at the root boundary may move a thin-margin verdict.

Third, the root margin is a transparent sensitivity measure. It states how many net per-side root units separate a verdict from abstention or reversal under the specified comparison. It is not a probability that the verdict is correct.

These statements suggest an engineering separation of concerns:

1. **Discovery:** declare where the system looked and what it failed to access.
2. **Provenance:** establish claim lineage and the identity and qualification of roots.
3. **Decision:** count qualified roots and expose the margin and abstention state.
4. **Authority:** apply a separate policy that determines whether any action is permitted.

The theorem occupies only the third layer and depends on the second. Evidence assessment does not grant operational authority.

## 7. Threats to validity and limitations

**Declared provenance may be false or incomplete.** An undetected copy appears as a new root and receives new weight. Copy invariance applies only when the parent relation is recorded correctly enough to preserve the root set.

**Root identity is not solved.** The model treats root equality as given. Canonicalization errors, aliases, shared control, key rotation, and colluding issuers can make one underlying observation appear as several roots.

**Distinct roots need not be independent.** Roots may share evidence, training data, incentives, ownership, or environmental causes. The paper does not convert structural distinctness into probabilistic or causal independence.

**Binary side consistency is restrictive.** Cross-side synthesis, uncertainty, multi-valued propositions, and claims that revise their sources are outside the theorem. Without side consistency the literal definition can count one root for both sides.

**The finite validation uses forests.** The Lean model permits multi-parent DAGs, but the v0.4 preregistered enumerator covers single-parent worlds. This does not weaken the proof; it limits what the empirical validation independently exercises.

**No comparative performance claim is made.** The manuscript does not report a head-to-head evaluation against released truth-discovery systems, behavioral dependence detectors, or debate aggregators. Such work requires matched inputs, coverage, tuning rules, and preregistered comparisons.

**No truth-recovery rate is claimed.** Accuracy depends on how roots are discovered, qualified, and distributed across sides. The theorem guarantees copy-invariant counting under its assumptions, not that the winning roots are true.

**The aggregator answers a symmetric question only.** Counting roots per side compares two counts, which decides *which side holds more independent evidence*. It does not decide a **universal** claim — *every member of a scope satisfies P* — which a single counterexample root settles against, whatever the confirming count; nor its **existential** dual, which a single verified root settles for, and against which roots reporting an unsuccessful search are absence of evidence rather than evidence of absence. Applied to a universal claim, the aggregator of Section 3.2 returns the confirming side while a counterexample root is present, and the margin of Section 4.5 then describes evidence that did not determine the answer. Nothing in Section 4 is affected: those theorems concern the symmetric aggregator and are correct about it. What does not follow is that the root margin is a decision-sensitivity measure for claims of the other two shapes. The divergence is recorded as CE-14 in the repository; the rules for both asymmetric shapes are separately defined and machine-checked there, and are implemented as a distinct function rather than as a mode of this aggregator.

**Operational incidents do not map directly to theorem units.** One compromised key may mint many roots, while one deleted record may orphan a large subtree. Converting root-margin units into security guarantees requires an external issuance and failure model.

## 8. Conclusion

In a finite binary rooted-claim graph, counting declared roots rather than claims makes recorded copying irrelevant. Under side consistency, the verdict depends only on root identities and their assertions; same-root copies and non-root rewiring add no weight. The root margin then exposes exact decision sensitivity in the model. These guarantees are simple because the difficult work is pushed to an explicit boundary: deciding what constitutes a root and whether roots deserve evidential weight. That boundary should not be hidden behind a crowd count. A system that cannot establish it should widen uncertainty or abstain rather than treat repeated claims as independent confirmation.

## Version history

**v1.2.0 (18 August 2026)** — adds one limitation to Section 7: the aggregator answers a symmetric question and does not decide universal or existential claims. No result, proof, validation number, or claim of v1.1.0 is retracted or changed. This is a **content revision**, not the metadata-only `v1.1.1` correction described in `ARCHIVAL-INTEGRITY.md`; that correction is superseded by this version rather than published separately, because a version that changes what the paper claims about its own scope must not be labelled metadata-only.

**v1.1.0 (16 August 2026)** — archived; that deposit is immutable and is not replaced. Per-version DOIs are recorded in `papers/peer-review/ARCHIVAL-INTEGRITY.md` rather than in this manuscript, so that the deposited artifact and the repository source cannot diverge.

## Data and code availability

All manuscript source, formal definitions and proofs, validation registrations, reference implementations, adverse findings, and result records are publicly available at https://github.com/Silentpartnercoding/minority-prophet. The reviewed source and PDF are fixed by the immutable `paper-v1.1.0` release tag. The archival preprint record, including the PDF and release archive, is available at https://doi.org/10.5281/zenodo.21965713.

## Ethics statement

This theoretical and software-verification study used no human participants, private personal data, or live authority decisions. The central deployment risk is epistemic overclaiming: root metadata can be mistaken for truth or independence. The manuscript therefore states the trust boundary and abstention conditions explicitly.

## Funding

No external funding is declared for this manuscript.

## Competing interests

The author declares no competing interests.

## Author contributions

James Siyuan He conceived the research program, specified the claims and repository controls, and is responsible for the manuscript and released evidence. AI coding assistants contributed implementation, proof-draft, synthesis, and editorial work under the author's direction. Their outputs were treated as same-controller work and were rechecked against the repository's executable and documentary records; they are not independent validation.

## Acknowledgments

The repository preserves detailed provenance for computational and editorial contributions. The author thanks future reviewers for treating adverse and null records as part of the evidence rather than as disposable development history.

## References

[1] S. Kaniovski. Aggregation of Correlated Votes and Condorcet's Jury Theorem. *Theory and Decision*, 69(3):453-468, 2010. https://doi.org/10.1007/s11238-008-9120-4

[2] F. Dietrich and K. Spiekermann. Independent Opinions? On the Causal Foundations of Belief Formation and Jury Theorems. *Mind*, 122(487):655-685, 2013. https://doi.org/10.1093/mind/fzt074

[3] L. Hong and S. E. Page. Interpreted and Generated Signals. *Journal of Economic Theory*, 144(5):2174-2196, 2009. https://doi.org/10.1016/j.jet.2009.01.006

[4] Y. Li, J. Gao, C. Meng, Q. Li, L. Su, B. Zhao, W. Fan, and J. Han. A Survey on Truth Discovery. *ACM SIGKDD Explorations Newsletter*, 17(2):1-16, 2015. https://doi.org/10.1145/2897350.2897352

[5] X. L. Dong, L. Berti-Equille, and D. Srivastava. Integrating Conflicting Data: The Role of Source Dependence. *Proceedings of the VLDB Endowment*, 2(1):550-561, 2009. https://www.vldb.org/pvldb/vol2/vldb09-pvldb47.pdf

[6] X. L. Dong, L. Berti-Equille, Y. Hu, and D. Srivastava. SOLOMON: Seeking the Truth Via Copying Detection. *Proceedings of the VLDB Endowment*, 3(2):1617-1620, 2010. https://vldb.org/pvldb/vol3/D26.pdf

[7] J. R. Douceur. The Sybil Attack. In *Proceedings of the First International Workshop on Peer-to-Peer Systems*, pages 251-260, 2002. https://doi.org/10.1007/3-540-45748-8_24

[8] L. de Moura, S. Kong, J. Avigad, F. van Doorn, and J. von Raumer. The Lean Theorem Prover (System Description). In *Automated Deduction - CADE-25*, pages 378-388, 2015. https://doi.org/10.1007/978-3-319-21401-6_26

[9] The Mathlib Community. The Lean Mathematical Library. In *Proceedings of the 9th ACM SIGPLAN International Conference on Certified Programs and Proofs*, pages 367-381, 2020. https://doi.org/10.1145/3372885.3373824
