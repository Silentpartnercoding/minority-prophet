#!/usr/bin/env python3
"""KL-011: does a conclusion survive crossing between independent systems?

Two arms, per `preregistration-v0.2.json`:

    direct   the receipt is read by the process that produced it
    crossed  the receipt is serialised, transported through the seven registered
             injections, and re-read by a SECOND PROCESS sharing no in-memory
             state with the first

Invalidation clause I1 voids the whole run if the two arms share an in-memory
object, because a simulated crossing tests nothing. So the crossed arm really does
spawn a subprocess and really does pass bytes: `_cross` writes JSON to a pipe and
a fresh interpreter reads it back. That is slower than calling a function and it
is the only version that answers the question.

Scope is DERIVED here, never supplied (ADV-001, invalidation clause I3): the
declared search space is computed from the transaction's own locations and a
supplied scope raises.
"""

from __future__ import annotations

import copy
import json
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve()
ROOT = HERE.parents[5]
sys.path.insert(0, str(ROOT))

from knowledge_ledger.transaction_v2 import evaluate_transaction_v2  # noqa: E402

INJECTIONS = ("paraphrase", "retry", "reordering", "duplication",
              "partial failure", "one malicious duplicate",
              "one unavailable location")


class ScopeSuppliedError(ValueError):
    """A transaction that declares its own scope instead of deriving it."""


def derive_scope(transaction: dict) -> list[dict]:
    """Compute the declared search space from the transaction itself.

    ADV-001: an under-declared scope is undetectable downstream, so coverage
    preservation is only ever as strong as the original declaration. Accepting a
    supplied scope would make this experiment measure the declarer rather than the
    transport.
    """
    if "declaredScope" in transaction.get("searchLedger", {}):
        raise ScopeSuppliedError(
            "searchLedger.declaredScope was supplied; KL-011 derives scope")
    return list(transaction["searchLedger"]["locations"])


# --- the seven registered injections ---------------------------------------

def _paraphrase(doc: dict) -> dict:
    """Re-serialise with different key order and spacing. Bytes differ, meaning
    does not. A transport that loses anything here loses it to formatting."""
    return json.loads(json.dumps(doc, sort_keys=True, indent=2))


def _retry(doc: dict) -> dict:
    return json.loads(json.dumps(doc))          # delivered twice, same content


def _reordering(doc: dict) -> dict:
    out = copy.deepcopy(doc)
    out["searchLedger"]["locations"] = list(reversed(out["searchLedger"]["locations"]))
    out["evidenceLedger"]["records"] = list(reversed(out["evidenceLedger"]["records"]))
    return out


def _duplication(doc: dict) -> dict:
    """The same record twice. Must collapse to one root, not two."""
    out = copy.deepcopy(doc)
    records = out["evidenceLedger"]["records"]
    if records:
        copied = copy.deepcopy(records[0])
        copied["recordId"] = f"{copied.get('recordId', 'r')}-dup"
        records.append(copied)
    return out


def _partial_failure(doc: dict) -> dict:
    """One location never resolved. Coverage must not silently complete."""
    out = copy.deepcopy(doc)
    locations = out["searchLedger"]["locations"]
    if locations:
        locations[-1] = dict(locations[-1], status="not_searched")
    return out


def _malicious_duplicate(doc: dict) -> dict:
    """A copy that flips its side while keeping its root. The evaluator must
    refuse it rather than let one root assert both ways."""
    out = copy.deepcopy(doc)
    records = out["evidenceLedger"]["records"]
    if records:
        forged = copy.deepcopy(records[0])
        forged["recordId"] = f"{forged.get('recordId', 'r')}-forged"
        forged["side"] = "support" if forged["side"] == "oppose" else "oppose"
        records.append(forged)
    return out


def _unavailable_location(doc: dict) -> dict:
    out = copy.deepcopy(doc)
    locations = out["searchLedger"]["locations"]
    if locations:
        locations[0] = dict(locations[0], status="unavailable")
    return out


INJECTORS = {
    "paraphrase": _paraphrase,
    "retry": _retry,
    "reordering": _reordering,
    "duplication": _duplication,
    "partial failure": _partial_failure,
    "one malicious duplicate": _malicious_duplicate,
    "one unavailable location": _unavailable_location,
}

_READER = """
import json, sys
sys.path.insert(0, %r)
from knowledge_ledger.transaction_v2 import evaluate_transaction_v2
payload = json.loads(sys.stdin.read())
try:
    print(json.dumps(evaluate_transaction_v2(payload)))
except Exception as exc:
    print(json.dumps({"__error__": f"{type(exc).__name__}: {exc}"}))
"""


def cross(transaction: dict) -> dict:
    """Evaluate in a separate interpreter, reached only through bytes.

    Invalidation clause I1. Nothing here returns an object the caller already
    holds: the payload is serialised to a pipe, a fresh process parses it, and the
    receipt comes back as text.
    """
    result = subprocess.run(
        [sys.executable, "-c", _READER % str(ROOT)],
        input=json.dumps(transaction), capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        return {"__error__": f"crossed process exited {result.returncode}: "
                             f"{result.stderr.strip()[:200]}"}
    return json.loads(result.stdout)


def direct(transaction: dict) -> dict:
    derive_scope(transaction)
    try:
        return evaluate_transaction_v2(transaction)
    except Exception as exc:                                   # noqa: BLE001
        return {"__error__": f"{type(exc).__name__}: {exc}"}
