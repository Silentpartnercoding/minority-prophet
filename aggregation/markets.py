"""Provider-neutral aggregation of public binary-market trading behavior."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from math import sqrt
from typing import Iterable


@dataclass(frozen=True)
class Trade:
    wallet: str
    timestamp: int
    size: float
    side: str
    outcome_index: int


@dataclass(frozen=True)
class MarketForecast:
    one_wallet: float | None
    exposure_weighted: float | None
    dependence_adjusted: float | None
    abstaining_dependence_adjusted: float | None
    wallets: int
    components: int


def signed_yes_exposure(trade: Trade) -> float:
    """Map YES/NO buys and sells onto one signed YES-exposure axis."""
    outcome_sign = 1.0 if trade.outcome_index == 0 else -1.0
    side_sign = 1.0 if trade.side.upper() == "BUY" else -1.0
    return trade.size * outcome_sign * side_sign


def _cosine(left: dict[int, float], right: dict[int, float]) -> tuple[float, int]:
    shared = left.keys() & right.keys()
    jointly_active = sum(left[key] != 0 and right[key] != 0 for key in shared)
    keys = left.keys() | right.keys()
    dot = sum(left.get(key, 0.0) * right.get(key, 0.0) for key in keys)
    left_norm = sqrt(sum(value * value for value in left.values()))
    right_norm = sqrt(sum(value * value for value in right.values()))
    if left_norm == 0 or right_norm == 0:
        return 0.0, jointly_active
    return dot / (left_norm * right_norm), jointly_active


def aggregate_trades(
    trades: Iterable[Trade],
    *,
    cutoff: int,
    similarity_threshold: float = 0.90,
    minimum_joint_bins: int = 3,
) -> MarketForecast:
    """Compute the four frozen wallet-based forecasts from pre-cutoff trades."""
    exposure: dict[str, float] = defaultdict(float)
    hourly: dict[str, dict[int, float]] = defaultdict(lambda: defaultdict(float))
    for trade in trades:
        if trade.timestamp > cutoff:
            continue
        signed = signed_yes_exposure(trade)
        exposure[trade.wallet] += signed
        hourly[trade.wallet][trade.timestamp // 3600] += signed

    exposure = {wallet: value for wallet, value in exposure.items() if value != 0}
    wallets = sorted(exposure)
    if not wallets:
        return MarketForecast(None, None, None, None, 0, 0)

    positive = sum(value > 0 for value in exposure.values())
    one_wallet = positive / len(wallets)
    total_exposure = sum(abs(value) for value in exposure.values())
    exposure_weighted = sum(max(0.0, value) for value in exposure.values()) / total_exposure

    parent = {wallet: wallet for wallet in wallets}

    def find(wallet: str) -> str:
        while parent[wallet] != wallet:
            parent[wallet] = parent[parent[wallet]]
            wallet = parent[wallet]
        return wallet

    def union(left: str, right: str) -> None:
        left_root, right_root = find(left), find(right)
        if left_root != right_root:
            parent[right_root] = left_root

    for index, left in enumerate(wallets):
        for right in wallets[index + 1 :]:
            similarity, joint_bins = _cosine(hourly[left], hourly[right])
            if joint_bins >= minimum_joint_bins and similarity >= similarity_threshold:
                union(left, right)

    component_exposure: dict[str, float] = defaultdict(float)
    for wallet in wallets:
        component_exposure[find(wallet)] += exposure[wallet]
    directions = [value for value in component_exposure.values() if value != 0]
    components = len(directions)
    dependence_adjusted = (
        sum(value > 0 for value in directions) / components if components else None
    )
    abstaining = dependence_adjusted
    if components < 10 or (
        dependence_adjusted is not None and 0.45 <= dependence_adjusted <= 0.55
    ):
        abstaining = None
    return MarketForecast(
        one_wallet,
        exposure_weighted,
        dependence_adjusted,
        abstaining,
        len(wallets),
        components,
    )


def brier(probability: float, outcome: int) -> float:
    return (probability - outcome) ** 2
