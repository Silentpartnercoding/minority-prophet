# KL-001 protocol v0.2 — FAILED on its primary endpoint

Run 2026-08-09 against the registered corpus `corpus/frozen-v1`, manifest digest
pinned in the preregistration. Reported as a failure and **preserved as one**.

## Result against the registered endpoints

| endpoint | registered | observed | |
|---|---|---|---|
| **primary** — false-clean rate | strictly below 12.2% | **12.2%** | **FAIL** |
| secondary — recall | at least 77.6% absolute | 81.7% | pass |
| secondary — per-class | no class below baseline | none | pass |

The registered `failureCondition` reads *"false-clean rate not lower ... Each is a
failure on its own."* It is not lower. Protocol v0.2 fails.

## Why: the corpus cannot exhibit the effect the endpoint asks about

    location statuses across the whole corpus:
      searched 208 · not_searched 0 · unavailable 0

Every file is readable and every scan succeeds, so **the search is always
complete**. The dual ledger's only lever — refusing a clean verdict when coverage
is incomplete — is never pulled. Both arms see identical evidence and reach
identical conclusions on all 60 repositories.

## What this does and does not establish

**It does not establish that the dual ledger fails.** It establishes that on a
corpus with no incomplete searches, a discipline about incomplete searches
changes nothing. That is close to a tautology, and the experiment as registered
could not have shown otherwise.

**It does establish where the mechanism's value must lie**: entirely in the
unhappy path. Unreadable files, parse failures, timeouts, skipped directories. A
corpus without them cannot distinguish the dual ledger from the plain scanner,
and this one has none.

## The defect is mine and it is the same one this programme keeps finding

`generate_corpus.py` writes only well-formed, readable files. I registered
endpoints against a corpus structurally incapable of moving the primary one, and
recommended the owner authorise it. That is the same class as a test that cannot
fail and a target with no denominator — both of which this programme removed in
the preceding days, from other people's work and then from its own.

The pre-flight would not have caught it: its traps ask whether tests can fail
given the registration, not whether the *population* can exhibit the effect the
endpoint measures. Recorded as **BL-060** — a trap for "can this corpus produce
the outcome the primary endpoint asks about?"

## Disposition

**The failure stands.** `frozen-v1`, its baseline, its endpoints and this result
are permanent record. Nothing here is re-baselined into a pass.

A corpus containing unreadable files and multi-defect files (BL-059) tests both
this mechanism and the taxonomy question, but it is **a new registration with its
own preregistered endpoints — protocol v0.3 — and not a retry of v0.2**. Building
a corpus after seeing v0.2 fail and re-running under the old endpoints would be
fitting the experiment to the outcome.
