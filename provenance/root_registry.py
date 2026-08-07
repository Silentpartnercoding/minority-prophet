"""Durable, bounded issuance for evidence roots.

This module is the operational enforcement point for R1.4.  It does not decide
that an observation is true.  It proves which authenticated issuer requested a
root, gives that request a canonical identity, limits issuance per time window,
and preserves ancestry through tombstones rather than hard deletion.

The registry deliberately accepts an injected ``IssuerVerifier``.  Production
deployments can verify mTLS identities, hardware attestations, workload
identities, or provider receipts without making any one provider part of the
Minority Prophet kernel.  ``HmacIssuerVerifier`` exists for deterministic tests
and local demonstrations only.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import sqlite3
import time
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Mapping, Protocol


class RootIssuanceError(RuntimeError):
    """Base class for fail-closed root issuance failures."""


class IssuerAuthenticationError(RootIssuanceError):
    pass


class IssuanceLimitError(RootIssuanceError):
    pass


class ReplayError(RootIssuanceError):
    pass


class RegistryIntegrityError(RootIssuanceError):
    pass


class ClockError(RootIssuanceError):
    pass


class IssuerVerifier(Protocol):
    def verify(self, issuer_id: str, key_id: str, message: bytes, signature: str) -> bool: ...


@dataclass(frozen=True)
class RootRequest:
    issuer_id: str
    key_id: str
    observation_id: str
    proposition_id: str
    value: bool
    evidence_digest: str
    observed_at: int
    nonce: str
    signature: str = ""

    def canonical_bytes(self) -> bytes:
        payload = {
            "evidence_digest": self.evidence_digest,
            "issuer_id": self.issuer_id,
            "key_id": self.key_id,
            "nonce": self.nonce,
            "observation_id": self.observation_id,
            "observed_at": self.observed_at,
            "proposition_id": self.proposition_id,
            "value": self.value,
        }
        return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()

    def with_signature(self, signature: str) -> "RootRequest":
        return RootRequest(**{**self.__dict__, "signature": signature})


@dataclass(frozen=True)
class RootReceipt:
    root_id: str
    issuer_id: str
    window_start: int
    sequence: int
    issued_at: int
    record_hash: str


class HmacIssuerVerifier:
    """Deterministic local verifier; not an identity-proofing service."""

    def __init__(self, keys: Mapping[tuple[str, str], bytes]) -> None:
        self._keys = dict(keys)

    def sign(self, request: RootRequest) -> str:
        key = self._keys[(request.issuer_id, request.key_id)]
        return hmac.new(key, request.canonical_bytes(), hashlib.sha256).hexdigest()

    def verify(self, issuer_id: str, key_id: str, message: bytes, signature: str) -> bool:
        key = self._keys.get((issuer_id, key_id))
        if key is None:
            return False
        expected = hmac.new(key, message, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)


class RootRegistry:
    """SQLite-backed append-only issuance ledger.

    ``BEGIN IMMEDIATE`` serializes quota allocation across processes.  A unique
    issuer/window/sequence constraint makes the bound durable.  Each record is
    HMAC-chained with a registry integrity key so offline mutation is detected
    before another root is issued.  The integrity key must be held outside the
    database in production.
    """

    def __init__(
        self,
        path: str | Path,
        *,
        verifier: IssuerVerifier,
        integrity_key: bytes,
        roots_per_window: int = 2,
        window_seconds: int = 3600,
        max_clock_skew_seconds: int = 300,
        clock: Callable[[], float] = time.time,
    ) -> None:
        if roots_per_window < 1 or window_seconds < 1:
            raise ValueError("issuance bounds must be positive")
        if not integrity_key:
            raise ValueError("registry integrity key is required")
        self.path = str(path)
        self.verifier = verifier
        self.integrity_key = integrity_key
        self.roots_per_window = roots_per_window
        self.window_seconds = window_seconds
        self.max_clock_skew_seconds = max_clock_skew_seconds
        self.clock = clock
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.path, timeout=10, isolation_level=None)
        db.row_factory = sqlite3.Row
        # A fresh registry may be opened by several spawned processes at once.
        # Install the busy handler before either process attempts the WAL-mode
        # transition; otherwise PRAGMA journal_mode can fail immediately while
        # the other process is creating the database.
        db.execute("PRAGMA busy_timeout=10000")
        deadline = time.monotonic() + 10
        while True:
            try:
                db.execute("PRAGMA journal_mode=WAL")
                break
            except sqlite3.OperationalError as exc:
                if "locked" not in str(exc).lower() or time.monotonic() >= deadline:
                    db.close()
                    raise
                time.sleep(0.01)
        db.execute("PRAGMA synchronous=FULL")
        db.execute("PRAGMA foreign_keys=ON")
        return db

    def _initialize(self) -> None:
        with closing(self._connect()) as db:
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS root_events (
                    event_index INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL CHECK(event_type IN ('issue','tombstone')),
                    root_id TEXT NOT NULL,
                    issuer_id TEXT NOT NULL,
                    key_id TEXT NOT NULL,
                    observation_id TEXT NOT NULL,
                    proposition_id TEXT NOT NULL,
                    value INTEGER NOT NULL CHECK(value IN (0,1)),
                    evidence_digest TEXT NOT NULL,
                    observed_at INTEGER NOT NULL,
                    issued_at INTEGER NOT NULL,
                    window_start INTEGER NOT NULL,
                    sequence INTEGER NOT NULL,
                    nonce TEXT NOT NULL,
                    reason TEXT,
                    previous_hash TEXT NOT NULL,
                    record_hash TEXT NOT NULL UNIQUE,
                    UNIQUE(issuer_id, nonce)
                );
                CREATE UNIQUE INDEX IF NOT EXISTS one_issuance_slot
                    ON root_events(issuer_id, window_start, sequence) WHERE event_type='issue';
                CREATE UNIQUE INDEX IF NOT EXISTS one_issue_per_root
                    ON root_events(root_id) WHERE event_type='issue';
                """
            )

    def issue(self, request: RootRequest) -> RootReceipt:
        now = int(self.clock())
        self._validate_request(request, now)
        root_id = self.root_identity(request)
        window_start = (request.observed_at // self.window_seconds) * self.window_seconds

        with closing(self._connect()) as db:
            db.execute("BEGIN IMMEDIATE")
            try:
                previous = self._verify_chain(db)
                used = db.execute(
                    "SELECT COUNT(*) FROM root_events WHERE issuer_id=? AND window_start=? "
                    "AND event_type='issue'",
                    (request.issuer_id, window_start),
                ).fetchone()[0]
                if used >= self.roots_per_window:
                    raise IssuanceLimitError("issuer root budget exhausted for this window")
                sequence = used + 1
                fields = {
                    "event_type": "issue", "root_id": root_id,
                    "issuer_id": request.issuer_id, "key_id": request.key_id,
                    "observation_id": request.observation_id,
                    "proposition_id": request.proposition_id, "value": int(request.value),
                    "evidence_digest": request.evidence_digest,
                    "observed_at": request.observed_at, "issued_at": now,
                    "window_start": window_start, "sequence": sequence,
                    "nonce": request.nonce, "reason": None, "previous_hash": previous,
                }
                record_hash = self._record_hash(fields)
                self._insert(db, fields, record_hash)
                db.commit()
            except sqlite3.IntegrityError as exc:
                db.rollback()
                raise ReplayError("duplicate root, observation nonce, or issuance slot") from exc
            except Exception:
                db.rollback()
                raise
        return RootReceipt(root_id, request.issuer_id, window_start, sequence, now, record_hash)

    def tombstone(self, root_id: str, *, reason: str, now: int | None = None) -> None:
        if not reason.strip():
            raise ValueError("tombstone reason is required")
        issued_at = int(self.clock() if now is None else now)
        with closing(self._connect()) as db:
            db.execute("BEGIN IMMEDIATE")
            try:
                previous = self._verify_chain(db)
                source = db.execute(
                    "SELECT * FROM root_events WHERE root_id=? AND event_type='issue'", (root_id,)
                ).fetchone()
                if source is None:
                    raise KeyError(root_id)
                if db.execute(
                    "SELECT 1 FROM root_events WHERE root_id=? AND event_type='tombstone'", (root_id,)
                ).fetchone():
                    raise ReplayError("root is already tombstoned")
                fields = {key: source[key] for key in (
                    "root_id", "issuer_id", "key_id", "observation_id", "proposition_id",
                    "value", "evidence_digest", "observed_at", "window_start", "sequence", "nonce"
                )}
                fields.update(event_type="tombstone", issued_at=issued_at,
                              nonce=f"tombstone:{root_id}", reason=reason, previous_hash=previous)
                record_hash = self._record_hash(fields)
                self._insert(db, fields, record_hash)
                db.commit()
            except Exception:
                db.rollback()
                raise

    def verify_integrity(self) -> bool:
        with closing(self._connect()) as db:
            self._verify_chain(db)
        return True

    def active_roots(self) -> frozenset[str]:
        with closing(self._connect()) as db:
            self._verify_chain(db)
            rows = db.execute(
                "SELECT root_id FROM root_events WHERE event_type='issue' AND root_id NOT IN "
                "(SELECT root_id FROM root_events WHERE event_type='tombstone')"
            ).fetchall()
        return frozenset(row[0] for row in rows)

    @staticmethod
    def root_identity(request: RootRequest) -> str:
        material = {
            "evidence_digest": request.evidence_digest,
            "issuer_id": request.issuer_id,
            "observation_id": request.observation_id,
            "proposition_id": request.proposition_id,
            "value": request.value,
        }
        digest = hashlib.sha256(
            json.dumps(material, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        return f"mp-root-v1:{digest}"

    def _validate_request(self, request: RootRequest, now: int) -> None:
        required = (request.issuer_id, request.key_id, request.observation_id,
                    request.proposition_id, request.evidence_digest, request.nonce)
        if any(not value for value in required):
            raise RootIssuanceError("all root identity fields are required")
        if len(request.evidence_digest) != 64 or any(c not in "0123456789abcdef" for c in request.evidence_digest):
            raise RootIssuanceError("evidence_digest must be lowercase SHA-256 hex")
        if abs(now - request.observed_at) > self.max_clock_skew_seconds:
            raise ClockError("observation is outside the accepted clock window")
        if not self.verifier.verify(
            request.issuer_id, request.key_id, request.canonical_bytes(), request.signature
        ):
            raise IssuerAuthenticationError("issuer identity or signature could not be verified")

    def _record_hash(self, fields: dict[str, object]) -> str:
        encoded = json.dumps(fields, sort_keys=True, separators=(",", ":")).encode()
        return hmac.new(self.integrity_key, encoded, hashlib.sha256).hexdigest()

    def _verify_chain(self, db: sqlite3.Connection) -> str:
        previous = "GENESIS"
        for row in db.execute("SELECT * FROM root_events ORDER BY event_index"):
            fields = {key: row[key] for key in (
                "event_type", "root_id", "issuer_id", "key_id", "observation_id",
                "proposition_id", "value", "evidence_digest", "observed_at", "issued_at",
                "window_start", "sequence", "nonce", "reason", "previous_hash"
            )}
            if row["previous_hash"] != previous or not hmac.compare_digest(
                row["record_hash"], self._record_hash(fields)
            ):
                raise RegistryIntegrityError(f"root ledger tampering at event {row['event_index']}")
            previous = row["record_hash"]
        return previous

    @staticmethod
    def _insert(db: sqlite3.Connection, fields: dict[str, object], record_hash: str) -> None:
        columns = list(fields) + ["record_hash"]
        db.execute(
            f"INSERT INTO root_events ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})",
            [fields[column] for column in fields] + [record_hash],
        )
