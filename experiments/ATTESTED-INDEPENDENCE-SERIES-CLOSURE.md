# Attested-independence series closure

<!-- mp-status: {"id":"aid-series-closure","class":"historical_snapshot","asOf":"2026-09-18","replacement":"emission-census","immutable":false,"theorems":["DR3"],"researchRecords":["AID-1-OBS","AID-1-V1","AID-2-V1","AID-3-V1","AID-4-V1"],"describesMechanisms":["attested_independence_point_policy","attested_independence_bounds_policy","collapse_robust_margin_policy","priced_exposure_policy","bounded_root_issuance"],"recommendedMechanisms":["bounded_root_issuance","recorded_dependence_robust_settlement"]} -->

**Later implementation state:** this closure correctly identified three copy
seams and recorded that none emitted the origin link at closure time. Root
issuance now does. Transport/relay and cache/fan-out remain unwired, and no
deployment use is established. See [`EMISSION-CENSUS.md`](../docs/EMISSION-CENSUS.md).

**Status:** AID-1 through AID-4 are complete. The series closes on an answer, and
the answer is negative for every policy it proposed.

It also closes with one constructive finding that is not a policy, and that is
the part worth carrying forward.

## The question the series asked

The decision-relative independence series closed on a theorem: no rule reading
the record can separate independent evidence from dependence the record does not
carry. This series asked the obvious follow-up. **If you cannot detect it, what
is the right thing to do?**

Three answers were proposed and all three were tested to destruction.

## Result chain

1. **Nobody could state it, and no format had a field for it.** AID-1-OBS, an
   observational census: of 52 claim objects across four corpora, none stated a
   witness depth, a backing, or an identity; and of five formats in which
   evidence crosses a boundary, none had anywhere to put one. The obstacle was
   not that witnesses refuse to say how deep they went. We had never given them
   a field. The vendor-neutral contract gained one
   (`contracts/authority-evidence-v0.2`), additive and omit-if-absent.
2. **Requiring attested depth destroys true minority claims.** AID-1, on a world
   by a subagent of the policy's author: rejected, 61 of 111. At full adoption it
   prevented 177 of 350 hidden-source errors at no cost — and settled against a
   true contrary claim in 720 of 720 decisions.
3. **The repair fixed the defect and not the harm.** AID-2, rejected 74 of 120.
   Returning a *range* rather than a count removed the original suppression
   entirely, and was inert against a decoy recorded kinship, and blind to a
   backed witness with a shared origin.
4. **The reviewer's own world made it total.** AID-3, rejected 17 of 23, on the
   adversarial review's world — which had been open, frozen and green in a pull
   request 35 minutes before AID-1 ran, and which the policy's author had not
   used. The repair demonstrably shut the hole the review aimed at. The
   suppression was untouched and **rate-independent**: 4,800 of 4,800.
5. **Both remaining roads failed.** AID-4, both policies rejected. The margin
   rule never settles *against* the minority and never settles *for* them — the
   baseline vindicates a true minority claim 3,600 times, the policy zero. The
   priced-exposure figure is a coin flip where powered (AUC 0.500–0.513 against a
   0.70 floor) and anti-correlated when pooled (0.31, 0.25, 0.19).

## The defensible conclusion

**Discounting witnesses who cannot prove themselves is the mechanism and the harm
at once.** Three worlds by three authors agree, and no repair separated them,
because they are not separable.

More generally, and this is what the four experiments actually demonstrate:
every policy tried to convert *we do not know* into a decision rule — discount
them, abstain, or publish a number. **Ignorance does not convert. It relocates.**
Discounting relocates it onto whoever cannot produce papers. Abstaining
relocates it onto whoever needed a decision. Pricing relocates it onto a reader
who now believes a number that predicts nothing.

## The constructive finding: the seam is the copier

The theorem is not a wall around reality. It is a wall around **reading**. The
record of five independent witnesses and the record of one witness plus four
echoes are identical *only because the link was never written down*. Write it
down and the two records differ, and the proved robustness rule — which is sound,
cheap, and untouched by this series — applies again.

The series spent four experiments asking the **witness** to supply that
distinction, after the fact. That cannot work, and the reason is not adoption:

- A witness can attest to **the path it took**. That is a fact about itself.
- A witness cannot attest to **what it shares with another witness**. Two
  reporters may honestly believe they have no common source while drinking from
  one well. AID-2 measured this directly: the good-faith-but-mistaken variant
  prevented nothing.
- And depth does not substitute. AID-2 and AID-4 both measured backed copies of
  one hidden parent: **a credential earns depth and says nothing about shared
  origin.**

The party that always knows is **whoever made the copy.** At the moment of
duplication, the copier holds the source and the destination at once. That is the
only point where the link is free to record, and it is the seam this programme
should have been working on from the start.

### The field already exists, and is already enforced

This is not a proposal for new machinery. `evidence_origin` in the vendor-neutral
contract already carries `origin_type` — `observation | derived | copied |
unknown` — and `parent_roots`. `conformance/authority_evidence.py` enforces it:
a `copied` or `derived` origin must carry non-empty parent roots, and its
`root_id` must appear among them, so **a copy cannot mint a fresh root**. The
knowledge ledger honours a declared link independently, walking `derivedFrom` to
an original and treating a document that declares no ancestry as *unattributable*
rather than as a root.

What was missing at series closure was emission. At that revision,
`origin_type`, `derived_from` and `parent_roots` appeared nowhere in
`provenance/` or `aggregation/`, and the only producing call sites in the estate
were inside one experiment's constructed scenario. The later root-issuance
repair closes that one seam without changing the closure's result; the other two
seams below remain open.

### The three seams where duplication happens

1. **Root issuance.** When an issuer mints a root for evidence it *received*
   rather than observed, that is a copy. `provenance/root_registry.py` already
   digests the evidence; a re-issue of a digest it has seen is exactly the moment
   to require `parent_roots`.
2. **Transport and relay.** When a claim crosses a boundary and is re-emitted
   under a different identity, same content, new issuer. This is the classic
   laundering point, and it is the seam that carries **no origin field at all**
   today.
3. **Cache, memoisation and fan-out.** Anything that serves a stored answer
   instead of recomputing it, and anything that hands one upstream context to
   many agents, is duplicating. Each consumer looks like a fresh witness and none
   of them is.

Stamping the link at any of these is ordinary engineering. It requires no
detector, no attestation ceremony, and nothing a witness has to know about
itself.

## Why the series stops

Not because a proposal remains untested. Because all three that existed were
tested and failed, and the frozen kill criterion for the last of them said
plainly that both failing leaves no remaining constructive proposal **of that
kind** — a rule applied at counting time, downstream of a record that omits what
it needs.

The remaining work is not a reading rule and not research. It is emission at the
three seams above, and intervention where the stakes justify paying for it
(DRI-8 measured that at 16–468 probes per error prevented).

## What this series established that is not negative

- A field for witness depth now exists in the vendor-neutral contract where none
  did, additive and backward-compatible.
- The copy rule is enforced where the field appears, and the enforcement is real
  rather than aspirational.
- **Author separation is not ceremony.** Two of AID-4's five criteria were blind
  in exactly the places that flattered the author's own proposals: the
  anti-suppression check could not fail by construction, and the cost check
  scoped itself out where cost was total. Neither was caught by the author. Both
  were caught by handing the world to someone else — who disclosed them before
  reading any data and declined to repair them. That is the methodological result
  of the series, and it is worth as much as any of the measurements.

## Canonical records

- `results/aid1-v1/canonical-manifest.json` — rejected
- `results/aid2-v1/canonical-manifest.json` — rejected
- `results/aid3-v1/canonical-manifest.json` — rejected
- `results/aid4-v1/canonical-manifest.json` — both policies rejected

Observational, not canonical: `experiments/aid1/OBSERVATIONAL-REPORT.md`.
