# AID-2 v1 confirmatory result

**Outcome: not supported.** 74 of 120 checks failed. Two executions semantically
identical. Criteria were frozen before the world existed; the world was written
by an author who did not write the policy and was briefed to make the primary
lose; three defects in the instrument were disclosed in the protocol before the
confirmatory salt was touched, two of them reproduced independently.

The question was narrow: AID-1 showed that a single count cannot serve both
"may I act" and "does this claim survive", because those need opposite
conservatism. The repair returns a range and settles only when both ends agree.
Does the range do what the number could not?

**It does, on the case it was built for. It is inert on the case it was not, and
it is blind to a backed witness with a shared origin.**

## 1. The range fixes the suppression it was designed to fix

`count_decides_survival` is AID-1's construction: an attested majority asserting
a falsehood against unattestable witnesses carrying the truth.

| α | 0.0 | 0.25 | 0.5 | 0.75 | 1.0 |
|---|---:|---:|---:|---:|---:|
| contrary claims surviving, bounds (FABRICATION) | 360 | 360 | 360 | 360 | 360 |
| ladder | 360 | 360 | 360 | 360 | 360 |

At the instrument class and full adoption the separation is exact: the **point**
arm preserves **0** of 360, the **bounds** arm preserves **360**. AID-1's
headline failure is gone, and the mechanism is the one the repair claimed.

## 2. And it creates a new one, on a case nobody anticipated

`recorded_kinship_decoy`: six genuinely independent witnesses, where only the
minority's *recorded kinship* is a decoy.

| α | 0.0 | 0.25 | 0.5 | 0.75 | 1.0 |
|---|---:|---:|---:|---:|---:|
| surviving, bounds | 360 | 306 | 204 | 48 | **0** |
| surviving, point | 360 | 306 | 204 | 48 | **0** |
| surviving, ladder | 360 | 360 | 360 | 360 | **360** |

The bounds arm and the point arm are **identical at every rate**. The range buys
nothing here: `_ladder_view` runs the ladder at *admissible* depth, so a witness
the policy discounts is discounted at both ends, and a recorded ancestry token
collapses the pair at both ends at once. Criterion 5 fails in 8 cells, and by
its own terms that fails the experiment outright.

## 3. It is blind to a backed witness with a shared origin

`adversary_attests_freely`, at α = 1.0, fabrication class:

| Variant | baseline critical silent | prevented | correct lost |
|---|---:|---:|---:|
| `claims_bonded_identity` | 328 | **328** | 32 |
| `declares_completeness` | 326 | **326** | 34 |
| `declares_depth_only` | 321 | **321** | 39 |
| **`device_attested_fabricator`** | 360 | **0** | 0 |

The repair closed all three free-declaration strains essentially completely, at
a cost of 32–39 correct settlements. Against three device-attested copies of one
fabricator it prevents **nothing** and makes 360 silent false settlements.

This is the first disclosed defect, measured: `independent_for` grants
independence to any two witnesses whose admissible depth clears the error class
and whose recorded ancestries are disjoint. A device attestation earns depth. It
says nothing whatever about shared origin. The A5 defect the policy exists to
remove is still present, gated behind a depth check rather than removed.

## 4. Prevention still decays as adoption rises

Hidden-source family, prevented / correct lost:

| α | FABRICATION | INSTRUMENT |
|---|---|---|
| 0.0 | 536 / 544 | 536 / 544 |
| 0.5 | 394 / 410 | 163 / 70 |
| 1.0 | 346 / 374 | **0 / 0** |

Same shape as AID-1 and the same cause: attestation raises admissible depth, an
attested witness clears the divergence test, and the independence the policy was
withholding is handed back. `mixed_attestation` decays identically
(360 → 354 → 294 → 114 → **0**).

## 5. It degenerates, but only at the deepest class

Criterion 6 fails in exactly **one** cell: `baseline_already_right`, α = 1.0,
fabrication — the primary settles **0** of the 360 the baseline settles. At
instrument and transcription it settles **360 of 360** and passes.

So "refusal with extra steps" is not a general property. It is specific to the
class where artifact backing tops out at `METHOD` and nothing clears the bar.
Where depth can be earned, the rule answers.

In `mixed_attestation` at α = 1.0 the refusal share is 1.00 with the range
undetermined on 720 of 720 decisions, so the degeneration is real where ranges
stay wide.

## 6. The third defect, measured and not scored

The rule reads the two diagonal corners of the count box while the box is
bounded by the other two, so both ends can agree on a settlement the range does
not determine. Counted as `endsAgreeInteriorDoesNot`:

| Family, α = 1.0, FABRICATION | count |
|---|---:|
| `minority_suppression` | 360 of 360 |
| `mixed_attestation` | 433 of 720 |
| all other families | 0 |

**Stated carefully:** this co-occurs with the criterion-5 failure and is *not
established as its cause*. At the fabrication class the counter reads 360 in
every minority cell including α = 0.0, where the ends also disagree 360 times;
at the instrument class it decays to 0 by full adoption while the suppression
persists. It is a real, measured defect in the rule as specified. It is not the
explanation, and the write-up does not claim it is. Section 6 of the
specification contains no criterion for it, so it is reported and not scored.

## 7. Failure counts

| Criterion | Failed / total |
|---|---:|
| 1. It prevents what it exists to prevent | 14 / 30 |
| 2. Cost is bounded by benefit, where benefit is possible | 3 / 9 |
| 3. It is not theatre | 5 / 15 |
| 4. It is not worse than refusing | 43 / 45 |
| 5. It does not suppress | 8 / 15 |
| 6. It is not refusal with extra steps | 1 / 3 |

45 powered cells, 45 underpowered. Criterion 1's failures are entirely in the
hidden-source family: transcription at every rate, where all arms are identical
by construction, and instrument from α = 0.5 upward. Fabrication passes
throughout.

**Criterion 4 remains low-discrimination**, as the world's author warned in the
preregistration before the run: `refuse_all_unrecorded` has zero correct
settlements, so "strictly more" fails whenever the primary also has zero. 43 of
45 failures carry little information, and the repaired wording did not fix that.

The two criteria repaired in advance did their job. Criterion 2's
`reportedNotScored` block records cost where no benefit was possible — 360
correct settlements lost in `nobody_can_attest` at fabrication and instrument,
360 in `baseline_already_right` at fabrication — without those becoming pass
marks.

## Run

- **Scope:** criteria on reversible decisions. Irreversible tallied without a
  pass mark.
- **Size:** 11,700 campaigns, 12 decisions each; 6 families, 11 variants, 5
  adoption rates × 3 error classes.
- **Reproducibility:** two executions identical, SHA-256
  `9fb5c69d88e738ec8134a2b34504db2a1cf31eec6d7be9fabf929741d631f990`.
- **Output:** `result.json`, SHA-256
  `dc10e29eb7647202741b7dc3a903eda51699d719ee0d8c39ece09af203b1a685`.
- **Campaign manifest:** SHA-256
  `1775b6430e65e11b818840f51f84c748ef6d5becac16ae8ebf2836684243f2b0`.
- **When:** 2026-09-17, 11:05:43 to 11:07:42 UTC.
- **Environment:** CPython 3.12.13 on macOS arm64, commit
  `c369daf3c9eec75f9b8deb4f53e15e45e9cc20fe`. `dirtyWorktree: true` because the
  shell redirect created this directory's `run-stdout.txt` before the run
  sampled git status; no tracked file differed, and the guarantee that matters
  is the pin check, which verified all thirteen frozen inputs including the
  artifact under test.

## What this does not establish

- **Not that the bounds idea is dead.** Two of the three defects are
  implementation errors in code written the same day, not properties of the
  idea. A successor that fixes the upper bound and reads all four corners is a
  different instrument and must be separately registered.
- **Not that a repaired policy fails.** Three defects were disclosed and
  deliberately left in place; this measures the policy as merged.
- **Not a real-world cost.** Adoption is a dial in a generator. The census in
  `experiments/aid1/` found zero records in this estate stating any depth.
- **Not independent validation.** The world shares the control domain and was
  written from a specification by the policy's author.
- **A narrow adversarial base.** Three of the sharpest traps rest on
  device-attested strains the author wrote; a reviewer who rejects a
  device-attested fabricator as implausible weakens three results at once.
