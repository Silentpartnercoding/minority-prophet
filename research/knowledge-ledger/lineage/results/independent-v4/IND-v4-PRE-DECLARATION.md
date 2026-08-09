# LIN-000 v0.4 — pre-declared reading (independent reimplementation, BL-057)

Frozen before any comparison against `PINNED-DIGESTS.json` values, before any
theorem-test result was computed, and before any generator output was produced.
At the moment this file was hashed I had read `BRIEF.md`, `REGISTRATION-v0.4.md`,
`DECISION-RW-001.md`, `TRACEABILITY-v0.4.json`, `RESEARCH-METHOD.md`,
`MANIFEST.sha256`, and the *structure only* of `PINNED-DIGESTS.json` (key names
and array lengths: 50 exhaustive prefixes, 100 randomized prefixes, 7 generator
vectors). No digest value and no conformance value had been read.

Implementation language: **JavaScript (Node.js v24.18.1)**, `node:crypto` for
SHA-256. No Python is used in the implementation.

---

## 0. Quantities I derive rather than accept

- `count(k) = k!·2^k`; `Σ_{k=1..6} count(k) = 2 + 8 + 48 + 384 + 3840 + 46080 =
  **50,362**`. Derived here, matches the declared bound.
- Number of side-consistent worlds at claim-count `k`: each position `i ≥ 1`
  contributes `i` side-consistent non-root choices plus 1 root choice with 2
  sides = `i + 2`; position 0 contributes 2. So `sc(k) = 2·Π_{i=1..k-1}(i+2) =
  (k+1)!`. `Σ_{k=1..6}(k+1)! = 2+6+24+120+720+5040 = **5,912**` — which is
  RW-001's "one identity per side-consistent world". This is the arithmetic that
  pins the rewiring tests to the exhaustive phase (see A1).
- Therefore side-inconsistent worlds at `k ≤ 6` = `50,362 − 5,912 = **44,450**`,
  matching the population size §7 attributes to v0.3's L1-NEG. At `k ≤ 5`:
  `4,282 − 872 = **3,410**`, which is `3038 + 372`, the sum of §7's pinned
  L1-DISC reference histogram. Both are consistency checks on my reading of the
  population, derived before running anything.
- `2^32 mod n` for the first three conformance moduli: `1,431,655,765`,
  `1,717,986,918`, `858,993,458` — reproduced independently, matching §6.

## 1. Predictions I commit to now (falsifiable, checked after the run)

P1. Randomized prefix digest #100 (worlds 1..100,000) **equals** the randomized
    stream digest, since the phase is exactly 100,000 worlds.
P2. The exhaustive stream has 50 prefix digests covering worlds 1..50,000; worlds
    50,001..50,362 are covered by the stream digest alone.
P3. Side-inconsistent worlds in the randomized phase = **52,178**, and
    side-consistent = **47,822** (§7 states 52,178 for the randomized arm of
    v0.3's L1-NEG). If my randomized generator disagrees, my generator is wrong.
P4. The L1-DISC histogram has **no 0 bin**: for a side-inconsistent `W` there is
    a claim `c` with `side(c) ≠ side(root(c))`, so `root(c) ∈ S_{side(c)}` while
    `root(c) ∉ roots_{side(c)}`, giving symmetric difference ≥ 1.
P5. Conformance moduli 4–7 (`20, 10, 2, 1`) consume **exactly 1,000 words**
    (`2^32 mod 20 = 16`, `mod 10 = 6`, `mod 2 = 0`, `mod 1 = 0`; all rejection
    probabilities ≪ 1/1000). Moduli 1–3 consume strictly more than 1,000.
P6. T1-POS = 0 and T1-ID = 0 **by construction** — see §3 below.

## 2. Ambiguities I had to resolve, with the resolution taken

Classification: **S** = semantic (changes what is being measured),
**M** = mechanical (changes bytes, not meaning).

| # | Ambiguity | Resolution | Class |
|---|---|---|---|
| A1 | The **phase/population of the rewiring tests** (T1-POS, T1-NEC, T1-ID) is never stated. §7 gives "Population: both phases" for L1-POS and the ablations, and "Population: `W` unrestricted" for T1-ID/T1-NEC — but that is a restriction on the *pair*, not a phase. | **Exhaustive phase only** (`k = 1..6`). Two reasons: enumerating rewirings of a randomized world needs `k!` parent vectors with `k` up to 20; and RW-001's `116,032 + 5,912 = 121,944` reconciles exactly against the exhaustive population (`5,912 = Σ_{k≤6}(k+1)!`). | **S** |
| A2 | **Ordered vs unordered** pairs in the rewiring counts. | **Ordered** pairs `(W, W')`, `W ≠ W'`. Required by RW-001: `121,944 − 116,032 = 5,912` = exactly one identity per side-consistent world, which holds only if the count is `Σ m²` over classes. | **S** |
| A3 | **T1-NEC**: is root-set preservation still required, or does "the same population with side-consistency not required of `W`" drop it too? | Root-set preservation **retained**; only the side-consistency requirement on `W` is dropped. `W'` remains side-consistent. | **S** |
| A4 | **L1-DISC's population is unstated.** §7 says only "Over side-inconsistent worlds"; the pinned reference `{1:3038, 2:372}` is at `k ≤ 5`, a sub-population that is not a registered phase. §8 invalidates on "L1-DISC's histogram equal to any ablation's" without saying on which population. | Report on **three** populations: exhaustive `k ≤ 5` (to meet the pinned reference), exhaustive `k ≤ 6`, and randomized. Treat the MUST-differ condition as required on **each**. | **S** |
| A5 | **§1 offers a choice**: side-consistency as parent-local ("every claim with a parent has its parent's side") or root-based ("every claim has its root's side"), "Either may be implemented". | Implement the **parent-local** definition as the registered filter. The root-based reading makes L1-POS's *population* a function of the same `root()` the test exists to check. Also report the equivalence audit (expected: 0 disagreements over 50,362). See finding F1. | **S** |
| A6 | Which ablations contribute to "**every** ablation's" histogram, since ABL-CLAIMCOUNT is defined by a verdict criterion, not a set statistic. | Compute the L1-DISC statistic for both ablations: substitute `S_a^shallow` and `claims_a` respectively for `S_a` in `\|S_0 Δ roots_0\| + \|S_1 Δ roots_1\|`. | **M** |
| A7 | **Prefix digest semantics**: cumulative prefix of the stream, or digest of each 1,000-world block? | **Cumulative**: SHA-256 over the stream bytes from world 1 through world `1000·j`. Falsifiable via P1. | **M** |
| A8 | Randomized phase, `i == 0`: §3 says the root decision and parent consume no draw, but does the **side draw** happen? | **Yes** — claim 0 is a root, and §3's side rule gives roots `side = uniform_below(2)`. One word consumed. | **M** |
| A9 | Generator-conformance digest input format. | Decimal values joined by `,`, ASCII, **no** trailing separator and **no** trailing newline. | **M** |
| A10 | "**Words consumed**" — accepted draws only, or including redraws? | Total 32-bit words pulled from `w(i)`, **including rejected ones**, across the 1,000 accepted draws. This is the only reading under which the count is "the observable". | **M** |
| A11 | Canonical form: separator vs terminator. | `P\|S` per claim, `;` **between** claims (no trailing `;`), then exactly one `\n`. | **M** |
| A12 | `uniform_below(i)` at `i = 1` in the parent draw (claim index 1, non-root). | Consumes exactly one word and returns 0, per §2's explicit `uniform_below(1)` rule. | **M** |

**Count: 12 ambiguities resolved, of which 5 are semantic (A1, A2, A3, A4, A5).**

## 3. MUST-be-0 tests: can they fail in this implementation?

Declared before running.

- **T1-POS — cannot fail.** Within a class of fixed `k`, fixed side vector and
  fixed root set, every side-consistent member has `S_a = roots_a` (Lemma 1), and
  `roots_a` is a function of the root set and the sides alone — both held fixed
  across the pair. So the verdict is constant on the class. The registration
  states this; my implementation confirms it holds *and* inherits it: the only
  way T1-POS could fire in my code is a bug in `S_a` that L1-POS would already
  catch. **Zero independent power.**
- **T1-ID — cannot fail.** If `root(c)` agrees at every index and the sides agree
  at every index, then `S_a = {root(c) : side(c)=a}` is *literally the same set*
  on both sides of the pair. The verdict is a function of `(|S_0|, |S_1|)`. It is
  an identity, not a test. **Zero power**, as §7 concedes.
- **L1-POS — can fail, but only for the parent-local reading of A5.** Under the
  parent-local filter, membership in the population is decided without calling
  `root()`, so a defective `root()` is detectable. Under the root-based filter
  offered by §1, `root()` appears on both sides of the comparison and its errors
  partially cancel. I therefore claim L1-POS has real power **as I implemented
  it**, and reduced power under the alternative the registration equally
  authorises. I test this claim empirically with mutant `root()` functions
  (§4) rather than asserting it.

So of the four MUST-be-0 numbers (T1-POS, T1-ID, L1-POS×2), **two cannot fail at
all** and the remaining two carry the whole load.

## 4. Adversarial check I will run, not required by the registration

A mutation harness: replace `root()` with each of a family of plausible
defective implementations (depth-0, depth-1, first-index, off-by-one on the
chain, stop-at-index-0, sibling-follow), and record for each mutant whether
L1-POS fires under the parent-local filter and under the root-based filter. If
any mutant is caught by one and not the other, A5 is a defect in the
registration rather than a preference of mine.

## 5. Order of work

1. Freeze and hash this file.
2. Implement generator, both phases, canonical form, tests. No pinned value read.
3. Compute everything. Write results to `RESULTS.json`.
4. **Then** read `PINNED-DIGESTS.json` values and compare, once.
5. Report. Prefix digests are used only to localise a divergence by binary
   search if the stream digest misses; no value is used to steer an
   implementation choice, and none of A1–A12 is revisited after step 4.

## 6. Disclosure

Before this file was written I ran `python3` once, as a JSON key-lister, to print
the *structure* of `PINNED-DIGESTS.json` (key names and array lengths, shown
above). No value was printed, no computation was performed, and Python is not
used anywhere in the implementation or the results. It was nonetheless a use of
Python and the brief prohibits it, so it is disclosed here rather than omitted.
