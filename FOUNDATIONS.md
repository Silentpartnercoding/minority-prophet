# Foundations

## Problem

Most multi-agent aggregation answers *which proposition has the most support?* Minority Prophet studies a different problem: *which proposition is best supported by attributable, sufficiently independent evidence?*

For a proposition \(p\), let a world contain ground truth \(T(p)\in\{0,1\}\), agents \(A\), observations \(O\), and a directed acyclic evidence graph \(G=(V,E)\). An edge \(u\rightarrow v\) means claim \(v\) was derived from, copied from, or transformed from \(u\). Each observation carries an observer, source, timestamp, confidence, evidence payload, signature field, and transformation history.

A truth aggregator is a function

\[
F: (G, C, K, \tau) \rightarrow (\hat{T}, q, r)
\]

where \(C\) is the claim set, \(K\) is available competence information, \(\tau\) is evaluation time, \(\hat{T}\) is the selected belief or abstention, \(q\) is calibrated confidence, and \(r\) is a machine-readable rationale.

## Philosophy

Truth is not popularity. A thousand copied claims may contain one underlying observation. Three causally independent measurements may contain three. Accordingly, aggregation must distinguish agents from evidence roots, confidence from calibration, global reputation from domain competence, and disagreement from error.

The present work makes no claims beyond evidence aggregation in controlled synthetic worlds.

## The Minority Prophet property

Let \(I_T\) be a minority coalition whose claims match ground truth and whose evidence roots are mutually independent. Let \(M_F\) be a larger coalition supporting a false claim primarily through copied ancestry. For ratio \(\rho=|M_F|/|I_T|\), an aggregator has minority-truth recovery at level \((\rho,\alpha)\) on distribution \(D\) when:

\[
\Pr_{w\sim D}[F(w)=T(w)\mid |M_F|\ge\rho|I_T|] \ge \alpha.
\]

This is a distributional benchmark property, not a proof that minority views are generally correct. The correct system must also reject ungrounded minorities.

## Desiderata

1. **Anonymity of labels:** renaming agents does not change the result when their attributes and lineage are unchanged.
2. **Copy invariance:** duplicating a claim without adding an independent evidence root should not increase its evidential mass.
3. **Evidence monotonicity:** adding reliable independent evidence for a proposition should not reduce its support, all else equal.
4. **Calibration:** among outputs assigned probability \(q\), the long-run truth frequency should approach \(q\).
5. **Abstention:** insufficient or contradictory evidence should permit no decision.
6. **Revision:** new evidence can change beliefs without erasing the prior state.
7. **Auditability:** an output must be traceable to claims, roots, weights, and transformations.
8. **Verifier independence:** a verifier is not trusted merely because it is a
   third party. Its rules must be transparent, it must remain independent of
   the evidence producer, it must expose uncertainty through abstention, and
   it must be unable to mint, alter, or promote the evidence it verifies. A
   component that both manufactures and verifies an evidence root cannot make
   that root independent by attesting to itself.

These properties can conflict. For example, monotonicity can fail under newly discovered dependence, and competence estimates can encode feedback loops. Experiments must state which assumptions are active.

## Foundational slice

Version 0.1 formalizes the core objects, defines reproducible synthetic worlds, implements two transparent vote-based baselines, records evidence ancestry, and reports a small set of evaluation metrics. It does not implement a provenance-aware truth engine. The benchmark is designed to expose the failure of the included baselines under one controlled copying regime.

## Mathematical limits and open questions

No deterministic aggregator can infer truth from votes alone when the observation process is unidentified: two worlds can yield the same vote vector with opposite ground truth. Recovery therefore depends on explicit assumptions about observation reliability, lineage accuracy, independence, adversarial power, or access to verification.

Verifier independence is therefore an assumption that must be evidenced, not
a label assigned by topology. Deployments must identify who can create roots,
who can verify them, which rules each applies, and what happens when those
roles overlap. Unknown or overlapping provenance widens uncertainty; it never
creates permission.

The immediate research task is to make those assumptions visible and test their failure boundaries. The next formal step is a machine-checked statement of copy invariance; the next experimental step is an ancestry-aware reference method evaluated against controls.
