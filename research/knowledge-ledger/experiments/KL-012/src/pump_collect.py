#!/usr/bin/env python3
"""KL-012 v0.2 population: cases and controls from pump.fun, per the frozen rule."""
import json, os, time, urllib.request, urllib.error, datetime

HERE=os.path.dirname(os.path.abspath(__file__)); ST=os.path.join(HERE,"kl012v2")
os.makedirs(ST,exist_ok=True)
UA={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                 "(KHTML, like Gecko) Chrome/126.0 Safari/537.36","Accept":"application/json"}
B="https://frontend-api-v3.pump.fun/coins?limit=50&sort=created_timestamp&order=DESC&includeNsfw=true"

def get(u,tries=4):
    for i in range(tries):
        try: return json.loads(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=40).read())
        except urllib.error.HTTPError as e:
            if e.code in (429,530): time.sleep(3+i*3); continue
            return None
        except Exception: time.sleep(2+i*2)
    return None

def harvest(complete):
    seen={}
    for off in range(0,1001,50):
        d=get(f"{B}&complete={'true' if complete else 'false'}&offset={off}")
        if not isinstance(d,list) or not d: break
        for c in d:
            if c.get("mint") and c.get("creator"): seen[c["mint"]]=c
        time.sleep(0.5)
    return seen

cases=harvest(True); controls=harvest(False)
print(f"  cases (graduated):     {len(cases)}")
print(f"  controls (not yet):    {len(controls)}")

# window rule: controls must lie inside the cases' created_timestamp span
cts=[c["created_timestamp"] for c in cases.values() if c.get("created_timestamp")]
lo,hi=min(cts),max(cts)
kept={m:c for m,c in controls.items()
      if c.get("created_timestamp") and lo<=c["created_timestamp"]<=hi}
dropped=len(controls)-len(kept)
f=lambda t: datetime.datetime.fromtimestamp(t/1000,datetime.UTC).strftime("%m-%d %H:%M")
print(f"  case window: {f(lo)} .. {f(hi)}")
print(f"  controls inside the window: {len(kept)}  (dropped {dropped}, not re-sampled)")

pop={"cases":{m:{"creator":c["creator"],"created":c["created_timestamp"],
                 "mcap":c.get("usd_market_cap"),"complete":True} for m,c in cases.items()},
     "controls":{m:{"creator":c["creator"],"created":c["created_timestamp"],
                    "mcap":c.get("usd_market_cap"),"complete":False} for m,c in kept.items()},
     "windowStart":lo,"windowEnd":hi,"controlsDropped":dropped}
json.dump(pop,open(os.path.join(ST,"population.json"),"w"),indent=1)
cr_a={v["creator"] for v in pop["cases"].values()}
cr_b={v["creator"] for v in pop["controls"].values()}
print(f"\n  distinct creators -- cases {len(cr_a)}, controls {len(cr_b)}, overlap {len(cr_a&cr_b)}")
print(f"  total creators to trace: {len(cr_a|cr_b)}")
