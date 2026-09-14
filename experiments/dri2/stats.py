"""Statistics for DRI-2, in the standard library only. DRAFT, NOT FROZEN."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from fractions import Fraction

Z95 = 1.959963984540054


def wilson_interval(successes: int, trials: int, z: float = Z95) -> tuple[float | None, float | None]:
    if trials == 0:
        return None, None
    p = successes / trials
    z2 = z * z
    denominator = 1 + z2 / trials
    centre = (p + z2 / (2 * trials)) / denominator
    half = z * math.sqrt(p * (1 - p) / trials + z2 / (4 * trials * trials)) / denominator
    return max(0.0, centre - half), min(1.0, centre + half)


def mcnemar_exact(first_only: int, second_only: int) -> float:
    """Two-sided exact McNemar test on the discordant pairs."""
    n = first_only + second_only
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, i) for i in range(min(first_only, second_only) + 1))
    return float(min(Fraction(1), Fraction(2 * tail, 2**n)))


def paired_difference_interval(
    first_only: int, second_only: int, pairs: int, z: float = Z95
) -> tuple[float | None, float | None, float | None]:
    """Difference in paired proportions (first minus second) with a Wald interval."""
    if pairs == 0:
        return None, None, None
    difference = (first_only - second_only) / pairs
    variance = (first_only + second_only - (first_only - second_only) ** 2 / pairs) / pairs**2
    half = z * math.sqrt(max(variance, 0.0))
    return difference, difference - half, difference + half


def holm(pvalues: Mapping[str, float]) -> dict[str, float]:
    """Holm step-down adjusted p-values."""
    ordered = sorted(pvalues.items(), key=lambda item: (item[1], item[0]))
    total = len(ordered)
    adjusted: dict[str, float] = {}
    running = 0.0
    for rank, (name, value) in enumerate(ordered):
        running = max(running, min(1.0, (total - rank) * value))
        adjusted[name] = running
    return adjusted


def wilcoxon_signed_rank(differences: Sequence[float]) -> dict[str, float | int]:
    """Two-sided Wilcoxon signed-rank test, normal approximation with tie and
    continuity correction. Zero differences are dropped."""
    nonzero = [value for value in differences if value != 0]
    n = len(nonzero)
    if n == 0:
        return {"n": 0, "wPlus": 0.0, "z": 0.0, "p": 1.0}
    order = sorted(range(n), key=lambda i: abs(nonzero[i]))
    ranks = [0.0] * n
    tie_sizes: list[int] = []
    start = 0
    while start < n:
        end = start
        while end + 1 < n and abs(nonzero[order[end + 1]]) == abs(nonzero[order[start]]):
            end += 1
        average = (start + end) / 2 + 1
        for position in range(start, end + 1):
            ranks[order[position]] = average
        if end > start:
            tie_sizes.append(end - start + 1)
        start = end + 1
    w_plus = sum(rank for rank, value in zip(ranks, nonzero) if value > 0)
    mean = n * (n + 1) / 4
    variance = n * (n + 1) * (2 * n + 1) / 24 - sum(t**3 - t for t in tie_sizes) / 48
    if variance <= 0:
        return {"n": n, "wPlus": w_plus, "z": 0.0, "p": 1.0}
    delta = w_plus - mean
    magnitude = max(abs(delta) - 0.5, 0.0) / math.sqrt(variance)
    z = math.copysign(magnitude, delta)
    return {"n": n, "wPlus": w_plus, "z": z, "p": min(1.0, math.erfc(magnitude / math.sqrt(2)))}


def mean_interval(values: Sequence[float], z: float = Z95) -> tuple[float | None, float | None, float | None]:
    n = len(values)
    if n == 0:
        return None, None, None
    mean = sum(values) / n
    if n < 2:
        return mean, None, None
    variance = sum((value - mean) ** 2 for value in values) / (n - 1)
    half = z * math.sqrt(variance / n)
    return mean, mean - half, mean + half
