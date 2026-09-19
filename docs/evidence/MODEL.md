# Canonical evidence model

<!-- mp-status: {"id":"evidence-model","class":"current","asOf":"2026-09-19","replacement":null,"immutable":false,"theorems":["T2","DR1","DR2","DR3","U1"],"researchRecords":["AID-1-V1","AID-2-V1","AID-3-V1","AID-4-V1"],"describesMechanisms":["recorded_graph_roots","bounded_root_issuance","proximate_mis_count","recorded_dependence_robust_settlement","attested_independence_point_policy","attested_independence_bounds_policy","collapse_robust_margin_policy","priced_exposure_policy"],"recommendedMechanisms":["recorded_graph_roots","bounded_root_issuance","recorded_dependence_robust_settlement"]} -->

This is the reader view of [`canon/model-registry.json`](../../canon/model-registry.json).
The registry routes each term and mechanism to existing theorem or research
authority; this page does not promote a result.

## The three nouns that must stay separate

- A **recorded root** is a claim record with no usable ancestry in the named
  record. It describes the record, not the world.
- An **issued root identity** is authenticated and quota-bounded, and can retain
  declared parent links. It does not prove truth, issuer honesty, deployment
  adoption, or a distinct real-world observation.
- An **effective witness** is one unit in an exact maximum independent set
  relative to a named possible-dependence graph and error class. It is not proof
  of independent observation.

A missing edge means “not recorded by this basis.” It never means that shared
origin is absent.

## What the current model can say

When a copy link is recorded, the compiled copy-invariance result applies and
the copy adds no recorded-root support. When positive dependence indications
define a possible-dependence graph, the current implementation can enumerate
reachable settlements and settle only if every grouping admitted by that graph
agrees. Counts are exact or refused.

These results are conditional on the named record, proposition, claim shape,
error class, and integrity assumptions. They do not discover omitted dependence,
prove truth, establish complete coverage, or grant authority to act.

## What failed

AID-1 through AID-4 rejected every downstream counting-time policy tested after
dependence was omitted: attested-depth deflation, its bounds repair as tested,
collapse-robust margin, and priced exposure. The bounds experiment repaired one
suppression case; it did not create knowledge of shared origin. The broader rule
to preserve and report uncertainty remains, but none of those four mechanisms
is a validated default.

## The constructive seam and its limit

The copier is the point that holds source and destination together and can write
the relationship without inference. Root issuance now emits and enforces
`origin_type` and `parent_roots`. That closes one seam. The repository search
recorded in [`docs/EMISSION-CENSUS.md`](../EMISSION-CENSUS.md) found
transport/relay and cache/fan-out still unwired, and found no evidence that a
deployment uses the repaired issuer path.

Nothing here defeats DR3: an external copier that omits or falsifies the link
returns the record to the indistinguishable case.

## Authority map

- Terms, dispositions, and navigation status:
  [`canon/model-registry.json`](../../canon/model-registry.json)
- Formal status: [`formal/THEOREM-LEDGER.json`](../../formal/THEOREM-LEDGER.json)
- Formal boundary: [`formal/CLAIM-SCOPE.md`](../../formal/CLAIM-SCOPE.md)
- Research lifecycle: [`research/records/`](../../research/records/)
- Canonical result index: [`CANONICAL-RECORDS.md`](../../CANONICAL-RECORDS.md)
- Current plain-language status: [`STATUS.md`](STATUS.md)
