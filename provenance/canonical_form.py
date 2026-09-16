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
DECLARED_EXCEPTIONS: dict[str, str] = {}
"""Empty, and it should stay that way.

root_registry and conformance/authority_evidence were aligned on 2026-09-16 once
it was established that neither had a persisted receipt or a frozen fixture
digest, so nothing was invalidated by the change.

The third entry was never a divergence. `interop/.../validate.py` serialises
inside a `uniqueItems` check to compare list members -- it produces no digest and
signs nothing. The detector matched it because it matched ANY sorted json.dumps,
which is the difference between finding a canonical form and finding a call that
happens to sort keys. That false positive is now excluded by purpose rather than
by path, and it is worth remembering: the loudest finding in the first scan was
the one that did not exist.
"""

# Spans newlines: a call wrapped across lines is the same call, and reading only
# to the end of the first line reported an aligned serialiser as divergent. The
# detector found that in itself, which is the second time its literal reading has
# been the thing that misled it.
_DUMPS = re.compile(r"json\.dumps\((?:[^()]|\([^()]*\))*\)", re.S)

# This module defines the convention, so it is not a divergence from it.
_SELF = "provenance/canonical_form.py"


def convention_of(source: str) -> tuple[str, str, str] | None:
    """The (ordering, spacing, encoding) of the first digest-shaped dumps call.

    LIMITS, both found by the detector misreading something:

      * It reads LITERAL keyword arguments. A module routing its convention
        through named constants is invisible here. It caught itself doing that.
      * It matched ANY sorted dumps, including one used to compare list members
        rather than to hash anything -- reporting a correct file as divergent.
        Purpose is now checked, not just shape.
    """
    for match in _DUMPS.finditer(source):
        call = match.group(0)
        if "sort_keys" not in call:
            continue
        # A canonical form is serialised to be hashed or signed. A sorted dumps
        # used to compare list members is not one, and reporting it as a
        # divergence sends a reader to fix something that is already correct.
        window = source[max(0, match.start() - 400): match.end() + 400]
        if not any(word in window for word in ("sha256", "digest", "sign", "canonical", "encode()")):
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
