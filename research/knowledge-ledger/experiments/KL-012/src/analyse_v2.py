#!/usr/bin/env python3
"""KL-012 v0.2 analysis. Written before the funder trace finished.

Endpoint, frozen in COLLECTION-SPEC-v0.2.json:
  H0  graduated and non-graduated tokens have the same creator-clustering rate
  statistic  share of creators in each group inside a multi-creator funding cluster
  test  Fisher exact, two-sided
  DIRECTION PREDICTED IN ADVANCE: controls (non-graduated) cluster MORE

A result in the opposite direction is a failure, not a discovery. That is what
predicting the direction is for.

Stdlib only.
"""
import json, os, sys
from math import comb

HERE=os.path.dirname(os.path.abspath(__file__)); ST=os.path.join(HERE,"kl012v2")
SPEC_ENV = os.environ.get("KL012_SPEC_V2")
def _spec():
    """Locate the frozen spec relative to this file, or via KL012_SPEC_V2.
    Never a hardcoded home path: that is the defect the boundary check exists for
    and it has now caught it five times in one day."""
    if SPEC_ENV and os.path.exists(SPEC_ENV): return SPEC_ENV
    import pathlib as _p
    for base in _p.Path(os.path.abspath(__file__)).resolve().parents:
        for rel in ("COLLECTION-SPEC-v0.2.json",
                    "research/knowledge-ledger/experiments/KL-012/COLLECTION-SPEC-v0.2.json"):
            if (base/rel).exists(): return str(base/rel)
    sys.exit("refusing to run: frozen spec v0.2 not found (set KL012_SPEC_V2)")
SPEC=json.load(open(_spec()))
MAX_HOPS=SPEC["exposure"]["MAX_HOPS"]


def fisher(a,b,c,d):
    """two-sided exact test on [[a,b],[c,d]]"""
    n=a+b+c+d; r1=a+b; c1=a+c
    def p(x):
        if x<0 or x>min(r1,c1) or r1-x>n-c1: return 0.0
        return comb(c1,x)*comb(n-c1,r1-x)/comb(n,r1)
    obs=p(a)
    return sum(p(x) for x in range(0,min(r1,c1)+1) if p(x)<=obs+1e-12)


def clusters(creators, funders, hubs):
    """Union-find over shared non-hub funders. One level, because the trace stores
    one funder per creator; deeper hops need the ancestor walk and are recorded as
    a limitation rather than silently approximated."""
    parent={c:c for c in creators}
    def find(x):
        while parent[x]!=x: parent[x]=parent[parent[x]]; x=parent[x]
        return x
    def union(a,b):
        ra,rb=find(a),find(b)
        if ra!=rb: parent[ra]=rb
    owner={}
    for c in creators:
        f=(funders.get(c) or {}).get("funder")
        if not f or f in hubs: continue
        if f in owner: union(c,owner[f])
        else: owner[f]=c
    groups={}
    for c in creators: groups.setdefault(find(c),[]).append(c)
    return groups


def main():
    pop=json.load(open(os.path.join(ST,"population.json")))
    fp=os.path.join(ST,"creator_funders.json")
    if not os.path.exists(fp): print("  funder trace not finished"); return
    funders=json.load(open(fp))

    cre_case={v["creator"] for v in pop["cases"].values()}
    cre_ctrl={v["creator"] for v in pop["controls"].values()}
    overlap=cre_case&cre_ctrl
    cre_case-=overlap; cre_ctrl-=overlap        # a creator in both groups is ambiguous
    allc=sorted(cre_case|cre_ctrl)
    traced=[c for c in allc if c in funders]
    print(f"  creators: cases {len(cre_case)} controls {len(cre_ctrl)} "
          f"(dropped {len(overlap)} appearing in both)")
    print(f"  traced: {len(traced)}/{len(allc)}")
    if len(traced)<len(allc):
        print("  trace incomplete -- rerun when it finishes"); return

    # hub rule: a funder is a hub if it funded many creators, or its history was
    # not fully retrievable. Fails closed: an unknown funder merges nothing.
    from collections import Counter
    fc=Counter((funders[c] or {}).get("funder") for c in traced
               if (funders[c] or {}).get("funder"))
    HUB_FANOUT=int(os.environ.get("HUB_FANOUT","25"))
    hubs={f for f,n in fc.items() if n>=HUB_FANOUT}
    hubs|={(funders[c] or {}).get("funder") for c in traced
           if not (funders[c] or {}).get("historyComplete")
           and (funders[c] or {}).get("funder")}
    print(f"  distinct funders {len(fc)} | treated as HUBS {len(hubs)} "
          f"(fanout>={HUB_FANOUT} or history incomplete)")

    groups=clusters(traced, funders, hubs)
    multi={r for r,m in groups.items() if len(m)>1}
    inmulti={c for r in multi for c in groups[r]}
    print(f"  clusters {len(groups)} | multi-creator clusters {len(multi)} "
          f"| creators inside one {len(inmulti)}")

    if not multi:
        print("\n  effectRequires FAILED: no multi-creator cluster exists, so voice")
        print("  and root counts are identical and the endpoint is unreachable. STOP.")
        return
    print("  effectRequires: SATISFIED\n")

    a=len([c for c in cre_ctrl if c in inmulti]); b=len(cre_ctrl)-a
    c_=len([c for c in cre_case if c in inmulti]); d=len(cre_case)-c_
    pa=a/max(a+b,1); pc=c_/max(c_+d,1)
    print(f"  {'group':<12}{'clustered':>10}{'not':>8}{'n':>7}{'rate':>9}")
    print(f"  {'controls':<12}{a:>10}{b:>8}{a+b:>7}{pa:>8.1%}")
    print(f"  {'cases':<12}{c_:>10}{d:>8}{c_+d:>7}{pc:>8.1%}")
    p=fisher(a,b,c_,d)
    print(f"\n  Fisher exact two-sided p = {p:.5f}")
    predicted = pa > pc
    print(f"  predicted direction (controls cluster MORE): {'HELD' if predicted else 'REVERSED'}")
    if p<0.05 and predicted:
        print("  ENDPOINT MET")
    elif p<0.05 and not predicted:
        print("  ENDPOINT NOT MET -- significant in the OPPOSITE direction to the")
        print("  registered prediction. This is a failure, not a finding.")
    else:
        print("  ENDPOINT NOT MET -- no significant difference")


if __name__=="__main__":
    main()
