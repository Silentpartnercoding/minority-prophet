#!/usr/bin/env python3
"""Regenerate the signed vectors for draft-hulea-wimse-agent-mandate-00.

Every output byte is a function of this file alone: keys come from fixed seed
labels, Ed25519 signing is deterministic, JSON is written with a fixed member
order and fixed whitespace, and all times are fixed epoch values.

Usage: python generate.py [output_dir]   (default: the directory of this file)
"""

import base64
import hashlib
import json
import os
import sys

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

DRAFT = "draft-hulea-wimse-agent-mandate-00"
SEED_PREFIX = "draft-hulea-wimse-agent-mandate-00 test vector key "
KEY_NAMES = ["as-1", "mi-1", "op-1", "ai-treasury-1", "ai-reconcile-1"]

# Identifiers from Appendix A.
TF = "https://tf.example/finance"
REGISTER = "https://register.example"
MANDATE_ISSUER = "https://mandates.treasury.example"
TREASURY = "spiffe://treasury.example/agents/payments-7"
RECONCILE = "spiffe://treasury.example/agents/reconcile-2"
RP = "https://bank.example"
PROFILE_URI = "https://bank.example/profiles/agents/3"
PRINCIPAL = {"id": "J40/0000/2020", "scheme": "urn:example:reg"}
DELEGATOR = {"id": "p-41f9", "scheme": "urn:example:pairwise"}
# Not named in Appendix A; chosen for these vectors (see README).
OPERATOR = "https://treasury.example"

T_BASELINE = 1792972800  # Appendix A Validation Result time
POP_NONCE = "vector-nonce-0001"


def b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def compact(obj) -> bytes:
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def pretty(obj) -> bytes:
    return (json.dumps(obj, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def sha256_b64u(data: bytes) -> str:
    return b64u(hashlib.sha256(data).digest())


# ---------------------------------------------------------------- keys

def derive_key(name: str):
    seed = hashlib.sha256((SEED_PREFIX + name).encode("utf-8")).digest()
    priv = Ed25519PrivateKey.from_private_bytes(seed)
    x = priv.public_key().public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw
    )
    return priv, seed, x


def public_jwk(x: bytes) -> dict:
    return {"kty": "OKP", "crv": "Ed25519", "x": b64u(x)}


def thumbprint(jwk: dict) -> str:
    # RFC 7638 with RFC 8037 required members for OKP: crv, kty, x.
    canon = compact({"crv": jwk["crv"], "kty": jwk["kty"], "x": jwk["x"]})
    return sha256_b64u(canon)


KEYS = {}
for _n in KEY_NAMES:
    _priv, _seed, _x = derive_key(_n)
    KEYS[_n] = {"priv": _priv, "seed": _seed, "x": _x, "pub": public_jwk(_x)}


def jkt(name: str) -> str:
    return thumbprint(KEYS[name]["pub"])


def sign(header: dict, payload: dict, key_name: str) -> str:
    signing_input = b64u(compact(header)) + "." + b64u(compact(payload))
    sig = KEYS[key_name]["priv"].sign(signing_input.encode("ascii"))
    return signing_input + "." + b64u(sig)


def ref(jws: str, **hints) -> dict:
    r = {"dig": sha256_b64u(jws.encode("ascii"))}
    r.update(hints)
    return r


# ---------------------------------------------------------------- profile

PAYMENT_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "required": ["type", "actions", "locations", "instructedAmount", "creditorAccount"],
    "properties": {
        "type": {"const": "payment_initiation"},
        "actions": {"type": "array", "items": {"type": "string"}},
        "locations": {"type": "array", "items": {"type": "string"}},
        "instructedAmount": {
            "type": "object",
            "required": ["currency", "amount"],
            "properties": {
                "currency": {"type": "string", "pattern": "^[A-Z]{3}$"},
                "amount": {"type": "string", "pattern": "^(0|[1-9][0-9]*)(\\.[0-9]+)?$"},
            },
            "additionalProperties": False,
        },
        "creditorAccount": {
            "type": "object",
            "required": ["iban"],
            "properties": {"iban": {"type": "string"}},
            "additionalProperties": False,
        },
        "remittanceInformation": {"type": "string"},
    },
}

PROFILE = {
    "max_clock_skew": 60,
    "max_pop_window": 60,
    "max_token_lifetime": 300,
    "max_status_age": 3600,
    "max_chain_length": 3,
    "predicates": ["eq", "in", "max", "min", "window", "sum_max", "cosign_above"],
    "types": {
        "payment_initiation": {
            "schema": PAYMENT_SCHEMA,
            "admitted_members": ["instructedAmount", "creditorAccount", "remittanceInformation"],
            "member_meanings": {
                "instructedAmount": "Currency and decimal amount of the payment to be initiated.",
                "creditorAccount": "Account of the payee, identified by IBAN.",
                "remittanceInformation": "Free text passed to the payee; it has no effect on the amount or the payee.",
            },
        }
    },
    "eat_profiles": [],
    "frameworks": {
        TF: {
            "algs": ["EdDSA"],
            "party_schemes": ["urn:example:pairwise", "urn:example:reg", "urn:example:workload"],
            "max_lifetime": {
                "mandate+jwt": 2592000,
                "authority+jwt": 31536000,
                "wit+jwt": 86400,
                "eat+jwt": 3600,
                "agent-exposure+jwt": 300,
                "sum_max_period": 2592000,
            },
            "status_required": [],
            "authority_frameworks": [TF],
        }
    },
}

TRUST_ANCHORS = {
    "mandate_issuer": [{"name": "mi-1", "iss": MANDATE_ISSUER, "keys": ["mi-1"], "frameworks": [TF]}],
    "authority_source": [{"name": "as-1", "iss": REGISTER, "keys": ["as-1"], "frameworks": [TF]}],
    "operator": [{"name": "op-1", "iss": OPERATOR, "keys": ["op-1"], "frameworks": [TF]}],
    "verifier": [],
    "exposure_observer": [],
    "status_issuer": [],
}

# ---------------------------------------------------------------- Appendix A story


def authority_payload(exp=1824336000):
    return {
        "iss": REGISTER,
        "jti": "aa-5c1e",
        "iat": 1792800000,
        "exp": exp,
        "principal": dict(PRINCIPAL),
        "delegator": dict(DELEGATOR),
        "powers": [{
            "type": "payment_initiation",
            "constraints": [
                {"pred": "eq", "ptr": "/instructedAmount/currency", "value": "EUR"},
                {"pred": "max", "ptr": "/instructedAmount/amount", "value": "100000.00"},
            ],
        }],
        "max_depth": 1,
        "tf": TF,
    }


def root_payload(aa_jws, root_max="20000.00"):
    return {
        "iss": MANDATE_ISSUER,
        "sub": TREASURY,
        "jti": "ma-90b2",
        "iat": 1792886400,
        "nbf": 1792886400,
        "exp": 1795478400,
        "cnf": {"jkt": jkt("ai-treasury-1")},
        "principal": dict(PRINCIPAL),
        "delegator": dict(DELEGATOR),
        "authority": [ref(aa_jws, iss=REGISTER)],
        "perms": [{
            "type": "payment_initiation",
            "actions": ["initiate"],
            "locations": ["https://bank.example/payments"],
            "constraints": [
                {"pred": "eq", "ptr": "/instructedAmount/currency", "value": "EUR"},
                {"pred": "max", "ptr": "/instructedAmount/amount", "value": root_max},
                {"pred": "in", "ptr": "/creditorAccount/iban",
                 "value": ["RO49AAAA1B31007593840000", "DE89370400440532013000"]},
                {"pred": "sum_max", "ptr": "/instructedAmount/amount",
                 "value": "50000.00", "period": 2592000, "budget": "monthly-out"},
                {"pred": "cosign_above", "ptr": "/instructedAmount/amount", "value": "10000.00"},
            ],
        }],
        "max_depth": 1,
        "aud": [RP],
        "tf": TF,
        "loa": "substantial",
    }


def sub_payload(root_jws):
    return {
        "iss": TREASURY,
        "sub": RECONCILE,
        "jti": "ma-17c4",
        "iat": 1792890000,
        "nbf": 1792890000,
        "exp": 1792976400,
        "cnf": {"jkt": jkt("ai-reconcile-1")},
        "principal": dict(PRINCIPAL),
        "delegator": {"id": TREASURY, "scheme": "urn:example:workload"},
        "parent": ref(root_jws),
        "perms": [{
            "type": "payment_initiation",
            "actions": ["initiate"],
            "locations": ["https://bank.example/payments"],
            "constraints": [
                {"pred": "eq", "ptr": "/instructedAmount/currency", "value": "EUR"},
                {"pred": "max", "ptr": "/instructedAmount/amount", "value": "5000.00"},
                {"pred": "eq", "ptr": "/creditorAccount/iban", "value": "DE89370400440532013000"},
                {"pred": "sum_max", "ptr": "/instructedAmount/amount",
                 "value": "20000.00", "period": 2592000, "budget": "monthly-out"},
                {"pred": "cosign_above", "ptr": "/instructedAmount/amount", "value": "5000.00"},
            ],
        }],
        "aud": [RP],
        "tf": TF,
    }


def wit_payload():
    jwk = dict(KEYS["ai-reconcile-1"]["pub"])
    jwk["alg"] = "EdDSA"
    return {
        "iss": OPERATOR,
        "sub": RECONCILE,
        "jti": "wit-reconcile-2-0001",
        "iat": 1792969200,
        "exp": 1792976400,
        "cnf": {"jwk": jwk},
    }


REQUEST = [{
    "type": "payment_initiation",
    "actions": ["initiate"],
    "locations": ["https://bank.example/payments"],
    "instructedAmount": {"currency": "EUR", "amount": "4000.00"},
    "creditorAccount": {"iban": "DE89370400440532013000"},
}]


def hdr(typ, kid=None, jwk=None):
    h = {"typ": typ, "alg": "EdDSA"}
    if kid is not None:
        h["kid"] = kid
    if jwk is not None:
        h["jwk"] = jwk
    return h


def build_case(variant):
    """variant: baseline | root_broader | aa_not_presented | aa_expired"""
    aa = sign(hdr("authority+jwt", kid="as-1"),
              authority_payload(exp=1792886400 if variant == "aa_expired" else 1824336000),
              "as-1")
    root_max = "200000.00" if variant == "root_broader" else "20000.00"
    root_p = root_payload(aa, root_max=root_max)
    root = sign(hdr("mandate+jwt", kid="mi-1"), root_p, "mi-1")
    sub_p = sub_payload(root)
    sub = sign(hdr("mandate+jwt", jwk=dict(KEYS["ai-treasury-1"]["pub"])), sub_p, "ai-treasury-1")
    wit_p = wit_payload()
    wit = sign(hdr("wit+jwt", kid="op-1"), wit_p, "op-1")
    evidence = [root] if variant == "aa_not_presented" else [root, aa]
    ad_bytes = compact(REQUEST)
    return {
        "aa": aa, "root": root, "sub": sub, "wit": wit,
        "aa_p": authority_payload(exp=1792886400 if variant == "aa_expired" else 1824336000),
        "root_p": root_p, "sub_p": sub_p, "wit_p": wit_p,
        "evidence": evidence, "ad_bytes": ad_bytes,
    }


# ---------------------------------------------------------------- expected results
# Errors are declared per case from the reading of Sections 9.3 and 9.4 given in
# README.md. Claims, chain and alternatives are assembled from the artifacts.

CASES = [
    {
        "dir": "00-baseline",
        "variant": "baseline",
        "title": "Valid baseline: Appendix A signed",
        "change": "None. This is the Appendix A story signed with the published keys.",
        "outcome": "valid",
        "authority": "established",
        "errors": lambda c: [],
        "aa_supports": True,
    },
    {
        "dir": "01-root-broader-than-powers",
        "variant": "root_broader",
        "title": "Root perms broader than powers",
        "change": "Root mandate max on /instructedAmount/amount is 200000.00 instead of 20000.00. "
                  "The Authority Assertion powers allow at most 100000.00.",
        "outcome": "invalid",
        "authority": "refuted",
        "errors": lambda c: [{"code": "authority_insufficient", "artifact": ref(c["root"])}],
        "aa_supports": False,
    },
    {
        "dir": "02-authority-not-presented",
        "variant": "aa_not_presented",
        "title": "Authority reference present, assertion not presented",
        "change": "The Authority Assertion is left out of mandate_evidence. "
                  "The root still references it, and delegator differs from principal.",
        "outcome": "invalid",
        "authority": "refuted",
        "errors": lambda c: [{"code": "authority_missing", "artifact": ref(c["root"])}],
        "aa_supports": False,
    },
    {
        "dir": "03-authority-expired",
        "variant": "aa_expired",
        "title": "Supporting assertion past exp",
        "change": "Authority Assertion exp is 1792886400 instead of 1824336000, "
                  "so at T it is past exp + max_clock_skew.",
        "outcome": "invalid",
        "authority": "refuted",
        "errors": lambda c: [
            {"code": "authority_insufficient", "artifact": ref(c["root"])},
            {"code": "expired", "artifact": ref(c["aa"])},
        ],
        "aa_supports": False,
    },
]


def claim(name, value, jws, role):
    return {"claim": name, "value": value, "artifact": ref(jws), "role": role}


def expected_result(case, c, profile_ref):
    claims = []
    for jws, p, role in ((c["root"], c["root_p"], "mandate_issuer"),
                         (c["sub"], c["sub_p"], "agent_instance")):
        for name in ("iss", "sub", "principal", "delegator", "perms", "loa"):
            if name in p:
                claims.append(claim(name, p[name], jws, role))
    if case["aa_supports"]:
        for name in ("iss", "principal", "delegator", "powers", "max_depth", "loa"):
            if name in c["aa_p"]:
                claims.append(claim(name, c["aa_p"][name], c["aa"], "authority_source"))
    for name in ("iss", "sub"):
        claims.append(claim(name, c["wit_p"][name], c["wit"], "operator"))

    errors = case["errors"](c)
    errors.sort(key=lambda e: (e["code"], e.get("artifact", {}).get("dig", ""), e.get("perm", -1)))
    return {
        "outcome": case["outcome"],
        "profile": profile_ref,
        "time": T_BASELINE,
        "tf": TF,
        "chain": [ref(c["root"]), ref(c["sub"])],
        "errors": errors,
        "diagnostics": [],
        "authority": case["authority"],
        "claims": claims,
        "alternatives": [{
            "perm": 0,
            "obligations": [{
                "type": "sum_max", "constraint": 3, "root": "ma-90b2",
                "budget": "monthly-out", "period": 2592000,
                "value": "20000.00", "amount": "4000.00",
            }],
        }],
        "evidence": [],
        "rejected": [],
        "status_evidence": [],
    }


# ---------------------------------------------------------------- output

def write(path, data: bytes):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)


def main(out):
    # keys
    thumbs = {}
    for name in KEY_NAMES:
        k = KEYS[name]
        jwk = dict(k["pub"])
        jwk["d"] = b64u(k["seed"])
        jwk["kid"] = name
        write(os.path.join(out, "keys", name + ".jwk.json"), pretty(jwk))
        thumbs[name] = {
            "seed_label": SEED_PREFIX + name,
            "seed_derivation": "d = SHA-256(UTF-8 bytes of seed_label)",
            "jkt": jkt(name),
        }
    write(os.path.join(out, "keys", "thumbprints.json"), pretty(thumbs))

    # profile
    profile_bytes = pretty(PROFILE)
    write(os.path.join(out, "profile", "profile.json"), profile_bytes)
    profile_ref = {"uri": PROFILE_URI, "dig": sha256_b64u(profile_bytes)}
    write(os.path.join(out, "profile", "profile-ref.json"), pretty(profile_ref))

    # trust anchors: keys inlined as public JWKs
    anchors = {}
    for role, lst in TRUST_ANCHORS.items():
        anchors[role] = []
        for a in lst:
            a2 = dict(a)
            a2["keys"] = [dict(KEYS[n]["pub"], kid=n) for n in a["keys"]]
            anchors[role].append(a2)
    write(os.path.join(out, "trust-anchors.json"), pretty(anchors))

    # cases
    for case in CASES:
        c = build_case(case["variant"])
        d = os.path.join(out, "cases", case["dir"])
        if case["variant"] != "aa_not_presented":
            write(os.path.join(d, "authority-assertion.jws"), c["aa"].encode("ascii"))
        write(os.path.join(d, "root-mandate.jws"), c["root"].encode("ascii"))
        write(os.path.join(d, "sub-mandate.jws"), c["sub"].encode("ascii"))
        write(os.path.join(d, "wit.jws"), c["wit"].encode("ascii"))
        write(os.path.join(d, "authorization_details.json"), c["ad_bytes"])
        presentation = {
            "subject_token": c["sub"],
            "subject_token_type": "urn:ietf:params:oauth:token-type:agent-mandate",
            "actor_token": c["wit"],
            "actor_token_type": "urn:ietf:params:oauth:token-type:jwt",
            "authorization_details": c["ad_bytes"].decode("utf-8"),
            "mandate_evidence": c["evidence"],
        }
        write(os.path.join(d, "presentation.json"), pretty(presentation))
        inputs = {
            "case": case["title"],
            "change_from_baseline": case["change"],
            "time": T_BASELINE,
            "rp": RP,
            "profile": profile_ref,
            "pop": {"outcome": "ok", "nonce": POP_NONCE},
            "status_list_tokens": [],
        }
        write(os.path.join(d, "inputs.json"), pretty(inputs))
        decoded = {}
        if case["variant"] != "aa_not_presented":
            decoded["authority_assertion"] = {"header": json.loads(_part(c["aa"], 0)), "payload": c["aa_p"]}
        decoded.update({
            "root_mandate": {"header": json.loads(_part(c["root"], 0)), "payload": c["root_p"]},
            "sub_mandate": {"header": json.loads(_part(c["sub"], 0)), "payload": c["sub_p"]},
            "wit": {"header": json.loads(_part(c["wit"], 0)), "payload": c["wit_p"]},
        })
        write(os.path.join(d, "decoded.json"), pretty(decoded))
        write(os.path.join(d, "expected-result.json"), pretty(expected_result(case, c, profile_ref)))


def _part(jws, i):
    s = jws.split(".")[i]
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__)))
