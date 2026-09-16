"""One canonical form, and a failing test when anything drifts from it.

KL-000's result rests on two independent implementations producing byte-identical
canonical forms. That only means something if the estate agrees on what canonical
means — and a scan found three conventions in the digest-bearing core. They agree
on every ASCII payload, which is why nothing has broken yet.
"""

import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from provenance.canonical_form import (  # noqa: E402
    DECLARED_EXCEPTIONS, NORMATIVE, canonical_bytes, convention_of, scan,
)


def test_the_divergence_is_real_and_only_shows_on_non_ascii():
    """The whole reason this went unnoticed."""
    payload = {"observation_id": "Müller-2026"}
    escaped = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    utf8 = canonical_bytes(payload)
    assert escaped != utf8
    assert hashlib.sha256(escaped).hexdigest() != hashlib.sha256(utf8).hexdigest()

    ascii_only = {"observation_id": "Muller-2026"}
    assert json.dumps(ascii_only, sort_keys=True, separators=(",", ":")).encode() \
        == canonical_bytes(ascii_only)


def test_no_undeclared_divergence_exists():
    """The gate. A module may differ from normative, but somebody has to have
    said so and why. A new entry in DECLARED_EXCEPTIONS is a decision to defend,
    not a default."""
    result = scan(ROOT)
    assert result["undeclared"] == [], (
        f"undeclared canonical-form divergence: {result['undeclared']}. "
        "Either align it with provenance.canonical_form, or declare it with a reason.")


def test_every_declared_exception_still_diverges():
    """The other direction: an exception that no longer applies is stale
    paperwork claiming a problem that was fixed."""
    diverging = {rel for rel, _ in scan(ROOT)["diverging"]}
    stale = [path for path in DECLARED_EXCEPTIONS if path not in diverging]
    assert stale == [], f"declared exceptions that no longer diverge: {stale}"


def test_the_frozen_evaluator_is_the_normative_one():
    """Normative was chosen because that module is the pinned artifact of a
    passed experiment whose independent reimplementation already matched it.
    Flips if the frozen evaluator's convention ever moves."""
    source = (ROOT / "knowledge_ledger/transaction.py").read_text()
    assert convention_of(source) == NORMATIVE


def test_the_interop_profile_is_the_furthest_from_normative():
    """Recorded because it is the highest-value one to fix: the profile an
    external implementer reads is the one that differs in two ways, not one."""
    conventions = dict(scan(ROOT)["diverging"])
    interop = conventions.get("interop/memory-evidence-profile-v0.1/validate.py")
    assert interop is not None
    differences = sum(1 for a, b in zip(interop, NORMATIVE) if a != b)
    assert differences == 2, "the interop profile differs in spacing AND encoding"


def test_the_detector_reads_literals_and_says_so():
    """Its blind spot, asserted rather than assumed: a convention routed through
    named constants is invisible to it."""
    assert convention_of("json.dumps(v, sort_keys=SORT, separators=SEP)") != NORMATIVE
    assert convention_of('json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=False)') \
        == NORMATIVE
