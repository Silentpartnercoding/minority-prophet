# What is actually established

<!-- mp-status: {"id":"evidence-status","class":"current","asOf":"2026-09-19","replacement":null,"immutable":false,"theorems":["DR1","DR2","DR3","U1"],"researchRecords":["DRI-2-V1","DRI-2-V2","DRI-3-V1","DRI-4-V1","DRI-5-V1","DRI-6-V1","DRI-8-V1","DRI-9-V1","DRI-10-V1","DRI-11-V1","AID-1-V1","AID-2-V1","AID-3-V1","AID-4-V1"],"describesMechanisms":["recorded_graph_roots","bounded_root_issuance","proximate_mis_count","recorded_dependence_robust_settlement","attested_independence_point_policy","attested_independence_bounds_policy","collapse_robust_margin_policy","priced_exposure_policy"],"recommendedMechanisms":["recorded_graph_roots","bounded_root_issuance","recorded_dependence_robust_settlement"]} -->

This is a reader-oriented status guide, not a new source of claim authority.
When wording conflicts, defer to [`PUBLIC-CLAIMS.md`](../../PUBLIC-CLAIMS.md),
[`EVIDENCE-ALIGNMENT.md`](../../EVIDENCE-ALIGNMENT.md),
[`CANONICAL-RECORDS.md`](../../CANONICAL-RECORDS.md), and the formal ledgers.

Current record status is listed in full in
[`CANONICAL-RECORDS.md`](../../CANONICAL-RECORDS.md), including the EXP, HVI,
HEO, HGD, HES, EAA, LIR, DRI and AID series and every rejected or incomplete
record registered there. Date is not a lifecycle class: records added after
2026-08-09 include canonical DRI and AID results. None establishes real-world
provenance recovery.

## Proved

The formal statements compile in Lean 4.33.1 against pinned Mathlib with zero
`sorry` and no added axioms. Full scope is in
[`formal/CLAIM-SCOPE.md`](../../formal/CLAIM-SCOPE.md), with statuses in
[`formal/THEOREM-LEDGER.json`](../../formal/THEOREM-LEDGER.json).

- Under side-consistency, `S_a` is exactly the `a`-asserting roots.
- Lineage may be arbitrarily wrong without moving a verdict when no edge crosses
  sides, no root is created or destroyed, and assertions are unchanged.
- Copies whose parent edge is recorded are free: they add no new root vote.
- A verdict flips only if net per-side root flow reaches the margin; flow equal
  to the margin abstains, while reversal needs margin plus one.
- With assertions fixed, `k` units of root-set change cannot move a verdict of
  margin greater than `k`.
- Conversions preserve margin parity, so conversion alone cannot drive an odd
  margin to abstention.
- Root identity (U1, closed): the independent-root count is a maximum
  independent set over the declared dependence graph, with dependence defined by
  proximate cause and always relative to a class of error. This bounds the count
  relative to that graph; it does not show the graph reflects real lineage, and a
  laundered record that removes edges makes the count over-report. See
  [`CLAIM-SCOPE.md`](../../formal/CLAIM-SCOPE.md).
- Asymmetric claims (AC1–AC5): universal and existential claims need a separate
  verdict rule. The symmetric margin answers a different question and is not a
  decision-sensitivity measure for them.

These are narrow mathematical results under stated assumptions. They are not a
proof of real-world truth recovery.

## Measured

Two world-facing quantities have been measured, without labeling whether the
inferred roots are truly independent observations.

Among 60.8 million journal articles from 2015–2024, 46.2% record no ancestry.
Each therefore becomes an evidence root under the recorded-lineage rule. In the
copy-dominant regime studied here, the resulting over-count floor is `u × N`,
with `u` ranging from 33% in medicine to 74% in arts and humanities. This is a
lower bound under the model, not an estimate of average causal duplication.

For four mathematical conjectures, 57% to 87% of the literature citing each one
before it was resolved descended from other literature citing the same
conjecture, against 0% for unrelated literature from the same eras. The control
arm collapsed to one case, and no predictive, belief, or independence claim is
permitted. See
[`KL-016 v0.2`](../../research/knowledge-ledger/experiments/KL-016/FINDING-v0.2.md).

## Established only in constructed or replay settings

The benchmark, archived replays, and finite Łoś-inspired pilot demonstrate
specific implementation behavior under recorded or injected lineage. In the
frozen synthetic pilot, root-aware and semantic aggregation recovered all
copied-majority worlds under correct declared lineage. All methods failed under
sufficiently corrupted lineage.

See [`experiments/EXPERIMENT-001.md`](../../experiments/EXPERIMENT-001.md) and
[`results/los-inspired-v0.1.md`](../../results/los-inspired-v0.1.md). This is an
implementation check on constructed data, not a literal ultraproduct and not a
general truth-discovery result.

Later constructed results, none canonical:

- **Adversarial weighting** (preregistered and hash-frozen before code). Weighting
  by declared competence halved the adversary fraction needed to break the
  verdict, from 0.40 to 0.20; capping weights did not help; trimming extremes
  held to 0.45 at a cost of about three and a half points with no adversary.
  See [`RESULTS.md`](../../research/adversarial-weighting/RESULTS.md).
- **Capability tournament** (preregistered conformance run). The deterministic
  root vote returned 128 of 128 expected dispositions; the best model scored 116.
  This checks conformance to the method, not truth in the world. See
  [`results`](../../evaluations/multi-model-v1/CAPABILITY-TOURNAMENT-V1-RESULTS.md).
- **Epistemic lift v1.1** (frozen candidate on development worlds). Adding the
  receipt to provenance improved two models by 28.1 and 21.9 points on 32 worlds.
  The worlds were designed alongside the analysis. See
  [`result`](../../evaluations/multi-model-v1/EPISTEMIC-LIFT-V11-RESULT.md).
- **Honest citation** is now recordable as ancestry. A claim that names what it
  read in `read_from` becomes a descendant of that source, so five honest readers
  of one paper count as one root. The field is opt-in and no shipped caller
  supplies it yet.

## Not established

- Whether one recorded evidence root corresponds to one real observation in the
  typical case. The relevant ground truth is absent precisely where ancestry is
  missing. See the
  [`HRI-1 blocker`](../../research/knowledge-ledger/experiments/KL-014/HRI1-BLOCKER-20260816.md).
- Whether missing provenance can be recovered reliably in open real-world
  systems.
- Whether a model can choose the correct causal or decision-relative
  independence cut in deployment. The preregistered DRI-1A run did not support
  even the oracle-supplied version against every fixed cut; it is recorded as an
  adverse, non-canonical result. See
  [`DRI-1A`](../../results/dri1a-v1/README.md). DRI-2, which withholds the failure
  domain, was also rejected: its method had as few false settlements as always escalating and far fewer than any fixed cut, but failed its frozen time criterion. See
  [`DRI-2`](../../results/dri2-v1/README.md). The final DRI-2 v2, on fresh worlds
  with no human and speed not a criterion, was supported in its synthetic model;
  see [`DRI-2 v2`](../../results/dri2-v2/README.md). Neither shows a model can
  choose the cut in deployment. DRI-3 showed that settling only on settlements
  robust to recorded stacked dependence removed silent false settlements in its
  synthetic model, at a cost in looks and lost settlements, and that it cannot
  catch dependence no record carries; see
  [`DRI-3`](../../results/dri3-v1/README.md). DRI-4 was rejected on two of 67
  checks: the proven guarantee held with a complete record, but protection eroded
  as shared identities went missing, never becoming worse than the old rule; see
  [`DRI-4`](../../results/dri4-v1/README.md). DRI-5 was rejected on four of 193
  checks: an exact content fingerprint fully restored protection where missing
  lineage hid copying, but not where it hid a shared component, and paraphrase
  largely defeated it; see [`DRI-5`](../../results/dri5-v1/README.md). DRI-6 was
  supported: erring lookups caused silent false settlements, and looking twice
  removed most of them; see [`DRI-6`](../../results/dri6-v1/README.md). DRI-8 met
  its criterion, but that criterion set no minimum effect: probing prevented
  0.3–3.5% of silent false settlements at 16–468 probes each; see
  [`DRI-8`](../../results/dri8-v1/README.md). DRI-9 rebuilt belief so it overrides
  the record and was rejected: the method named in advance cleared its effect floor
  in 1 of 8 cells, while a simpler reported arm cleared it in 8 of 8 on a world
  that planted the mark on the hidden group and planted no markers in the decoy;
  see [`DRI-9`](../../results/dri9-v1/README.md). DRI-10 then named that simpler arm
  on a world written by the review, where error and mark are separate knobs, and
  rejected it on 12 of 40 checks: a mark is not dependence. It collapsed a shared
  library carrying no shared error, lost correct settlements wherever marks leaked,
  and prevented nothing where the dependence carried no mark; see
  [`DRI-10`](../../results/dri10-v1/README.md). DRI-11 named two rules before the
  reviewer's world existed and rejected both, 66 of 134: refusal is blind to trios
  (0 of 925-961 prevented) and refused all 2,400 decisions in a family the baseline
  settles correctly, while one shock satisfied both signals a corroboration rule
  requires (342-439 false merges, zero true); see
  [`DRI-11`](../../results/dri11-v1/README.md). The series is now closed on that
  answer rather than on exhaustion, with the result chain and what stays open in
  [`the series closure`](../../experiments/DECISION-RELATIVE-INDEPENDENCE-SERIES-CLOSURE.md);
  what followed from it was a policy proposal rather than detection. That
  attested-independence proposal was subsequently rejected with every other AID
  counting-time policy; see the
  [`AID series closure`](../../experiments/ATTESTED-INDEPENDENCE-SERIES-CLOSURE.md).
- Why counting only attested witnesses is not current policy. The proposal was
  intended to fail closed instead of converting the record's silence into
  independence. Its first specification, before the experiments ran, is
  [`AID-1-DESIGN-DRAFT.md`](../../research/attested-independence/AID-1-DESIGN-DRAFT.md),
  the first experiment of a new series rather than a continuation of the closed
  one. An observational census run first found that the policy's input does not
  exist yet: of 52 claim objects across four corpora, none states a witness
  depth, and none of five formats in which evidence crosses a boundary permits
  stating one, because each closes its origin object to additions. The binding
  constraint is therefore the contract rather than the policy; see
  [`AID-1-OBS`](../../experiments/aid1/OBSERVATIONAL-REPORT.md), which is
  observational and refuted by a single counterexample. The contract was then
  given a slot —
  [`authority-evidence-v0.2`](../../contracts/authority-evidence-v0.2/README.md),
  four optional fields, v0.1 still valid, no digest moved — so the census now
  returns 1 of 6 formats. No producer states a depth yet: 0 of 52 claim objects,
  unchanged. Whether witnesses will state one is still open; what refusing to
  count those who do not actually costs was measured and the policy was
  rejected. At full adoption it prevents about half of the hidden-source silent
  false settlements at no cost in correct settlements, but it loses every
  settlement where witnesses cannot attest, loses all protection one error class
  up as adoption rises, and settles 720 of 720 minority decisions against a true
  contrary claim. See [`AID-1`](../../results/aid1-v1/README.md). The policy is
  not usable as scoped, and its scope guard cannot hold because the use is
  caller-declared. The structural replacement was then measured and also
  rejected: returning the range the record supports removes that suppression
  entirely — the true claim survives 360 of 360 where a single count deleted all
  360 — but it is inert where a decoy recorded kinship collapses a witness at
  both ends, and it is blind to a backed witness with a shared origin, preventing
  0 of 360 against device-attested copies of one fabricator. Depth attestation
  earns depth and says nothing about shared origin. See
  [`AID-2`](../../results/aid2-v1/README.md). Two of the three disclosed defects
  are implementation errors rather than properties of the bounds idea, so the
  question is open rather than closed. A third experiment then ran the
  adversarial review's own world — written against the pre-repair policy, and
  open in a pull request 35 minutes before the first experiment was run, which
  the first two records did not use. It closes one question and sharpens the
  other: the repair demonstrably shuts the defect that world was built around,
  and the suppression is untouched and total, with the policy settling against a
  true contrary claim in 4,800 of 4,800 decisions at every adoption rate while
  every other arm abstains. See [`AID-3`](../../results/aid3-v1/README.md).
  Three worlds by three authors now agree: requiring attested depth cannot be
  made minority-safe by tuning, because discounting witnesses who cannot prove
  themselves is the mechanism and the harm at once. The two remaining roads were
  then tested together and both were rejected: a collapse-robust margin rule
  vindicates a true minority claim 0 times where the baseline vindicates it
  3,600, and a published exposure figure is a coin flip where powered and
  anti-correlated when pooled, so it predicts nothing. See
  [`AID-4`](../../results/aid4-v1/README.md). Every policy in the series tried to
  convert *we do not know* into a decision rule, and ignorance does not convert —
  it relocates, onto whoever cannot produce papers, whoever needed a decision, or
  a reader who now trusts a meaningless number. The series is closed in
  [`the attested-independence closure`](../../experiments/ATTESTED-INDEPENDENCE-SERIES-CLOSURE.md),
  which records the one constructive finding: the link that would break the
  theorem can only be written by whoever makes the copy. At series closure the
  field existed and was enforced but no production path emitted it. Root issuance
  now emits and preserves the link; transport/relay and cache/fan-out remain
  unwired, and deployment use is not established. See the
  [`emission census`](../EMISSION-CENSUS.md).
- Whether any weighted aggregator is safe. Weighted roots are closed by decision
  (`not_pursued`), not solved.
- Whether the development-set model lift survives a hidden, independently
  audited benchmark. That study is designed but not run.
- Whether the current reference runtime is production-ready infrastructure.

Accordingly, `flip_budget` is publishable as a count of root-set units, which is
what it provably is, and not as an operational security budget.

## Not claimed

Minority Prophet does not claim that it discovers truth, that agreement implies
independence, or that the approach has been validated as a general solution
outside synthetic worlds and public bibliographic metadata.
