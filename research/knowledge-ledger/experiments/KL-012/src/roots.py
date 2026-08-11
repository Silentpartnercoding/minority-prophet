#!/usr/bin/env python3
"""KL-012 root measure: collapse voices into independent roots.

Reads every threshold from the frozen spec. Two accounts are the same root if
they share a funding ancestor within MAX_HOPS, after HUBS are excluded.

WHY HUB EXCLUSION IS THE WHOLE GAME. Fifty accounts funded from one exchange are
fifty people. Merging them would make the method appear predictive for a reason
that has nothing to do with independence -- exchange-funded accounts are also more
likely to be retail, which correlates with everything. The pilot could not measure
this at all: 14 of 32 funders exceeded a 4,000-transaction cap, so their true size
was unknown.

A funder whose full history CANNOT BE RETRIEVED is treated as a HUB and never
merges anything. That fails closed. Merging on unknown evidence is the error that
matters here, and refusing to merge only ever costs sensitivity.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from collect import SPEC, rpc, load, save, _n

RM = SPEC["rootMeasure"]
MAX_HOPS = RM["MAX_HOPS"]
HUB_TX = RM["hubExclusion"]["HUB_MIN_TX"]
HUB_FANOUT = RM["hubExclusion"]["HUB_MIN_FANOUT"]


def history(addr, cap):
    """Page until the true beginning or `cap`. Returns (n, complete)."""
    n, before = 0, None
    while n < cap:
        p = {"limit": 1000}
        if before: p["before"] = before
        r = rpc("getSignaturesForAddress", [addr, p]).get("result")
        if not r: return n, True
        n += len(r)
        if len(r) < 1000: return n, True
        before = r[-1]["signature"]
    return n, False


def classify(addr, cache):
    """HUB / NORMAL / UNKNOWN->HUB. Cached: hubs recur constantly."""
    if addr in cache: return cache[addr]
    n, complete = history(addr, cap=HUB_TX)
    if not complete or n >= HUB_TX:
        v = {"hub": True, "why": "history exceeds HUB_MIN_TX" if complete
             else "history not fully retrievable -- failing closed", "txSeen": n}
    else:
        v = {"hub": False, "why": "normal", "txSeen": n}
    cache[addr] = v
    return v


def funder_of(addr, cache):
    """The account that funded `addr`'s first ever transaction."""
    if addr in cache: return cache[addr]
    sigs, before, oldest = [], None, None
    while True:
        p = {"limit": 1000}
        if before: p["before"] = before
        r = rpc("getSignaturesForAddress", [addr, p]).get("result")
        if not r: break
        oldest = r[-1]["signature"]
        if len(r) < 1000: break
        before = oldest
        if len(sigs) > 20000: break
    if not oldest:
        cache[addr] = None; return None
    t = rpc("getTransaction", [oldest, {"encoding":"jsonParsed",
                                        "maxSupportedTransactionVersion":0}]).get("result")
    if not t:
        cache[addr] = None; return None
    keys = [a["pubkey"] for a in t["transaction"]["message"]["accountKeys"]]
    pre, post = t["meta"]["preBalances"], t["meta"]["postBalances"]
    delta = {k: post[i]-pre[i] for i, k in enumerate(keys)}
    others = {k: v for k, v in delta.items() if k != addr and v < 0}
    f = min(others, key=others.get) if others else None
    cache[addr] = f
    return f


def ancestors(addr, fcache, hcache):
    """Non-hub funding ancestors within MAX_HOPS. Hubs terminate the walk."""
    out, cur = [], addr
    for _ in range(MAX_HOPS):
        f = funder_of(cur, fcache)
        if not f or f == cur: break
        if classify(f, hcache)["hub"]: break        # a hub links nobody
        out.append(f); cur = f
    return out


def cluster(signers, fcache, hcache):
    """Union-find over shared non-hub ancestors."""
    parent = {s: s for s in signers}
    def find(x):
        while parent[x] != x: parent[x] = parent[parent[x]]; x = parent[x]
        return x
    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb: parent[ra] = rb
    owner = {}
    for s in signers:
        for a in ancestors(s, fcache, hcache):
            if a in owner: union(s, owner[a])
            else: owner[a] = s
    return len({find(s) for s in signers})


def main(limit):
    live = load("liveness.json", {})
    res = load("rootcounts.json", {})
    fcache = load("funder_cache.json", {})
    hcache = load("hub_cache.json", {})
    pool = [m for m, v in live.items() if v["qualifies"] and m not in res][:limit]
    print(f"  root-counting {len(pool)} qualifying tokens "
          f"(MAX_HOPS={MAX_HOPS}, HUB_MIN_TX={HUB_TX:,})")
    for i, m in enumerate(pool):
        signers = live[m]["signers"]
        roots = cluster(signers, fcache, hcache)
        res[m] = {"voiceCount": len(signers), "rootCount": roots,
                  "inflation": round(len(signers)/roots, 3) if roots else None}
        if (i+1) % 5 == 0:
            save("rootcounts.json", res); save("funder_cache.json", fcache)
            save("hub_cache.json", hcache)
            hubs = sum(1 for v in hcache.values() if v["hub"])
            print(f"    {i+1}/{len(pool)} | hubs found {hubs}/{len(hcache)} | "
                  f"{_n[0]} calls", flush=True)
    save("rootcounts.json", res); save("funder_cache.json", fcache); save("hub_cache.json", hcache)
    if res:
        inf = [v["inflation"] for v in res.values() if v["inflation"]]
        print(f"  DONE: {len(res)} tokens | median voice/root inflation "
              f"{sorted(inf)[len(inf)//2]:.2f}x" if inf else "  DONE")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 10**9)
