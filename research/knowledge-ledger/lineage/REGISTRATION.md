# LIN-000 — lineage-bearing schema and end-to-end tests for Theorem 1 and Lemma 1

Registered by RUN-20260807-10 **before implementation**, KL-000 style. This
is new experimental work under the paper's own world model; it is **not a
registry kernel**, advances no kernel state, and modifies neither schema
v0.1 nor any KL-000 registration. Its registration lives here (not as a
`preregistration.json`) deliberately, so the twelve-kernel conformance
tooling is untouched.

## Why

Theorem 1 (immunity to root-preserving, side-consistent rewiring) and
Lemma 1 (side-locality) are proved and — per paper v1.0.4 [E8] — only
shadow-tested: schema v0.1 records carry `{id, rootId, side}` with no parent
edges, so every claim is its own root and both results are vacuous in the
tested model. This experiment builds the minimal schema in which they can
fail.

## Schema: `minority-prophet.lineage-world.v0.1` (new; v0.1 knowledge-transaction schema untouched)

A world is an ordered list of claims `[{id, parentIndex, side}]`:

- `parentIndex` is `null` (the claim is a **root**) or the index of an
  **earlier** claim (time order, the paper's `parent(c).t < c.t`).
- `side ∈ {0, 1}` (the paper's `assert`).
- `root(c)`: walk parent edges to the chain head.
- **Side-consistent** iff every edge joins same-side claims.
- `S_a = {root(c) : side(c) = a}` — the paper's **literal** S_a, computed
  over all claims, deliberately not restricted to roots, so Lemma 1 is a
  *theorem about* this function, not baked into it.
- Verdict: `1` if `|S₁| > |S₀|`, `0` if reversed, `abstain` on ties
  (τ = 0, per [E6]).

## Phases and declared bounds

**Exhaustive.** All worlds with k = 1..6 claims: position i has (i+1)
parent choices ({null} ∪ earlier) × 2 sides, so
`count(k) = k! · 2^k` and the **declared total is 50,362**
(2 + 8 + 48 + 384 + 3,840 + 46,080), asserted before any evaluation; a
mismatch invalidates the run. Side-consistent and side-inconsistent worlds
are both enumerated (the negatives need the latter).

**Randomized.** Frozen seed **20260808**, `random.Random`, **100,000
worlds**, k uniform in 1..20; each claim: root with probability 0.3, else
parent uniform among earlier claims; side uniform for roots, else parent's
side with probability 0.9 (0.1 gives deliberate side-inconsistency). The
draw schedule is this sentence, in order, per claim. (F11 lesson: the
schedule is registered, not just the seed.)

## Tests that can fail — registered expectations

- **L1-positive.** Every side-consistent world: `S_a` equals the set of
  a-asserting roots, both sides. Expected violations: 0.
- **L1-negative.** Side-inconsistent worlds where the literal `S_a` differs
  from the a-asserting roots MUST exist (expected: > 0; count reported),
  including the paper's scope-note phenomenon — one root appearing in both
  S₀ and S₁. A minimal two-claim witness is pinned.
- **T1-positive.** Every side-consistent world × **every single-claim
  reparenting that preserves the root set and side-consistency** (non-root
  claim re-attached to a different earlier same-side claim): S₀, S₁, and
  the verdict unchanged. Expected violations: 0. Declared scope: single-step
  rewirings, complete; arbitrary root-set-preserving rewirings are finite
  compositions of these, and each step preserving (S₀, S₁) extends the
  result — stated, not silently assumed.
- **T1-violation (i), root-set broken.** Orphaning a non-root claim (new
  root) or attaching a root under an earlier claim (root removed): worlds
  where the verdict changes MUST exist (expected: > 0; counts reported).
  The theorem's protection must not extend here.
- **T1-violation (ii), side-consistency broken.** Reparenting across sides:
  worlds where S_a or the verdict changes MUST exist (expected: > 0).

**Must-fail ablations (checker power, KL-000 style).**

- **LB-shallow**: `root(c)` returns the immediate parent's head only one
  step up (parent if any, else self). MUST be caught by T1-positive
  (reparenting changes its attribution).
- **LB-claimcount**: `S_a` computed from claims' own sides without
  root-collapsing (the head-count ghost). MUST be caught by L1-positive on
  side-consistent worlds containing any chain of length ≥ 2.

If either ablation passes its test, the checker is vacuous and the run is
invalidated — not reported as a pass.

## Invalidation

Exhaustive count ≠ 50,362; seed failing to reproduce an identical stream
(regenerate-and-compare); any expected-nonzero count observed zero; any
ablation uncaught; any L1-positive or T1-positive violation by the real
implementation (that would be a **finding against the formalisation or the
paper**, preserved with its world, and an owner matter — the paper is not
edited by this experiment).

## Boundaries

Synthetic only; no kernel state advanced; KL-000 untouched at v1.3.0; if
the run cannot complete inside RUN-20260807-10, this registration stands
and the remainder is recorded (the brief's own scoping).
