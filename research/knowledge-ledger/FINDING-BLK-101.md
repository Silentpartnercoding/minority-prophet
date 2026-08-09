# BLK-101 — a public blocklist is a directory of what is worth hiding

Audit prompted by the owner: *"whats these block lists exposing what should be
blocked is there any more of that please audit."* Repaired in the same change,
because the repair is small and leaving a disclosure recorded-but-live would be
worse than the disclosure.

## The class

A control that protects secret vocabulary by enumerating it, in a public file,
publishes the vocabulary. The list meant to keep terms out of public documents
is itself a public document naming them — and it is the highest-signal one,
because it is a curated index of exactly what the owner considers sensitive.

This is not hypothetical here. The pattern was found first in a finding
*document*: `FINDING-PBC-101.md` quoted the blocked phrases while explaining
that one was missing, and CI blocked it. That was the rule working. The audit
below asked whether the rule itself had the same defect.

## Audited

| artifact | verdict |
|---|---|
| `scripts/check_public_boundary.py` — secret-shape rules (private key, GitHub/AWS/Slack/Google tokens, bearer, assigned secret, credential URL, local path) | **fine.** Industry-standard signatures; every scanner has them. Publishing them reveals nothing. |
| `scripts/check_public_boundary.py` — the component rule | **leak.** Named an internal control-plane component in the clear. |
| `scripts/check_public_boundary.py` — the strategy-wording rule | **leak.** Named six business-vocabulary phrases in the clear. |
| `tests/test_public_boundary.py` | **leak.** Reproduced one of those phrases in a natural sentence as a fixture. |
| `.gitignore` | fine — generic build and env patterns only. |
| redaction markers across the repository | fine — no marker describes the content it removed. |
| `LIVE-COMMISSIONS.json` | fine — declares bounds and status, never the withheld values. |
| Gate and Border repositories | fine — zero occurrences of any audited term. |

## The substantive disclosure, found in a run record

`RUN-20260807-1/inputs/PROMPT.txt` — public since before the 2026-08-08
delivery — contained a sentence naming an internal control-plane directory and
stating that it **holds keys**. The instruction was that the directory is out of
scope; publishing the instruction published the location.

This is why the checker had a rule for that component at all: the term had
already leaked, the rule was written to stop it recurring, and the rule then
republished the name in a more prominent place than the original leak.

Redacted in place in both captured prompts, with a marker stating what was
removed and why. Neither file is digest-pinned (verified before editing).
Precedent: `754354d` redacted the internal-tooling paragraph from RUN-10's
captured brief on the same grounds.

## Repair

Sensitive vocabulary is now matched by **SHA-256 of the lowercased term** over
1–3 word n-grams. The shipped list contains only 64-character digests; a test
asserts that every entry is a hex digest, so a plaintext term cannot be
reintroduced without failing CI.

**Honest limit, stated in the source.** A digest of a short guessable phrase is
recoverable by anyone willing to hash a wordlist. This raises the cost from
"read the file" to "run a dictionary" — a real improvement for multi-word
phrases, a weak one for single common words. **It is obscurity, not secrecy.**
For vocabulary that must genuinely not be recoverable, `MP_BOUNDARY_TERMS` loads
newline-separated terms from a CI secret; those never enter the tree in any
form. The shipped digests are the baseline, not the ceiling.

The regression tests were rewritten to inject their own term through that
environment variable, so the test file names nothing real either.

## BL-050 closed in the same change

Gap 1 is repaired. The local-path rule required an enumerated delimiter before
the path, so assignments and scp-style remotes passed. Replaying the 37 real
leaked lines this program removed on 2026-08-08:

    blocked before : 26 / 37
    blocked after  : 37 / 37

Gap 2 is repaired: the internal tooling term the owner named as never-public is
now in the digest set, and was measurably allowed before.

## What this does not fix

Nothing here addresses publishing *answers* rather than *secrets* — the M27
class, where ordinary integers in a results table retire a live commission's
pass condition. **BL-048 is now built** — `scripts/check_withheld_leak.py`, wired into CI
beside the boundary check. It reads `LIVE-COMMISSIONS.json`, derives each live
commission's withheld set from its results file minus declared bounds, and
rejects additions containing those values in bare or comma-grouped form.

Values below 100 are excluded: a blocked set containing 2 or 7 makes every
document a violation and the control is switched off within a day. A live
commission whose results file is missing fails closed rather than passing
silently. Closing a commission unblocks its values, because the answer is then
legitimately publishable — that is what closing means.

The decisive test replays the actual regression: given LIN-000 declared live,
RUN-20260807-10's draft run report is rejected. The check catches the leak that
motivated it.

## Follow-on: the inherited list contains generic English

Demonstrated by this document. An earlier draft of the audit table used a
two-word phrase descriptively, in ordinary prose about governance, and the new
digest matcher blocked it. The phrase is plain English, not proprietary.

Three of the six inherited business-vocabulary phrases are of that kind. They
carry two costs: they false-positive on any document that discusses strategy in
the abstract, and hashing buys them nothing, since a two-word English phrase
falls to a wordlist immediately. The genuinely distinctive terms -- a coined
component name, an internal tooling name -- are the ones the digest set protects
usefully.

**BL-052 — owner decision, 2026-08-08: "generic english does not belong".**
Five inherited entries were ordinary business English and are removed. Two more
were hyphenated variants the matcher can never reach — it tokenises on word
characters, so the one-word digest already covered them; they were dead weight
that made the list look larger than its coverage.

Three digests remain, all coined or internal names. Generic vocabulary is a
review question, not a boundary rule: it blocks honest writing and protects
nothing, since a two-word English phrase falls to a wordlist immediately.
