#!/usr/bin/env python3
"""SCH-001 repair (RUN-20260807-8): migrate KL-001..KL-011 preregistrations
from minority-prophet.preregistration.v0.1 to v0.2.

Committed so the migration is reproducible and reviewable. Populated v0.1
values are carried verbatim; fields the kernel genuinely cannot answer yet
become {"status": "unanswered", "reason": ...} with a kernel-grounded reason
-- never null. Safety boundaries and authorization requirements ARE
answerable now, from the program record, and are populated per kernel.
KL-000 is untouched (its registrations are frozen records already at v0.2).
Migration does not advance any kernel's state: a schema with more fields is
not evidence.
"""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
EXPERIMENTS = REPO / "research" / "knowledge-ledger" / "experiments"

TEN_CONTROLS = [
    "head or record counting",
    "source counting",
    "evidence ledger without search coverage",
    "search ledger without root collapse",
    "dual ledger",
    "a genuinely independent-evidence condition",
    "a copied or shared-dependency condition",
    "an incomplete-coverage condition",
    "a counterexample in a searched location",
    "a counterexample in an unsearched location",
]

# Per-kernel facts that ARE answerable today, grounded in the program record
# (STATUS blockers, EXPERIMENT-REGISTRY, run constraints). Everything not
# listed here becomes unanswered-with-reason.
KERNEL = {
    "KL-001": {
        "safety": "Synthetic repositories only; no real codebases, credentials, or vulnerability disclosures. The mapping pipeline's scope declaration is the kernel's risk surface (ADV-001, demonstrated at FC1's W3).",
        "auth": "Execution needs no authorization if the pipeline under test is deterministic tooling; any metered model in the pipeline requires founder authorization BEFORE use. Publication and promotion always require the owner.",
        "extra": "Baseline true-positive recall must be measured BEFORE the dual ledger is applied, or the 95%-preservation target is unfalsifiable (standing blocker).",
    },
    "KL-002": {
        "safety": "Controlled source-laundering packets only; no live-model output is published as fact. Root identity is byte identity (ADV-004): a paraphrase pipeline emitting inconsistent rootIds splits one source into many without any adversary.",
        "auth": "Metered model calls may exceed the approved budget; founder authorization required before any paid inference. Publication and promotion require the owner.",
        "extra": None,
    },
    "KL-003": {
        "safety": "Public replication datasets only, and none before its licence is reviewed (standing blocker). No human-subjects data.",
        "auth": "Dataset licence review is a prerequisite for acquisition; no dataset has been selected -- that selection, not the analysis, is the binding prerequisite. Publication and promotion require the owner.",
        "extra": None,
    },
    "KL-004": {
        "safety": "RETROSPECTIVE RESEARCH ONLY. Never emits patient guidance; no live decision authority; no patient-level records (published aggregate data only -- patient-level data would require explicit human authorization and is out of scope for this program). Blocked-safety beyond the retrospective stage regardless of result quality.",
        "auth": "Execution beyond retrospective analysis is not authorizable within this program. Publication and promotion require the owner.",
        "extra": None,
    },
    "KL-005": {
        "safety": "Timestamped closed news events only; no live-event confirmation is ever emitted.",
        "auth": "Publication and promotion require the owner.",
        "extra": "The two-sided metric (false early confirmation AND delay to correct confirmation) is the design prerequisite: a single-endpoint design lets indefinite abstention win.",
    },
    "KL-006": {
        "safety": "Synthetic or closed case files only. NEVER emits a real verdict or risk score.",
        "auth": "Publication and promotion require the owner.",
        "extra": "ADV-005: shared upstream dependency between roots is not representable in receipt schema v0.1, and dependency structure is this kernel's entire subject; the receipt-schema extension is a prerequisite beyond this preregistration migration.",
    },
    "KL-007": {
        "safety": "Measures evidence accounting (sources, exclusions, dependencies, uncertainty), explicitly NOT policy agreement; an endpoint rewarding forced agreement would invalidate the design.",
        "auth": "Contacting or recruiting human reconstruction teams requires explicit founder authorization BEFORE any engagement. Publication and promotion require the owner.",
        "extra": None,
    },
    "KL-008": {
        "safety": "Simulation or archived ground truth only; no live sensor or model feed.",
        "auth": "Publication and promotion require the owner.",
        "extra": "ADV-005: one instrument feeding many derived products is a shared-dependency structure the receipt schema cannot yet represent; prerequisite as for KL-006.",
    },
    "KL-009": {
        "safety": "SIMULATION ONLY. Never connected to live actuation; the simulator must refuse to expose any actuation interface (its own first falsifiable check). Blocked-safety beyond shadow stage; no live authority is sought by this program.",
        "auth": "Execution beyond simulation/shadow is not authorizable within this program. The maximum unnecessary-fallback rate is preregistered BEFORE measuring catastrophic-action reduction, so the tradeoff cannot be chosen after seeing results.",
        "extra": None,
    },
    "KL-010": {
        "safety": "Known textual genealogies with held-out expert source families; competing interpretations and missing archives must SURVIVE in the output -- an endpoint rewarding a single resolved reconstruction would violate the dispute-preservation requirement.",
        "auth": "Publication and promotion require the owner.",
        "extra": None,
    },
    "KL-011": {
        "safety": "Synthetic bounded claims only; five stages (discovery, collection, provenance, decision, presentation) with the registered injection set: paraphrase, retry, reordering, duplication, partial failure, one malicious duplicate, one unavailable location. No cross-system claim is promoted by any run.",
        "auth": "Requires two independently written implementations (met in substance -- see STATUS correctionRecord) and owner commissioning for any cross-system execution. Publication and promotion require the owner.",
        "extra": "Inherited design constraints from KL-000's close: A2 undecided (19,152 worlds of conclusion semantics any transaction transports); SCH-005 (protected fields the receipt never emits cannot be shown to survive crossing systems); ADV-001; F11.",
    },
}


def unanswered(reason: str) -> dict:
    return {"status": "unanswered", "reason": reason}


def carry(value, fallback_reason: str):
    """Carry a populated v0.1 value; convert null/empty to unanswered."""
    if value is None or value == [] or value == {}:
        return unanswered(fallback_reason)
    return value


def migrate(kernel_id: str) -> dict:
    kdir = EXPERIMENTS / kernel_id
    v01 = json.loads((kdir / "preregistration.json").read_text())
    status = json.loads((kdir / "STATUS.json").read_text())
    facts = KERNEL[kernel_id]
    gate = status["nextGate"]
    gate_ref = f"determined by this kernel's next gate (STATUS.json): {gate[:220]}..."

    if v01.get("schema") != "minority-prophet.preregistration.v0.1":
        raise SystemExit(f"{kernel_id}: expected a v0.1 document, found {v01.get('schema')!r}")

    doc = {
        "schema": "minority-prophet.preregistration.v0.2",
        "experimentId": kernel_id,
        "protocolVersion": unanswered(
            "assigned at registration, when this kernel's protocol is written and frozen; "
            "the kernel is seeded and has no protocol yet"
        ),
        "status": "seeded-migrated-v0.2",
        "migrationRecord": {
            "migratedBy": "RUN-20260807-8",
            "from": "minority-prophet.preregistration.v0.1 (preserved in git history at this path)",
            "stateEffect": "NONE. Migration does not advance the kernel: it remains seeded. A schema with more fields is not evidence (SCH-001 repair only).",
        },
        "question": carry(v01.get("question"), "the registry question was never seeded -- must be fixed before registration"),
        "null": carry(v01.get("null"), "the null hypothesis was never seeded -- must be fixed before registration"),
        "target": carry(v01.get("target"), "the target hypothesis was never seeded -- must be fixed before registration"),
        "population": unanswered(
            "requires the concrete corpus/world-generator this kernel's next gate builds; " + gate_ref
        ),
        "searchSpace": unanswered(
            "defined with the population at registration; the bounded-absence discipline requires declared "
            "bounds that do not exist until the generator or corpus exists; " + gate_ref
        ),
        "rootDefinition": unanswered(
            "the operational root definition (what counts as one evidence root in this kernel's domain, and "
            "what counts as a copy) is fixed at registration; KL-000's rootDefinition is the precedent form"
        ),
        "baselines": unanswered(
            "the ablated comparators are designed with the pipeline at registration; KL-000's B1-B5 with "
            "registered must-fail expectations are the precedent form, including the lesson that each "
            "baseline's expected failure must be checkable as registered (KL-000 finding F1)"
        ),
        "controls": [
            {"requirement": req,
             "fixture": unanswered("fixtures are constructed at registration; the requirement list is fixed by RESEARCH-METHOD.md 'Controls required everywhere'")}
            for req in TEN_CONTROLS
        ],
        "primaryEndpoint": carry(v01.get("primaryEndpoint"), "the primary endpoint was never seeded -- must be fixed before registration"),
        "secondaryEndpoints": unanswered(
            "chosen at registration with the endpoints' measurement plan; must include enough reporting "
            "granularity that a fail-closed path cannot hide an implementation defect (KL-000 amendment 2(b) precedent)"
        ),
        "effectSize": unanswered(
            "requires the registered endpoint and its measurement scale; for conformance-style kernels the "
            "KL-000 precedent (exact-zero target, power via must-fail baselines) may apply instead of a "
            "minimum detectable effect -- decided at registration"
        ),
        "uncertainty": unanswered(
            "stated at registration for the registered endpoints (KL-000 precedent: rule-of-three bounds "
            "with fail-closed effective-sample caveats)"
        ),
        "multipleTestingCorrection": unanswered(
            "stated at registration once the endpoint family is fixed (KL-000 precedent: none on an "
            "exact-zero primary endpoint; Bonferroni on secondary rate bounds)"
        ),
        "successCondition": unanswered("fixed at registration with the endpoints; " + gate_ref),
        "failureCondition": unanswered("fixed at registration with the endpoints"),
        "invalidationCondition": unanswered(
            "fixed at registration; KL-000 precedent: generator/corpus drift, count mismatches, hash "
            "mismatches, unexpected fail-closed causes, and any passing must-fail baseline all invalidate "
            "rather than fail"
        ),
        "stopCondition": carry(v01.get("stopCondition"), "fixed at registration with the endpoints"),
        "frozenSeedsOrSplits": unanswered(
            "seeds/splits are frozen at registration, immediately before the confirmatory run -- freezing "
            "them now, with no generator or corpus to consume them, would freeze nothing (KL-000 finding "
            "F11: a frozen seed without a registered draw schedule does not even freeze a stream)"
        ),
        "protocolCommit": None,
        "protocolCommitNote": (
            "Null by design, per the registered sidecar discipline (KL-000 PROTOCOL.md, 'Why protocolCommit "
            "is deliberately null'): git assigns the registration commit; a PROTOCOL-COMMIT sidecar records "
            "it afterwards; the registered file is never edited. Bound when this kernel registers."
        ),
        "environment": unanswered(
            "pinned at registration time (interpreter, platform, dependency policy); recording today's "
            "environment for an experiment that will not run in it would be provenance theatre"
        ),
        "artifacts": unanswered(
            "paths are declared when the kernel's directory is scaffolded (fixtures/, src/, tests/, "
            "results/, REPRODUCE.md -- constraint ENG-001, still open). Lesson carried from LEAK-101/IND "
            "reviews: artifact lists in registration documents leak structure into commission packages; "
            "record roles rather than paths in any package derived from this document"
        ),
        "safetyBoundary": facts["safety"],
        "humanAuthorization": facts["auth"],
    }
    if facts["extra"]:
        doc["kernelSpecificConstraint"] = facts["extra"]
    return doc


SCHEMA_BLOCKER_MARKERS = (
    "preregistration is minority-prophet.preregistration.v0.1",
    "schema v0.1 has no key for 4 of",
)


def update_status(kernel_id: str) -> None:
    path = EXPERIMENTS / kernel_id / "STATUS.json"
    status = json.loads(path.read_text())
    new_blockers = []
    discharged = 0
    for blocker in status["blockers"]:
        if any(m in blocker for m in SCHEMA_BLOCKER_MARKERS):
            discharged += 1
            new_blockers.append(
                "DISCHARGED at RUN-20260807-8, retained for the record: '" + blocker + "' -- the "
                "preregistration is now schema v0.2 with every required field present or "
                "unanswered-with-reason (SCH-001 repaired). The remaining work is CONTENT at "
                "registration, not schema."
            )
        else:
            new_blockers.append(blocker)
    status["blockers"] = new_blockers
    status["reviewedByRun"] = "RUN-20260807-8"
    status["schemaMigration"] = (
        f"preregistration.json migrated v0.1 -> v0.2 by RUN-20260807-8 ({discharged} schema blocker(s) "
        "discharged). State unchanged: seeded. A schema with more fields is not evidence."
    )
    path.write_text(json.dumps(status, indent=2, ensure_ascii=False) + "\n")


def main() -> None:
    for i in range(1, 12):
        kernel_id = f"KL-{i:03d}"
        doc = migrate(kernel_id)
        out = EXPERIMENTS / kernel_id / "preregistration.json"
        out.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
        update_status(kernel_id)
        print(f"{kernel_id}: migrated; state {json.loads((EXPERIMENTS / kernel_id / 'STATUS.json').read_text())['state']}")


if __name__ == "__main__":
    main()
