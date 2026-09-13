"""Render an Agent Incident Attribution Report from a reconstruction."""

from __future__ import annotations

from reconstruct import Reconstruction
from record import ForensicRecord

RULE = "=" * 72


def render(record: ForensicRecord, rec: Reconstruction) -> str:
    out: list[str] = []
    add = out.append

    add(RULE)
    add(f"AGENT INCIDENT ATTRIBUTION REPORT v0.1")
    add(f"Incident: {rec.incident_id}")
    add(RULE)
    add("")
    add("1. EXECUTIVE SUMMARY")
    add(f"   {record.summary}")
    add(f"   Outcome: {record.outcome}")
    add("")

    add("2. EXECUTION TIMELINE")
    for e in record.execution:
        tgt = f" -> {e.target}" if e.target else ""
        add(f"   {e.seq:>2}. {e.actor}{tgt}: {e.action}. {e.detail}".rstrip())
    add("")

    add("3. FINDINGS")
    for i, f in enumerate(rec.findings, 1):
        marker = "   " if f.determinate else "  !"
        add(f"{marker}{i}. {f.heading}")
        add(f"      {f.statement}")
        for s in f.support:
            if s and s.strip():
                add(f"        - {s}")
        add("")

    add("4. WHAT CANNOT BE DETERMINED")
    if rec.indeterminate:
        for s in rec.indeterminate:
            add(f"   - BLOCKING: {s}")
    else:
        add("   Nothing blocking. The attribution above is supported by the record.")
    for s in rec.limitations:
        add(f"   - NOTED: {s}")
    add("")

    add("5. MISSING TELEMETRY")
    if rec.missing_telemetry:
        add("   The following would have been required to answer the open questions:")
        for s in rec.missing_telemetry:
            add(f"   - {s}")
    else:
        add("   None. The record was sufficient for this reconstruction.")
    add("")

    add("6. LIMITATIONS")
    add("   This report reconstructs evidence, authority and sequence. It does not")
    add("   assign legal liability, and it does not assert any actor's mental state")
    add("   beyond information demonstrably present in the record.")
    add("")
    add(RULE)
    verdict_line = (
        f"Apparent support {rec.apparent_support} -> independent roots {rec.independent_roots}"
        if rec.is_determinate else "Independence: INDETERMINATE"
    )
    add(f"RESULT: {verdict_line}")
    add(RULE)
    return "\n".join(out)
