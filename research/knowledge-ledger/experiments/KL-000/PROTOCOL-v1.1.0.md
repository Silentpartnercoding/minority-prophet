# KL-000: dual-ledger conformance — protocol v1.1.0

Status: **preregistered.** This document and `preregistration-v1.1.0.json` are
committed before the v1.1.0 confirmatory re-run is executed and before any of
its outcomes are inspected.

## Relationship to v1.0.0

v1.1.0 is a **new registration, not an edit**. `PROTOCOL.md` (v1.0.0),
`preregistration.json`, and the ten fixtures `fixtures/c01…c10.json` are
preserved byte-for-byte as registered at commit `c977347`; RUN-20260807-1's
result and the independent reimplementation's result both stand under v1.0.0
and are not reinterpreted by this document. The v1.1.0 fixture C11 lives under
`fixtures/v1.1.0/` precisely so the v1.0.0 fixture set is untouched.

**The evaluator under test is unchanged**: `knowledge_ledger/transaction.py`
at `sha256:15dfd50051ef5da3db13d8e591f58537325ee50aa4e3573914f86e4ff3a3e21f`,
the same bytes v1.0.0 froze. v1.1.0 changes specification text only. Every
repair below either documents behaviour both existing implementations already
have, or resolves an ambiguity in favour of the existing reference behaviour.

**Preregistered prediction, and the point of the re-run:** because the
repairs are documentation rather than behaviour change, the v1.1.0
confirmatory run must reproduce RUN-20260807-1's numbers *exactly*:

| Quantity | Required value |
|---|---|
| exhaustive worlds / receipts / fail-closed / violations | 176,120 / 110,840 / 65,280 / 0 |
| exhaustive conclusions (absent / not_established / present / supported) | 160 / 49,480 / 41,820 / 19,380 |
| randomized worlds / violations | 1,000,000 / 0 |
| randomized receipts / fail-closed | 243,381 / 756,619 |
| baseline violations B1 / B2 / B3 / B4 | 634,440 / 26,880 / 26,208 / 189,720 |
| fail-closed causes | exactly one per phase: `ValueError: One root cannot support opposing sides.` |

**If any number moves, the run halts and the deviation is reported as a
finding**: it would mean a "repair" changed behaviour, and the claim that
v1.1.0 merely documents existing conduct would be false. Identical numbers
are the evidence for that claim, which is why the full re-run is performed
rather than asserted away.

## Why v1.1.0 exists

The independent Rust reimplementation (results and findings imported under
`results/independent/`) reproduced the exhaustive phase exactly and passed all
ten invariants, yet disagreed with the reference on the `conclusion` of 22,440
of 110,840 receipt-producing worlds — a divergence it predicted and quantified
before any comparison (its ambiguity A3). No invariant constrains
`conclusion`, so the divergence was invisible to the entire v1.0.0 test
surface. Three further specification defects (its findings F8, F9, F10) were
found to be repaired in *both* implementations' behaviour without either
having been told to. v1.1.0 writes these four things down.

## The four repairs

### R1 — tie rule for presence claims (resolves ambiguity A3) — OWNER DECISION

**A presence claim with equal counts of distinct supporting and distinct
opposing roots concludes `not_established`. Ties are undecided, not
supported.** In full: for `claim.type == "presence"` the conclusion is
`supported` if and only if the number of distinct supporting roots strictly
exceeds the number of distinct opposing roots, and `not_established`
otherwise. A presence claim never concludes `present` or
`absent_within_declared_scope`; those belong to absence claims, whose rule is
unchanged (any opposing root → `present`; complete coverage and no opposing
root → `absent_within_declared_scope`; otherwise `not_established`).

This is recorded explicitly as a **decision by the owner, not a derivation.
It could defensibly have gone the other way.** The independent implementer
read presence as existential — one witness settles it, opposition cannot
defeat "it was found" — and that reading is preserved, with its rationale, in
`results/independent/FINDINGS.md` (F6, ambiguity A3). The owner decided that
ties are undecided. The decided rule matches what the reference already
implements (`transaction.py:69`, strict `>`), so the expected numeric change
is zero.

Surface of the decision, measured: 22,440 exhaustive worlds (20.2% of
receipts) — 16,320 tie worlds decided directly by this rule, plus 6,120
strict-minority worlds (opposing > supporting ≥ 1) that follow a fortiori:
if a tie is not established, a minority cannot be. Fixture C11 pins the tie
case with a registered expected conclusion.

### R2 — non-empty declared scope (repairs finding F8)

**`search.complete` requires `declared > 0`, and a search ledger declaring
zero locations is inadmissible: evaluation refuses fail-closed and no receipt
is produced.** Under the v1.0.0 text — `declared == len(locations)`,
`complete == (searched == declared)` — a zero-location ledger had
`declared == 0`, `searched == 0`, `complete == true`, and I2's antecedent was
satisfied vacuously, issuing `absent_within_declared_scope` for a world in
which nothing was searched. That is the limiting case of exactly the
laundering this experiment exists to prevent, reachable by following the
specification literally.

Verified before registration: the reference refuses
(`ValueError: The declared search space must not be empty.`,
`transaction.py:31–32`) and the independent implementation refuses (its attack
A06, cause `empty_search_ledger`). **Neither was told to by the
specification.** Both exceeded it in the same direction; v1.1.0 makes that
conduct required rather than fortunate. Expected numeric change: zero — the
declared bounds already say `locationCount ≥ 1`, so no enumerated or sampled
world reaches this rule; only adversarial input does.

### R3 — location identifier uniqueness, as invariant I11 (repairs finding F9)

**I11 (new, hard): the `id` values of `searchLedger.locations` must be
pairwise distinct. A ledger containing a duplicate location id is
inadmissible: evaluation refuses fail-closed and no receipt is produced.**

Without I11, nothing in the invariant set stops duplicate location ids
inflating `declared`: padding the ledger with copies of an already-`searched`
location changes the coverage arithmetic — the search-ledger mirror of the
copy attack I1 prevents on the evidence ledger.

**Why a new invariant I11 rather than an extension of I8.** I8 constrains the
*arithmetic of an emitted receipt* against its world; its violations are
wrong numbers in a receipt that exists. I11, like I3 and I9, is an
*admissibility* rule whose correct outcome is that no receipt exists at all —
a different observable, checked on a different path. Folding it into I8 would
also change I8's registered statement between versions and muddy any
cross-version comparison of I8 violation counts. I11 is therefore registered
as its own hard invariant, eleventh in the set.

Verified before registration: the reference refuses
(`ValueError: Search-location identifiers must be unique.`,
`transaction.py:34–36`) and the independent implementation refuses (its attack
A07, cause `duplicate_location_id`). Neither was required to. Expected
numeric change: zero — the exhaustive generator enumerates positional
location ledgers with distinct ids and the randomized generator likewise, so
I11's enforcement is exercised by the adversarial phase, not the enumerated
ones.

### R4 — canonical form and digest scope (repairs finding F10)

v1.0.0's I4 required "byte-identical canonical JSON" and I6 a self-verifying
`contentDigest` while defining neither, so both invariants constrained an
implementation against itself rather than against the protocol, and digest
values could not agree across implementations even in principle. v1.1.0
defines both. The definition below matches the reference's existing output
byte-for-byte; expected numeric change: zero.

**Canonical JSON.** The canonical form of a value is the UTF-8 encoding
(no BOM, no trailing newline) of its JSON serialisation with:

1. **Object member ordering:** members sorted by key, keys compared as
   sequences of Unicode code points, ascending.
2. **No whitespace:** the item separator is `,` and the key separator is `:`;
   no other bytes appear between tokens.
3. **String escaping, minimal:** `"` is emitted as `\"`, `\` as `\\`; the
   control characters U+0008, U+0009, U+000A, U+000C, U+000D are emitted as
   `\b`, `\t`, `\n`, `\f`, `\r`; every other code point below U+0020 is
   emitted as `\u00XX` with lowercase hex. **Every code point at or above
   U+0020, including all non-ASCII, is emitted literally as raw UTF-8** — no
   `\uXXXX` escapes for printable characters, no surrogate-pair escapes.
4. **Numbers:** every number in a receipt is a non-negative integer, emitted
   in base 10 with no sign, no decimal point, no exponent, and no leading
   zeros. Booleans are `true`/`false`. Receipts contain no floats and no
   nulls; a receipt that contained either would have no defined canonical
   form under this protocol.
5. **Arrays** preserve their order; canonicalisation never reorders them
   (order *invariance* of receipt content is I7's job, achieved by the
   evaluator sorting root lists before emission, not by the codec).

This is exactly the output of Python's
`json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")`,
stated here language-neutrally so that conformance does not require Python.

**Digest scope.** `contentDigest` is computed over the receipt object with
its **top-level `contentDigest` member removed** and nothing else removed:
all other fields — `schema`, `transactionId`, `claim` (both members),
`search` (all four members), `evidence` (all seven members), `conclusion`,
`reason`, `limits` — are covered. The digest string is
`"sha256:" + lowercase-hex(SHA-256(canonical bytes of the unsigned receipt))`.
Verification recomputes and string-compares.

**Fixture C11** (`fixtures/v1.1.0/c11-canonical-digest.json`) carries an
expected `contentDigest`
(`sha256:84e63c21271a19c3bfbb1d42c5ce61e60288456a48c33829a66ae916bc33eafe`,
unsigned canonical form 703 bytes), so the definition is testable across
implementations rather than self-referential. Its proposition contains a
non-ASCII letter, a typographic dash, a double quote, and a backslash, making
rules 1–3 load-bearing; its evidence ledger is a tie, making R1 load-bearing
in the same fixture. Its `margin` is 0, **deliberately sign-agnostic** so the
fixture does not silently resolve the still-open margin-sign ambiguity
(finding F5; see "What v1.1.0 does not repair").

## Phases

As v1.0.0, with the fixture phase extended:

1. **Fixture.** C01–C10 as registered under v1.0.0, unchanged, plus **C11**
   with its pinned digest.
2. **Exhaustive-small.** Identical to v1.0.0: 176,120 worlds, same bounds,
   same derivation, count asserted before any invariant is evaluated.
3. **Randomized.** Identical to v1.0.0: 1,000,000 worlds, frozen seed
   `20260807`, same bounds. (The seed freezes *this implementation's* stream
   only; see "What v1.1.0 does not repair", F11.)
4. **Adversarial.** The v1.0.0 suite plus permanent tests for R2 and R3
   refusals.

Baselines B1–B5 exactly as v1.0.0, full exhaustive set, same checker.

## Stop, failure, and invalidation

All v1.0.0 conditions carry over unchanged (first hard violation halts and is
preserved; any B5 violation fails KL-000; generator drift, count mismatch,
hash mismatch, seed non-reproduction, or any passing baseline invalidates).
v1.1.0 adds one invalidation condition: **any required value in the
preregistered-prediction table differing from the observed value invalidates
the "documentation-only" claim** and halts the run as a finding. I11 joins
the hard-invariant set, so a receipt emitted for a duplicate-id ledger in the
adversarial phase is a hard violation.

## What v1.1.0 does not repair, deliberately

These findings from `results/independent/FINDINGS.md` are real, open, and
**not** addressed here, because the owner's repair list for this version is
exactly R1–R4 and mixing owner decisions with agent additions inside a
registration would obscure who decided what. Candidates for v1.2.0:

- **F1/F2:** I2 and I5 are stated over receipt fields, so an evaluator that
  fabricates or omits those fields satisfies them vacuously (the registered
  baseline B2 does not fail I2 as literally read — measured, not
  hypothetical). Repair direction: state both world-referentially, or
  register the receipt-internal and world-referential forms separately.
- **F3:** B2 and B3 describe the same ablation unless B2 is read as
  fabricating its search block; the four positive controls may be three.
- **F4:** `conversionsToReverse` is used in fixtures and I1's freeze list but
  defined nowhere; its value on an empty ledger (1, with no root available to
  convert) is arguably wrong. Reverse-engineered formula:
  `floor(|margin|/2) + 1`.
- **F5:** the sign of `margin` is unpinned (reference: absolute value;
  independent: signed). 38,760 exhaustive worlds' receipts differ between
  readings. C11 was deliberately made sign-agnostic rather than resolving
  this by the back door.
- **F11:** the frozen seed does not freeze a cross-implementation world
  stream; the randomized phase can only ever be a replication between
  implementations. Repair direction: register a draw schedule, or adopt the
  independent implementation's `worldStreamHash` primitive.
- **F12:** the adversarial phase is defined by reference to a test file
  rather than by specification, so it is not reproducible from the protocol.
- **F13:** C06's note ("absence is admissible here and only here") is
  contradicted by C04 and C07 in the same fixture set.
- **F14:** `unavailable` is reported and reconciled by I8 but no conclusion
  depends on it.

## Safety boundary

Unchanged from v1.0.0: synthetic worlds only; no personal, patient, sealed,
classified, or restricted data; no network; no spend; no actuation; no
decision authority. Execution needs no human authorization; publishing and
promotion do, and neither is performed by the run that produces the result.

## Claim discipline

**Strongest supported claim if the v1.1.0 re-run passes with identical
numbers:** within the declared bounds, the reference evaluator conforms to
protocol v1.1.0, and v1.1.0's four repairs documented behaviour the evaluator
already had — no number moved.

**What the independent reproduction has established so far** (and the re-run
does not change): agreement of two implementations on the ten v1.0.0
invariants over an exactly-reproduced exhaustive enumeration, with the
conclusion function contested on 20.2% of receipts until R1 decided it, and a
replication (not reproduction) of the randomized phase. **"Verified" is not
licensed** — the word for this state is *reproduced under a specification
now known to have been ambiguous where the implementations disagreed*.

**Nearest unsupported extension:** that the independent implementation
conforms to v1.1.0 (its re-run against v1.1.0 is a separate, future
commission and is this kernel's next gate); that the dual ledger recovers
truth; that the invariants hold outside declared bounds; that any real
process is improved.

## Amendment log

None at registration. Amendments, if any, will be listed here rather than
applied silently, following the v1.0.0 discipline.

| # | When | Change | Experimental content affected |
|---|---|---|---|
| 1 | RUN-20260807-9, after the program's close-outs; a **provenance correction, not a rule change** | R1's characterisation above — "a decision, not a derivation; could defensibly have gone the other way" — is **corrected: the rule was derivable from the published paper, and the specification lost the connection.** `papers/minority-prophet-v1.0.3.md` §3 (line 53) defines the evidence-root aggregator: *"returns 1 if \|S₁\| > \|S₀\|, 0 if reversed, **abstaining on ties** (optionally below a margin threshold)"*. Ties abstain; strict minorities take the opposing verdict; the existential reading contradicts the published aggregator on all 22,440 divergent worlds. The 22,440-world divergence was therefore not two defensible readings of an underspecified rule — it was one implementation contradicting a published definition **because no KL-000 document cited the paper** (zero citations, grep-verified, RUN-20260807-9). The registered text is preserved above unrewritten; the independent implementer's reading remains defensible *given the package it received*, which is exactly the point: the package severed a derivation chain that existed. The owner's choice happened to match the paper. R1's behaviour is unchanged. | **None.** Behaviour identical; provenance only. |

## `protocolCommit` remains null

Same registration mechanics as v1.0.0, same reasoning (see `PROTOCOL.md`,
"Why `protocolCommit` is deliberately null"): the sidecar
`PROTOCOL-COMMIT-v1.1.0.txt` records the registration commit after git
assigns it, and

```bash
P=research/knowledge-ledger/experiments/KL-000
test "$(git log -1 --format=%H -- $P/preregistration-v1.1.0.json)" \
   = "$(cat $P/PROTOCOL-COMMIT-v1.1.0.txt)" && echo "unedited since registration"
```

is the immutability check for this registration, independent of v1.0.0's.
