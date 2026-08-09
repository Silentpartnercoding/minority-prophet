# LIN-000 v0.2 — lineage-bearing schema, with a self-contained generator

Registered by RUN-20260808-3 **before the v0.2 reference exists**, KL-000 style.
Supersedes the randomized phase and the enumeration order of
`REGISTRATION.md` (v0.1), which is preserved unchanged. Not a registry kernel;
advances no kernel state; modifies no KL-000 registration.

## Why v0.2

BL-044 commissioned an independent Rust implementation against v0.1 and measured
the result rather than guessing at it (`FINDING-BL044.md`). Both pre-declared
readings **missed**. The matches were found by sweeping **96** enumeration orders
and **72** draw-schedule readings, one correct each.

The F11 repair — "register the draw schedule, not just the seed" — is therefore
**necessary but not sufficient**. It moved the program from "no cross-language
stream is possible" to "one coin-flip away". This registration closes the
remaining gap, and re-commissioning is the test of whether it did.

Three defects are fixed. Each was measured, not supposed.

**D1 — the schedule named a language's generator instead of defining one.**
v0.1 said `random.Random`. Reproducing it required knowing that CPython's
`_randbelow` uses `getrandbits` with rejection, that `_randbelow(1)` still
consumes a bit, and how CPython builds a 53-bit float from two words. None of
that is in the registration; it is CPython source knowledge. The implementer
further showed **two conforming MT19937s diverge on the same seed**, so even
naming the algorithm and seed under-determines the stream.

**D2 — draws were registered as distributions, not primitives.** "k uniform in
1..20" has several standard realisations that are distribution-identical and
**stream-distinct**, because they consume different numbers of draws. One extra
word shifts everything after it.

**D3 — the exhaustive phase had no registered order.** That phase contains no
PRNG and still missed, because a digest is order-sensitive and the order was
never stated.

## Schema

Unchanged from v0.1: `minority-prophet.lineage-world.v0.1`. A world is an ordered
list of claims `[{id, parentIndex, side}]`; `parentIndex` is `null` (a **root**)
or the index of an **earlier** claim; `side ∈ {0,1}`; `root(c)` walks parent
edges to the chain head; side-consistent iff every edge joins same-side claims;
`S_a = {root(c) : side(c) = a}` computed over **all** claims, deliberately not
restricted to roots, so Lemma 1 is a theorem *about* this function rather than
baked into it. Verdict: `1` if `|S₁| > |S₀|`, `0` if reversed, `abstain` on ties
(τ = 0, per paper [E6]).

## Generator — defined here, referenced from nowhere

Let `seed = 20260808`, encoded as 8 bytes big-endian: `seed_be`.

The generator is an infinite sequence of 32-bit unsigned words `w(0), w(1), …`:

    block(m) = SHA-256( seed_be || uint64_be(m) )        # 32 bytes
    w(i)     = uint32_be( block(i // 8)[ 4*(i % 8) : 4*(i % 8) + 4 ] )

Draws are consumed strictly in order, starting at `w(0)`. A draw *consumes* one
or more words; the next draw begins at the first unconsumed word.

Nothing about this depends on a language runtime. Two implementations that agree
on SHA-256 and big-endian integers agree on every word.

### `uniform_below(n)` — the only sampling primitive

For integer `n ≥ 1`:

    limit = 2**32 - (2**32 mod n)
    repeat:
        take the next word w
        if w < limit: return w mod n
        # otherwise the word is rejected and another is taken

**`uniform_below(1)` consumes exactly one word and returns 0.** With `n = 1`,
`2**32 mod 1 = 0`, so `limit = 2**32` and no word can be rejected. This is the
degenerate case v0.1 left open (D2); it is now stated, and an implementation
that short-circuits it will diverge and should.

There is no float primitive and no other sampler. Probabilities are integer
comparisons:

- "with probability 3/10" means `uniform_below(10) < 3`
- "with probability 9/10" means `uniform_below(10) < 9`

## Randomized phase — the draw schedule, per claim, in order

**100,000 worlds.** For each world, in order:

1. `k = 1 + uniform_below(20)`.
2. For claim index `i = 0 .. k-1`, in ascending order:
   - **Root decision.** If `i == 0`, the claim is a root and **no draw is
     consumed**. Otherwise consume `is_root = uniform_below(10) < 3`.
   - **Parent.** If the claim is not a root, `parentIndex = uniform_below(i)`.
     If it is a root, `parentIndex = null` and no parent draw is consumed.
   - **Side.** If the claim is a root, `side = uniform_below(2)`. Otherwise
     consume `keep = uniform_below(10) < 9`; `side` is the parent's side if
     `keep`, else `1 - parent's side`.

Claim 0's boundary case (D2, the implementer's R3 — *"a genuine coin-flip in the
prose"*) is now decided in the text: **no draw is consumed.** The 0.3 branch is
undefined at `i = 0` because its alternative ranges over an empty set, so the
draw would decide nothing.

Every draw in this phase is a `uniform_below` call. The word cost of a world is
therefore fully determined by its own outcomes.

## Exhaustive phase — the enumeration order, registered

All worlds with `k = 1..6`; position `i` has `(i+1)` parent choices
(`{null} ∪ earlier`) and 2 sides, so `count(k) = k! · 2^k` and the **declared
total is 50,362** (2 + 8 + 48 + 384 + 3,840 + 46,080), asserted before any
evaluation; a mismatch invalidates the run.

Order (D3):

1. **Across k:** ascending, `k = 1, 2, …, 6`.
2. **Within k:** an odometer over positions `0 .. k-1` in which **position `k-1`
   varies fastest** and position `0` slowest.
3. **Within a position `i`:** parent-major. Parent choices in the order
   `null, 0, 1, …, i-1`; for each parent choice, `side = 0` then `side = 1`.

Side-consistent and side-inconsistent worlds are both enumerated; the negative
controls need the latter.

## Canonical stream form — in the registration, not the brief

For each world, in emission order, render each claim as `P|S` where `P` is the
decimal `parentIndex` or the single character `-` for a root, and `S` is the
decimal side. Join a world's claims with `;`. Terminate each world with a single
`\n` (U+000A). Encode as ASCII. The **stream digest** is SHA-256 over that
concatenation.

## Prefix digests

Each phase publishes, alongside its total digest, the SHA-256 of the stream
prefix after every **1,000 worlds**. This costs nothing, leaks no more than the
total, and converts an unlocalisable miss into a binary search — the
implementer's recommendation, adopted.

## Tests that can fail — registered expectations

Unchanged in substance from v0.1, restated for completeness:

- **L1-positive:** on side-consistent worlds, `S_a` equals the set of roots
  asserting `a`. Violations MUST be 0.
- **L1-negative:** side-inconsistent worlds where `S_a` differs from that set
  MUST exist (expected > 0; count reported), else the positive test is vacuous.
- **T1-positive:** under root-preserving, side-consistent rewiring the verdict
  MUST NOT change. Violations MUST be 0; rewirings checked is reported.
- **T1-negative:** rewirings that break root-preservation or side-consistency and
  DO change the verdict MUST exist (expected > 0).
- **Ablations:** a shallow-`S_a` and a claim-count ablation MUST each be caught.

## Invalidation

Exhaustive count ≠ 50,362; any expected-nonzero count observed zero; any
`uniform_below` implemented with a float; any phase whose regenerated stream
digest differs from its first computation within the same run.

## What v0.2 does not change

The schema, the theorems under test, τ = 0, and the declared bounds. Only the
generator, the draw schedule's precision, the enumeration order, and the
canonical form move. The v0.1 results remain valid **as v0.1 results**; they are
not comparable to v0.2 streams and are not expected to be.
