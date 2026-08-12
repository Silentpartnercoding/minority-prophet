#!/usr/bin/env python3
"""Do winner-holders survive MP root-collapse better than control-holders?

The comparison every run today has lacked. Root-collapse was applied to winning
tokens only, which cannot distinguish 'winner-holders have independent records'
from 'any wallet holding several tokens looks like this'.

No new RPC. Same holders file, same evaluator, both arms.
"""
import json, os, pathlib, sys
from collections import defaultdict
from math import comb

ROOT = pathlib.Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT))
from knowledge_ledger.transaction_v2 import evaluate_transaction_v2   # noqa: E402

D = pathlib.Path(os.environ["KL014_DATA"])
holders  = json.loads((D/"kl014/holders.json").read_text())
profiles = json.loads((D/"kl014/custodian_profiles.json").read_text())
pop      = json.loads((D/"kl012v3/population.json").read_text())["tokens"]
funders  = json.loads((D/"kl012v3/creator_funders.json").read_text())

CUST_SOL, CUST_TOK, CUST_PARTIES = 2000, 300, 8
def custodial(w):
    c = profiles.get(w)
    if not c or not c.get("profiled"): return True
    return c["sol"]>=CUST_SOL or c["tokens"]>=CUST_TOK or c["parties"]>=CUST_PARTIES

fanout = defaultdict(int)
for c, r in funders.items():
    f = (r or {}).get("funder")
    if f: fanout[f] += 1

def token_root(mint):
    cre = (pop.get(mint) or {}).get("creator")
    if not cre: return None
    f = (funders.get(cre) or {}).get("funder")
    if f and fanout[f] < 25: return f"fund:{f}"
    return f"creator:{cre}"

def arm(kind):
    toks = {m: v for m, v in holders.items() if v["kind"] == kind}
    per = defaultdict(list)
    for m, v in toks.items():
        for w in set(v["wallets"]):
            per[w].append(m)
    multi = {w: ts for w, ts in per.items() if len(ts) >= 2}
    profiled = {w: ts for w, ts in multi.items() if w in profiles}
    kept = {w: ts for w, ts in profiled.items() if not custodial(w)}
    rows = []
    for w, ts in kept.items():
        recs = []
        for i, m in enumerate(ts):
            r = token_root(m)
            recs.append({"recordId": f"r{i}", "side": "oppose"} if r is None
                        else {"recordId": f"r{i}", "rootId": r, "side": "oppose"})
        rec = evaluate_transaction_v2({
            "schema":"minority-prophet.knowledge-transaction.v0.2",
            "transactionId": f"cmp-{w[:8]}",
            "claim":{"type":"absence","statement":"no independently-rooted record"},
            "searchLedger":{"locations":[{"id":m,"status":"searched"} for m in ts]},
            "evidenceLedger":{"records":recs}})
        rows.append((w, len(ts), rec["evidence"]["distinctRoots"]))
    return toks, per, multi, profiled, kept, rows

print("  NOTE: only wallets already profiled are eligible in BOTH arms -- profiling")
print("  was run on winner-recurring wallets, so control coverage is partial and")
print("  this is stated rather than papered over.\n")
res = {}
for kind in ("winner","control"):
    toks, per, multi, prof, kept, rows = arm(kind)
    surv = [r for r in rows if r[2] >= 2]
    res[kind] = (len(toks), len(per), len(multi), len(prof), len(kept), rows, surv)
    print(f"  {kind:8s} tokens {len(toks):>3} | wallets {len(per):>4} | in>=2 {len(multi):>3} "
          f"| profiled {len(prof):>3} | non-custodial {len(kept):>3} | >=2 roots {len(surv):>3}")

wt, _, wm, wp, wk, wrows, wsurv = res["winner"]
ct, _, cm, cp, ck, crows, csurv = res["control"]
print(f"\n  among PROFILED multi-token wallets, share surviving root-collapse:")
for k,(p,s) in (("winner",(wp,len(wsurv))),("control",(cp,len(csurv)))):
    print(f"    {k:8s} {s}/{p}" + (f" = {s/p:.0%}" if p else " = n/a"))
if wp and cp:
    a,b,c,d = len(wsurv), wp-len(wsurv), len(csurv), cp-len(csurv)
    n=a+b+c+d; r1=a+b; c1=a+c
    def pr(x):
        if x<0 or x>min(r1,c1) or r1-x>n-c1: return 0.0
        return comb(c1,x)*comb(n-c1,r1-x)/comb(n,r1)
    o=pr(a); p=sum(pr(x) for x in range(0,min(r1,c1)+1) if pr(x)<=o+1e-12)
    print(f"    Fisher exact two-sided p = {p:.4f}")
else:
    print("    NOT COMPARABLE: one arm has no profiled multi-token wallets.")
    print("    Reporting that rather than a number.")
inf_w = sum(r[1] for r in wrows)/max(sum(r[2] for r in wrows),1)
inf_c = sum(r[1] for r in crows)/max(sum(r[2] for r in crows),1)
print(f"\n  root-collapse inflation: winners {inf_w:.2f}x | controls {inf_c:.2f}x")
