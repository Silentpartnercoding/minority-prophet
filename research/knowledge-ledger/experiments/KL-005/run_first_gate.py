#!/usr/bin/env python3
"""KL-005 first gate: wire copies and circular citations cannot count as
independent confirmation -- and the metric must penalise silence.

Deterministic. No inference, no network. Writes probe/first-gate.json.
"""

from __future__ import annotations

import collections
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from src.metric import Event, Judgement, delay_cost, one_sided_score, two_sided_score  # noqa: E402
from src.syndication import independent_origins, resolve_root  # noqa: E402


def main() -> int:
    fx = json.loads((HERE / "fixtures/syndication.json").read_text())
    reports = fx["reports"]

    by_event = collections.defaultdict(list)
    for rid, r in reports.items():
        by_event[r["event"]].append(rid)

    counting = {}
    for eid, rids in by_event.items():
        origins = independent_origins(rids, reports)
        counting[eid] = {
            "reports": len(rids),
            "independentOrigins": len(origins),
            "collapsedBy": len(rids) - len(origins),
            "circular": all(resolve_root(r, reports) is None for r in rids),
        }

    events = [Event(e["eventId"], e["isTrue"], e["independentlyReportableAt"])
              for e in fx["events"]]

    scores = {}
    for name, sysdef in fx["systems"].items():
        js = [Judgement(eid, day) for eid, day in sysdef["judgements"].items()]
        scores[name] = {
            "note": sysdef["note"],
            "oneSided": round(one_sided_score(events, js), 6),
            "delayCost": round(delay_cost(events, js), 6),
            "twoSided": round(two_sided_score(events, js), 6),
        }

    one_best = min(scores, key=lambda n: scores[n]["oneSided"])
    two_best = min(scores, key=lambda n: scores[n]["twoSided"])
    silent_wins_one = scores["silent"]["oneSided"] <= min(s["oneSided"] for s in scores.values())
    silent_wins_two = scores["silent"]["twoSided"] <= min(s["twoSided"] for s in scores.values())

    gate_a = all(c["independentOrigins"] < c["reports"] or c["reports"] == c["independentOrigins"]
                 for c in counting.values())
    # The gate proper: no syndicated or circular event may present more
    # independent origins than it truly has.
    gate_syndication = (counting["E1-true-wire"]["independentOrigins"] == 1
                        and counting["E2-false-cycle"]["independentOrigins"] == 0
                        and counting["E4-false-single"]["independentOrigins"] == 1
                        and counting["E3-true-three"]["independentOrigins"] == 3)
    gate_metric = (not silent_wins_two) and silent_wins_one

    result = {
        "schema": "minority-prophet.kl005-first-gate.v1",
        "gates": {
            "syndicationCannotManufactureIndependence": gate_syndication,
            "twoSidedMetricDeniesSilenceTheWin": gate_metric,
        },
        "counting": counting,
        "scores": scores,
        "oneSidedWinner": one_best,
        "twoSidedWinner": two_best,
        "silentWinsUnderOneSided": silent_wins_one,
        "silentWinsUnderTwoSided": silent_wins_two,
        "boundaries": [
            "This is a structural fixture, not a news corpus. No rate is reported and none is derivable; KL-005 proper requires timestamped closed real events.",
            "The metric's weights are declared equal, not fitted. Any weighting that lets one term dominate reintroduces the single-endpoint defect in the other direction.",
            "A circular citation resolving to zero origins is fail-closed by choice. It refuses to mint an origin that does not exist, at the cost of discarding a genuine original that is only reachable through a cycle.",
            "Root collapse here trusts declared descent. It does not detect an undisclosed wire relationship, which is the journalism analogue of ADV-001's under-declared search space.",
        ],
    }
    (HERE / "probe/first-gate.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ("gates", "counting", "scores", "oneSidedWinner", "twoSidedWinner")}, indent=2))
    return 0 if (gate_syndication and gate_metric) else 1


if __name__ == "__main__":
    raise SystemExit(main())
