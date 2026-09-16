"""The one canonical serialization, and a detector for anything that diverges.

KL-000's result rests on two independent implementations producing BYTE-IDENTICAL
canonical forms for the same receipt. That only means something if the estate
agrees on what canonical means -- and it does not. A scan of the digest-bearing
core found three conventions:

    sorted / compact / utf8       knowledge_ledger/transaction.py
    sorted / compact / escaped    provenance/root_registry.py
                                  conformance/authority_evidence.py
    sorted / spaced  / escaped    interop/memory-evidence-profile-v0.1/validate.py

They agree on every ASCII payload, which is why nothing has broken. They diverge
the moment a name carries an accent:

    escaped   {"observation_id":"M\\u00fcller-2026"}   sha256 7794fdc4...
    utf8      {"observation_id":"Müller-2026"}        sha256 7c123ec2...

NORMATIVE: `sorted / compact / utf8`, as in knowledge_ledger/transaction.py.
Chosen because that module is the pinned artifact of a passed experiment whose
independent reimplementation already matched it. Picking any other convention
would make the one verified agreement the odd one out.

This module is NOT a migration. Changing root_registry's convention would alter
the bytes its existing signatures were made over, and transaction.py is frozen.
The divergences are recorded as declared exceptions and a test fails if the list
grows -- the same treatment every other known hole in this repository gets.

The `interop/` profile is the one that matters most. It is what an outside
implementer reads, and it is the furthest from normative.
"""

from __future__ import annotations

import json
import pathlib
import re
from typing import Any

SORT_KEYS = True
SEPARATORS = (",", ":")
ENSURE_ASCII = False


def canonical_bytes(value: Any) -> bytes:
    """The normative form. Sorted keys, no whitespace, UTF-8 rather than escapes."""
    return json.dumps(value, sort_keys=SORT_KEYS, separators=SEPARATORS,
                      ensure_ascii=ENSURE_ASCII).encode("utf-8")


# Paths whose convention differs from normative today, with why each is left
# alone. A new entry here is a decision someone has to defend, not a default.
DECLARED_EXCEPTIONS = {
    "provenance/root_registry.py": (
        "escaped rather than utf8; changing it would alter the bytes existing "
        "signatures were made over"),
    "conformance/authority_evidence.py": (
        "escaped rather than utf8; a conformance fixture, aligned with root_registry"),
    "interop/memory-evidence-profile-v0.1/validate.py": (
        "spaced separators AND escaped; the profile an external implementer reads, "
        "and the furthest from normative -- the highest-value thing to align"),
}

_DUMPS = re.compile(r"json\.dumps\([^\n]*")

# This module defines the convention, so it is not a divergence from it.
_SELF = "provenance/canonical_form.py"


def convention_of(source: str) -> tuple[str, str, str] | None:
    """The (ordering, spacing, encoding) of the first digest-shaped dumps call.

    LIMIT, stated because it is the detector's blind spot: this reads LITERAL
    keyword arguments. A module that routes its convention through named
    constants is invisible here and will read as divergent or not at all. The
    detector caught itself doing exactly that on first run, which is the only
    reason the limit is written down rather than assumed away.
    """
    for match in _DUMPS.finditer(source):
        call = match.group(0)
        if "sort_keys" not in call:
            continue
        return (
            "sorted" if "sort_keys=True" in call else "UNSORTED",
            "compact" if re.search(r'separators=\(\s*["\'],["\']\s*,\s*["\']:["\']\s*\)', call) else "spaced",
            "utf8" if "ensure_ascii=False" in call else "escaped",
        )
    return None


NORMATIVE = ("sorted", "compact", "utf8")


def scan(root: pathlib.Path, areas=("provenance", "knowledge_ledger", "canon",
                                    "aggregation", "conformance", "interop", "verification")) -> dict:
    """Every digest-bearing module's convention, split into agreeing and not."""
    agreeing, diverging = [], []
    for area in areas:
        for path in sorted((root / area).rglob("*.py")):
            if "__pycache__" in str(path):
                continue
            convention = convention_of(path.read_text(errors="ignore"))
            if convention is None:
                continue
            rel = str(path.relative_to(root))
            if rel == _SELF:
                continue
            (agreeing if convention == NORMATIVE else diverging).append((rel, convention))
    return {"normative": NORMATIVE, "agreeing": agreeing, "diverging": diverging,
            "undeclared": [rel for rel, _ in diverging if rel not in DECLARED_EXCEPTIONS]}
