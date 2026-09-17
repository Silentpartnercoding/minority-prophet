# AID-1-OBS — who states a witness depth today

*Not a preregistration. This file is deliberately not named one; see section 2.*

**Status: OBSERVATIONAL. Read section 2 before citing any figure.** First
measurement of the attested-independence series. It does not test the policy in
[`canon/ATTESTED-INDEPENDENCE.md`](../../canon/ATTESTED-INDEPENDENCE.md); it
measures whether the input that policy requires exists anywhere.

## 1. Why this exists

The policy refuses to convert the record's silence into independence. A witness
earns independence by stating how far it went and backing that statement. The
obvious question before measuring what the policy costs in a simulated world is
whether any witness, anywhere, states such a thing today.

## 2. What is not preregistered, stated first

A repository-wide search that established the **direction** of this result was
run before this document and its configuration existed, and the direction was
already implied by reading the code: no producer in the estate sets the axis
fields. Consequences a later reader should not have to reconstruct:

- **No hypothesis was frozen in ignorance of the outcome.**
- **Corpus choice was made with the data visible.** Which corpora count as
  bearing on adoption is a judgement made here, after looking.
- **The figures are a census of one estate at one moment, not an estimate** of
  anything about the wider world.

What survives that: a census is refuted by one counterexample, and the slot
finding in section 4 is a fact about published schemas that anyone can check
without access to us.

## 3. Instances: what records actually say

Claim objects are objects asserting a value with an origin. Counts, not rates.

| Corpus | Origin | Claim objects | State any axis | State legacy basis | Earn admissible depth |
|---|---|---:|---:|---:|---:|
| interop memory-evidence-profile cases | authored fixture | 18 | 0 | 0 | 0 |
| decision-relative independence fixtures | authored fixture | 12 | 0 | 0 | 0 |
| field-evidence claims, 2026-08-06 | derived from a real run, sanitised here | 22 | 0 | 0 | 0 |
| research lifecycle records | authored fixture | **0** | 0 | 0 | 0 |

**52 claim objects examined. None states a witness depth, a depth basis, a
witness identity, or even the legacy `independence_basis`. None earns any
admissible depth under the policy.**

The fourth row is reported because it would otherwise inflate the first three.
Those 17 files contain no claim objects at all — they record experiments, not
witnesses — so they report nothing either way. Zero over zero and zero over 52
print identically, which is the negative-control lesson from DRI-7 applied to
ourselves.

Only the third row bears on adoption at all, and it bears on it weakly: it
derives from a real system run, but the sanitisation was done here, so it
carries our vocabulary rather than the producer's.

## 4. Slots: where a depth could be stated at all

The stronger half, because it does not depend on which corpus was chosen.

| Format | Has a depth field | Evidence object closed to additions | Could a producer state depth? |
|---|---|---|---|
| authority-evidence-v0.1 (signed, vendor-neutral) | no | yes (9 closed objects) | **no** |
| evidence-lineage-v0.1 | no | yes | **no** |
| decision-context-v0.1 | no | yes | **no** |
| memory-evidence-profile-v0.1 (interop) | no | yes (8 closed objects) | **no** |
| lir1-claim-instance-v1 | no | yes | **no** |

**Zero of five formats permit stating a witness depth.** In every one, the
object carrying a claim's origin is `additionalProperties: false`, so a producer
that tried to state depth would emit an envelope that fails validation.

The signed vendor-neutral contract is the sharpest case. Its `evidence_origin`
object requires `independence_basis`, whose enum is the four retired values —
`attested`, `declared`, `inferred`, `unknown` — three of which carry no depth at
all. That contract is the seam where an **outside** party states what its
evidence is worth, and depth cannot be expressed across it.

## 5. What this establishes

- **The policy's input does not exist today.** Applied now, it would grant no
  witness independence from any other, because no witness has stated a depth.
- **This is not the producers' fault.** The axes are plumbed end to end
  internally — `provenance/root_registry.py` carries them on a signed,
  omit-if-absent root request, and `aggregation/root_vote.py` reads them through
  to the verdict — but the formats in which evidence actually crosses a boundary
  have no slot. The two non-test producers of a root request in this repository
  state none of the axes; the production decision path carries `roots` and
  `basis` on the legacy vocabulary, which decomposes to `UNSTATED`.
- **So the binding constraint is the contract, not the policy.** This is the
  programme's own fourth kill criterion — metadata that cannot be obtained
  without adoption friction — reached by a different route than expected. The
  obstacle found is not that witnesses would refuse to say how far they went. It
  is that we never gave them anywhere to say it.

## 6. What this does **not** establish

- **Not the cost of the policy.** How many decisions become unanswerable in
  operation is the question of AID-1, which is specified and unrun. This census
  says the input is absent; it says nothing about the shape of the trade once it
  is present.
- **Not that witnesses would decline to attest.** Nobody has been asked.
- **Not a rate.** One estate, one moment, 52 claim objects, three of the four
  corpora authored here.
- **Not an external finding.** Every format measured is one we publish.

## 7. The next step it names, which needs an owner decision

Add an optional depth object to the vendor-neutral contract, so that an outside
party *can* state how far its witness went and sign that statement. It is
additive and omit-if-absent, exactly as the internal root request already is, so
no existing envelope or signature is invalidated.

That is a change to a contract other parties implement, and it is therefore not
made here. It is proposed, and it waits.

## 8. Reproduce

```bash
python3 experiments/aid1/measure.py
```

Read-only. Emits counts, never record content. A private corpus may be supplied
with `AID1_PRIVATE_CORPUS`; it is never copied and its cells are suppressed
below 10.

**Refutation: exhibit one instance, in any corpus, that states a witness depth.**
