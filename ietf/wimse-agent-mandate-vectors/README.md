# Test vectors for draft-hulea-wimse-agent-mandate-00

Signed vectors for the Appendix A story, plus three negative cases about
authority. Each negative case makes one change from the baseline.

| Case | Change from baseline | Expected outcome | authority | errors |
|---|---|---|---|---|
| 00-baseline | none | valid | established | none |
| 01-root-broader-than-powers | root `max` on `/instructedAmount/amount` is 200000.00 (assertion powers allow 100000.00) | invalid | refuted | authority_insufficient |
| 02-authority-not-presented | the Authority Assertion is left out of `mandate_evidence`; the root still references it | invalid | refuted | authority_missing |
| 03-authority-expired | Authority Assertion `exp` is 1792886400, before T minus `max_clock_skew` | invalid | refuted | authority_insufficient, expired |

In cases 01 and 03 the change to the Authority Assertion or root changes its
digest, so the downstream Artifact References and signatures change too. In
case 02 every presented artifact is byte-identical to the baseline.

## Layout

```
keys/                 one Ed25519 JWK per role, with d, and thumbprints.json (RFC 7638)
profile/profile.json  the Validation Profile, exact bytes that are digested
profile/profile-ref.json  {uri, dig}
trust-anchors.json    the Trust Anchor Set the Validator is configured with
cases/<case>/
  *.jws                       compact JWS of each artifact
  authorization_details.json  exact request bytes
  presentation.json           subject_token, actor_token, mandate_evidence, authorization_details
  inputs.json                 time, RP identifier, profile reference, PoP outcome
  decoded.json                headers and payloads, for reading only
  expected-result.json        the Validation Result (Section 9.6)
generate.py           regenerates every file above
check.py              independent checker
```

## Keys

| kid | role | signs |
|---|---|---|
| as-1 | authority_source (https://register.example) | Authority Assertion |
| mi-1 | mandate_issuer (https://mandates.treasury.example) | root mandate |
| op-1 | operator (https://treasury.example) | WIT |
| ai-treasury-1 | agent instance payments-7 | sub-mandate, bound by root `cnf.jkt` |
| ai-reconcile-1 | agent instance reconcile-2 | key in WIT `cnf.jwk`, bound by sub-mandate `cnf.jkt` |

Each private key is the 32-byte seed
`SHA-256("draft-hulea-wimse-agent-mandate-00 test vector key " || kid)`.
These keys are published for testing. Never use them for anything else.

Anchor-signed artifacts carry `kid` in the JOSE header. The sub-mandate
carries the ai-treasury-1 public key in `jwk`.

## Profile

URI `https://bank.example/profiles/agents/3`. The digest is the base64url
SHA-256 of the bytes of `profile/profile.json`:
`piDpzEhpQ73OrTFkmm162vb6Z-oFNfJpBTp2AzkP3Cg`.
`max_clock_skew` is 60. `status_required` is empty, so no case uses status
and there is no status_issuer key.

## Fixed values

T = 1792972800. RP = `https://bank.example`. PoP outcome `ok` with nonce
`vector-nonce-0001`. All other times are in `decoded.json`.

## Regenerate and check

```
python3 -m venv venv
venv/bin/pip install -r requirements.txt
venv/bin/python generate.py          # writes into this directory
venv/bin/python generate.py /tmp/a   # or anywhere else
diff -r /tmp/a .                     # expect no differences apart from the scripts
venv/bin/python check.py             # verifies every case
```

Ed25519 signatures are deterministic, so two runs produce identical bytes.

`check.py` imports nothing from `generate.py`. It verifies every signature
against `trust-anchors.json` and the key binding chain, runs Section 9.3
steps 1 to 12 as far as these cases need, builds a result, and compares it
with `expected-result.json` as JSON values under Section 4.6 (no
canonicalization; numbers compare by their text, and `true` never equals 1).

## Ambiguities found

1. Sections 9.4 and 9.6: the authority_* codes do not say which artifact, if
   any, they carry. These vectors attach the root mandate's reference.
2. Sections 9.6 and 11: claim `role` values are not enumerated, and the
   sub-delegated mandate is signed by an agent instance key rather than an
   anchor role. These vectors use `agent_instance` for it.
3. Sections 8 and 8.1: the Validation Profile has no defined JSON shape (the
   `types` and `frameworks` layout, Type Profile member names, `max_lifetime`
   keys, `status_required` item names). The shape here is a guess.
4. Section 8: which bytes the profile digest covers. These vectors digest the
   file bytes as published.
5. Section 9.1 item 5: the Trust Anchor Set has no defined format.
   `trust-anchors.json` is one possible layout.
6. Sections 4.3 and 9.6: whether Artifact References in the result carry
   `iss` and `jti` hints. Under Section 4.6 identity this changes whether two
   results match. These vectors use `dig` only, as Appendix A does.
7. Section 6.1 and Appendix A: no WIT or operator identifier is given. These
   vectors use `https://treasury.example` and `jti` `wit-reconcile-2-0001`.
8. Sections 9.2 and 9.3: a required assertion that is absent has no code
   other than authority_missing (case 02).
9. Section 9.3: steps run in full after a failure, so `alternatives` is
   listed even when the outcome is invalid. These vectors list it.
10. Section 9.6: an authenticated Authority Assertion that does not support
    the root has its claims left out (case 01), so the RP cannot see the
    powers that caused authority_insufficient.
11. Section 4.6: the rule that numbers are identical only when their text is
    identical is hard to apply to a result that a Validator re-serializes
    (for example `time`).
12. Section 9.1 item 8: the Validator takes the PoP outcome as an input, so
    no PoP proof or HTTP signature is included.
13. Appendix B: the framework_mismatch and `_sd` rows also imply
    authority_insufficient, the same pattern as case 03.
