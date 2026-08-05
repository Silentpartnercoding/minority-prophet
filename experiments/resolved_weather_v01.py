"""Acquire and score Experiment 002's resolved binary weather markets.

Provider-specific records are consumed at this boundary.  Committed outputs
contain only normalized forecasts, outcomes, counts, and source identifiers;
wallet identifiers and raw trades remain outside the repository.
"""

from __future__ import annotations

import argparse
import json
import random
import time
import urllib.parse
import urllib.request
from urllib.error import HTTPError
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from statistics import mean
from typing import Any

from aggregation.markets import Trade, aggregate_trades, brier


GAMMA = "https://gamma-api.polymarket.com"
DATA = "https://data-api.polymarket.com"
CLOB = "https://clob.polymarket.com"
WEATHER_TAG_ID = "84"


def timestamp(value: str) -> int:
    return int(datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp())


def get_json(url: str, retries: int = 4) -> Any:
    for attempt in range(retries):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "minority-prophet/0.1"})
            with urllib.request.urlopen(request, timeout=45) as response:
                return json.load(response)
        except Exception:
            if attempt + 1 == retries:
                raise
            time.sleep(2**attempt)
    raise RuntimeError("unreachable")


def fetch_event_frame(max_offset: int = 2000) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for offset in range(0, max_offset + 1, 100):
        query = urllib.parse.urlencode(
            {"tag_id": WEATHER_TAG_ID, "closed": "true", "limit": 100, "offset": offset}
        )
        page = get_json(f"{GAMMA}/events?{query}")
        events.extend(page)
        if len(page) < 100:
            break
    return events


def metadata_candidates(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    candidates = []
    for event in events:
        for market in event.get("markets", []):
            try:
                outcomes = json.loads(market["outcomes"])
                prices = [float(value) for value in json.loads(market["outcomePrices"])]
                tokens = json.loads(market["clobTokenIds"])
                start, end = timestamp(market["startDate"]), timestamp(market["endDate"])
                duration = (end - start) / 86_400
                volume = float(market.get("volumeNum") or market.get("volume") or 0)
            except (KeyError, TypeError, ValueError, json.JSONDecodeError):
                continue
            if not (
                market.get("closed") is True
                and len(outcomes) == len(prices) == len(tokens) == 2
                and sorted(prices) == [0.0, 1.0]
                and 1 <= duration <= 90
                and volume >= 1_000
            ):
                continue
            yes_index = next((index for index, value in enumerate(outcomes) if value == "Yes"), None)
            if yes_index is None:
                continue
            candidates.append(
                {
                    "market_id": str(market["id"]),
                    "condition_id": market["conditionId"],
                    "question": market["question"],
                    "start": start,
                    "end": end,
                    "cutoff": end - 86_400,
                    "yes_token": tokens[yes_index],
                    "yes_outcome_index": yes_index,
                    "outcome": int(prices[yes_index]),
                    "volume": volume,
                }
            )
    return sorted(candidates, key=lambda row: (row["start"], row["market_id"]), reverse=True)


def fetch_market(candidate: dict[str, Any]) -> dict[str, Any] | None:
    cutoff = candidate["cutoff"]
    price_query = urllib.parse.urlencode(
        {
            "market": candidate["yes_token"],
            "startTs": candidate["start"],
            "endTs": cutoff,
            "fidelity": 60,
        }
    )
    try:
        history = get_json(f"{CLOB}/prices-history?{price_query}").get("history", [])
    except HTTPError as error:
        if error.code in {400, 404, 422}:
            return None
        raise
    prices = [point for point in history if int(point["t"]) <= cutoff]
    if not prices:
        return None

    trade_query = urllib.parse.urlencode(
        {"market": candidate["condition_id"], "limit": 10_000, "offset": 0}
    )
    records = get_json(f"{DATA}/trades?{trade_query}")
    if len(records) == 10_000:
        second_query = urllib.parse.urlencode(
            {"market": candidate["condition_id"], "limit": 10_000, "offset": 10_000}
        )
        second = get_json(f"{DATA}/trades?{second_query}")
        if len(second) == 10_000:
            return None
        records.extend(second)

    trades = [
        Trade(
            wallet=record["proxyWallet"],
            timestamp=int(record["timestamp"]),
            size=float(record["size"]),
            side=record["side"],
            outcome_index=(
                0
                if int(record["outcomeIndex"]) == candidate["yes_outcome_index"]
                else 1
            ),
        )
        for record in records
        if record.get("proxyWallet") and int(record["timestamp"]) <= cutoff
    ]
    forecast = aggregate_trades(trades, cutoff=cutoff)
    if forecast.wallets < 10:
        return None
    return {
        "market_id": candidate["market_id"],
        "cutoff": datetime.fromtimestamp(cutoff, timezone.utc).isoformat(),
        "outcome": candidate["outcome"],
        "market_probability": float(max(prices, key=lambda point: point["t"])["p"]),
        **asdict(forecast),
    }


def score(rows: list[dict[str, Any]], frame: dict[str, Any]) -> dict[str, Any]:
    methods = ["market_probability", "one_wallet", "exposure_weighted", "dependence_adjusted"]
    metrics: dict[str, Any] = {}
    for method in methods:
        values = [(row[method], row["outcome"]) for row in rows if row[method] is not None]
        metrics[method] = {
            "n": len(values),
            "brier": mean(brier(probability, outcome) for probability, outcome in values),
            "accuracy": mean((probability >= 0.5) == bool(outcome) for probability, outcome in values),
            "ece_10_bins": calibration_error(values),
        }
    answered = [row for row in rows if row["abstaining_dependence_adjusted"] is not None]
    metrics["abstaining_dependence_adjusted"] = {
        "n": len(answered),
        "coverage": len(answered) / len(rows),
        "accuracy": mean(
            (row["abstaining_dependence_adjusted"] >= 0.5) == bool(row["outcome"])
            for row in answered
        )
        if answered
        else None,
    }
    paired = [
        brier(row["one_wallet"], row["outcome"])
        - brier(row["dependence_adjusted"], row["outcome"])
        for row in rows
    ]
    generator = random.Random(20260805)
    bootstrap = sorted(
        mean(generator.choice(paired) for _ in paired) for _ in range(10_000)
    )
    improvement = mean(paired)
    underdogs = [row for row in rows if row["one_wallet"] < 0.5 and row["outcome"] == 1]
    one_correct = [
        row for row in rows if (row["one_wallet"] >= 0.5) == bool(row["outcome"])
    ]
    diagnostics = {
        "paired_brier_improvement_dependence_over_wallet": improvement,
        "paired_brier_improvement_95_ci": [bootstrap[249], bootstrap[9749]],
        "correct_underdog_cases": len(underdogs),
        "correct_underdog_recovery": {
            method: sum(row[method] >= 0.5 for row in underdogs)
            for method in ("exposure_weighted", "dependence_adjusted")
        },
        "false_majority_reversal_rate": {
            method: mean(
                (row[method] >= 0.5) != bool(row["outcome"]) for row in one_correct
            )
            if one_correct
            else None
            for method in ("exposure_weighted", "dependence_adjusted")
        },
    }
    return {
        "schema_version": "0.1",
        "frame": frame,
        "metrics": metrics,
        "diagnostics": diagnostics,
        "markets": rows,
    }


def calibration_error(values: list[tuple[float, int]]) -> float:
    if not values:
        return 0.0
    error = 0.0
    for index in range(10):
        lower, upper = index / 10, (index + 1) / 10
        group = [
            (probability, outcome)
            for probability, outcome in values
            if lower <= probability < upper or (index == 9 and probability == 1.0)
        ]
        if group:
            error += len(group) / len(values) * abs(
                mean(probability for probability, _ in group)
                - mean(outcome for _, outcome in group)
            )
    return error


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-limit", type=int, default=0)
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    events = fetch_event_frame()
    candidates = metadata_candidates(events)
    selected = candidates[: args.candidate_limit or None]
    rows = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(fetch_market, candidate): candidate for candidate in selected}
        for index, future in enumerate(as_completed(futures), 1):
            row = future.result()
            if row is not None:
                rows.append(row)
            if index % 100 == 0:
                print(f"processed={index} eligible={len(rows)}", flush=True)
    rows.sort(key=lambda row: row["market_id"])
    frame = {
        "acquired_at": datetime.now(timezone.utc).isoformat(),
        "weather_tag_id": WEATHER_TAG_ID,
        "events_returned": len(events),
        "metadata_candidates": len(candidates),
        "candidates_processed": len(selected),
        "eligible_markets": len(rows),
        "candidate_limit": args.candidate_limit or None,
        "confirmatory": args.candidate_limit == 0 and len(rows) >= 100,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(score(rows, frame), indent=2) + "\n")
    print(json.dumps(frame, indent=2))


if __name__ == "__main__":
    main()
