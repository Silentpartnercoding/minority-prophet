#!/usr/bin/env python3
"""KL-015: pull each qualifying token's FULL history, then build the baseline."""
import json, os, random, time, urllib.request
SPEC=json.load(open(os.environ["KL015_SPEC"]))
RPC=os.environ["SOL_RPC"]; RATE=8.0; _last=[0.0]; _n=[0]
WIN=SPEC["measure"]["LEAD_WINDOW_S"]; NB=SPEC["baseline"]["BASELINE_WINDOWS"]
def rpc(m,p,tries=4):
    for i in range(tries):
        w=_last[0]+1.0/RATE-time.monotonic()
        if w>0: time.sleep(w)
        _last[0]=time.monotonic(); _n[0]+=1
        try:
            r=urllib.request.Request(RPC,method="POST",
              data=json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode(),
              headers={"Content-Type":"application/json"})
            d=json.loads(urllib.request.urlopen(r,timeout=60).read())
            if "result" in d: return d["result"]
        except Exception: time.sleep(1+i)
    return None

cand=json.load(open("kl015_candidates.json"))
MAXAGE=SPEC["population"]["RECENCY_GATE"]["MAX_AGE_HOURS"]
toks=[m for m,v in cand.items() if (v.get("age_h") or 99)<=MAXAGE]
print(f"  {len(toks)} tokens pass tradeability + recency gates",flush=True)

hist={}
p="kl015/history.json"
if os.path.exists(p): hist=json.load(open(p))
for i,m in enumerate([t for t in toks if t not in hist]):
    before=None; sigs=[]; pages=0
    while pages<15:
        q={"limit":1000}
        if before: q["before"]=before
        r=rpc("getSignaturesForAddress",[m,q]); pages+=1
        if not r: break
        sigs+= [(s["signature"],s.get("blockTime")) for s in r if s.get("blockTime")]
        if len(r)<1000: break
        before=r[-1]["signature"]
    hist[m]={"sigs":sigs,"complete":pages<15}
    json.dump(hist,open(p,"w"))
    print(f"    {i+1} {m[:14]}.. {len(sigs)} sigs, complete={hist[m]['complete']} | {_n[0]} calls",flush=True)

# BASELINE FIRST -- no subject event has been identified yet
rng=random.Random(20260812)
base={}
for m,v in hist.items():
    ts=[t for _,t in v["sigs"]]
    if len(ts)<40: continue
    lo,hi=min(ts),max(ts)
    if hi-lo<=WIN: continue
    counts=[]
    for _ in range(NB):
        st=rng.randint(lo,hi-WIN)
        ins=[s for s,t in v["sigs"] if st<=t<st+WIN]
        wal=set()
        for s in ins[:25]:
            tx=rpc("getTransaction",[s,{"encoding":"jsonParsed","maxSupportedTransactionVersion":0}])
            if not tx: continue
            for a in tx["transaction"]["message"]["accountKeys"]:
                if a.get("signer"): wal.add(a["pubkey"])
        counts.append(len(wal))
    base[m]={"windows":counts,"lo":lo,"hi":hi}
    json.dump(base,open("kl015/baseline.json","w"))
    print(f"    baseline {m[:14]}.. median={sorted(counts)[len(counts)//2]} | {_n[0]} calls",flush=True)
json.dump(base,open("kl015/baseline.json","w"))
allw=[c for v in base.values() for c in v["windows"]]
sv=sorted(allw)
print(f"\n  BASELINE BUILT FIRST: {len(base)} tokens, {len(allw)} windows")
print(f"  distinct wallets per arbitrary 60s: median {sv[len(sv)//2]}, p90 {sv[int(len(sv)*.9)]}, max {sv[-1]}")
degen=sum(1 for v in base.values() if len(set(v['windows']))<2)
print(f"  degenerate tokens (all windows identical): {degen}/{len(base)}")
