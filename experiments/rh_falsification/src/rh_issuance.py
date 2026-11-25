"""Issue every calculation root through the canonical root registry.

``provenance/root_registry.py`` bounds roots per signed identity per time
window. In this pack the bound is 2 roots per hour per identity. Each
distinct calculation is issued once, as a registry root, by the identity
that first posted it. Later reports of the same calculation attach to that
root and issue nothing. A calculation the registry refuses because the
identity's budget for that hour is spent never becomes a root.

The graph is built with ``root_authority`` set to this issuer, so a
parentless node the registry did not issue is refused. No calculation
enters the candidate graph as a cited ``source:`` node, which is the path
the graph does not check against the authority.

Synthetic setting: identities sign with keys derived from their name by
``HmacIssuerVerifier``, and the registry clock follows each report's
``observed_at``. That is a deterministic test fixture. A deployment injects
a real identity verifier and a real clock.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import shutil
import sys
import tempfile
import weakref
from typing import Dict, FrozenSet, Optional, Tuple

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from provenance.root_registry import (  # noqa: E402
    IssuanceLimitError,
    RootRegistry,
    RootRequest,
)

ROOTS_PER_HOUR = 2
WINDOW_SECONDS = 3600
# Synthetic epoch, aligned to an hour boundary.
SYNTHETIC_T0 = 1_800_000_000
_KEY_ID = "synthetic"


def _key_for(identity: str) -> bytes:
    return hashlib.sha256(f"rh-synthetic-key:{identity}".encode()).digest()


class _DerivedKeyVerifier:
    """HMAC check with keys derived from the identity name. Synthetic only."""

    def sign(self, request: RootRequest) -> str:
        return hmac.new(_key_for(request.issuer_id), request.canonical_bytes(),
                        hashlib.sha256).hexdigest()

    def verify(self, issuer_id: str, key_id: str, message: bytes, signature: str) -> bool:
        if key_id != _KEY_ID:
            return False
        expected = hmac.new(_key_for(issuer_id), message, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)


class CalculationIssuer:
    """One registry, one root per distinct calculation, capped per identity."""

    def __init__(
        self,
        path: Optional[str] = None,
        *,
        roots_per_window: int = ROOTS_PER_HOUR,
        window_seconds: int = WINDOW_SECONDS,
    ) -> None:
        if path is None:
            tmp = tempfile.mkdtemp(prefix="rh-registry-")
            weakref.finalize(self, shutil.rmtree, tmp, True)
            path = os.path.join(tmp, "roots.sqlite")
        self._now = SYNTHETIC_T0
        self._verifier = _DerivedKeyVerifier()
        self.registry = RootRegistry(
            path,
            verifier=self._verifier,
            integrity_key=b"rh-synthetic-registry-integrity",
            roots_per_window=roots_per_window,
            window_seconds=window_seconds,
            clock=lambda: self._now,
        )
        self._issued: Dict[Tuple[str, str], str] = {}
        self.refused: Dict[Tuple[str, str], str] = {}

    def issue(
        self,
        *,
        identity: str,
        fingerprint: str,
        proposition_id: str,
        value: bool,
        observed_at: int = SYNTHETIC_T0,
    ) -> Optional[str]:
        """Registry root id for this calculation, or None if refused."""
        key = (proposition_id, fingerprint)
        if key in self._issued:
            return self._issued[key]
        self._now = observed_at
        digest = hashlib.sha256(fingerprint.encode()).hexdigest()
        nonce = hashlib.sha256(
            f"{identity}|{proposition_id}|{fingerprint}|{observed_at}".encode()
        ).hexdigest()
        request = RootRequest(
            issuer_id=identity,
            key_id=_KEY_ID,
            observation_id=fingerprint,
            proposition_id=proposition_id,
            value=value,
            evidence_digest=digest,
            observed_at=observed_at,
            nonce=nonce,
            origin_type="observation",
        )
        request = request.with_signature(self._verifier.sign(request))
        try:
            receipt = self.registry.issue(request)
        except IssuanceLimitError:
            self.refused[key] = identity
            return None
        self._issued[key] = receipt.root_id
        return receipt.root_id

    def active_roots(self) -> FrozenSet[str]:
        return self.registry.active_roots()
