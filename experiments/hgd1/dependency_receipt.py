"""Emit and validate the dependency receipt HGD-1 publishes but never wrote.

`dependency-receipt.schema.json` is a published artifact — it carries a
GitHub Pages `$id`, and `research/knowledge-ledger/GATE-COVERAGE.json` cites it
as the evidence discharging KL-006/KL-008/ADV-005: "shared upstream dependency
is not representable in schema v0.1". The coverage claim is that
`components[]` carrying `componentId`, `kind`, `sharedWeightLower` and
`sharedWeightUpper` makes shared dependency representable as interval-valued
shared weight.

Nothing ever produced a document in that shape.

`run_hgd1.py` builds components as `{id, members, low, high, true}` and receipts
as `{origin, claim, components, support}` — an internal vocabulary that shares
not one field name with the schema it ships beside. So the gate-coverage map
cited a representation that existed only as a declaration. That is a sharper
version of the same defect the emission census was written to find: not a field
nothing writes, but an entire published artifact shape nothing writes.

This module is a separate file ON PURPOSE. `run_hgd1.py` is a frozen
confirmatory runner pinned to `PROTOCOL_COMMIT`; editing it would invalidate the
registration chain to change something that is not part of what was run. The
serialiser converts the runner's output after the fact, and the validator checks
the published form, without touching the frozen artifact.

Read-only with respect to the experiment: this changes no measured result.
"""

from __future__ import annotations

import re
from typing import Any, Iterable, Mapping

SCHEMA_ID = "minority-prophet.dependency-receipt.v1"

#: From the schema. `other` is the escape hatch and is used whenever a component
#: id does not name one of the specific kinds.
COMPONENT_KINDS = (
    "instrument", "station", "calibration", "operator", "model", "dataset", "other",
)

SUPPORT_STATUSES = ("supported", "unknown", "conflicting", "revoked")

_DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")


class DependencyReceiptError(ValueError):
    """A dependency receipt cannot be produced or read as written."""


def component_kind(component_id: str) -> str:
    """The schema `kind` a component id names.

    HGD-1's ids are `station`, `station-a`, `station-b`, `calibration` and
    `model` — the kind is the segment before any hyphen. Anything unrecognised
    becomes `other` rather than raising, because `kind` is a coarse label for
    audit and guessing wrong is worse than declining to guess. The runner never
    declared a kind at all, so every value here is inferred, and that is recorded
    rather than presented as something the experiment stated.
    """
    head = component_id.split("-", 1)[0].strip().lower()
    return head if head in COMPONENT_KINDS else "other"


def serialise_component(component: Mapping[str, Any]) -> dict[str, Any]:
    """One internal component, in the published shape.

    `low`/`high` are the interval-valued shared weight the coverage claim rests
    on, and they map to `sharedWeightLower`/`sharedWeightUpper` unchanged. The
    internal `true` weight is deliberately dropped: it is the generator's ground
    truth, known only inside a simulation, and publishing it in a receipt would
    put a value in the audit record that no real observer could ever supply.
    """
    try:
        component_id = str(component["id"])
        lower = float(component["low"])
        upper = float(component["high"])
    except (KeyError, TypeError, ValueError) as exc:
        raise DependencyReceiptError(f"component is not serialisable: {exc}") from exc
    if not component_id:
        raise DependencyReceiptError("componentId must be non-empty")
    if not 0.0 <= lower <= upper <= 1.0:
        raise DependencyReceiptError(
            f"shared weight interval [{lower}, {upper}] must satisfy 0 <= lower <= upper <= 1"
        )
    return {
        "componentId": component_id,
        "kind": component_kind(component_id),
        "sharedWeightLower": lower,
        "sharedWeightUpper": upper,
    }


def build_receipt(
    origin_digest: str,
    components: Iterable[Mapping[str, Any]],
    *,
    support_status: str = "supported",
    receipt_digest: str,
) -> dict[str, Any]:
    """A dependency receipt in the published schema's shape."""
    if not _DIGEST.match(origin_digest):
        raise DependencyReceiptError("originDigest must match sha256:<64 hex>")
    if not _DIGEST.match(receipt_digest):
        raise DependencyReceiptError("support.receiptDigest must match sha256:<64 hex>")
    if support_status not in SUPPORT_STATUSES:
        raise DependencyReceiptError(
            f"unrecognised support status {support_status!r}; "
            f"expected one of {', '.join(SUPPORT_STATUSES)}"
        )
    return {
        "schema": SCHEMA_ID,
        "originDigest": origin_digest,
        "components": [serialise_component(item) for item in components],
        "support": {"status": support_status, "receiptDigest": receipt_digest},
    }


def receipt_errors(document: object) -> list[str]:
    """Everything wrong with a receipt, as a list. Empty means well-formed.

    Hand-written rather than delegated to a JSON Schema library, because this
    repository takes no runtime dependency for validation and the rest of the
    estate validates the same way (`conformance/authority_evidence.py`).
    """
    if not isinstance(document, Mapping):
        return ["receipt must be an object"]

    errors: list[str] = []
    permitted = {"schema", "originDigest", "components", "support"}
    unknown = sorted(set(document) - permitted)
    if unknown:
        errors.append("unpermitted receipt keys: " + ", ".join(unknown))

    if document.get("schema") != SCHEMA_ID:
        errors.append(f"schema must be {SCHEMA_ID}")

    origin = document.get("originDigest")
    if not isinstance(origin, str) or not _DIGEST.match(origin):
        errors.append("originDigest must match sha256:<64 hex>")

    components = document.get("components")
    if not isinstance(components, list):
        errors.append("components must be an array")
    else:
        seen: set[str] = set()
        for index, item in enumerate(components):
            errors.extend(_component_errors(item, index, seen))

    support = document.get("support")
    if not isinstance(support, Mapping):
        errors.append("support must be an object")
    else:
        if support.get("status") not in SUPPORT_STATUSES:
            errors.append("unrecognised support status")
        digest = support.get("receiptDigest")
        if not isinstance(digest, str) or not _DIGEST.match(digest):
            errors.append("support.receiptDigest must match sha256:<64 hex>")
    return errors


def _component_errors(item: object, index: int, seen: set[str]) -> list[str]:
    if not isinstance(item, Mapping):
        return [f"components[{index}] must be an object"]

    errors: list[str] = []
    permitted = {"componentId", "kind", "sharedWeightLower", "sharedWeightUpper"}
    unknown = sorted(set(item) - permitted)
    if unknown:
        errors.append(f"components[{index}] unpermitted keys: " + ", ".join(unknown))

    component_id = item.get("componentId")
    if not isinstance(component_id, str) or not 1 <= len(component_id) <= 160:
        errors.append(f"components[{index}].componentId must be 1-160 characters")
    elif component_id in seen:
        # Not a schema rule, but two components sharing an id makes the receipt
        # unreadable as an audit record: the weights could not be attributed.
        errors.append(f"components[{index}].componentId {component_id!r} is duplicated")
    else:
        seen.add(component_id)

    if item.get("kind") not in COMPONENT_KINDS:
        errors.append(f"components[{index}].kind is unrecognised")

    lower = item.get("sharedWeightLower")
    upper = item.get("sharedWeightUpper")
    for name, value in (("sharedWeightLower", lower), ("sharedWeightUpper", upper)):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            errors.append(f"components[{index}].{name} must be a number")
        elif not 0.0 <= float(value) <= 1.0:
            errors.append(f"components[{index}].{name} must be within [0, 1]")
    if (isinstance(lower, (int, float)) and isinstance(upper, (int, float))
            and not isinstance(lower, bool) and not isinstance(upper, bool)
            and float(lower) > float(upper)):
        errors.append(
            f"components[{index}] shared weight lower bound exceeds its upper bound"
        )
    return errors
