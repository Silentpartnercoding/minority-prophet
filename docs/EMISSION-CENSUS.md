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
names, 827 Python files.

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
on its own. Every class below was confirmed by hand.

## What was found, and what is now closed

### Declared and referenced by nothing at all — all closed

| Field | Declared in | Closed by |
|---|---|---|
| `result_digest` | `contracts/authority-evidence-v0.1`, `v0.2` | validated in `conformance/authority_evidence.py` |
| `external_attestation` | `provenance/claim-warrant.schema.json` | carried by `provenance/claim_warrant.py` |
| `componentId` | `experiments/hgd1/dependency-receipt.schema.json` | emitted by `experiments/hgd1/dependency_receipt.py` |

`external_attestation` was the one worth flagging. The attested-independence
series spent four rejected experiments on what attestation buys, and concluded
that only `DEVICE_ATTESTED` or a resolved bond reaches `REALITY`. The
claim-warrant schema had carried a field for exactly that the whole time, read
and written by nothing.

`componentId` turned out to be the sharpest case in the census, and not a
naming slip. The whole hgd1 schema is camelCase, and its siblings
(`originDigest`, `sharedWeightLower`) *are* referenced. What was missing was
larger than a field: `run_hgd1.py` builds components as
`{id, members, low, high}` and receipts as `{origin, claim, components, support}`
— an internal vocabulary sharing not one field name with the schema published
beside it. Meanwhile `research/knowledge-ledger/GATE-COVERAGE.json:48` cites
that schema as the artifact discharging KL-006/KL-008/ADV-005, "shared upstream
dependency is not representable in schema v0.1". The coverage claim rested on a
document shape nothing in the corpus emitted. That is the same defect as the
duplication link, one level up: not a field nothing writes, but an entire
published artifact shape nothing writes.

### Production reads it, only tests write it, and that is correct

`action_digest`, `algorithm`, `attempt_count`, `delegation_id`, `principal_id`,
`request_id`, `subject_id`, `schema_version`, `evidence_origin`, and now
`result_digest`.

These sit on evidence the repository **receives and verifies**, rather than
issues. `conformance/authority_evidence.py:66` iterates `request_id`,
`subject_id`, `principal_id`, `delegation_id` to validate an inbound authority
receipt. The repository is the verifier here, not the issuer, so having no
production producer is the expected shape and not a defect.

`stage`, `support` and `witness` are the same story for research records and
experiment receipts: written by the harnesses that produce them, read by the
integrity checkers that consume them.

Recording all of these anyway matters: the boundary between "nothing emits this
because an external caller does" and "nothing emits this because we forgot" is
exactly the distinction that hid the duplication link for the length of a whole
experimental series. The two look identical from inside a passing test suite.

### Production reads it, only tests write it, and that is a gap — all closed

`verify_determinism` (`provenance/claim-warrant.schema.json`) is consumed by
`provenance/warrant_recheck.py:88`, which documented a warrant "asserting a
`claim_type` and `verify_determinism` this module has no" standing to decide.
Three test files supplied it; no production path did. The schema says two things
about the field — "DERIVED, never author-supplied" and "consumers recompute
rather than trust it" — and both were unimplemented. `provenance/claim_warrant.py`
is the producer side `warrant_recheck` was deferring to: it derives the value
from `claim_type`, declines to accept it as a parameter, and recomputes rather
than trusts it on the way back in.

`minimum_winning_roots` and `candidate_cuts`
(`provenance/decision-context.schema.json`) were read by three and two production
call sites and written only by the DRI experiment harnesses. No production path
assembled a decision context; every decision this corpus has ever scored was
scored on a context built by an experiment.
`provenance/decision_context_document.py` reads the declared document form and
fails closed on anything it cannot read as written.

## The pin lesson, which cost eleven failing tests

The decision-context loader was first written as a function added directly to
`provenance/decision_relative.py`. That broke eleven tests across nine
preregistered experiments — DRI-3, 4, 5, 6, 8, 9, 10, 11 and AID-2.

`decision_relative.py` is a **pinned frozen input**. Ten runners record its
SHA-256 in a `PINNED` map and `verify_pins()` refuses to run if the digest has
moved. Those digests are the evidence that each experiment ran against exactly
that code. A purely additive function still changes the file's hash, and
therefore still invalidates all nine proofs.

The tempting repair — re-derive the pins so the suite goes green — would have
been far worse than the failure that suggested it. It would have made the record
assert that experiments frozen weeks ago ran against code written tonight. The
pins are not a build inconvenience to be routed around; they are the only reason
a frozen result means anything.

So the rule this census ends on: **closing an emission gap must never modify a
pinned file.** The loader moved to its own module and imports `DecisionContext`
unchanged. `conformance/authority_evidence.py` was checked against every `PINNED`
map before being edited, and appears in none. The hgd1 serialiser is a sibling
file precisely because `run_hgd1.py` is a frozen runner; converting its output
after the fact changes no measured result.

## What was fixed

`origin_type` and `parent_roots` are emitted at issuance, which is the seam the
series closure identified — the copier is the one process that holds the source
and the destination at the same instant, and therefore knows without inference
that the second is the first. `provenance/root_registry.py` carries the link on
`RootRequest`, covers it in `canonical_bytes` under omit-if-absent (so signatures
made against the previous version still verify), refuses the incoherent
combinations in `_validate_request`, and resolves a copy to its parent's identity
in `root_identity` rather than minting a fresh root. That last one makes the
contract's rule true by construction at issuance instead of merely checked
afterwards at the boundary.

The remaining five fields are closed as described above, by four modules and
four test files. The census now reports **no field declared in any schema and
referenced by no Python file**, and every field it still lists is inbound
evidence the repository verifies rather than issues.

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

Nor does closing a gap mean the field is now load-bearing in production. A
producer exists and is tested; whether any deployment calls it is a separate
question the census cannot answer, and the honest reading of these closures is
that the corpus can now demonstrate its own plumbing, not that water is running
through it.
