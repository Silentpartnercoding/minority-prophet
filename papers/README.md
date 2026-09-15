# Papers

Start with **[the current paper](./minority-prophet-v1.0.7.md)**.

For external review, use the narrower **[peer-review candidate](./peer-review/minority-prophet-peer-review-v1.2.0.md)**. It isolates the Lean-checked copy-invariance core, includes a complete literature audit for retained claims, and deliberately omits the broader v1.0.7 programs that require separate papers or comparison work.

| File | Status |
| --- | --- |
| [`minority-prophet-v1.0.7.md`](./minority-prophet-v1.0.7.md) | Current reader-first, evidence-aligned pre-submission manuscript |
| [`minority-prophet-v1.0.6.md`](./minority-prophet-v1.0.6.md) | Preserved prior snapshot; closes LIR-1–LIR-4 |
| [`minority-prophet-v1.0.5.md`](./minority-prophet-v1.0.5.md) | Preserved prior snapshot |
| [`minority-prophet-v1.0.4.md`](./minority-prophet-v1.0.4.md) | Preserved prior snapshot |
| [`minority-prophet-v1.0.3.md`](./minority-prophet-v1.0.3.md) | Preserved historical snapshot |
| [`minority-prophet-v1.0.2.md`](./minority-prophet-v1.0.2.md) | Preserved historical snapshot |
| [`minority-prophet-v1.0.1.md`](./minority-prophet-v1.0.1.md) | Preserved historical snapshot; consult the errata |
| [`minority-prophet-v1.0.md`](./minority-prophet-v1.0.md) | Preserved historical snapshot; consult the errata |
| [`MINORITY-PROPHET-PAPER-v0.9.md`](./MINORITY-PROPHET-PAPER-v0.9.md) | Historical draft; superseded |

[`ERRATA.md`](./ERRATA.md) records corrections without erasing prior versions.

## Publication sequence

1. **Published foundation:** *The Minority Prophet Property: Copy-Invariant Evidence Aggregation in Rooted Claim Graphs* isolates the Lean-checked structural guarantee and root-margin bounds. Archival record, all versions: https://doi.org/10.5281/zenodo.21965712. Current version, v1.2.0: https://doi.org/10.5281/zenodo.21997434. Cite the all-versions DOI unless a specific version is required; https://doi.org/10.5281/zenodo.21965713 is v1.1.0 and is superseded.
2. **Paper II working title:** *An Echo Is Not a Witness: Evaluating Provenance-Aware Aggregation Under Copying Pressure*. Its candidate scope is the empirical material intentionally omitted from the focused foundation paper: adversarial lineage inference, conservative hybrid recovery, identity and origin controls, multi-agent comparisons, and their null or rejected results. It must not be submitted until its exact evidence set, comparator implementations, and claim boundaries are frozen.
3. **Companion paper, [draft v0.1](./companion/independence-without-equivalence-v0.1-DRAFT.md):** *Independence Without Equivalence: Root Identity by Proximate Cause*. Scope is the material added after the foundation paper was deposited and which resolves limitations that paper states: `RootIdentity.lean` (U1 closed by a doctrine of remoteness) and `Responsiveness.lean` (the converse of invariance — a material change must move the verdict). `Asymmetric.lean` was originally listed here and is now item 4, because it is a different kind of result. Recorded in `ERRATA.md` under `[E9]`. It must carry the residual with it: the closure defines what a root is and does not promise that a laundered root will be detected.

4. **Companion paper, [draft v0.1](./companion/asymmetric-claims-v0.1-DRAFT.md):** *When Counting Is the Wrong Instrument: Asymmetric Claims in Rooted Evidence Graphs*. Scope is `Asymmetric.lean` (AC1–AC5) and `aggregation/root_vote.asymmetric_verdict`. It exhibits a machine-checked world where the counting aggregator returns the *opposite* side from the correct verdict, proves that no margin threshold repairs it, and states the scope condition this places on the foundation paper's theorems. Separate from the U1 companion because it is a different result: not a closed open problem, but a class of claims the core instrument cannot address.

5. **Companion paper, [draft v0.1](./companion/safety-was-never-scarce-v0.1-DRAFT.md):** *Safety Was Never the Scarce Property: Liveness Conditions for Narrow Admission Gates*. Scope is `NarrowGate.lean`. It proves the gate's safety theorem, then shows the theorem is achievable in full by a gate that admits nothing — with a machine-checked system that is perfectly safe and permanently paralysed — and identifies controlled invariance as the hypothesis that buys liveness back. Also settles the contraction objection: authority that only narrows is a termination argument, not a safety property.

6. **Later architecture paper:** the dual evidence/search ledger remains a research direction until the schemas, conclusion-strength rules, incomplete-coverage controls, matched comparisons, and a real-provider test are preregistered and evaluated.
