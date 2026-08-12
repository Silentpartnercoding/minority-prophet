#!/usr/bin/env python3
"""KL-014 analysed with Minority Prophet, not with ad-hoc counting.

THE QUESTION RESTATED IN MP'S TERMS.

A wallet holding a top position in six winning tokens looks like six pieces of
evidence that it picks winners. MP's whole claim is that this is wrong when the
six are not independent: copies, derivations and commonly-controlled sources
collapse into one root, and counting them separately is manufactured consensus.

Two winning tokens are the SAME ROOT here when their creators share a funding
ancestor, or when one creator made both. So a wallet in six tokens from one
operator has one independent root, not six -- and that is a claim about one
operator's launches, not about picking winners.

This is the first time this programme has run its own evaluator on data it did not
generate. The receipt is produced by knowledge_ledger.transaction_v2, which emits
the uncertainty fields v0.1 could not carry (SCH-005), so 'we could not attribute
this evidence' is visible in the output rather than silently dropped.
"""
import json, os, pathlib, sys
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT))
from knowledge_ledger.transaction_v2 import evaluate_transaction_v2   # noqa: E402

SCRATCH = pathlib.Path(os.environ["KL014_DATA"])
holders = json.loads((SCRATCH / "kl014/holders.json").read_text())
profiles = json.loads((SCRATCH / "kl014/custodian_profiles.json").read_text())
pop = json.loads((SCRATCH / "kl012v3/population.json").read_text())["tokens"]
funders = json.loads((SCRATCH / "kl012v3/creator_funders.json").read_text())

CUST_SOL, CUST_TOK, CUST_PARTIES = 2000, 300, 8
def custodial(w):
    c = profiles.get(w)
    if not c or not c.get("profiled"): return True          # fail closed
    return c["sol"] >= CUST_SOL or c["tokens"] >= CUST_TOK or c["parties"] >= CUST_PARTIES

winners = {m: v for m, v in holders.items() if v["kind"] == "winner"}

# token -> its operator root: the creator's funding cluster, else the creator
def token_root(mint):
    cre = (pop.get(mint) or {}).get("creator")
    if not cre: return None
    f = (funders.get(cre) or {}).get("funder")
    fanout = sum(1 for c, r in funders.items() if (r or {}).get("funder") == f)
    if f and fanout < 25:            # a hub funder identifies nobody
        return f"fund:{f}"
    return f"creator:{cre}"

subject_tokens = defaultdict(list)
for m, v in winners.items():
    for w in set(v["wallets"]):
        if not custodial(w): subject_tokens[w].append(m)
subjects = {w: ts for w, ts in subject_tokens.items() if len(ts) >= 2}
print(f"  non-custodial wallets in >=2 winners: {len(subjects)}\n")

print(f"  {'wallet':<16}{'tokens':>7}{'MP roots':>10}  {'conclusion':<28}{'flip':>5}{'unattr':>7}")
rows = []
for w, toks in sorted(subjects.items(), key=lambda x: -len(x[1])):
    records, unattributed = [], 0
    for i, m in enumerate(toks):
        r = token_root(m)
        if r is None:
            unattributed += 1
            records.append({"recordId": f"r{i}", "side": "oppose"})     # no rootId
        else:
            records.append({"recordId": f"r{i}", "rootId": r, "side": "oppose"})
    tx = {
        "schema": "minority-prophet.knowledge-transaction.v0.2",
        "transactionId": f"kl014-{w[:8]}",
        # ABSENCE claim: "this wallet has no independently-rooted record of holding
        # winners". A counterexample root refutes it; more roots make it stronger.
        "claim": {"type": "absence",
                  "statement": f"{w[:8]} holds no independently-rooted winning position"},
        "searchLedger": {"locations": [{"id": m, "status": "searched"} for m in toks]},
        "evidenceLedger": {"records": records},
    }
    rec = evaluate_transaction_v2(tx)
    ev = rec["evidence"]
    rows.append((w, len(toks), ev["distinctRoots"], rec["conclusion"],
                 ev["flipBudget"], ev["unattributedRecords"], rec))
    print(f"  {w[:14]:<16}{len(toks):>7}{ev['distinctRoots']:>10}  {rec['conclusion']:<28}"
          f"{ev['flipBudget']:>5}{ev['unattributedRecords']:>7}")

print(f"\n  COLLAPSE: raw token counts vs independent MP roots")
tot_t = sum(r[1] for r in rows); tot_r = sum(r[2] for r in rows)
print(f"    tokens claimed as evidence : {tot_t}")
print(f"    independent roots          : {tot_r}")
print(f"    inflation                  : {tot_t/max(tot_r,1):.2f}x")
survive = [r for r in rows if r[2] >= 2]
print(f"\n  wallets with >=2 INDEPENDENT roots: {len(survive)} of {len(rows)}")
for w, t, r, c, fb, un, _ in survive:
    print(f"    {w[:20]}  {t} tokens -> {r} roots, flipBudget {fb}")
json.dump({w: rec for w, _, _, _, _, _, rec in rows},
          open(SCRATCH / "kl014/mp_receipts.json", "w"), indent=1)
