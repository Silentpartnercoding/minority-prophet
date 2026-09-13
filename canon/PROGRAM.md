# MP CANON — program specification

A bounded research-and-specification program producing a small set of
independently defensible mathematical laws governing the transition

> reasoning → authority → action → consequence.

## What this is not

This is not a mathematical translation of any religious text. Historical texts —
including scripture — are used **only** as a source of candidate structural
propositions to be attacked. The finished canon contains no theology, no
supernatural premises, no appeal to religious authority, and no proposition
accepted because of who said it.

Source provenance is preserved internally so every law stays auditable. That
provenance confers **exactly zero** additional mathematical authority. A law
survives on its definitions, counterexamples and tests, or it does not survive.

Corollary, stated so it cannot be quietly dropped: **if a candidate proposition
fails, it fails.** The program has no mechanism for rescuing a proposition
because of where it came from, and a canon in which every extracted candidate
survived would be evidence that the falsification standard was not applied.

## Verdict vocabulary

Every candidate receives exactly one verdict. Two of them are honourable and
four of them mean "this is not ours."

| Verdict | Meaning |
|---|---|
| `REJECTED` | A counterexample refutes it as stated. |
| `TRIVIAL` | True but vacuous — carries no constraint that matters. |
| `KNOWN RESULT` | Correct, and already established elsewhere. Cite it; do not claim it. |
| `USEFUL REFORMULATION` | Known content, but restated in a form that makes it checkable in MP. |
| `NOVEL COMBINATION` | The individual parts are known; this composition is not. |
| `MP INVARIANT` | Load-bearing in MP, formalized, tested, and defended. |
| `UNRESOLVED` | Open. Stated with its open question attached. |

`KNOWN RESULT` is the expected verdict for most candidates and is **not a
failure of the program**. Establishing that an ancient structural intuition
coincides with a modern theorem is a real finding. Relabelling that coincidence
as an MP discovery is misconduct.

## Required falsification standard

No candidate advances without all eight:

1. a formal definition with stated domains,
2. explicit boundary conditions,
3. at least one attempted counterexample,
4. adversarial analysis (how does an attacker exploit the law itself?),
5. comparison against existing mathematics and computer science,
6. identification of the cases in which it fails,
7. a test demonstrating whether it improves MP behaviour,
8. a verdict.

Item 4 is the one most often skipped. Several of the Phase I candidates are
individually sound and jointly exploitable — a law that says "deny on conflict"
is a denial-of-service primitive if an adversary can manufacture conflict.
See `NOVELTY-AUDIT.md` L7.

## Extraction pipeline

```
SOURCE TEXT
  ↓  literal claim
  ↓  remove supernatural / theological premises
  ↓  structural proposition
  ↓  variables + domains
  ↓  mathematical conjecture
  ↓  counterexample search
  ↓  adversarial attack
  ↓  proof | simulation | empirical test
  ↓  REJECT | TRIVIAL | KNOWN | REFORMULATION | COMBINATION | INVARIANT | UNRESOLVED
MP candidate law
```

## Provenance record (internal only)

One record per candidate, retained whatever the verdict:

```
source_id, passage, translation, literal_claim, structural_claim,
formalization, assumptions, counterexamples, test, result,
prior_art, canonical_status, provenance_hash
```

The runtime specification does not carry the source. It remains retrievable
through the provenance record.

## Phase I corpus (bounded — do not expand)

Canonical New Testament, plus Proverbs, Ecclesiastes, and selected Torah
passages, restricted to material concerning: evidence, witnesses, judgment,
authority, action, consequence, measurement, planning, boundedness,
contradiction, stewardship, verification, causation, deception, prediction,
failure, resilience.

Phase I does not attempt the history of human religion. Corpus expansion
requires an explicit owner decision recorded in this file.

## Canon size

`7 ≤ N_laws ≤ 21`. Each canonical law carries exactly: NAME · FORMAL STATEMENT ·
DEFINITIONS · INTUITION · FAILURE MODE PREVENTED · COUNTEREXAMPLE / LIMIT ·
IMPLEMENTATION IN MP · TEST · PROVENANCE HASH.

## Success criterion

The program succeeds only if the laws improve measured MP behaviour against a
baseline of `mandate → LLM judgment → tool`, on:

`UnauthorizedEffectRate`, `CatastrophicEffectRate`, `FalseAllowRate`,
`FalseDenyRate`, `AuthorityExpansionRate`, `RecoveryRate`, `ReceiptCompleteness`.

A gate that denies everything scores perfectly on the first three and is
worthless. `FalseDenyRate` is therefore not a secondary metric — it is the
metric that stops the program from succeeding trivially.

## Hard constraints

Do not: claim mathematical proof of any religion; presuppose divine authorship;
assign special evidentiary weight to scripture; conceal source provenance; force
passages into mathematics; treat metaphors as equations without justification;
manufacture novelty; let the corpus grow without an owner decision; or modify
production MP before candidate laws pass their tests.

## Status

Phase I, tranche 1. **Placement and retractions recorded in `PLACEMENT.md`**
after reading the shipped Border / MP / Gate / stack architecture: the gate and
precedent modules re-derived work that already exists in stronger form, and are
retained as evidence of that rather than as proposals. Prior-art audit of the ten seed candidates complete
(`NOVELTY-AUDIT.md`). Formal core in progress (`formal/lean/MinorityProphetCore/NarrowGate.lean`).
No extraction from source texts has been performed yet — the seed candidates were
supplied directly by the owner and are being audited first, on the principle that
prior-art screening is cheaper than formalization and should precede it.
