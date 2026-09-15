# Evidence alignment ledger

This ledger states which public claims are supported by which immutable record.
`CANONICAL-RECORDS.md` controls status; a paper cannot promote an experiment.

## EXP007 correction

Earlier paper drafts reported an E7 optimum of `(0.93, 0.91, 0.35, 0.36)`,
accuracy `0.357`, margins `3.88` and `5.71`, and Welch t `9.89`. The archived
runner did not contain a completed optimizer: its attack functions returned
`None` after printing the optimizer heading. EXP007R canonically reproduced
that incompleteness. Those numeric claims therefore have no canonical support
and are withdrawn from the active manuscript.

EXP007A is a distinct new experiment, not a retroactive repair. Its protocol
and implementation were committed before execution at
`9906f50485455172cbcd3a0d456c6c6aa9cee0d6`. Its two clean outputs were
byte-identical with SHA-256
`a9400e24f483fcb3911c2daf143c840744f23db5d634f3c72c45a838600c55c4`.

The supported synthetic-model claims are:

- selected `(paraphrase, forged citation, sybil, timing)` parameters:
  `(0.701175, 1.0, 0.0, 0.0)`;
- selected holdout accuracy `0.371544`, versus `0.446144` for uniform-0.5 and
  `0.413321` for uniform-1.0;
- incorrect-verdict mean honest margin `3.7684`, versus `5.6886` for correct
  verdicts, with Welch t `25.1144`;
- both preregistered hypotheses supported on ten untouched holdout seeds.

Permitted interpretation: within the frozen synthetic model, a budget-limited
attack against inferred lineage outperformed uniform comparators and failures
concentrated in thinner-margin worlds.

Not permitted: claiming an external exploit, general security performance,
the historical optimum, or proof that any identity/attestation provider solves
causal independence.

## Other canonical boundaries

| Record | Supported statement | Unsupported extension |
| --- | --- | --- |
| EXP001 | Frozen constructed pilot reproduced its declared output. | General truth recovery. |
| EXP002 | Frozen derived market record and declared source boundary are hash-bound. | Replay of mutable upstream bytes or superiority to market prices. |
| EXP003R–EXP005R | Archived implementations replayed deterministically. | External validity or promotion of legacy E3–E5. |
| EXP006R | Archived implementation replayed; H5 was rejected at spread 0.651. | A universal scalar failure curve. |
| EXP007R | Archived multi-seed section ran; optimizer was incomplete. | Any optimizer optimum. |
| EXP007A | New synthetic optimizer and holdout result are canonical. | Real-world exploitability or provider validation. |
| EXP008R | Archived runner and output table replayed deterministically. | Canonical comparison against released third-party implementations. |
| EXP009 | Frozen selective hybrid recovered 1.98% of majority-wrong cases at a 0.64% false-reversal rate and 0.11-point accuracy cost in the attack regime. | External validity, reliable deployed lineage inference, or authority to act. |
| HVI-1 | Control-domain aggregation admitted zero additional roots from aliases, key rotation, service splitting, or self-verification and escalated all unknown-control cases. | Discovery of hidden common control, causal evidence independence, truth, or authorization. |
| HEO-1 | Evidence-origin aggregation admitted zero additional roots from supported copies and transformations; unknown and forged origins always escalated. | Discovery of undisclosed common sources, truth of root observations, or authorization. |
| HGD-1 | Interval accounting reduced false-confident error, but its primary claim was rejected after missing the frozen absolute-effect threshold. | Proof that collocation establishes dependence, historical measurements were wrong, or the mechanism may grant authority. |
| HGD-2 | Interval accounting improved safety and preserved control accuracy, but failed frozen coverage and usefulness criteria. | A generally useful steering mechanism or proof that abstention alone solves dependent evidence. |
| HES-1 | Frozen evidence seeking recovered substantial environmental and software coverage after abstention; all seven hypotheses passed. | Universal source competence, especially for software false-negative claims, or authority to act. |
| EAA-P5 | One frozen out-of-tree unified auditor preserved conservative dependence labeling but failed its collapse-point and external selective-risk criteria. | Promotion of that composition, a claim that Minority Prophet as a whole failed, third-party validation, hidden-control discovery, independence certification, truth, or authority. |
| LIR-1/PHEME-R2 | At 40% hidden recorded edges, hidden-parent F1 was 0.1044 (case-bootstrap 95% interval 0.0846–0.1261), rejecting the greater-than-0.50 criterion; root-pair recall was 0.2256. | Causal evidence-independence inference, all social platforms, or proof that stronger methods must fail. |
| LIR-1E | In the 36-case constructed echo holdout at 40% hiding, root-pair F1 was 0.8309 and declared-advantage survival was 0.84 (case-bootstrap 95% interval 0.6818–0.9615), supporting the frozen criterion; inferred collapse answered 25 cases and was correct on 21. | Causal evidence independence, full-coverage truth recovery, uncontrolled real-world performance, or treating textual difference as independent observation. |
| LIR-2 | On a new 36-case constructed holdout, direct root grouping achieved precision 1.0, recall 0.9522, answered 34 cases, and was correct on all 34; the same-case LIR-1E baseline answered 29 and was correct on 25. | Causal source independence, authentication, universal zero-error performance, or generalization beyond the frozen synthetic generator and model pair. |
| LIR-2/PHEME | Fixed threshold 0.75 transferred with precision 1.0 but recall 0.2020, F1 0.3362, and root-count MAE 5.5517, rejecting all coverage/error thresholds. | Claiming that constructed echo performance transferred to real recorded reply lineage, or that failure on one known corpus rules out stronger methods. |
| LIR-3/PHEME | With 40% of exact parent-status IDs hidden but reply-target author retained, the frozen author-only rule achieved recorded-root precision, recall, and F1 of 1.0 with zero root-count error on 425 sealed cases. | Causal copying, evidence independence, author authentication, content truth, cross-platform generalization, or general provenance recovery. |
| LIR-4/PHEME | At 50% missing reply-target identity among hidden-edge records, precision remained 1.0 but recall fell to 0.4329, F1 to 0.6043, and root-count MAE rose to 2.405, rejecting graceful degradation. | General resistance to false identity or cross-root misbinding; only one final-holdout case had multiple roots, so the safety diagnostic was underpowered. |
| DRI-2-V1 | On 12,624 frozen synthetic worlds with lineage undisclosed, the decision-sensitivity guided method avoided false settlement in 0.997–1.000 of runs in every structured family, significantly more often than headcount, every fixed cut and weakest link, with at most 29 human calls beyond those required; the joint criterion was rejected because it was slower than determined-or-escalate and weakest link in the joint and shared-origin families under the frozen clock. The speed checks were misplaced; all 44 other checks passed (`results/dri2-v1/POST-RESULT-NOTE.md`). | That it is faster than asking, that the result is insensitive to the frozen probe and escalation charges, real-world lineage availability, independent validation, or authority to act. |
| DRI-2-V2 | On 12,624 fresh synthetic worlds with lineage undisclosed and no human, the unchanged decision-sensitivity guided method avoided false settlement in 0.999–1.000 of runs in every structured family, significantly more often than headcount and every fixed cut, with 0–41 unneeded abstentions against 324–2,945 for the abstaining arms; all 44 checks passed. | A blind test of the criterion (fixed after v1), speed advantage (it is slower by its probes), real-world lineage availability, independent validation, or authority to act. |
| DRI-3-V1 | On 42,000 synthetic decisions with truthful lookups, the tiered rule made zero silent false settlements and zero irreversible false settlements in each of six recorded-dependence families (95% bounds 0.000499 and 0.000998), against 23 (joint) and 757 (three-stacked) false settlements by the agreement rule; the reversible scorecard was 47.9 extra looks per prevented false settlement, driven by one family. | Immunity to unrecorded dependence (817 false settlements in that family), behaviour with imperfect lookups, side-asymmetric stacking, real-world frequency of stacked dependence, that the result is more than the rule's by-construction property, independent validation, or authority to act. |
| DRI-4-V1 | On 240,000 synthetic decisions with truthful lookups, the tiered rule made zero silent false settlements at a complete record in all five families (bounds 0.000499), and in every one of 30 incomplete-record cells made no more silent false settlements than the agreement rule; it prevented 33–87% of them at 10% missing and 10–26% at 50%; two powered comparisons (shared origin, 10% missing) were not significant, so the criterion was rejected. | That the rule stays protective when records are substantially incomplete, real-world rates of missing or spurious identities, behaviour with imperfect lookups, a rescue of the failed checks, independent validation, or authority to act. |
| DRI-5-V1 | On 360,000 synthetic decisions with truthful lookups, the content tiered rule never made a silent false settlement where the tiered rule did not, nor where lineage and content made the true grouping admissible; in the trap family, exact content took silent false settlements from 2,012 and 4,065 to zero; elsewhere it prevented 0–64% depending on paraphrase and collisions; 4 of 32 powered recovery comparisons were not significant, so the criterion was rejected. | That content fingerprints protect against missing lineage in general, that they catch shared components or origins, real-world content-similarity, paraphrase or collision rates, fuzzy matching, a rescue of the failed checks, independent validation, or authority to act. |
| DRI-6-V1 | On 150,000 synthetic decision scorings with a complete lineage record, erring lookups caused every silent false settlement the tiered rule made; the confirmed tiered rule, which looks twice and settles only on agreement, made significantly fewer in all 16 powered comparisons, removing 68–100%, at 2.9–42.6 extra looks per prevented false settlement against missed dependence; the record check caught no missed dependence. | That lookups in real systems err independently across calls, protection against a lookup wrong the same way every time, real lookup-error rates, behaviour with missing lineage or content fingerprints, independent validation, or authority to act. |

## Non-canonical results summarized on public pages (2026-09-14)

`PUBLIC-CLAIMS.md` and `docs/evidence/STATUS.md` now list results added after
2026-08-09 so that adverse and null outcomes are visible. None is a canonical
record and none is added to `CANONICAL-RECORDS.md`. Each public statement maps
to its source as follows.

| Source | Label as recorded | Supported statement | Unsupported extension |
| --- | --- | --- | --- |
| `research/adversarial-weighting/RESULTS.md` | Preregistered, hash-frozen before code; synthetic | Uniform counting broke at adversary fraction 0.40; declared-competence weighting at 0.20 (0.25 under sleeper); capping at `2/n` did not move breakdown (H2 not supported); trimming held to 0.45. | That any weighting or trimming scheme is safe, or any real-world adversary rate. |
| `results/dri1a-v1/result.json`, `research/records/DRI-1A-V1.json` | Imported, verdict `rejected`; its README keeps it out of the canonical registry | Oracle false-settlement reduction was 0.130737304 against the fixed controller cut and 0.130615234 against fixed evidence origin, below the frozen 0.15; against fixed upstream component it was -0.057495118. | That decision-relative selection beats fixed cuts, or that a model or person can select the cut. |
| `research/knowledge-ledger/experiments/KL-016/FINDING-v0.2.md` | v0.2 primary endpoint measured; real bibliographic data | Root ratios 0.429, 0.295, 0.132 and 0.298 for four conjectures (57–87% derived); unrelated control 1.000. | Prediction, belief, independence of roots, or anything about unlisted conjectures. The control arm collapsed to one case. |
| `evaluations/multi-model-v1/EPISTEMIC-LIFT-V11-RESULT.md` | `SUPPORTED_IN_FROZEN_CANDIDATE`; development worlds | C − B of +28.125 points (p 0.003906) and +21.875 points (p 0.015625) on 32 worlds per model. | Any public empirical claim before a hidden, independently audited benchmark, which the result itself requires. |
| `evaluations/multi-model-v1/CAPABILITY-TOURNAMENT-V1-RESULTS.md` | Preregistered conformance run | Deterministic root vote 128/128 dispositions; best model 116/128. | Truth in the world, origin honesty, or real-world independence. |
| `research/knowledge-ledger/experiments/KL-018/FINDING-KL018.md` | Registered endpoint met, refuted by its own control | Sign test 35 positive, 0 negative; before-and-after control p = 0.087. | Any copy-trading effect. |
| `formal/THEOREM-LEDGER.json` U1, `formal/CLAIM-SCOPE.md` | `proved_compiled` (was `underspecified`); closed by owner decision | Root identity is defined by proximate cause; the count is a maximum independent set over the declared dependence graph, relative to a class of error. | That the supplied graph reflects real lineage, that dependence is detected, or that independence is a scalar. A laundered record over-reports the count. |
| `formal/THEOREM-LEDGER.json` U3 | `not_pursued` (was `underspecified`) | Weighted roots are closed by decision; no theorem covers a weighted aggregator. | That weighting is solved or shown unsafe in general. |
| `formal/THEOREM-LEDGER.json` AC1–AC5 | `proved_compiled` | Universal and existential claims need the separate asymmetric rule; the symmetric margin is not their decision-sensitivity measure. | That either verdict rule is correct for a given deployment. |
| `provenance/graph.py` `read_from` | Shipped, tested, opt-in | Naming what a claim read records ancestry, so honest readers of one source share one root. | That existing callers use it, or that it detects fabricated roots. |

## v1.0.7 manuscript alignment

The active manuscript corrects two inherited presentation defects without
altering earlier snapshots:

- Earlier papers reported `121,944 rewirings`. The independent audit records
  `5,912` side-consistent forest worlds and `116,032` root-preserving forest
  rewirings; `121,944` was their sum, not a rewiring count.
- Earlier prose used a singular parent function while calling the structure a
  DAG. The compiler-ratified model is a multi-parent DAG. v1.0.5 now uses a
  parent relation and a set of root ancestors, matching `formal/PROOFS.md` and
  `formal/lean/`.
- v1.0.6 closes LIR-1–LIR-4 as one bounded empirical series. It states both the
  supported typed-provenance bridge and the rejected degradation claim, while
  preserving the distinction between recorded platform roots and causal
  evidence independence.
- v1.0.7 adds a reader-first abstract, example, visual, boundary table, results
  map, glossary, and selected primary-source links. It changes no theorem,
  canonical status, result, limitation, or release blocker.

## Manuscript policy

- `papers/minority-prophet-v1.0.7.md` is the active evidence-aligned draft, adopted
  2026-08-09.
- v0.9, v1.0, v1.0.1, v1.0.2, v1.0.3, v1.0.4, v1.0.5, and v1.0.6 are preserved historical drafts and defer to
  this ledger.
- EXP008's archived attack mixture is not EXP007A's selected attack.
- All point estimates must name their record and scope.
- Rejected, incomplete, and null results remain visible.

## Remaining release blockers

1. E2 matched-coverage analysis and final H2c status.
2. Canonical head-to-head against released truth-discovery implementations for
   E8/E8b comparative claims.
3. Verbatim verification of every literature citation against primary sources.
4. A vendor-neutral evidence contract and conformance suite tested against at
   least one real provider, without treating identity as proof of independence.
