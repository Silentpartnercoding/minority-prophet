"""Reconstruct an incident from the forensic record alone.

The reconstructor never receives `GroundTruth`. Everything below is derived from
what the record retained, and anything the record does not support is reported
as indeterminate rather than inferred.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from aggregation.root_vote import Verdict, verdict

from record import ForensicRecord


@dataclass(frozen=True)
class Finding:
    heading: str
    statement: str
    support: tuple[str, ...] = ()
    determinate: bool = True


@dataclass(frozen=True)
class Reconstruction:
    incident_id: str
    findings: tuple[Finding, ...]
    indeterminate: tuple[str, ...]
    """Gaps that BLOCK an attribution hypothesis."""
    limitations: tuple[str, ...]
    """Gaps that narrow the report but do not block attribution."""
    missing_telemetry: tuple[str, ...]
    evidence_verdict: str
    apparent_support: int
    independent_roots: int

    @property
    def is_determinate(self) -> bool:
        return not self.indeterminate


def reconstruct(record: ForensicRecord) -> Reconstruction:
    findings: list[Finding] = []
    indeterminate: list[str] = []
    limitations: list[str] = []
    missing: list[str] = []

    supporting = [c for c in record.evidence if c.value and c.suppressed_at is None]
    contradicting = [c for c in record.evidence if not c.value]
    considered = [c for c in record.evidence if c.suppressed_at is None]

    # --- evidence independence, via the canonical dependence-aware aggregator ---
    v = verdict(considered)
    roots_for = len(v.support_true)
    roots_against = len(v.support_false)

    findings.append(Finding(
        "Decision-critical belief",
        f"The consequential action rested on the belief that {record.decision_claim!r}.",
        tuple(f"{e.seq}. {e.actor} {e.action} {e.detail}".rstrip()
              for e in record.execution if e.action in {"decide", "invoke"}),
    ))

    if v.unattributed:
        indeterminate.append(
            f"{v.unattributed} claim(s) carry no recorded evidentiary root, so the "
            "number of independent sources cannot be established from this record.")
        missing.append("Per-claim evidentiary root or derivation edge for every recorded belief.")
        findings.append(Finding(
            "Evidence independence",
            "Cannot be determined. The record does not say where these beliefs came from.",
            determinate=False,
        ))
    else:
        findings.append(Finding(
            "Evidence independence",
            (f"{len(supporting)} supporting claim(s) resolve to {roots_for} independent "
             f"evidentiary root(s). Apparent agreement overstated independent support by "
             f"{len(supporting) - roots_for}."),
            tuple(f"{c.claim_id} from {c.asserted_by}: origin {c.origin_type}"
                  + (f", derived_from {c.derived_from}" if c.derived_from else "")
                  + f" -> root {c.root_id}"
                  for c in supporting),
        ))
        findings.append(Finding(
            "Verdict on the evidence as presented",
            (f"Dependence-aware verdict: {v.verdict.value}. Signed margin {v.margin}, "
             f"reversible by {v.conversions_to_reverse} side conversion(s). "
             f"Weakest counted basis: {v.weakest_basis}."),
        ))

        # A typed origin that disagrees with the root structure is the failure
        # this programme keeps hitting: a status asserted beside an artifact that
        # contradicts it. Check the two against each other rather than trusting
        # either alone.
        disagreements = [
            c.claim_id for c in record.evidence
            if (c.origin_type == "observation" and c.derived_from)
        ]
        roots_claiming_observation: dict[str, list[str]] = {}
        for c in record.evidence:
            if c.origin_type == "observation" and c.root_id:
                roots_claiming_observation.setdefault(c.root_id, []).append(c.claim_id)
        disagreements += [
            cid for ids in roots_claiming_observation.values() if len(ids) > 1
            for cid in ids
        ]
        if disagreements:
            findings.append(Finding(
                "Origin and structure disagree",
                (f"Claim(s) {', '.join(sorted(set(disagreements)))} declare a direct "
                 "observation that the recorded topology contradicts, either by carrying "
                 "a derivation edge or by sharing a root with another declared "
                 "observation. The declaration and the structure cannot both be right."),
            ))

    # --- suppression ---
    suppressed = [c for c in record.evidence if c.suppressed_at]
    if suppressed:
        for c in suppressed:
            findings.append(Finding(
                "Suppressed contradiction",
                (f"{c.claim_id} from {c.asserted_by} contradicted the decision and was "
                 f"removed at {c.suppressed_at} before the decision was taken."),
                (c.note,),
            ))
        if not v.unattributed:
            with_suppressed = verdict(record.evidence)
            findings.append(Finding(
                "Counterfactual on the suppressed evidence",
                (f"Had the suppressed claim reached the decision point, the verdict over "
                 f"independent roots would have been {with_suppressed.verdict.value} "
                 f"(margin {with_suppressed.margin}), not {v.verdict.value}."),
            ))
    elif contradicting:
        findings.append(Finding("Contradictions", "Recorded and carried to the decision point."))

    # --- authority ---
    widened = [g for g in record.authority if not g.attested]
    if record.authority:
        findings.append(Finding(
            "Authority chain",
            " -> ".join(f"{g.grantor} grants {g.grantee}: {g.scope}"
                        + (f" (limit: {g.limit})" if g.limit else "")
                        for g in record.authority),
        ))
    if widened:
        limitations.append(
            "One or more delegations are unattested, so this report cannot confirm "
            "that authority only narrowed across each hop. It does not block the "
            "finding below, which rests on the evidence chain.")

    # Authorization is not a separate axis. It requires a granted capability AND
    # attack-resistant independent evidence: each necessary, neither sufficient.
    if not v.unattributed:
        capability_held = bool(record.authority)
        attack_resistant = v.conversions_to_reverse > 1 and v.weakest_basis == "attested"
        if capability_held and not attack_resistant:
            findings.append(Finding(
                "Authorization preconditions",
                (f"The acting agent held a granted capability, but the evidence "
                 f"supporting the action was not attack-resistant: the verdict reverses "
                 f"on {v.conversions_to_reverse} side conversion(s) and its weakest "
                 f"counted basis is {v.weakest_basis}. Capability was satisfied; "
                 "evidence sufficiency was not. Both are required."),
            ))
        elif not capability_held:
            findings.append(Finding(
                "Authorization preconditions",
                "No granted capability is recorded for the acting agent.",
            ))
        missing.append("Attested delegation receipts at each authority hop.")

    # --- world state ---
    unverified = [o for o in record.observations if not o.verified]
    for o in unverified:
        findings.append(Finding(
            "World-state verification",
            (f"No independent check confirmed that {o.subject} reached the claimed state "
             f"{o.claimed_state!r}. Downstream reasoning treated it as fact."),
        ))
        missing.append(f"Independent post-action state verification for {o.subject}.")

    # --- attribution hypotheses, only where supported ---
    if v.unattributed:
        findings.append(Finding(
            "Attribution",
            ("INDETERMINATE. The record establishes the sequence of actions and the "
             "loss, but not why the decisive belief was held, so no responsibility "
             "hypothesis is supported by this evidence."),
            determinate=False,
        ))
    else:
        findings.append(Finding(
            "Structure and dependence, ranked by support",
            ("1. The aggregation step is the first node where evidence already in the "
             "record would have changed the outcome: it held both the dependence among "
             "supporting claims and the independent contradiction, and passed on neither. "
             "2. The acting agent operated within its granted scope on the evidence it "
             "was shown. "
             "3. This report establishes structure, attribution and dependence. It does "
             "not establish correspondence, meaning whether any claim matched the world, "
             "and it assigns no legal liability."),
        ))

    return Reconstruction(
        incident_id=record.incident_id,
        findings=tuple(findings),
        indeterminate=tuple(indeterminate),
        limitations=tuple(dict.fromkeys(limitations)),
        missing_telemetry=tuple(dict.fromkeys(missing)),
        evidence_verdict=v.verdict.value,
        apparent_support=len(supporting),
        independent_roots=roots_for,
    )
