#!/usr/bin/env python3
"""Trace each creator to its first funder. Solana RPC only, at the measured rate."""
import json, os, sys, time, threading, urllib.request, urllib.error

HERE=os.path.dirname(os.path.abspath(__file__)); ST=os.path.join(HERE,"kl012v2")
RPC=os.environ.get("SOL_RPC","https://api.mainnet-beta.solana.com")
RATE=float(os.environ.get("SOL_RPS","1"))
_lock=threading.Lock(); _last=[0.0]; _n=[0]; _http={}

def _throttle():
    with _lock:
        w=_last[0]+1.0/RATE-time.monotonic()
        if w>0: time.sleep(w)
        _last[0]=time.monotonic(); _n[0]+=1

def rpc(m,p,tries=5):
    for i in range(tries):
        _throttle()
        try:
            r=urllib.request.Request(RPC,method="POST",
              data=json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode(),
              headers={"Content-Type":"application/json"})
            d=json.loads(urllib.request.urlopen(r,timeout=90).read())
            if "error" not in d: return d
            time.sleep(2**i)
        except urllib.error.HTTPError as e:
            _http[e.code]=_http.get(e.code,0)+1; time.sleep(min(2**i,20))
        except Exception:
            time.sleep(min(2**i,20))
    return {"error":"exhausted"}

def first_tx(addr, max_pages=8):
    """Page back to the earliest retained signature. Returns (sig, reached_start)."""
    before=None; oldest=None; pages=0
    while pages<max_pages:
        p={"limit":1000}
        if before: p["before"]=before
        r=rpc("getSignaturesForAddress",[addr,p]).get("result")
        if not r: return oldest, True
        oldest=r[-1]["signature"]; pages+=1
        if len(r)<1000: return oldest, True
        before=oldest
    return oldest, False

def funder(addr):
    sig, complete = first_tx(addr)
    if not sig: return {"funder":None,"why":"no history"}
    t=rpc("getTransaction",[sig,{"encoding":"jsonParsed","maxSupportedTransactionVersion":0}]).get("result")
    if not t: return {"funder":None,"why":"tx unavailable"}
    keys=[a["pubkey"] for a in t["transaction"]["message"]["accountKeys"]]
    pre,post=t["meta"]["preBalances"],t["meta"]["postBalances"]
    delta={k:post[i]-pre[i] for i,k in enumerate(keys)}
    others={k:v for k,v in delta.items() if k!=addr and v<0}
    f=min(others,key=others.get) if others else None
    return {"funder":f,"amountSol":round(-others[f]/1e9,6) if f else None,
            "historyComplete":complete,"firstSlot":t.get("slot"),
            "firstTime":t.get("blockTime")}

pop=json.load(open(os.path.join(ST,"population.json")))
creators=sorted({v["creator"] for g in ("cases","controls") for v in pop[g].values()})
out={}
p=os.path.join(ST,"creator_funders.json")
if os.path.exists(p): out=json.load(open(p))
todo=[c for c in creators if c not in out]
print(f"  {len(creators)} creators | {len(todo)} to trace | {RATE} req/s",flush=True)
t0=time.time()
for i,c in enumerate(todo):
    out[c]=funder(c)
    if (i+1)%25==0:
        json.dump(out,open(p,"w"))
        el=time.time()-t0
        print(f"    {i+1}/{len(todo)} | {_n[0]} calls | {el/(i+1):.1f}s/creator "
              f"| eta {(len(todo)-i-1)*el/(i+1)/60:.0f}m"
              f"{'' if not _http else ' | HTTP '+str(_http)}",flush=True)
json.dump(out,open(p,"w"))
ok=sum(1 for v in out.values() if v.get("funder"))
print(f"  DONE: {len(out)} creators, {ok} with an identified funder",flush=True)
