"""Prospective power for the Epistemic Lift confirmatory study.

The decision rule is fixed by v1.0 and v1.1: for EVERY model configuration the
observed C-minus-B difference must meet an effect threshold AND the exact
two-sided paired sign test on discordant B-to-C pairs must return p < 0.05.

Two consequences drive the design.

1. The sign test sees only discordant pairs. With d discordant pairs all in one
   direction the two-sided p-value is 2 * 0.5**d, so d must reach 6 before any
   result can clear 0.05. No sample size rescues a run that produces five
   improvements and no regressions.
2. The study passes only if every model passes. Joint power is the product of
   the per-model powers, so a design adequate for one model is not adequate
   for two.

Run: python3 evaluations/multi-model-v1/lift-power.py
"""

from __future__ import annotations

from math import comb

ALPHA = 0.05
MODELS = 2
EFFECT_THRESHOLD = 0.10
TARGET_JOINT_POWER = 0.80


def sign_test_p(improvements: int, regressions: int) -> float:
    """Exact two-sided paired sign test.

    Reproduces the v1.1 reported values: 9 improvements and 0 regressions gives
    0.00390625; 7 and 0 gives 0.015625.
    """
    d = improvements + regressions
    if d == 0:
        return 1.0
    extreme = max(improvements, regressions)
    tail = sum(comb(d, k) for k in range(extreme, d + 1)) * 0.5**d
    return min(1.0, 2 * tail)


def power(n: int, p_improve: float, p_regress: float,
          effect_threshold: float = EFFECT_THRESHOLD) -> float:
    """Exact P(reject) for one model over the trinomial outcome space."""
    p_same = 1.0 - p_improve - p_regress
    if p_same < 0:
        raise ValueError("improvement and regression rates exceed 1")
    total = 0.0
    for i in range(n + 1):
        for j in range(n - i + 1):
            k = n - i - j
            prob = (comb(n, i) * comb(n - i, j)
                    * p_improve**i * p_regress**j * p_same**k)
            if prob == 0.0:
                continue
            if (i - j) / n >= effect_threshold and sign_test_p(i, j) < ALPHA:
                total += prob
    return total


SCENARIOS = (
    ("conservative", 0.10, 0.02),
    ("moderate", 0.125, 0.01),
    ("v1.1-like", 0.25, 0.00),
)


def main() -> None:
    print("Exact two-sided sign test: minimum discordant pairs to clear alpha")
    for d in range(4, 8):
        p = 2 * 0.5**d
        print(f"  d={d}  p={p:.6f}  {'PASS' if p < ALPHA else 'fail'}")
    print()

    print(f"Effect threshold {EFFECT_THRESHOLD:.2f}, below the 0.15 used in v1.0 and v1.1.")
    print(f"Joint power = per-model power ** {MODELS}, because every model must pass.")
    print()
    print(f"{'worlds':>7}" + "".join(f"{name:>20}" for name, _, _ in SCENARIOS))
    print(f"{'':>7}" + "".join(f"{'per / joint':>20}" for _ in SCENARIOS))

    chosen = None
    for n in (32, 48, 64, 96, 128, 160):
        row = f"{n:>7}"
        joints = []
        for _, pi, pr in SCENARIOS:
            per = power(n, pi, pr)
            joints.append(per**MODELS)
            row += f"{per:>9.2f} /{joints[-1]:>9.2f}"
        print(row)
        if chosen is None and joints[0] >= TARGET_JOINT_POWER:
            chosen = n

    print()
    for name, pi, pr in SCENARIOS:
        print(f"  {name:<13} improve {pi:.3f}  regress {pr:.3f}")
    print()
    if chosen:
        print(f"Smallest N meeting joint power {TARGET_JOINT_POWER:.2f} "
              f"under the conservative scenario: {chosen} worlds per model.")
    else:
        print(f"No tested N reaches joint power {TARGET_JOINT_POWER:.2f} "
              "under the conservative scenario.")


if __name__ == "__main__":
    main()
