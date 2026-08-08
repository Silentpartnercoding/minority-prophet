# LIN-000 reimplementation — reading decisions, frozen before comparison

Written **before** computing either digest. Every choice below is forced by an
under-determination in `REGISTRATION.md`; each is recorded with the alternatives
I rejected, because the hypothesis under test is precisely whether the
registered prose fixes a stream.

Implementation language: **Rust** (no dependencies, no build script, no Python
at any point — including validation; checking my PRNG against CPython would
reintroduce exactly the circularity the brief forbids).

Independent validation of primitives uses published constants I can state
without consulting the reference:
- SHA-256 against FIPS-180-4 vectors for `""` and `"abc"`, plus a cross-check of
  a multi-megabyte file against system `shasum -a 256`.
- MT19937 against the reference `mt19937ar.c` output: `init_genrand(5489)` first
  output `3499211612`; `init_by_array([0x123,0x234,0x345,0x456])` first outputs
  `1067595299, 955945823, 477289528, 4107686914`; first `genrand_res53()`
  `0.76275443`.

---

## Derived, not adopted

`count(k) = prod_{i=0..k-1} 2*(i+1) = 2^k * k!` — position i has (i+1) parent
choices (`{null} ∪ earlier`) and 2 sides. k=1..6 gives
2, 8, 48, 384, 3840, 46080, total **50362**. Derived before reading the
registration's stated total; it agrees.

---

## E. Exhaustive-phase ambiguities

The registration fixes *which* worlds are enumerated and never fixes their
**order**, yet the digest is order-sensitive. This is an ambiguity in its own
right, independent of the randomized phase.

- **E1 — order across k.** Ascending k = 1..6.
  *Chosen because* the registration's own sum is written in ascending order.
  Confidence: high.
- **E2 — which position varies fastest.** The **last** position (odometer with
  position k-1 least significant), i.e. `itertools.product` semantics.
  *Rejected:* first position fastest. Confidence: medium.
- **E3 — parent ordering within a position.** `null` first, then earlier claims
  ascending `0..i-1`.
  *Chosen because* the registration writes the choice set as `{null} ∪ earlier`,
  null first. *Rejected:* earlier-first-then-null; descending. Confidence: medium.
- **E4 — parent-major or side-major within a position.** **Parent-major**: for
  each parent choice, side 0 then side 1.
  *Rejected:* side-major. Confidence: low — nothing in the text speaks to this.

## R. Randomized-phase ambiguities

Seed `20260808`, `random.Random` ⇒ MT19937 seeded via CPython `init_by_array`
with the 32-bit little-endian limb array of `abs(seed)`, i.e. key `[20260808]`
(one limb, since 20260808 < 2^32). This part is unambiguous *given* that the
schedule names a specific language's generator — which is itself the finding
under test.

- **R1 — order of draws within a claim.** root-decision, then parent (if
  non-root), then side. *Fixed by* "the draw schedule is this sentence, in
  order, per claim". Confidence: high.
- **R2 — `k uniform in 1..20`.** `1 + _randbelow(20)`: `getrandbits(5)`,
  rejecting values ≥ 20. This is what `randint(1,20)`, `randrange(1,21)` and
  `choice(range(1,21))` all reduce to.
  *Rejected:* `1 + int(random()*20)` (consumes two 32-bit words, not one-plus-
  rejections). Confidence: high.
- **R3 — does claim 0 consume the root-decision draw?** **Yes.**
  This is the decision I am least sure of and it is a genuine coin-flip in the
  prose. Claim 0 has no earlier claims, so "root with probability 0.3, else
  parent uniform among earlier claims" is *undefined* for it: the else-branch
  ranges over an empty set. Two repairs exist:
    (a) draw anyway, discard the outcome, force root — the **literal** reading of
        "the draw schedule is this sentence, in order, per claim", since claim 0
        is a claim;
    (b) short-circuit `if i == 0 or random() < 0.3`, consuming no draw — the
        more idiomatic thing to *write*.
  I take **(a)**, because the registration is the specification under test and
  its literal reading is (a). I record that (b) is at least as likely to be what
  the reference does, and that the two streams diverge inside world 0.
  Confidence: low.
- **R4 — `parent uniform among earlier claims`.** `_randbelow(i)`:
  `getrandbits(i.bit_length())` with rejection. Note this **consumes draws even
  when i == 1** (`_randbelow(1)` draws 1 bit and rejects until it sees 0), which
  a hand-written `if i == 1: parent = 0` would not.
  *Rejected:* `int(random()*i)`; special-casing i == 1. Confidence: medium-high.
- **R5 — `side uniform for roots`.** `_randbelow(2)`, i.e. `getrandbits(2)`
  rejecting values ≥ 2. This is what both `randint(0,1)` and `choice((0,1))`
  reduce to.
  *Rejected:* `getrandbits(1)` (one word, never rejects — a stream-visible
  difference); `random() < 0.5` (two words). Confidence: low-medium. "Uniform"
  names a distribution, and at least three idioms realise it with three
  different draw counts.
- **R6 — `parent's side with probability 0.9`.** One `random()`; keep the
  parent's side iff `u < 0.9`, else flip.
  *Rejected:* `u < 0.1 ⇒ flip` (same distribution, **different stream** —
  it flips on exactly the draws the chosen reading keeps); `u > 0.9 ⇒ flip`.
  Confidence: medium.
- **R7 — non-root claims and the side draw.** A non-root claim consumes the
  parent draw *and* the 0.9 draw; a root claim consumes the uniform side draw.
  No claim consumes both side draws. Confidence: high.
- **R8 — world loop.** k is drawn per world, immediately before that world's
  claims; worlds are emitted in generation order. Confidence: high.

## Post-hoc protocol

If the primary reading above misses a digest, I will report that miss first and
plainly. Only then will I sweep the enumerated alternative readings — not to
"reach" the digest, but because *how many distinct readings the registered prose
admits* is the quantitative answer to the F11 question. A match found by sweep
is reported as a sweep result and never as a reproduction.
