# Vendor-neutral authority and evidence contract v0.2

v0.2 adds one thing to [v0.1](../authority-evidence-v0.1/README.md): somewhere
to say **how far the witness went**, and what that claim is backed by.

Everything else is byte-for-byte v0.1. No field was removed, renamed, retyped or
made required.

## Why

v0.1 separates five facts, and the fifth — evidence origin — could say only
whether a claim was an observation, a derivation, a copy or unknown, plus one
`independence_basis` value from `attested | declared | inferred | unknown`.

Three of those four values carry no information about whether anyone went and
looked. `attested` and `declared` differ only in *who vouched*; `inferred`
differs in *how far back toward the world the claim reached*. Ranking them on
one scale forces an exchange rate between vouching and looking, and there is
none: it puts a notarised piece of hearsay above an anonymous eyewitness. The
decomposition is in `aggregation/independence_axes.py`; the consequence for
counting is in `canon/ATTESTED-INDEPENDENCE.md`.

A census of this estate
([`experiments/aid1/OBSERVATIONAL-REPORT.md`](../../experiments/aid1/OBSERVATIONAL-REPORT.md))
found that no record anywhere stated a witness depth, and that **no published
format had anywhere to put one** — every format closed its origin object to
additions, so a producer who tried would emit an invalid envelope. The obstacle
was not that witnesses refuse to say how deep they went. It was that we never
gave them a field.

This is that field.

## What was added

Four optional properties on `receipt.evidence_origin`:

| Property | Values | What it records |
|---|---|---|
| `witness_depth` | `reality`, `method`, `replication`, `raw`, `analysis`, `text`, `unstated` | how far back toward the world this witness independently reached |
| `depth_basis` | `declared`, `procedural`, `artifact`, `device-attested` | what that claim is backed by |
| `witness_identity` | `anonymous`, `pseudonymous`, `named`, `verified`, `bonded` | whether the observer can be identified and held to the claim |
| `attestation` | `none`, `self`, `internal`, `independent`, `adversarial` | who vouched for the claim, and how disinterested they were |

The value strings are the estate's existing wire vocabulary, unchanged. They are
duplicated byte-for-byte in `aggregation/independence_axes.py` and
`provenance/root_registry.py`; a conformance test asserts the three copies are
identical, because a vocabulary that drifts silently is worse than one that was
never shared.

## Compatibility

- **Omit-if-absent.** A receipt stating none of the four is a v0.1 receipt with
  a different `schema_version`. Every field, ordering and digest is unchanged.
- **No digest or signature moves.** `action_digest` is computed over
  `request.action`, which v0.2 does not touch. Nothing needs re-signing.
- **v0.1 remains valid** and is still accepted by the checker. It is not
  deprecated; a producer with nothing to say about depth has no reason to move.
- **A v0.1 envelope may not carry the new fields.** Stating them under
  `schema_version: "0.1"` fails closed rather than being quietly accepted, so a
  v0.1 consumer never receives a field it does not know to read.

## Invariants v0.2 adds

- **Unknown values are refused, never coerced.** An unrecognised depth, basis,
  identity or attestation is an error. There is no default; silence is
  `unstated`, and `unstated` is a statement that nothing was stated.
- **A copy cannot claim to have reached the world.** `origin_type: "copied"`
  with a depth deeper than `text` is refused. Copying is re-reading at best.
- **Unknown independence cannot carry a testament.** `independence_basis:
  "unknown"` with any attestation other than `none` is refused, extending v0.1's
  "unknown independence stays unknown" to the new axis.

## What stating a depth does **not** buy

Nothing, by itself. A consumer grants a witness only what its **backing**
supports: a `reality` claim backed by nothing but assertion, from a source
nobody can find, is granted `text` — which is what a bare assertion has always
been worth (`aggregation/independence_axes.py::admissible_depth`).

So overclaiming is not punished here; it is simply ineffective. This contract
records what a party *claims* and what backs it. It does not adjudicate the
claim, and no field in it is evidence that the claim is true.

## What it still does not do

- It does not verify signatures, resolve a bond, or check that a named artifact
  exists. Those are the consumer's job, and `stake_reference` resolution is
  deliberately not modelled here.
- It does not make independence detectable. Ledger DR3 proves no rule reading a
  record can separate independent witnesses from copies of one hidden source,
  and adding a field a producer fills in does not touch that proof. What it
  changes is whether an honest witness *can* tell you, not whether a dishonest
  one can be caught.
- It is a draft interoperability contract, not a production authorization
  service, cryptographic verifier, patent opinion, or proof of independence.

## Files

- `schema.json` — structural JSON Schema for one request/receipt envelope.
- `conformance/authority_evidence.py` — stdlib canonicalization, digest, and
  semantic invariant checker. Accepts v0.1 and v0.2.
- `tests/test_authority_evidence_contract.py` — valid and adversarial
  conformance vectors expressed as executable tests.
