"""Exploratory incident-reconstruction demo.

Lane: EXPLORATORY. Output is a labeled fixture and a prototype. It is not a
canonical result and no claim here is promoted.

    python3 experiments/incident-reconstruction/run_incident_reconstruction.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

from reconstruct import reconstruct  # noqa: E402
from report import render  # noqa: E402
from scenario import pressure_vessel_incident  # noqa: E402

REDACTED = frozenset({"claim-A", "claim-B", "claim-C", "claim-D"})


def main() -> int:
    record, truth = pressure_vessel_incident()

    full = reconstruct(record)
    print(render(record, full))
    print()

    degraded_record = record.redacted(drop_roots_for=REDACTED)
    degraded = reconstruct(degraded_record)
    print(render(degraded_record, degraded))
    print()

    print("=" * 72)
    print("SELF-CHECK against held-out ground truth")
    print("=" * 72)
    checks = (
        ("full run recovers the true independent-root count", full.independent_roots == 1),
        ("full run reports fewer roots than apparent agreement",
         full.independent_roots < truth.apparent_agreement),
        ("full run names the suppressed claim",
         any("claim-D" in f.statement for f in full.findings)),
        ("full run reaches a supported finding", full.is_determinate),
        ("degraded run refuses rather than guesses", not degraded.is_determinate),
        ("degraded run names the telemetry it needed", bool(degraded.missing_telemetry)),
    )
    failures = 0
    for label, ok in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
        failures += 0 if ok else 1
    print()
    print("Ground truth, never shown to the reconstructor:")
    print(f"  {truth.narrative}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
