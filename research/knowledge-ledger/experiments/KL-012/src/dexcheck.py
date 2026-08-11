#!/usr/bin/env python3
"""Which of the blind population ever became tradeable? External oracle, no RPC."""
import json, os, sys, time, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
ST = os.path.join(HERE, "kl012")
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36",
      "Accept": "application/json"}

def get(u, tries=4):
    for i in range(tries):
        try:
            return json.loads(urllib.request.urlopen(
                urllib.request.Request(u, headers=UA), timeout=45).read())
        except urllib.error.HTTPError as e:
            if e.code == 429: time.sleep(3 + i*3); continue
            return {"__err__": f"http {e.code}"}
        except Exception as e:
            time.sleep(2 + i*2)
    return {"__err__": "exhausted"}

toks = json.load(open(os.path.join(ST, "tokens.json")))
mints = sorted(toks)
out = {}
p = os.path.join(ST, "dex.json")
if os.path.exists(p): out = json.load(open(p))
todo = [m for m in mints if m not in out]
print(f"  {len(mints)} blind mints | {len(todo)} to check", flush=True)

CONTROL_OK = False
ctl = get("https://api.dexscreener.com/latest/dex/search?q=SOL")
known = [x["baseToken"]["address"] for x in (ctl.get("pairs") or [])
         if x.get("chainId") == "solana"][:3]
if known:
    c = get("https://api.dexscreener.com/latest/dex/tokens/" + ",".join(known))
    CONTROL_OK = bool(c.get("pairs"))
print(f"  instrument control (known-live mints return pairs): {CONTROL_OK}", flush=True)
if not CONTROL_OK:
    sys.exit("  refusing to record zeros from an instrument that cannot find a live token")

for i in range(0, len(todo), 30):
    chunk = todo[i:i+30]
    d = get("https://api.dexscreener.com/latest/dex/tokens/" + ",".join(chunk))
    if "__err__" in d:
        print(f"    batch {i//30}: {d['__err__']}", flush=True); continue
    pairs = d.get("pairs") or []
    by = {}
    for pr in pairs:
        a = pr["baseToken"]["address"]
        cur = by.get(a)
        liq = (pr.get("liquidity") or {}).get("usd") or 0
        if not cur or liq > cur["liquidityUsd"]:
            by[a] = {"marketCap": pr.get("marketCap"), "fdv": pr.get("fdv"),
                     "liquidityUsd": liq, "priceUsd": pr.get("priceUsd"),
                     "h24": (pr.get("priceChange") or {}).get("h24"),
                     "vol24": (pr.get("volume") or {}).get("h24"),
                     "pairCreatedAt": pr.get("pairCreatedAt"), "dex": pr.get("dexId")}
    for m in chunk:
        out[m] = by.get(m) or {"tradeable": False}
    json.dump(out, open(p, "w"))
    if (i//30) % 5 == 0:
        t = sum(1 for v in out.values() if v.get("tradeable") is not False)
        print(f"    {len(out)}/{len(mints)} checked | tradeable {t}", flush=True)
    time.sleep(0.6)

json.dump(out, open(p, "w"))
tr = [m for m, v in out.items() if v.get("tradeable") is not False]
print(f"\n  DONE: {len(out)} checked, {len(tr)} ever tradeable "
      f"({len(tr)/max(len(out),1):.1%})", flush=True)
