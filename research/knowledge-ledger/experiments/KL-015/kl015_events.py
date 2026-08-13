#!/usr/bin/env python3
"""KL-015 subject events, measured AFTER the baseline was fixed."""
import json, os, time, urllib.request
from collections import Counter, defaultdict
SPEC=json.load(open(os.environ["KL015_SPEC"]))
RPC=os.environ["SOL_RPC"]; RATE=8.0; _last=[0.0]; _n=[0]
WIN=SPEC["measure"]["LEAD_WINDOW_S"]
CR=SPEC["subjects"]["custodianRule"]
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
TOKPROG="TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
hist=json.load(open("kl015/history.json")); base=json.load(open("kl015/baseline.json"))
toks=[m for m in base]
print(f"  {len(toks)} tokens with a baseline",flush=True)

# candidate subjects: top holders, then wallets appearing in >=2 tokens
hold={}
p="kl015/holders.json"
if os.path.exists(p): hold=json.load(open(p))
for m in [t for t in toks if t not in hold]:
    la=rpc("getTokenLargestAccounts",[m]) or {}
    ws=[]
    for a in (la.get("value") or [])[:20]:
        ai=rpc("getAccountInfo",[a["address"],{"encoding":"jsonParsed"}])
        o=(((ai or {}).get("value") or {}).get("data") or {}).get("parsed",{}).get("info",{})
        if o.get("owner"): ws.append(o["owner"])
    hold[m]=ws; json.dump(hold,open(p,"w"))
print(f"  holders collected | {_n[0]} calls",flush=True)

cnt=Counter(w for ws in hold.values() for w in set(ws))
cands=[w for w,n in cnt.items() if n>=2]
print(f"  wallets in >=2 qualifying tokens: {len(cands)}",flush=True)

prof={}
pp="kl015/profiles.json"
if os.path.exists(pp): prof=json.load(open(pp))
for w in [c for c in cands if c not in prof]:
    bal=(rpc("getBalance",[w]) or {}).get("value") or 0
    ta=rpc("getTokenAccountsByOwner",[w,{"programId":TOKPROG},{"encoding":"jsonParsed"}]) or {}
    nz=sum(1 for a in (ta.get("value") or [])
           if float((a["account"]["data"]["parsed"]["info"]["tokenAmount"] or {}).get("uiAmount") or 0)>0)
    sg=rpc("getSignaturesForAddress",[w,{"limit":25}]) or []
    parties=set()
    for s in sg[:10]:
        tx=rpc("getTransaction",[s["signature"],{"encoding":"jsonParsed","maxSupportedTransactionVersion":0}])
        if not tx: continue
        for a in tx["transaction"]["message"]["accountKeys"]:
            if a.get("signer") and a["pubkey"]!=w: parties.add(a["pubkey"])
    prof[w]={"sol":bal/1e9,"tokens":nz,"parties":len(parties),"profiled":bool(sg)}
    json.dump(prof,open(pp,"w"))
def cust(w):
    c=prof.get(w)
    if not c or not c["profiled"]: return True
    return c["sol"]>=CR["MAX_SOL"] or c["tokens"]>=CR["MAX_TOKEN_POSITIONS"] or c["parties"]>=CR["MAX_COUNTERPARTIES"]
subs=[w for w in cands if not cust(w)]
print(f"  non-custodial subjects: {len(subs)} of {len(cands)} | {_n[0]} calls",flush=True)

events=[]
for w in subs:
    for m in [t for t in toks if w in hold.get(t,[])]:
        ta=rpc("getTokenAccountsByOwner",[w,{"mint":m},{"encoding":"jsonParsed"}]) or {}
        v=ta.get("value") or []
        if not v: continue
        sg=rpc("getSignaturesForAddress",[v[0]["pubkey"],{"limit":1000}]) or []
        ts=[s.get("blockTime") for s in sg if s.get("blockTime")]
        if not ts: continue
        ev=min(ts)
        lo,hi=base[m]["lo"],base[m]["hi"]
        if not (lo<=ev<=hi):          # effectRequires: discard, do not compare
            events.append({"w":w,"m":m,"discarded":"outside reachable history"}); continue
        ins=[s for s,t in hist[m]["sigs"] if ev<t<=ev+WIN]
        wal=set()
        for s in ins[:25]:
            tx=rpc("getTransaction",[s,{"encoding":"jsonParsed","maxSupportedTransactionVersion":0}])
            if not tx: continue
            for a in tx["transaction"]["message"]["accountKeys"]:
                if a.get("signer") and a["pubkey"]!=w: wal.add(a["pubkey"])
        bw=sorted(base[m]["windows"]); med=bw[len(bw)//2]
        events.append({"w":w,"m":m,"followers":len(wal),"baselineMedian":med,
                       "diff":len(wal)-med})
        json.dump(events,open("kl015/events.json","w"))
json.dump(events,open("kl015/events.json","w"))
ok=[e for e in events if "diff" in e]
print(f"\n  events measured {len(ok)} | discarded {len(events)-len(ok)} | {_n[0]} calls",flush=True)
