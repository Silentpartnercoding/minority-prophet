# Evidence and claim map

<!-- mp-status: {"id":"evidence-index","class":"current","asOf":"2026-09-19","replacement":null,"immutable":false,"theorems":["DR1","DR2","DR3","U1"],"researchRecords":[],"describesMechanisms":["recorded_graph_roots","bounded_root_issuance","recorded_dependence_robust_settlement"],"recommendedMechanisms":["recorded_graph_roots","bounded_root_issuance","recorded_dependence_robust_settlement"]} -->

Use this section to answer two different questions:

1. What does Minority Prophet currently claim?
2. Which evidence package supports that claim?

## Fastest audit path

1. Read [`MODEL.md`](MODEL.md) for the canonical objects, mechanisms, and
   non-equivalences.
2. Read [`STATUS.md`](STATUS.md) for the plain-language boundary between proved,
   measured, experimental, and unestablished work.
3. Read [`PUBLIC-CLAIMS.md`](../../PUBLIC-CLAIMS.md) for the shortest supported
   public claim set.
4. Use [`EVIDENCE-ALIGNMENT.md`](../../EVIDENCE-ALIGNMENT.md) to follow a claim
   to its exact record.
5. Confirm status and promotion rules in
   [`CANONICAL-RECORDS.md`](../../CANONICAL-RECORDS.md).
6. Inspect the content-bound record in [`research/records/`](../../research/records/)
   and the referenced material in [`results/`](../../results/).

## Evidence surfaces

| Surface | Role | Authority |
|---|---|---|
| [`MODEL.md`](MODEL.md) | Canonical evidence objects and mechanism dispositions | Derived from the machine registry |
| [`canon/model-registry.json`](../../canon/model-registry.json) | Machine-readable terms, mechanisms, and navigation status | Controls model vocabulary and disposition |
| [`PUBLIC-CLAIMS.md`](../../PUBLIC-CLAIMS.md) | Concise public summary | Derived from the ledgers below |
| [`CLAIMS.md`](../../CLAIMS.md) | Detailed and adversarial claim review | Explanatory audit surface |
| [`formal/CLAIM-SCOPE.md`](../../formal/CLAIM-SCOPE.md) | Exact scope of proved statements | Controls formal wording |
| [`formal/THEOREM-LEDGER.json`](../../formal/THEOREM-LEDGER.json) | Machine-readable theorem status | Controls formal status |
| [`CANONICAL-RECORDS.md`](../../CANONICAL-RECORDS.md) | Canonical/imported record registry | Current record-status authority |
| [`EVIDENCE-ALIGNMENT.md`](../../EVIDENCE-ALIGNMENT.md) | Claim-to-record links and corrections | Current alignment authority |
| [`research/records/`](../../research/records/) | Immutable per-record lifecycle metadata | Machine-readable source |
| [`results/`](../../results/) | Result packages, manifests, and adverse outcomes | Evidence artifacts; status varies |
| [`papers/`](../../papers/) | Manuscripts and preserved versions | Narrative; follow the stable current-paper pointer |

## What “preserved” means

Canonical and imported records are not edited in place. Corrections receive a
new identifier and record. Null, rejected, incomplete, and adverse outcomes are
part of the evidence base and remain navigable even when a later result becomes
the current reference.

Generated output is not automatically canonical. A result becomes authoritative
only through the research lifecycle described in
[`research/integrity/`](../../research/integrity/) and
[`research/records/README.md`](../../research/records/README.md).

## What the evidence does not establish

The repository does not establish that:

- recorded roots always correspond to real independent observations;
- identity difference proves causal independence;
- missing ancestry can be reliably reconstructed in general;
- agreement, confidence, or agent count determines truth; or
- an evidence assessment authorizes a real-world action.

Those are research boundaries, not small-print disclaimers. Any new public page
or paper must preserve them.
