# Emission census — which declared fields does nothing actually emit?

A field can be declared in a schema, enforced by a checker, and read by a
consumer, and still be written by nothing outside a fixture. That gap is
invisible to every test in this repository, because a test that supplies the
field passes whether or not any real producer ever would.

The attested-independence series ended on exactly that shape. `origin_type` and
`parent_roots` have been in the vendor-neutral contract since v0.1;
`conformance/authority_evidence.py` has enforced since then that a copy may not
mint a fresh root; the knowledge ledger honours the link independently. And no
production path wrote either field. The one mechanism that could have broken the
identical-record theorem had a socket and no wire.

This census generalises the question across the corpus:
`scripts/check_emission_census.py`, read-only, 13 schemas, 123 declared field
names, 821 Python files.

## What the census can and cannot say

It is grep-shaped evidence, and it fails in one direction: it invents gaps
rather than hiding them. The first run demonstrated both of its error modes.

It over-reported generic names — `action`, `model` and `question` were listed as
emission gaps purely because those words are common English that appears
throughout unrelated code. Those are now declared out in `TOO_GENERIC` rather
than silently mis-measured.

It under-detected producers. `recheck_reference` was reported as written by
nothing, while `provenance/warrant_recheck.py:101` writes it as
`updated["recheck_reference"] = reference`. The write pattern did not match
subscript assignment. Fixed, and the field no longer appears.

So every line of output is a **candidate to confirm by reading**, never a finding
on its own. Each class below was confirmed by hand.

## Class 1 — declared, and referenced by nothing at all

| Field | Declared in |
|---|---|
| `result_digest` | `contracts/authority-evidence-v0.1`, `v0.2` |
| `external_attestation` | `provenance/claim-warrant.schema.json` |
| `componentId` | `experiments/hgd1/dependency-receipt.schema.json` |

Zero references in any Python file — not production, not research, not tests.
These are declarations no code has ever touched in either direction.

`external_attestation` is the one worth flagging. The attested-independence
series spent four rejected experiments on the question of what attestation buys,
and concluded that only `DEVICE_ATTESTED` or a resolved bond reaches `REALITY`.
The claim-warrant schema has carried a field for exactly that since before the
series began, and nothing reads or writes it. `componentId` is also the only
camelCase field in the corpus, which suggests it was never wired because it was
never spelled the way anything looks for it.

## Class 2 — production reads it, only tests write it, and that is correct

`action_digest`, `algorithm`, `attempt_count`, `delegation_id`, `principal_id`,
`request_id`, `subject_id`, `schema_version`, `evidence_origin`, `source_digest`.

These sit on evidence the repository **receives and verifies**, rather than
issues. `conformance/authority_evidence.py:66` iterates `request_id`,
`subject_id`, `principal_id`, `delegation_id` to validate an inbound authority
receipt; `provenance/graph.py:114` validates an inbound warrant's
`source_digest`. The repository is the verifier here, not the issuer, so having
no production producer is the expected shape and not a defect.

Recording them anyway matters: the boundary between "nothing emits this because
an external caller does" and "nothing emits this because we forgot" is exactly
the distinction that hid the duplication link for the length of a whole
experimental series. The two look identical from inside a passing test suite.

## Class 3 — production reads it, only tests write it, and that is a gap

Two survive the reading.

`verify_determinism` (`provenance/claim-warrant.schema.json`) is consumed by
`provenance/warrant_recheck.py:88`, which documents a warrant "asserting a
`claim_type` and `verify_determinism` this module has no" means of producing.
Three test files supply it. No production path does.

`minimum_winning_roots` and `candidate_cuts`
(`provenance/decision-context.schema.json`) are read by three and two production
call sites respectively, and written only by the DRI experiment harnesses —
`experiments/dri1/run_confirmatory.py`, `dri2/world.py`, `dri3/world.py`,
`dri8/arms.py`, `dri9/rule.py`. No production path assembles a decision context.
Every decision this corpus has ever scored was scored on a context built by an
experiment.

That is not a bug in the sense that something computes a wrong answer. It is the
same structural fact the series closure named: the corpus cannot demonstrate its
own plumbing, so a defect in the plumbing is undetectable from within it.

## What was fixed

`origin_type` and `parent_roots` are now emitted at issuance, which is the seam
the series closure identified — the copier is the one process that holds the
source and the destination at the same instant, and therefore knows without
inference that the second is the first.

`provenance/root_registry.py` now carries the link on `RootRequest`, covers it
in `canonical_bytes` under omit-if-absent (so signatures made against the
previous version still verify), refuses the incoherent combinations in
`_validate_request` — a copy naming no parent, a parent named with no
relationship, an origin outside the contract's vocabulary — and, in
`root_identity`, resolves a copy to its parent's identity rather than a fresh
root. That last one makes the contract's rule true by construction at issuance
instead of merely checked afterwards at the boundary.

`tests/test_root_duplication_link.py` covers all of it, including the
over-merge direction: two genuinely separate observations that declare
themselves as such keep distinct identities. A duplication check that collapsed
real witnesses would trade one failure for a worse one.

Both fields have since dropped off the census gap list, which is what the census
is for.

## What this does not claim

This does not claim the theorem is defeated. `DR3.no_record_rule_is_immune`
stands exactly as proved: where shared origin is unrecorded, no reading rule can
separate five witnesses from one witness and four echoes. The response is not a
better reading rule. It is refusing to let the record be unrecorded at the one
moment the fact is free to obtain.

It also does not claim the seam is closed. Root issuance is one of the three
seams the closure named. Transport/relay and cache/fan-out remain unwired, and
nothing here forces a copier outside this repository to tell the truth — a
copier that declines to state `origin_type` is back in the theorem's world. What
changed is that a copier that wants to be honest now has somewhere to say so,
and one that lies has to do it under a signature.
