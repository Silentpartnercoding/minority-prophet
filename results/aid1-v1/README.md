# AID-1 v1 confirmatory result

**Outcome: not supported.** 61 of 111 checks failed. The world was written by an
author who did not write the policy and was briefed to make it lose; the
criteria were frozen before that world existed; two defects in the policy were
disclosed in the protocol *before* the run rather than discovered in it.

The verdict is a rejection, and the shape of the failure is more useful than the
verdict. The policy works where it was designed to work, at a price that
adoption removes — and it fails on a case its own scope clause was written to
prevent and did not.

A dated [post-result note](POST-RESULT-NOTE.md) records what happened to the
policy *after* this run: both disclosed defects were repaired, and the repair's
direction was observed on the development salt. The verdict below is unchanged,
nothing in it was re-scored, and the repair is not promoted by that note.

## 1. It does prevent what it exists to prevent, at full adoption

`hidden_shared_source` is DR3's case: witnesses drawing on one hidden source
with nothing in the record connecting them. No instrument in the closed series
touched it.

| α | baseline correct | correct lost | correct gained | baseline silent | prevented | unneeded abstentions |
|---:|---:|---:|---:|---:|---:|---:|
| 0.0 | 363 | 363 | 0 | 357 | 357 | 579 |
| 0.25 | 377 | 273 | 32 | 343 | 301 | 439 |
| 0.5 | 347 | 111 | 101 | 373 | 266 | 184 |
| 0.75 | 333 | 48 | 116 | 387 | 241 | 92 |
| **1.0** | 370 | **0** | 100 | 350 | **177** | **0** |

At full adoption against fabrication it prevents 177 of 350 silent false
settlements — about half — while losing **no** correct settlements and forcing
**no** unneeded abstentions. Criteria 1 and 2 both pass in that cell. At zero
adoption the same protection costs every settlement in the family.

## 2. And prevention decays to nothing as adoption rises, one class up

The same family, scored against `INSTRUMENT` instead of `FABRICATION`:

| α | prevented | correct lost |
|---:|---:|---:|
| 0.0 | 357 | 363 |
| 0.25 | 261 | 205 |
| 0.5 | 140 | 28 |
| 0.75 | 98 | 1 |
| **1.0** | **0** | 0 |

This is the run's least expected result and it is not a bug. Attestation raises
a witness's *admissible depth*, and a witness backed to `METHOD` or
`REPLICATION` then clears the divergence test at the instrument rung. Attesting
buys back exactly the independence the policy was withholding. The policy's
protection at shallower error classes was coming from witnesses being
**unattested**, so the more of them attest, the less it protects.

Prevention and cost fall together. There is no adoption rate at which both are
good, one error class up from fabrication.

## 3. The benefit at full adoption comes from one variant only

The protocol required the hidden family to be split so the aggregate could not
hide this. It could have.

| variant | α=0.0 | 0.25 | 0.5 | 0.75 | 1.0 |
|---|---:|---:|---:|---:|---:|
| `aware` prevented (FABRICATION) | 174 | 166 | 183 | 186 | **177** |
| `unaware` prevented (FABRICATION) | 183 | 135 | 83 | 55 | **0** |

`aware` knows its record is incomplete and never attests completeness.
`unaware` attests completeness in good faith and is wrong. At full adoption the
entire benefit is the `aware` variant; the honest-but-mistaken half hands its
independence straight back. **The policy's safety rests on the attestation being
true, and nothing in it can tell a sincere false attestation from a correct
one.**

## 4. Where nobody can attest, it is pure cost that adoption cannot fix

| family | α | correct lost | prevented | unneeded |
|---|---:|---:|---:|---:|
| `nobody_can_attest` | every α, including 1.0 | **360 of 360** | **0** | 360 |

Honest witnesses who went to the world and can prove nothing — no artifact, no
key, unfindable. They are structurally unattestable, so no adoption rate reaches
them. The policy discards every settlement they would have supported and
prevents no error in exchange. This is criterion 2's failure and it is the case
that matters most outside a generator.

By contrast, `baseline_already_right` — nothing hidden, everyone attestable —
costs 360 settlements at α=0 and **nothing** at α=1.0. Where attestation is
available, adoption buys the whole cost back.

## 5. It suppresses a true minority claim, and worse as adoption rises

`minority_suppression`: three attestable majority witnesses asserting the false
value against three unattestable witnesses carrying the true one, all six
genuinely independent, 720 decisions per cell.

| α | policy false settlements | ladder | theatre arm | refusal arm |
|---:|---:|---|---|---|
| 0.0 | 0 | abstains | abstains | abstains |
| 0.25 | 84 | abstains | abstains | abstains |
| 0.5 | 228 | abstains | abstains | abstains |
| 0.75 | 456 | abstains | abstains | abstains |
| **1.0** | **720 of 720** | abstains | abstains | abstains |

Contrary-claim survival goes **360 → 0**. Every other arm abstains and the claim
lives; the policy settles against it, in every decision, at full adoption.

The mechanism is the policy working as designed: the attested majority keeps its
independence, the unattestable minority deflates toward one, and the majority
crosses a threshold the baseline refused to cross. `canon/ATTESTED-INDEPENDENCE.md`
anticipated this and scoped the policy to forbid counting that decides whether a
claim survives, enforced by a `ScopeViolation` on `Use.DECIDE_SURVIVAL`. **The
guard did not hold, because it cannot.** The use is caller-declared and nothing
in a record distinguishes the two: a caller deciding whether to act declares
`PERMIT_ACTION` truthfully while the same count deletes the claim.

Criterion 5 says any loss here fails the experiment outright, whatever else
holds. It fails in 8 cells.

## 6. Two criteria failed for reasons that are defects in the criteria

Stated plainly rather than quietly discounted. Neither was softened, and the
verdict stands as computed.

- **Criterion 4 failed 30 of 30 cells.** `refuse_all_unrecorded`, implemented
  exactly as the specification words it, refuses essentially everything, so it
  trivially "prevents everything" and the clause *at no worse prevention* can
  never be satisfied by any arm that answers anything. The comparison as written
  cannot discriminate. The world's author flagged this in the preregistration
  before the run.
- **Criterion 3 failed only at `TRANSCRIPTION`** (5 of 15). At the bottom error
  class every admissible depth clears the divergence test, so all four arms are
  identical by construction and "does materially worse" is unmeasurable there.
  At `FABRICATION` and `INSTRUMENT` criterion 3 **passes**: the backing
  machinery does real work, and the policy is not theatre.

## 7. Failure counts

| Criterion | Failed / total |
|---|---:|
| 1. It prevents what it exists to prevent | 14 / 30 |
| 2. Cost is bounded by benefit | 4 / 18 |
| 3. It is not theatre | 5 / 15 |
| 4. It is cheaper than refusing | 30 / 30 |
| 5. It does not suppress | 8 / 15 |

Powered: all 15 cells of `adversary_attests_freely` and all 15 of
`hidden_shared_source`. Underpowered and therefore reported without a pass mark:
`baseline_already_right`, `minority_suppression`, `mixed_attestation`,
`nobody_can_attest` — the baseline makes too few margin-critical silent false
settlements in each. Criterion 5 is scored without a power requirement, by the
frozen criteria, because any loss fails outright.

## 8. The two defects, disclosed before the run

Both were found by the world's author, reproduced independently, and recorded in
the frozen protocol before the confirmatory salt was touched. Both contradict
the policy's own doctrine that independence must be *earned* by backing.

1. **Declaring completeness bypasses the backing machinery.** `independent_for`
   returns `True` on mutual `ancestry_complete` before any depth is consulted,
   so two unbacked anonymous witnesses that merely say their record is complete
   are granted full independence.
2. **`Witness.admissible` never applies `honoured_identity`.** A self-declared
   `BONDED` with no `stake_reference` buys `REALITY`. The guard that degrades an
   unreferenced stake already exists one module away and was not wired in.

The run measured the policy **as shipped**. Repairing it first would have meant
editing the artifact after a world was built to expose its specific defects and
after development-salt outcomes were seen, which is the tuning this repository
forbids. The repair belongs to a registered successor, and its effect is not
measured here.

## Run

- **Scope:** criteria on reversible decisions, per the owner's standing scope
  decision. Irreversible decisions are tallied without a pass mark.
- **Size:** 8,100 campaigns, 12 decisions each; 6 families, 9 variants, 5
  adoption rates × 3 error classes.
- **Reproducibility:** two executions gave identical semantic results, SHA-256
  `c7e94d4d4800b5b278feb7571a11b223e6f9355e34b4ca1f1c56997a6953ee38`.
- **Output:** `result.json`, SHA-256
  `9ef4fcc4b8e58ce8216b64d0cc3a922ee341bb92274e4f41ecbfa38b197156fc`.
- **Campaign manifest:** SHA-256
  `2c63c0c41427a1279bb7a7b87dd38a389b1796180058bf11d3953632802acf85`.
- **When:** 2026-09-17, 07:58:53 to 07:59:29 UTC.
- **Environment:** CPython 3.12.13 on macOS arm64, commit
  `fb379a8de52c0c780242173011abcb5b4373508c`. The runner recorded
  `dirtyWorktree: true`: the shell redirect created this directory's
  `run-stdout.txt` before the run sampled git status. No tracked file differed,
  and the guarantee that matters is the pin check, which verified all 13 frozen
  inputs including the artifact under test.

## What this does not establish

- **Not that the repaired policy fails.** Two defects were known before the run
  and left in place deliberately. A successor must re-register and re-run.
- **Not a real-world cost.** Every rate here is synthetic. The adoption rate is
  a dial in a generator, not a measurement of anyone's willingness to attest.
- **Not that attestation is unobtainable.** Nobody has been asked.
- **Not independent validation.** The world shares the control domain with the
  policy, and was written by a same-operator author from the frozen spec.
- **Not a verdict on the ladder.** The baseline is `canon.proximity`, which has
  its own A5 defect — granting independence from silence — that this policy
  exists to correct. Both can be wrong at once.
