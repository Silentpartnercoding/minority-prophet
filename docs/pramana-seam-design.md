# Pramana seam — design

**Status: Phase B partial.** The mapping table is **not** here; it maps `TODO(wire)` sites that
do not exist in this repository yet. Everything below is the half that needed no such input,
because it goes in a place the ledger already provided.

Companion: `pramana-seam-notes.md` (Phase A inventory and reframing).

## What is being taken, and what is not

**Taken:** one distinction — some claims can be re-checked mechanically, others require an
oracle.

**Not taken:** no code, no package, no JSON schema (Pramana ships none — its variants are
Pydantic models), no wire extension, no `verify_endpoint_hint`, no CA-1/2/3, no `RootRegistry`,
and none of the sibling protocols in that stack.

**The test this is built to pass:** if `ravikiran438/pramana-attestation` were deleted tomorrow,
nothing here breaks. `provenance/claim-warrant.schema.json` is written locally, from the
inventory, with our own field names. The typology it encodes is the classical set of pramanas —
perception, inference, comparison, testimony — which predates any repository by roughly two
thousand years. The modern formulation is cited (Zenodo DOI 10.5281/zenodo.20283647, Apache-2.0),
and nothing here validates that work's formal claims.

## Where it goes: the space that already existed

`evidence-lineage.schema.json` requires `evidence: {"type": "object"}` on every node — an
unconstrained bag, already mandatory, already carried. **The warrant goes there.** No node field
changes. No new required field. No migration.

This is forced rather than chosen, and the reason matters: a ClaimAttestation cannot *become* a
node. A node is a position on a shared proposition with an ancestry — `proposition_id`,
`value: boolean`, `copied_from`. An attestation has none of those and never claimed to. It is a
**warrant**: a statement of how an assertion could be checked. Warrants attach to positions;
they are not positions.

## The two fields

`claim_type` ∈ `measured | inferred | analogized | cited`
`verify_determinism` ∈ `deterministic | oracle_conditional` — **derived, never author-supplied**

The mapping is fixed: `measured` and `cited` are deterministic; `inferred` and `analogized` are
oracle-conditional. Consumers recompute rather than trust a supplied value, because a false
prophet's cheapest move is to mislabel an inference as a measurement.

## Three-valued outcome, preserved

`verify_outcome.result` ∈ `verified | rejected | unverifiable`

**`unverifiable` must never be collapsed into `rejected`.** A dead URI costs an adversary
nothing, produces no failed check, and — under any binary encoding — is indistinguishable from a
claim that simply was not examined. The distinction is the signal; folding it destroys the thing
being measured.

`reason` carries the discriminating detail: `fetch_failed`, `not_decodable`, `digest_malformed`,
`oracle_absent`, `sla_timeout`.

## Independence is untouched, structurally

`copied_from` and `transformations` are not read, written, or referenced by anything above. The
warrant is a per-node attribute and cannot become an edge, because the source vocabulary has no
edges to contribute — Pramana types individual claims and never relates them to one another.

The Phase B requirement that "type must not silently alter independence semantics" is therefore
satisfied by construction rather than by discipline. There is no code path through which it
could.

Verifiability and independence are orthogonal:

|  | Independent | Dependent |
|---|---|---|
| **Verifiable** | strong evidence | one fact counted many times — *what this project exists to catch* |
| **Unverifiable** | weak but genuine | worthless — *the most attractive position for a false prophet* |

A verifiable claim can be entirely dependent (copying someone's correct citation). An
unverifiable claim can be entirely independent. The warrant adds an axis; it does not duplicate
one.

## The check this makes possible

`epistemic-ci` check 8, Effect Reachability:

> requires every stratum the endpoint depends on to contain instances. A population with 208
> searched and 0 not-searched is positive, fingerprinted, and structurally unable to move the
> endpoint.

False-prophet screening depends on mechanical re-checkability. `verify_determinism` partitions a
corpus into exactly the two strata that dependence bears on. **If a corpus is entirely
`oracle_conditional`, a screen that relies on re-checking is structurally unable to move** — it
returns green and could never have returned anything else.

Until `claim_type` is recorded, that check cannot be run at all, because nothing distinguishes
the strata.

**Required behaviour:** a false-prophet screen reports the stratum distribution of the corpus it
ran on, and declares itself non-informative when the deterministic stratum is empty. That is a
validity precondition, not a score adjustment, and it is worth more than the weighting feature it
sits next to.

The `epistemic-ci` README already records a second instance of check 8 in this programme — *"a
method consuming recorded ancestry, evaluated on a corpus where 5.5% of items record any
ancestry."* Same shape one level over: an apparatus depending on a property most of the
population lacks.

## Type-aware weighting

As specified in the task: behind the existing hard gates, config-gated, **off by default**, so
baseline runs cannot be contaminated. Weighting is downstream of everything above and is the
least important part of this design. The stratum report is useful even with weighting disabled
forever.

## Still blocked

- The `TODO(wire)` mapping table — one side does not exist.
- Where warrant construction is invoked — depends on `ledger_adapter.py`.
- The scorer hook's exact placement — depends on the existing hard gates.
- Whether the ledger's required `confidence` should defer to `InferenceClaim.confidence` when a
  warrant carries one. Three of four types have no confidence to offer, so a local default must
  govern; that default lives in the file that is missing.

---

## Correction: the adapter is less load-bearing than assumed, and there is a gate interaction

Found by reading `provenance/graph.py` on main rather than inferring from the task brief.

**1. The node machinery is already live.** `EvidenceNode` is a real dataclass with all ten
fields, referenced by `benchmark/world.py`, `audit/core_models.py`, `audit/falsify.py` and three
test suites. Nodes are constructed today with no `ledger_adapter.py` involved. A warrant can
therefore be attached at existing construction sites; the adapter is the doorway the *task*
assumes, not the only doorway that exists.

**2. A one-bit version of this distinction already ships.** `resolvable_reference(evidence)`
matches evidence values against url / hash / arxiv / urn forms and documents its own limit:

> This checks SHAPE, NOT EXISTENCE. A well-formed DOI that was never registered passes... The
> guarantee is narrow and deliberate: the claim named something that could in principle be
> checked, rather than prose that could not.

`UnattributedRootError` gates parentless claims on it. So this repository had already decided
that checkability matters and built a hard gate on it. The warrant is a **refinement of an
existing commitment**, not an imported concept: it adds which kind of check, whether that check
needs an oracle, and what happened when it was run — the last being precisely what
`resolvable_reference` declines to establish.

**3. A hard-gate interaction, flagged rather than decided.**

`resolvable_reference` iterates `evidence.values()` and matches strings against
`^[0-9a-f]{32,128}$` among others. A warrant's `source_digest` is a hex digest of that length
and **would match**. A node that previously raised `UnattributedRootError` could begin passing
solely because a warrant was attached — a hard gate silently moving.

**Required placement:** the warrant is nested under a single key, e.g.
`evidence["claim_warrant"] = {...}`. `evidence.values()` then yields a `dict`, the
`isinstance(value, str)` guard skips it, and gate behaviour is provably unchanged. **The warrant
must never be flattened into `evidence`.**

This satisfies the acceptance criterion "provenance independence provably unchanged for untyped
inputs" for the gate as well, and the regression test is cheap: construct a node with and
without a warrant and assert `resolvable_reference` returns the same value.

Whether `source_digest` *should* count as a resolvable reference is a separate question with a
defensible answer either way. It is a hard-gate semantics change and belongs to the owner, not
to this design.

---

## Correction: sparse coverage, and the failure this design nearly reproduced

Raised in review: *"will things not work if we aren't getting that supplemental data?"*

### Backward compatibility — verified, not asserted

Nothing requires a warrant. `evidence` remains `{"type": "object"}` and `{}` is still valid.
`claim-warrant.schema.json` is standalone and is not referenced from
`evidence-lineage.schema.json`. The only occurrences of `WARRANT_KEY` in the codebase are its
definition, the skip in `resolvable_reference`, a docstring, and tests.

Untyped evidence resolves exactly as before:

| evidence | result |
|---|---|
| `{}` | `None` |
| `{"source": "trust me"}` | `None` |
| `{"source": "10.1038/nature12373"}` | `doi` |
| `{"url": "https://example.org/x"}` | `url` |
| `{"digest": "a"*64}` | `hash` |
| `{"arxiv": "2605.20312"}` | `arxiv` |

The acceptance criterion "provenance independence provably unchanged for untyped inputs" holds
for the gate as well, and `tests/test_claim_warrant_gate.py` pins it.

### The hole: a stratum report that ignores untyped nodes is the failure it exists to catch

The earlier specification said a screen "declares itself non-informative when the deterministic
stratum is empty." That is insufficient, and dangerously so.

Take 400 nodes of which 5 carry warrants — 3 deterministic, 2 oracle-conditional, 395 untyped.
The deterministic stratum is non-empty, so under that rule the screen reports itself informative,
having classified **1.25%** of the corpus.

That is Effect Reachability failing in the apparatus built to detect Effect Reachability failure.
It is also the same shape as the second instance already recorded in `epistemic-ci` — *"a method
consuming recorded ancestry, evaluated on a corpus where 5.5% of items record any ancestry."*
A method that depends on a property most of the population lacks.

### Required, replacing the earlier rule

**Three strata, not two.** `deterministic`, `oracle_conditional`, and **`untyped`** — untyped is
first-class and reported, never silently dropped from the denominator.

A false-prophet screen must report, alongside any result:

- counts in all three strata, and warrant **coverage** as a fraction of the corpus;
- an explicit non-informative verdict when *either* the deterministic stratum is empty *or*
  coverage is below a declared threshold;
- the threshold itself, recorded with the run rather than assumed.

**A screen may never report a clean result computed over a minority of classified nodes without
saying so.** Sparse coverage is the expected condition — warrants arrive incrementally, and most
existing corpora will have none at all — so this is the normal path, not an edge case.

This makes the design degrade honestly rather than silently: with zero warrants the screen
reports 100% untyped and declares itself non-informative, which is the correct answer and is
strictly more useful than the pre-warrant behaviour of reporting nothing about its own coverage
at all.
