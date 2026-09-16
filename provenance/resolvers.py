"""Doormen. One per reference form, each answering only "does this exist?".

A resolver is deliberately NOT a source of truth. It answers existence, never
quality, never relevance, never whether the claim it backs is correct. The moment
a resolver starts grading a source it becomes a new thing that has to be trusted,
and the problem has moved rather than gone.

Three values, always: True (exists), False (does not), None (could not tell). The
third is not a failure mode to be tidied away -- it is the honest answer whenever
a doorman is offline, rate-limited, or not configured, and `root_dereference`
depends on it staying distinct.

OFFLINE BY DEFAULT. `local_resolver` touches nothing but this machine. The HTTP
one must be constructed explicitly, takes an allowlist of hosts, and returns None
rather than raising on any transport problem, so a flaky network degrades a run
to `unverifiable` instead of manufacturing absence.
"""

from __future__ import annotations

import hashlib
import os
import re
import subprocess
from pathlib import Path
from typing import Callable, Iterable

SHA_LIKE = re.compile(r"^[0-9a-f]{32,128}$", re.I)


# ---------------------------------------------------------------- local forms

def git_object_resolver(repositories: Iterable[str]) -> Callable[[str, str], bool | None]:
    """Resolve a `hash` reference as a git object in any of the given repositories.

    Returns None when no repository is readable here -- "I have nowhere to look"
    is not "the object does not exist", and a job whose repository lives on
    another machine has not failed.
    """
    repos = [Path(r) for r in repositories]

    def resolve(form: str, reference: str) -> bool | None:
        if form != "hash" or not SHA_LIKE.match(reference):
            return None
        readable = [r for r in repos if (r / ".git").exists()]
        if not readable:
            return None
        for repo in readable:
            try:
                subprocess.run(["git", "-C", str(repo), "cat-file", "-e", f"{reference}^{{commit}}"],
                               check=True, capture_output=True, timeout=30)
                return True
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError):
                continue
        return False

    return resolve


def content_store_resolver(store: str) -> Callable[[str, str], bool | None]:
    """Resolve a `hash` reference by content-addressed lookup under `store`.

    Hashes every file once and compares. This is the move DRI-7 measured: of 284
    references whose recorded path had died, 82% were still recoverable by
    content. A path is a rumour about where something was; a digest is the thing.
    """
    root = Path(store)
    cache: dict[str, set[str]] = {}

    def digests() -> set[str]:
        if "d" not in cache:
            found: set[str] = set()
            if root.is_dir():
                for path in root.rglob("*"):
                    if path.is_file():
                        try:
                            found.add(hashlib.sha256(path.read_bytes()).hexdigest())
                        except OSError:
                            continue
            cache["d"] = found
        return cache["d"]

    def resolve(form: str, reference: str) -> bool | None:
        if form != "hash" or not SHA_LIKE.match(reference):
            return None
        if not root.is_dir():
            return None
        return reference.lower() in digests()

    return resolve


def file_resolver(roots: Iterable[str]) -> Callable[[str, str], bool | None]:
    """Resolve a `url` reference of the form file:// under one of `roots`.

    Confined to the declared roots on purpose: a resolver that will stat any path
    it is handed is a file-existence oracle for the whole disk.
    """
    bases = [Path(r).resolve() for r in roots]

    def resolve(form: str, reference: str) -> bool | None:
        if form != "url" or not reference.lower().startswith("file://"):
            return None
        target = Path(reference[7:])
        try:
            resolved = target.resolve()
        except OSError:
            return None
        if not any(resolved == b or b in resolved.parents for b in bases):
            return None          # outside the declared roots: not ours to answer
        return resolved.exists()

    return resolve


# ---------------------------------------------------------------- network form

def http_resolver(allowed_hosts: Iterable[str], *, timeout: float = 10.0,
                  opener=None) -> Callable[[str, str], bool | None]:
    """Resolve `doi`, `url` and `arxiv` by asking the network. EXPLICIT ONLY.

    Constructed by hand, never by default, and confined to an allowlist -- a
    resolver that will fetch anything is a crawler wearing a verification badge,
    and it makes a result depend on when you ran it.

    Every transport failure returns None. A 404 is the only thing that returns
    False, because it is the only response that says the reference is not there.
    """
    allowed = {h.lower() for h in allowed_hosts}
    if opener is None:                                  # pragma: no cover
        from urllib.request import urlopen as opener_  # imported lazily on purpose
        opener = opener_

    def url_for(form: str, reference: str) -> str | None:
        if form == "doi":
            bare = re.sub(r"^https?://(dx\.)?doi\.org/", "", reference, flags=re.I)
            return f"https://doi.org/{bare}"
        if form == "arxiv":
            return f"https://arxiv.org/abs/{re.sub(r'^arxiv:', '', reference, flags=re.I)}"
        if form == "url":
            return reference if reference.lower().startswith(("http://", "https://")) else None
        return None

    def resolve(form: str, reference: str) -> bool | None:
        target = url_for(form, reference)
        if target is None:
            return None
        host = re.sub(r"^https?://", "", target).split("/")[0].lower()
        if host not in allowed:
            return None                                  # not ours to answer
        try:
            with opener(target, timeout=timeout) as response:
                return 200 <= getattr(response, "status", 200) < 400
        except Exception as error:                       # noqa: BLE001
            if "404" in str(error) or "410" in str(error):
                return False
            return None                                  # everything else: cannot tell

    return resolve


# ---------------------------------------------------------------- composition

def first_answer(*resolvers: Callable[[str, str], bool | None]) -> Callable[[str, str], bool | None]:
    """Ask each doorman in turn; take the first one that can answer.

    Order matters and cheap-and-local should come first: an offline lookup that
    succeeds saves a network call, and a network call that fails must not
    override a local answer that succeeded.
    """
    def resolve(form: str, reference: str) -> bool | None:
        for candidate in resolvers:
            answer = candidate(form, reference)
            if answer is not None:
                return answer
        return None
    return resolve


def local_resolver(*, repositories: Iterable[str] = (), content_store: str | None = None,
                   file_roots: Iterable[str] = ()) -> Callable[[str, str], bool | None]:
    """Everything answerable without a network. Safe to run anywhere, any time."""
    parts = []
    if repositories:
        parts.append(git_object_resolver(repositories))
    if content_store:
        parts.append(content_store_resolver(content_store))
    if file_roots:
        parts.append(file_resolver(file_roots))
    return first_answer(*parts) if parts else (lambda form, reference: None)
