# DEFINITION-AUDIT.md

Workstream A. Base commit `e1403a7` (minority-prophet), `a120274`
(minority-prophet-gate). The audited revisions are recorded in
`formal/THEOREM-LEDGER.json`.

Purpose: reconstruct the smallest self-consistent mathematical model the
repository can support, and mark every place where prose, Python and Lean say
different things.

---

## 0. Summary of the audit

There are **three different models** in the repository, and they are not the
same model:

| Where | Lineage shape | Roots per claim | Can express partial dependence? |
|---|---|---|---|
| `formal/PROOFS.md` | `parent : C → Option C` (forest) | exactly 1 | no |
| `formal/MinorityProphetV2.lean` | `parent : Fin n → Option (Fin n)` (forest) | exactly 1 | no |
| `verification/independent_check_2026-08.py` | `p[c] ∈ {-1} ∪ [0,c)` (forest) | exactly 1 | no |
| `provenance/graph.py` | `copied_from : tuple[str,...]` (DAG) | arbitrary | yes |
| `FOUNDATIONS.md` | "directed acyclic evidence graph" (DAG) | arbitrary | yes |

The formal artifacts model a **forest**. The implementation and the stated
philosophy model a **DAG**.

Tested consequence (Workstream C, `audit/falsify.py`): for T1, T2, Lemma 1 and
the ±1 edge lemma behind T5, **the mismatch is harmless** — all four survive
verbatim in the DAG (0 violations over 252 side-consistent DAG worlds, 1,992
root-preserving rewirings, 962 duplications, 1,072 single-edge edits, maximum
root-count movement 1). This refutes the strong form of the audit's own opening
hypothesis and is recorded as such.

The mismatch is **not** harmless for what the model can *express*. In a forest,
"shares ancestry" is all-or-nothing: two claims either have the same root or
disjoint roots. Partial dependence — the object `EvidenceGraph.independent`
actually tests with `frozenset.isdisjoint` — has no representation in the forest
at all. The project's headline question ("genuinely independent evidence")
therefore lives strictly outside the formalized model.

**Action taken:** the new Lean kernel (`formal/lean/`) formalizes the DAG. It
subsumes the forest, so nothing was weakened to make proofs go through.

---

## 1. Definition-by-definition

Legend for **Layer**: `CORE` = belongs in the immutable kernel; `ADAPTER` =
belongs in a versioned layer outside the kernel; `TRUSTED` = not mathematics,
must be supplied by infrastructure.

---

### 1.1 Claim

- **Exact meaning (formal):** an element of a finite index set; in Lean, `Fin n`,
  where the index doubles as the time order.
- **Exact meaning (implementation):** `EvidenceNode`, a frozen dataclass with
  11 fields, keyed by an opaque caller-supplied `node_id: str`.
- **Consistent?** No. The formal model has exactly two attributes (parent,
  assertion). The implementation has eleven, of which the theorems use one
  (`copied_from`) and *do not use* `value` for anything the graph enforces.
- **Implicit assumption:** claim index = time order. This is how acyclicity is
  obtained in all three formal artifacts. `EvidenceGraph` obtains acyclicity
  differently — by insertion order, since `add` rejects unknown ancestors — so
  the two agree by accident rather than by construction. Worth recording as an
  invariant, because it is load-bearing and undocumented.
- **Required for a theorem?** Yes.
- **Layer:** CORE (index + assertion only). Everything else → ADAPTER.

---

### 1.2 Root identity  ⚠️ **most under-specified definition in the repository**

- **Exact meaning (formal):** none given. In Lean, identity is definitionally
  the index `Fin n`, which assumes the question away. In `PROOFS.md`, `S_a` is a
  *set* of roots, so the verdict depends entirely on when two roots count as one
  — and that criterion is never stated.
- **Exact meaning (implementation):** string equality on `node_id`, supplied by
  the caller. `EvidenceGraph.add` enforces only *uniqueness*, never *meaning*.
- **Consistent?** Vacuously — there is nothing to be consistent with.
- **Implicit assumption:** that distinct root IDs correspond to causally
  independent observations. Nothing anywhere checks or even defines this.
- **Ambiguity:** "root" is overloaded three ways: (a) a parentless claim, (b) an
  underlying observation event, (c) an identity in the attestation layer. The
  theorems are about (a); the security story is about (b) and (c).
- **Required for a theorem?** Yes — every counting theorem.
- **Consequence:** any de-duplication, canonicalisation or semantic-identity
  step is **inside the trusted base**, not outside it. One identity merge moves
  a side count (CE-08).
- **Layer:** the *predicate* "is parentless" is CORE. The *identity criterion*
  is TRUSTED, and must be named as such in every claim the project makes.

---

### 1.3 Parent / ancestry

- **Exact meaning (formal):** partial function `C → C`, `parent(c).t < c.t`.
- **Exact meaning (implementation):** `copied_from: tuple[str, ...]`, a tuple of
  ancestor IDs, all of which must already exist.
- **Consistent?** **No** — arity 1 vs arity n. See §0.
- **Implicit assumptions:** (i) edges mean "derived from", with no distinction
  between *copy*, *transformation* and *inference* even though `EvidenceNode`
  carries a separate `transformations` field the theorems ignore; (ii) an
  absent edge means "independent", not "unknown". Assumption (ii) is the
  hinge of CE-01 and is nowhere stated.
- **Required for a theorem?** Yes.
- **Layer:** CORE (as a `Finset` of strictly-earlier indices). Edge *kinds*
  (`transformations`, `edge_confidence`, `inferred`) → ADAPTER.

---

### 1.4 Acyclicity

- **Exact meaning (formal):** enforced structurally by the time order, in all
  three formal artifacts and in the new kernel (`World.acyclic`).
- **Exact meaning (implementation):** *emergent*, not enforced. `EvidenceGraph`
  is append-only and `add` rejects unknown ancestors, so a cycle cannot be
  built. But `roots()` is unmemoised, uncycle-guarded recursion: given a cyclic
  graph constructed by any other path (direct `_nodes` mutation, deserialisation
  via `to_dict`/round-trip, a future `update` method) it recurses forever.
- **Implicit assumption:** no ingest path other than `add` exists.
- **Required for a theorem?** Yes — `rootsOf` is only well-defined on a DAG.
- **Layer:** CORE as a structural hypothesis; **the enforcement is TRUSTED**.
  Recommendation: make the invariant explicit rather than emergent, since
  `to_dict` already exposes a serialisation with no matching validating loader.

---

### 1.5 Side consistency (R2)

- **Exact meaning (formal):** `∀ i j, j ∈ parents i → assert j = assert i`.
- **Exact meaning (implementation):** **absent.** `EvidenceGraph.add` never
  compares `value` across an edge (CE-09), and never compares `proposition_id`
  across an edge either (CE-10).
- **Consistent?** No. `PROVENANCE-REQUIREMENTS.md` calls R2 a *hard requirement*
  and the "surprising minimum"; it has no enforcement point in code.
- **Implicit assumption, and it is a big one:** in the DAG, side-consistency
  forbids any claim derived from evidence on *both* sides — i.e. it forbids
  synthesis, not merely "camp blending" (CE-07). In the single-parent forest
  this restrictiveness is *invisible*, because a claim with two parents cannot
  be written down. The prose describes R2 as mild because it was read off the
  forest model.
- **Failure mode is not graceful:** without R2 the literal `S_a` places some
  root in **both** side sets in **100%** of non-side-consistent worlds tested
  (3,410/3,410 at n≤5 here; 44,450/44,450 at n≤6 in the repository's own check).
  It does not degrade — it double-counts.
- **Required for a theorem?** Yes — it is the *only* place Lemma 1 consumes an
  assumption, and every other theorem sits on Lemma 1.
- **Layer:** CORE as a hypothesis; **enforcement is input validation (ADAPTER)**
  and must fail closed.

---

### 1.6 `S_a` — the side-root set

- **Exact meaning (formal):** `S_a(W) = { root(c) : assert(c) = a }` (forest);
  in the DAG, `⋃ { rootsOf(c) : assert(c) = a }`.
- **Set or multiset?** **Set**, everywhere — `frozenset` in Python, `Finset` in
  Lean. This is deliberate and correct (it is what makes copies free), but it
  means the aggregator is *insensitive to how many claims rest on a root* and
  *maximally sensitive to root identity* (§1.2).
- **Under side-consistency** it reduces to "the `a`-asserting parentless
  claims", proved as `side_locality`. This is the whole content of Lemma 1.
- **Layer:** CORE.

---

### 1.7 Verdict `F` and abstention

- **Exact meaning (formal):** `1` if `|S_1| > |S_0|`, `0` if `|S_0| > |S_1|`,
  else abstain.
- **Exact meaning (implementation):** **there is no implementation of `F`.**
  The closest artifact, `aggregation.semantic.evidence_root_vote`, is a
  different function: it takes one `root_id: str | None` per claim, silently
  **drops** claims with `root_id is None` (CE-12), and resolves duplicate root
  IDs by `dict.setdefault` — first writer wins — which makes it
  **order-dependent** exactly in the R2-violating case (CE-11). It then votes
  proposition-wise at a 0.5 threshold.
- **Consistent?** For a single proposition with total, conflict-free root
  attribution, `evidence_root_vote` agrees with `F`. Outside that, no.
- **Abstention is overloaded three ways:** (a) `F`'s tie; (b)
  `evidence_root_vote`'s `any(p == 0.5)`; (c) `semantic_coalition`'s
  `margin < abstain_margin` float threshold. Only (a) is theorised.
- **Layer:** `F` is CORE. `evidence_root_vote`, `semantic_coalition`,
  `weighted_vote` are all ADAPTER, and should not be described as "the
  aggregator the theorems are about".

---

### 1.8 Margin

- **Exact meaning:** `|S_1| − |S_0|`, signed in the new kernel (`margin`),
  absolute in `independent_check_2026-08.py` (`margin()` uses `abs`).
- **Consistency:** the sign matters for T4/T4'/T5 and is dropped in the Python
  helper; the script compensates with an ad-hoc `if d > 0` branch.
- **Layer:** CORE.

---

### 1.9 Phantom flow  ⚠️ **overloaded, with a factor-of-2 security consequence**

- **Meaning A (T4, and the Python check):** `p_a = ` net root gain of side `a`;
  the quantity that matters is `p_0 − p_1`, which is exactly the drop in the
  margin. In the new kernel this is `flow`.
- **Meaning B (T4' and R3 prose, "net **cross-side** phantom root flow"):** the
  number of roots that *move from one side to the other*.
- These differ by a factor of two: one root crossing sides is `−1` to one side
  and `+1` to the other, i.e. **2 units of Meaning A**.
- `PROOFS.md` T4 uses Meaning A. `PROOFS.md` T4' and `PROVENANCE-REQUIREMENTS.md`
  R3 ("the attack budget IS the margin") read as Meaning B. The stated
  conclusions are only true under Meaning A.
- **Consequence (CE-02, CE-03):** measured in adversary *actions* that convert a
  root's side, reversal costs `⌊margin/2⌋ + 1`, not `margin + 1`. At margin 8
  that is 5 actions, not 9.
- **Layer:** CORE, but **the unit must be stated in every use**.

---

### 1.10 Root-preserving vs root-changing transformation

- **Formal meaning (T1):** "re-targets existing edges, never deletes or
  creates". This is stated as a restriction on *edits*.
- **Better formulation, adopted in the new kernel:** state T1 on *pairs of
  worlds* with equal assertions and equal root sets. This is strictly more
  general — it covers any edit pattern at all, including additions and
  deletions that happen to leave the root set fixed — and it removes the need to
  formalize "an edit" at all.
- **Layer:** CORE.

---

### 1.11 Copied vs derived claim

- **Formal meaning:** no distinction exists. A claim with a recorded parent is a
  copy; a claim without one is a root. That is the entire taxonomy.
- **Implementation:** `copied_from` and `transformations` are separate fields,
  and `EvidenceNode` carries `source_id` and `observer_id` distinctly — four
  ways to express provenance, one of which the theorems read.
- **The critical gap (CE-01):** the theorems classify by *what is recorded*, and
  the threat model is about *what is true*. An **undetected copy is a root**.
  T2's plain-English form — "adding copied claims cannot change the verdict" —
  is therefore **false**, and false in precisely the direction that matters.
- **Layer:** CORE (recorded-parent predicate). Copy *detection* is TRUSTED.

---

### 1.12 Invalid / unknown claims

- **Formal meaning:** none. There is no third assertion value, no "unknown", no
  "retracted".
- **Implementation:** `value: bool` — no null. `evidence_root_vote` treats
  `root_id is None` as "delete this claim silently" (CE-12), which is the
  closest thing to an "unknown" and is the wrong default: unattributable
  evidence should push toward abstention, not evaporate.
- **Layer:** out of CORE. Needs an ADAPTER (see EXTENSION-SOCKETS.md §3).

---

### 1.13 Can one root support both sides?

- **Under side-consistency: no** — proved (`sideRoots_disjoint`).
- **Without it: always** — 3,410/3,410 non-SC worlds at n≤5. This is the
  sharpest statement of why R2 is load-bearing.
- **In the DAG this is the normal case for synthesis** (CE-07), which is why R2
  is much more restrictive than the prose suggests.

---

### 1.14 Weighted roots

- **In the core: they do not exist.** `F` is a pure cardinality comparison; a
  root of confidence 0.01 and a root of confidence 1.0 count identically.
- **In the implementation they do**, in three incompatible ways:
  `weighted_vote` (confidence × competence, clamped to [0,1]),
  `semantic_coalition` (same weight, used for a scored ranking), and `F`
  (unweighted). Negative weights are silently clamped to 0; zero-weight roots
  are counted at full strength by `F` and at zero by `weighted_vote`.
- **No theorem covers any weighted aggregator.**
- **Layer:** ADAPTER. See EXTENSION-SOCKETS.md §2.

---

### 1.15 Temporal change, expiry, revocation

- **In the core: absent.** `World` is static. `timestamp` exists on
  `EvidenceNode` and is used only as a default field.
- `FOUNDATIONS.md` desideratum 6 ("Revision") and the `τ` (evaluation time)
  argument of its abstract aggregator `F: (G, C, K, τ) → (T̂, q, r)` are
  **not** in any theorem. The formalized `F` has no `τ`, no `K`, no `q`, no `r`.
- **Layer:** out of CORE. See EXTENSION-SOCKETS.md §4.

---

### 1.16 Proposition / subject identity

- **In the core: one proposition per world**, implicitly. `assert : C → Bool`
  has no proposition argument.
- **In the implementation:** `proposition_id` exists on every node and is
  **never compared across an edge** (CE-10) — a claim may record as its parent a
  claim about a different proposition. Subject substitution is unconstrained at
  the data layer.
- **Layer:** CORE assumes single-proposition worlds. Multi-proposition is an
  ADAPTER; see EXTENSION-SOCKETS.md §1 and §5.

---

## 2. The proposed kernel

Six definitions, and nothing else, are needed for T1/T2/T4/T4'/T5:

```
World        = (parents : Fin n → Finset (Fin n), assert : Fin n → Bool, acyclic)
SideConsistent W  ⟺  ∀ i j, j ∈ parents i → assert j = assert i
rootsOf W i  = parentless ancestors of i
rootSet W    = { i : parents i = ∅ }
sideRoots W a = ⋃ { rootsOf W i : assert i = a }
F W          = compare |sideRoots W true| with |sideRoots W false|
margin W     = |sideRoots W true| − |sideRoots W false|   (signed, over ℤ)
```

Everything else in the repository — competence, confidence, weights, `τ`,
proposition IDs, transformations, edge confidence, semantic coalitions,
calibration, markets — is **outside** the kernel and must not be described as
covered by these theorems.

## 3. Terminology that must be retired or qualified

| Term | Problem | Replace with |
|---|---|---|
| "flow" | two meanings, factor 2 apart (§1.9) | "margin units (`p₀ − p₁`)" vs "root conversions" |
| "copy invariance" | true only for *recorded* copies | "recorded-copy invariance" |
| "k root-integrity errors" | one real error ≠ one unit | "k units of root-set change, assertions fixed" |
| "attribution is irrelevant" | true only among non-roots | "non-root attribution is irrelevant" |
| "the attack budget IS the margin" | true in units of `p₀−p₁`, not actions | state the unit |
| "exhaustive" (multivalue verifier) | samples above 200 combinations | "exhaustive to n≤5, sampled beyond 200 rewirings" |
| "abstention" | three different definitions (§1.7) | qualify per aggregator |
