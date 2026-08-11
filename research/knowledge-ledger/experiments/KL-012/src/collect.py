#!/usr/bin/env python3
"""KL-012 collector. Runs to the frozen COLLECTION-SPEC-v0.1.json and nothing else.

Throttled, resumable, and it does not decide anything: every threshold comes from
the spec. If the spec is absent it refuses to run, because a collector that
supplies its own thresholds is choosing them while looking at the data.

    export SOL_RPC='https://solana-mainnet.g.alchemy.com/v2/KEY'
    python3 collect.py blocks 2000        # discover token creations
    python3 collect.py liveness           # apply the liveness filter
    python3 collect.py outcomes           # time-to-death
    python3 collect.py status
"""
import json, os, sys, time, threading, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, "kl012")
os.makedirs(STATE, exist_ok=True)
SPEC_PATH = os.environ.get("KL012_SPEC", os.path.join(
    "/Users/james/Development/minority-prophet-first-transmission",
    "research/knowledge-ledger/experiments/KL-012/COLLECTION-SPEC-v0.1.json"))
if not os.path.exists(SPEC_PATH):
    sys.exit("refusing to run: frozen collection spec not found")
SPEC = json.load(open(SPEC_PATH))

RPC = os.environ.get("SOL_RPC", "https://api.mainnet-beta.solana.com")
IS_PUBLIC = "api.mainnet-beta" in RPC
RATE = float(os.environ.get("SOL_RPS", "8" if not IS_PUBLIC else "2"))

_lock = threading.Lock(); _last = [0.0]; _n = [0]
def _throttle():
    with _lock:
        gap = 1.0 / RATE
        wait = _last[0] + gap - time.monotonic()
        if wait > 0: time.sleep(wait)
        _last[0] = time.monotonic(); _n[0] += 1

def rpc(method, params, tries=6):
    for i in range(tries):
        _throttle()
        try:
            req = urllib.request.Request(RPC, method="POST",
                data=json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params}).encode(),
                headers={"Content-Type":"application/json"})
            d = json.loads(urllib.request.urlopen(req, timeout=120).read())
            if "error" not in d: return d
            msg = str(d["error"]).lower()
            if "rate" in msg or "429" in msg or "-32429" in msg:
                time.sleep(2 ** i); continue
            return d
        except Exception:
            time.sleep(min(2 ** i, 30))
    return {"error": "exhausted"}

def rpc_batch(calls, tries=5):
    """JSON-RPC batch: many calls, one HTTP round trip. The endpoint supports it,
    which is the difference between this stage taking hours and taking days."""
    body = [{"jsonrpc":"2.0","id":i,"method":m,"params":p} for i,(m,p) in enumerate(calls)]
    for a in range(tries):
        _throttle()
        try:
            req = urllib.request.Request(RPC, method="POST",
                data=json.dumps(body).encode(), headers={"Content-Type":"application/json"})
            d = json.loads(urllib.request.urlopen(req, timeout=180).read())
            if isinstance(d, list):
                out = [None]*len(calls)
                for r in d:
                    if isinstance(r.get("id"), int) and "result" in r: out[r["id"]] = r["result"]
                return out
        except Exception:
            time.sleep(min(2 ** a, 30))
    return [None]*len(calls)


def load(n, d=None):
    p = os.path.join(STATE, n)
    return json.load(open(p)) if os.path.exists(p) else d
def save(n, o):
    tmp = os.path.join(STATE, n + ".tmp")
    with open(tmp, "w") as f: json.dump(o, f)
    os.replace(tmp, os.path.join(STATE, n))

def collect_blocks(target):
    man = load("manifest.json") or {}
    if "blockRangeStart" not in man:
        cur = rpc("getSlot", [])["result"]
        # start far enough back that OBSERVATION_HOURS has already elapsed
        hours = SPEC["outcome"]["OBSERVATION_HOURS"]
        man = {"blockRangeStart": cur - int(hours*3600/0.4) - 200_000,
               "declaredTarget": target, "spec": SPEC_PATH,
               "startedAt": int(time.time())}
        save("manifest.json", man)
        print(f"  declared block range start: {man['blockRangeStart']:,} (fixed, not extendable)")
    cursor = load("cursor", man["blockRangeStart"])
    toks = load("tokens.json", {})
    done = load("blocks_done", 0)
    while done < target:
        d = rpc("getBlock", [cursor, {"encoding":"jsonParsed","maxSupportedTransactionVersion":0,
                                      "transactionDetails":"full","rewards":False}])
        cursor += 1
        if "error" not in d and d.get("result"):
            done += 1
            bt = d["result"].get("blockTime")
            for t in d["result"]["transactions"]:
                msg = t["transaction"]["message"]
                signer = next((a["pubkey"] for a in msg["accountKeys"] if a.get("signer")), None)
                groups = [msg.get("instructions", [])]
                groups += [g.get("instructions", []) for g in (t.get("meta") or {}).get("innerInstructions") or []]
                for grp in groups:
                    for ins in grp:
                        p = ins.get("parsed")
                        if isinstance(p, dict) and p.get("type") in ("initializeMint","initializeMint2"):
                            m = p["info"].get("mint")
                            if m and m not in toks:
                                toks[m] = {"deployer": signer, "slot": cursor-1, "born": bt}
        if done % 25 == 0:
            save("cursor", cursor); save("tokens.json", toks); save("blocks_done", done)
            print(f"    {done}/{target} blocks | {len(toks)} tokens | {_n[0]} calls", flush=True)
    save("cursor", cursor); save("tokens.json", toks); save("blocks_done", done)
    print(f"  DONE: {done} blocks, {len(toks)} tokens, {_n[0]} rpc calls")

def liveness(limit):
    """Spec rule: a token enters the population only with >= MIN_DISTINCT_SIGNERS
    distinct signing accounts against its mint within LIVENESS_WINDOW_HOURS."""
    f = SPEC["population"]["livenessFilter"]
    need, window = f["MIN_DISTINCT_SIGNERS"], f["LIVENESS_WINDOW_HOURS"]*3600
    toks = load("tokens.json", {}); live = load("liveness.json", {})
    todo = [m for m in toks if m not in live][:limit]
    print(f"  liveness: {len(todo)} of {len(toks)-len(live)} remaining "
          f"(need >={need} signers within {window//3600}h)")
    for i, m in enumerate(todo):
        born = toks[m].get("born")
        sigs = rpc("getSignaturesForAddress", [m, {"limit": 1000}]).get("result") or []
        inwin = [x["signature"] for x in sigs
                 if born and x.get("blockTime") and 0 <= x["blockTime"]-born <= window]
        signers = set()
        for j in range(0, len(inwin), 20):
            chunk = inwin[j:j+20]
            res = rpc_batch([("getTransaction",
                              [sg, {"encoding":"jsonParsed","maxSupportedTransactionVersion":0}])
                             for sg in chunk])
            for r in res:
                if not r: continue
                for a in r["transaction"]["message"]["accountKeys"]:
                    if a.get("signer"): signers.add(a["pubkey"])
            if len(signers) >= need and len(inwin) > 60: break   # already qualifies
        live[m] = {"txInWindow": len(inwin), "distinctSigners": len(signers),
                   "qualifies": len(signers) >= need,
                   "signers": sorted(signers)[:200]}
        if (i+1) % 20 == 0:
            save("liveness.json", live)
            q = sum(1 for v in live.values() if v["qualifies"])
            print(f"    {i+1}/{len(todo)} | qualifying {q}/{len(live)} | {_n[0]} calls", flush=True)
    save("liveness.json", live)
    q = sum(1 for v in live.values() if v["qualifies"])
    print(f"  DONE: {len(live)} checked, {q} qualify ({q/max(len(live),1):.0%})")


def outcomes(limit):
    """Spec outcome: hours to death, right-censored at OBSERVATION_HOURS."""
    o = SPEC["outcome"]
    idle_s, obs_s = o["DEATH_IDLE_HOURS"]*3600, o["OBSERVATION_HOURS"]*3600
    toks = load("tokens.json", {}); live = load("liveness.json", {})
    out = load("outcomes.json", {})
    pool = [m for m, v in live.items() if v["qualifies"] and m not in out][:limit]
    print(f"  outcomes: {len(pool)} qualifying tokens to measure")
    for i, m in enumerate(pool):
        born = toks[m].get("born")
        sup = rpc("getTokenSupply", [m])
        gone = "error" in sup
        amt = None if gone else sup["result"]["value"]["uiAmount"]
        sigs = rpc("getSignaturesForAddress", [m, {"limit": 1}]).get("result") or []
        last = sigs[0].get("blockTime") if sigs else None
        if gone or amt in (0, None):
            death, why = (last or born), ("mint gone" if gone else "zero supply")
        elif last and (born + obs_s) - last > idle_s:
            death, why = last + idle_s, "idle"
        else:
            death, why = None, "censored"
        out[m] = {"born": born, "lastSeen": last,
                  "hoursToDeath": round((death-born)/3600, 1) if death and born else None,
                  "censored": death is None, "why": why}
        if (i+1) % 20 == 0:
            save("outcomes.json", out); print(f"    {i+1}/{len(pool)} | {_n[0]} calls", flush=True)
    save("outcomes.json", out)
    dead = sum(1 for v in out.values() if not v["censored"])
    print(f"  DONE: {len(out)} measured, {dead} dead ({dead/max(len(out),1):.0%})")
    lo, hi = 0.20, 0.80
    r = dead/max(len(out),1)
    print(f"  effectRequires outcome-variance band 20-80%: "
          f"{'SATISFIED' if lo<=r<=hi else 'FAILED -- spec says STOP and report'}")


def status():
    man = load("manifest.json") or {}
    print(f"  rpc: {'ALCHEMY/private' if not IS_PUBLIC else 'PUBLIC (slow)'} @ {RATE}/s")
    print(f"  blocks done : {load('blocks_done', 0)} / {man.get('declaredTarget','-')}")
    print(f"  tokens      : {len(load('tokens.json', {}))}")
    print(f"  live-checked: {len(load('liveness.json', {}))}")
    print(f"  outcomes    : {len(load('outcomes.json', {}))}")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "blocks": collect_blocks(int(sys.argv[2]))
    elif cmd == "liveness": liveness(int(sys.argv[2]) if len(sys.argv)>2 else 10**9)
    elif cmd == "outcomes": outcomes(int(sys.argv[2]) if len(sys.argv)>2 else 10**9)
    else: status()
