#!/usr/bin/env python3
"""AID-1-OBS: who states witness depth today.

Two censuses, because "nobody states it" has two different causes and only one
of them is fixable by asking nicely:

1. **Slots.** For each format in which evidence crosses a boundary, is there
   anywhere to *put* a witness depth? A format whose evidence object is closed
   (`additionalProperties: false`) and carries no depth field cannot be used to
   state one: a producer that tried would emit an invalid envelope.
2. **Instances.** For each corpus of actual records, how many state depth,
   backing or witness identity — and how many would earn any admissible depth
   at all under `canon/ATTESTED-INDEPENDENCE.md`?

Read-only. Emits counts, never record content. The optional private corpus is
pointed at by an environment variable, is never copied, and its cells are
suppressed below `MIN_CELL`; no corpus outside this repository is bundled.

Refutation: exhibit one instance, in any corpus, that states a witness depth.

Usage:
    python3 experiments/aid1/measure.py
    AID1_PRIVATE_CORPUS=/path/to/claims.json python3 experiments/aid1/measure.py
"""

from __future__ import annotations

import json
import os
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from aggregation.independence_axes import (  # noqa: E402
    DepthBasis,
    WitnessDepth,
    WitnessIdentity,
    admissible_depth,
)

MIN_CELL = 10

#: The axis fields a producer would state. `attestation` is listed because it is
#: the axis that DOES have wire support in the legacy vocabulary, which is why
#: finding it stated while depth is not would be informative rather than noise.
AXIS_FIELDS = ("witness_depth", "depth_basis", "witness_identity", "attestation")
LEGACY_FIELD = "independence_basis"

#: Formats in which evidence crosses a boundary, with the object that carries a
#: claim's origin. Each is checked for an axis slot and for whether the object
#: is closed to additions.
SLOT_TARGETS = (
    ("authority-evidence-v0.1 (signed, vendor-neutral)",
     "contracts/authority-evidence-v0.1/schema.json"),
    ("evidence-lineage-v0.1", "provenance/evidence-lineage.schema.json"),
    ("decision-context-v0.1", "provenance/decision-context.schema.json"),
    ("memory-evidence-profile-v0.1 (interop)",
     "interop/memory-evidence-profile-v0.1/schema.json"),
    ("lir1-claim-instance-v1", "experiments/lir1/schema/claim-instance.schema.json"),
)

#: Corpora of actual records, with how each came to exist. A corpus this
#: programme authored as a fixture says nothing about adoption by anyone else:
#: it states depth if and only if we wrote depth into it. Only a corpus derived
#: from a real run bears on adoption at all, and even there the sanitisation was
#: done here, so it inherits our vocabulary and not the producer's.
AUTHORED = "authored-fixture"
DERIVED = "derived-from-a-real-run, sanitised here"
PRIVATE = "supplied-privately, not bundled"

INSTANCE_CORPORA = (
    ("interop memory-evidence-profile cases",
     "interop/memory-evidence-profile-v0.1", "*.json", AUTHORED),
    ("decision-relative independence fixtures",
     "benchmark", "decision-relative-independence-v0.1.json", AUTHORED),
    ("research lifecycle records", "research/records", "*.json", AUTHORED),
    ("field-evidence claims, 2026-08-06",
     "research/field-evidence/2026-08-06", "claims.generic.json", DERIVED),
)


def suppress(n: int) -> object:
    return n if n == 0 or n >= MIN_CELL else "1-9"


def _walk(node):
    """Every dict in a JSON document, at any depth."""
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from _walk(value)
    elif isinstance(node, list):
        for value in node:
            yield from _walk(value)


def slot_census() -> list[dict]:
    """Can a producer state depth in this format at all?"""
    rows = []
    for name, relative in SLOT_TARGETS:
        path = ROOT / relative
        if not path.is_file():
            rows.append({"format": name, "present": False})
            continue
        text = path.read_text(encoding="utf-8")
        document = json.loads(text)
        closed = sum(1 for node in _walk(document)
                     if node.get("additionalProperties") is False)
        rows.append({
            "format": name,
            "present": True,
            "states_any_axis_field": any(field in text for field in AXIS_FIELDS),
            "has_legacy_basis_field": LEGACY_FIELD in text,
            "objects_closed_to_additions": closed,
            "a_producer_could_state_depth": any(f in text for f in AXIS_FIELDS) or closed == 0,
        })
    return rows


def _admissible(record: dict) -> bool:
    """Would this record earn any depth under the policy?

    Silence is not a default: a record stating no depth is `UNSTATED`, and
    `admissible_depth` leaves it there whatever its backing.
    """
    raw_depth = record.get("witness_depth")
    depth = {d.name.lower(): d for d in WitnessDepth}.get(str(raw_depth).lower())
    if depth is None:
        return False
    basis = {b.name.lower().replace("_", "-"): b for b in DepthBasis}.get(
        str(record.get("depth_basis")).lower(), DepthBasis.DECLARED)
    identity = {i.name.lower(): i for i in WitnessIdentity}.get(
        str(record.get("witness_identity")).lower(), WitnessIdentity.ANONYMOUS)
    return admissible_depth(depth, basis, identity) is not WitnessDepth.UNSTATED


def instance_census(name, relative, pattern, origin, *, private=False) -> dict:
    base = pathlib.Path(relative) if private else ROOT / relative
    paths = ([base] if base.is_file()
             else sorted(base.glob(pattern)) if base.is_dir() else [])
    objects = states_axis = states_legacy = earns_depth = 0
    for path in paths:
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        for node in _walk(document):
            # A claim-like object: something asserting a value with an origin.
            if not ({"value", "root_id", "roots", "observer", "source"} & node.keys()):
                continue
            objects += 1
            states_axis += any(field in node for field in AXIS_FIELDS)
            states_legacy += LEGACY_FIELD in node
            earns_depth += _admissible(node)
    hide = suppress if private else (lambda n: n)
    row = {
        "corpus": name,
        "origin": origin,
        "files": hide(len(paths)),
        "claim_objects": hide(objects),
        "state_any_axis": hide(states_axis),
        "state_only_legacy_basis": hide(states_legacy),
        "earn_admissible_depth": hide(earns_depth),
    }
    if objects == 0:
        # DRI-7's negative control, applied to ourselves: zero over zero and
        # zero over many print the same. A corpus with no claim objects in it
        # has not reported a finding, and must say so in its own row.
        row["note"] = ("no claim objects found: nothing here asserts a value "
                       "with an origin, so this corpus reports nothing either "
                       "way. Zero over zero is not a finding.")
    return row


def main() -> int:
    corpora = [instance_census(*row) for row in INSTANCE_CORPORA]

    private = os.environ.get("AID1_PRIVATE_CORPUS")
    if private:
        corpora.append(instance_census(
            "private corpus (not bundled)", private, "*.json",
            PRIVATE, private=True))

    slots = slot_census()
    result = {
        "slot_census": slots,
        "instance_census": corpora,
        "totals": {
            "formats_in_which_depth_can_be_stated":
                sum(1 for row in slots if row.get("a_producer_could_state_depth")),
            "formats_checked": len(slots),
            "claim_objects_examined":
                sum(row["claim_objects"] for row in corpora
                    if isinstance(row["claim_objects"], int)),
            "claim_objects_stating_any_axis":
                sum(row["state_any_axis"] for row in corpora
                    if isinstance(row["state_any_axis"], int)),
            "claim_objects_earning_admissible_depth":
                sum(row["earn_admissible_depth"] for row in corpora
                    if isinstance(row["earn_admissible_depth"], int)),
        },
        "boundary": (
            "A corpus this programme authored says nothing about adoption by anyone "
            "else. One machine, one estate. Absence of a stated depth is absence of "
            "a statement, not evidence that the witness was shallow."
        ),
        "refutation": "Exhibit one instance, in any corpus, that states a witness depth.",
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
