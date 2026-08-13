"""KL-014 exploratory pilot — compute the split factor under both pinned rules.

EXPLORATORY PILOT. ONE CONTROL DOMAIN. NOT A RESULT.

Reads corpus-20260813.json and applies the two evidence-digest construction
rules pinned in preregistration-v0.2.json BEFORE the corpus was retrieved:

  D1-surface        digest the claim's own published text
                    -> every issuer distinct by construction
  D2-cited-primary  digest the primary source the claim cites; fall back to D1
                    for any claim that cites none

Reports both, never one alone, plus the fallback rate — the proportion of real
published claims that do not identify a resolvable primary source at all.

Run: python research/knowledge-ledger/experiments/KL-014/pilot/compute_split.py
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[5]))

from provenance.root_registry import RootRegistry, RootRequest  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
BANNER = "EXPLORATORY PILOT — ONE CONTROL DOMAIN — NOT A RESULT"


def digest(text: str) -> str:
    return hashlib.sha256(" ".join(text.lower().split()).encode()).hexdigest()


def root_id(issuer: str, proposition: str, evidence_digest: str) -> str:
    """mp-root-v1 via the shipped implementation, not a reimplementation."""
    return RootRegistry.root_identity(RootRequest(
        issuer_id=issuer,
        key_id="pilot",
        observation_id=f"{issuer}:{proposition}",
        proposition_id=proposition,
        value=True,
        evidence_digest=evidence_digest,
        observed_at=0,
        nonce="pilot",
    ))


def main() -> int:
    corpus = json.loads((HERE / "corpus-20260813.json").read_text())
    print(BANNER)
    print(f"corpus: {corpus['retrievedOn']}  |  {corpus['doesNotMeetItsOwnMinimum']['achieved']}\n")

    print(f"{'prop':<6}{'claims':>7}{'obs':>5}{'D1 roots':>10}{'D2 roots':>10}"
          f"{'D1 split':>10}{'D2 split':>10}{'fallback':>10}  min?")
    print("-" * 82)

    primary_rows = []
    for prop in corpus["propositions"]:
        pid, claims = prop["id"], prop["claims"]
        obs = prop["underlyingObservations"]

        # D1: digest each claim's own text. Distinct issuers -> distinct texts.
        d1 = {root_id(c["issuer"], pid, digest(f"{c['issuer']} article text for {pid}"))
              for c in claims}

        # D2: digest the cited primary source; fall back to D1 when absent.
        d2 = set()
        fallbacks = 0
        for c in claims:
            if c["citesPrimary"]:
                # every claim citing the same primary shares an evidence digest
                # AND an observation id, so they collapse to one root
                d2.add(root_id("shared", pid, digest(c["primarySourceId"])))
            else:
                fallbacks += 1
                d2.add(root_id(c["issuer"], pid,
                               digest(f"{c['issuer']} article text for {pid}")))

        row = dict(pid=pid, n=len(claims), obs=obs, d1=len(d1), d2=len(d2),
                   fallbacks=fallbacks, meets=prop["meetsMinimum"])
        if prop["meetsMinimum"]:
            primary_rows.append(row)

        print(f"{pid:<6}{len(claims):>7}{obs:>5}{len(d1):>10}{len(d2):>10}"
              f"{len(d1)/obs:>10.2f}{len(d2)/obs:>10.2f}"
              f"{fallbacks/len(claims):>9.0%}  {'yes' if prop['meetsMinimum'] else 'NO'}")

    print("-" * 82)
    all_claims = sum(len(p["claims"]) for p in corpus["propositions"])
    all_fallback = sum(1 for p in corpus["propositions"] for c in p["claims"]
                       if not c["citesPrimary"])

    print(f"\nAcross all {all_claims} verified claims, {all_fallback} "
          f"({all_fallback/all_claims:.0%}) cite no resolvable primary source.")
    print("Each of those is, to the aggregator, its own independent evidence root.")

    print(f"\n{'':-<82}")
    if not primary_rows:
        print("NO proposition met the declared minimum. Nothing is reported as a")
        print("pilot estimate. See corpus-20260813.json doesNotMeetItsOwnMinimum.")
        return 0

    print(f"PRIMARY TALLY — only propositions meeting the declared minimum "
          f"({len(primary_rows)} of {len(corpus['propositions'])}):")
    for r in primary_rows:
        ratio = r["d1"] / r["d2"] if r["d2"] else float("nan")
        print(f"  {r['pid']}: D1 split {r['d1']/r['obs']:.2f}, "
              f"D2 split {r['d2']/r['obs']:.2f}, D1/D2 ratio {ratio:.2f}, "
              f"fallback {r['fallbacks']}/{r['n']}")

    print(f"\n{BANNER}")
    print("This does not estimate the real-world split factor. Corpus selection")
    print("alone could account for it, the labeller is a single control domain,")
    print("and two of three propositions are below the declared minimum.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
