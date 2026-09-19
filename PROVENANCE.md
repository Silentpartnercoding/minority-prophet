# Provenance

The claims this repository makes, what is proved about each, what is
deliberately **not** claimed, when each entered the public record, and what was
adopted from other people's work.

Dates are here because provenance is part of evidence. A claim is checkable only
if you can see when it entered the record and run the check yourself. Every date
below is a commit in this repository's public history:

```
git log --reverse --format='%ad %H' --date=short -S'<term>' -- .
```

---

## The claim this work is about

**Counting repeated claims is not counting evidence. Recorded copies add no
evidence.**

Five agents repeating one source are one source. An aggregator that counts
attestations rather than independent roots can be moved by duplication alone,
without any new observation entering the world.

This is stated in `PUBLIC-CLAIMS.md` as invariant 1 and is the subject of the
formal core.

---

## What is proved

The repository carries **25 claims at `proof_status: proved_compiled`** in
`formal/THEOREM-LEDGER.json` — Lean proofs that compile from the pinned
environment with no `sorry`, no `admit`, and no axioms beyond
`propext` / `Classical.choice` / `Quot.sound`.

Three bear directly on the claim above.

### T3 — Majority voting is not copy-invariant

> There exist a claim vector `v` and its duplication `dup` such that
> `majority(v) = true` and `majority(dup) = false`.

`proof_status: proved_compiled` · `MinorityProphet.majority_not_copy_invariant`
· `formal/lean/MinorityProphetCore/Copy.lean`

Duplication alone flips the verdict. No new evidence is added; the record is
copied.

### T1 — Immunity to lineage corruption

> If `W` and `W'` are side-consistent, have the same assertion function, and
> have the same root set, then `F(W) = F(W')`. No constraint whatsoever is
> placed on how the non-root lineage differs.

`proof_status: proved_compiled` · `MinorityProphet.immunity` ·
`formal/lean/MinorityProphetCore/Immunity.lean`

Finite verification recorded in the ledger: **116,032 root-preserving forest
rewirings** (`verification/independent_check_2026-08.py`) and **1,992
root-preserving DAG rewirings** (`audit/falsify.py`), **zero violations**.
`lineage/reference_mutant_audit.py` *reproduces* the 116,032 figure; it does not
add to it.

Counting roots rather than attestations is what makes the verdict immovable by
rewriting.

### DR3 — No rule that reads only the record is immune to an unrecorded dependence

`proof_status: proved_compiled` ·
`MinorityProphetCore.DependenceRobustness.no_record_rule_is_immune` ·
`formal/lean/MinorityProphetCore/DependenceRobustness.lean`

Immunity to missing lineage cannot come from a better rule over the same
record. It requires an observable the loss does not remove.

---

## What is NOT claimed

These limits are carried in the ledger as `prohibited_overstatement` on the
claims themselves and are repeated here so this file cannot be read as stronger
than its sources.

- **T3 is an existence claim about a witness.** It says nothing about how often
  majority voting fails in practice.
- **T1 does not cover root-changing rewirings.** Those change the verdict, and
  the repository records its own figure for how often.
- **DR3 is an existence witness, not a rate.** It does not show that any added
  observable is sufficient.
- **T5 must never be stated as immunity to key compromise or operator error.**
  That reading is falsified by CE-04 and CE-05.
- Finite verification is `verified_finite` — exhaustive over a bounded domain.
  It is **not** a proof of the universally quantified statement, and the ledger
  keeps the two statuses distinct for exactly that reason.
- Nothing here has been independently reproduced except where
  `research/knowledge-ledger/EXTERNAL-REPRODUCTIONS.json` records it, with what
  each reproduction does **not** discharge.

---

## When each claim entered the public record

| Concept | First public | Commit |
|---|---|---|
| `copy-invariant` | 2026-08-05 | `e1403a7` |
| "Recorded copies add no evidence" | 2026-08-06 | `5c3d7ae` |
| `opposingRoots` / root counting | 2026-08-07 | `f6904c0` |
| `unverifiable` | 2026-08-05 | `e1403a7` |
| `not_established` | 2026-08-07 | `f6904c0` |
| declared search space | 2026-08-07 | `6daaaf3` |
| conservative abstention | 2026-08-12 | `28b2fb9` |

---

## What a date here means

It means: **this text existed in a public Apache-2.0 repository on this date.**

It does **not** mean anyone read it, that it was submitted anywhere, or that it
constitutes a publication. It is not a claim of invention, and it is not
directed at anyone.

---

## Work adopted from others

Two distinctions this repository had been using internally were published, and
published better, by other people on 2026-09-16: **Mikhail Sergeev** in
`draft-sergeev-claim-boundaries-00`, and **Bradley B** in IETF `agentproto` list
discussion separating independence from completeness.

Sergeev's three outcomes add *downgrade* — report the strongest claim the
evidence does support — which this work did not have. Bradley's axis split
distinguishes two failures this work had folded into one verdict, and the two
failures need different repairs.

Both are adopted here rather than contested.
`research/verifier-evidence/ADOPTED-EXTERNAL.md` records what was taken, from
whom, and what changed as a result. A draft prepared here dropped its
completeness half entirely rather than restate theirs.

This section belongs in a provenance record for the same reason the rest of it
does: a file that traced only the ideas originating here, and stayed silent on
the ones that came from elsewhere, would be the selective attribution this
repository exists to detect.
