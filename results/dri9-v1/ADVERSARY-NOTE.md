# DRI-9 v1 — adversary note

**The verdict is unchanged: rejected.** This note does not resticker bait as
supported. It attacks the record, the write-up, the criterion, and the proposed
sequel. `result.json`, the manifest and the frozen protocol are untouched. Every
figure below was re-derived from `results/dri9-v1/result.json` or generated from
the pinned world, not copied from prose.

Same control domain as the author. This is not independent validation.

## Do not run DRI-10 that only names bait

`results/dri9-v1/README.md` § "What it does not establish" says bait must not be
declared the winner, so a successor must name it in advance and test it on fresh
worlds. That is the spin.

`experiments/dri9/PREREGISTRATION.md` §12 already said, before the confirmatory
salt was touched, that development had shown bait beating the ladder, that the
ladder stayed named so the favourite could not be rewritten, and that **if bait
won again on the confirmatory salt, that was the finding**. Bait won. The finding
is written. Naming it now and rerunning the same generator is the rewrite §12
refused.

Naming does not change a number. Pointing `evaluate_criterion` at this
`semanticResult` with `success_criterion.method_under_test = "bait"` returns
**supported, 65/65, zero failures**. A new salt on the same world reprints that
green. A sequel that does only that is claim-laundering, not a new experiment.

## What is actually wrong

### 1. The decoy never plants markers. Bait's "no harm" pass is free.

`world.py` sets `marked_component` from hidden components only. In
`coincident_independents` every source has `component is None`, so `marked` is
`None`. Markers are appended only when `carries and marked is not None`.
`marker_leak = 0.02` is dead in the decoy.

Reproduced, development and confirmatory salts, 8 campaigns × 4 cells:

| Salt | Family | Decisions | Markers |
|---|---|---:|---:|
| both | `shared_upstream_pair` | 384 | 592–593 |
| both | `shared_upstream_trio` | 384 | 854–857 |
| both | `coincident_independents` | 384 | **0** |

`result.json` then reports bait in every decoy cell as 0 true merges, 0 false
merges, 0 silent errors, 3,000/3,000 correct settlements. That is not a harm
test. The instrument is unplugged.

`EVIDENCE-ALIGNMENT.md` still cites "causing zero harm in the decoy" as a
measured claim. `CANONICAL-RECORDS.md` says bait cleared 8 of 8 "with no harm".
Both are true as arithmetic and false as a test of bait.

The leak that *does* exist (independents in the hidden families, 40–138 false
merges per cell) is mixed with the true signal. It is not the decoy.

A successor that names bait without giving the decoy a marked component, a
shared-leak family, or some other way to carry `marker_leak`, will pass the same
vacuous clause again.

### 2. The ladder was AND-gated after seeing the best ingredient win.

After development showed reflection destroying correct settlements, timing was
dropped and `ladder_signals` became `["bait", "coerror"]` with
`ladder_score_to_merge = 2`. That is not "a combination of weak signals." It is
**do not trust bait until a slower feedback counter agrees**. Co-error needs
`coerror_minimum_joint_decisions = 4` at `coerror_threshold = 0.5`, even though
`feedback_rate = 1.0` so feedback itself is not scarce.

Of course the ladder is precise (209–942 true merges, 0–6 false; no correct
settlement lost) and late (critical prevention 0.147–0.276 against bait
0.360–0.768). §12 already measured that on development (27 and 18 remaining
silent errors for bait against 65 and 68 for the ladder, baseline 85 and 87).
Naming the cautious AND as the method under test, then proposing to name the
thing that already won, is two laps of the same choice.

`arms.py`'s module docstring still says the ladder uses "bait, timing, co-error".
The config does not. The write-up's 217–942 range drops the 209 cell.

### 3. The world is built for bait.

Hidden families *are* "one unmarked shared component." Bait plants a marker on
that component. Pickup ∈ {0.5, 0.9} is stated, not measured. Prevention tracks
pickup (pair 0.36 then 0.70; trio 0.45 then 0.76) because that is the planting
rate. Finding the thing you planted, at the rate you planted it, is the
mechanism working inside a toy that assumes the mechanism.

DR3 still holds for *reading* the record. This experiment does not show that a
real upstream can be marked. The preregistration says so. The result README then
calls intervention "legible" as if the legibility were a discovery rather than
the generator.

### 4. "Supported" can mean "we did not test."

If every hidden cell has `criticalTieredSilent < minimum_critical_silent_for_test`
(12), `evaluate_criterion` skips the floor and the significance checks and
returns `supported: True`. `tests/test_dri9_protocol.py` asserts that
(`quiet["supported"]` with critical=3). It did not fire this run — all 8 cells
were powered — but the bar is vacuous when the experiment is quiet.

Two executions on the same salt producing one semantic hash is determinism, not
replication. Check `semanticResultReproducible` only asks that.

### 5. The no-harm clause does not measure harm.

For every arm, "no significant harm" is only: not significantly *more silent
false settlements* than baseline in the decoy. Baseline silent there is already
0. Reflection therefore **passes** all four decoy `noSignificantHarm` checks
while making 6,497–8,782 false merges and cutting correct settlements from 3,000
to ~1,300. The 95% correct-settlement floor and false≤true merges apply only to
the named method.

The write-up's "4 harm flags" for reflection and ablation are commentary. They
are not among the 65 checks. Prevention-without-harm is meaningless, as they
say, and they did not score it except as prose.

### 6. "Margin-critical" did no work in the pair family.

In every pair cell, `criticalTieredSilent == reversibleTieredSilent`
(965=965, 956=956, 923=923, 1009=1009). The 25% floor there is 25% of all
silent errors. The trio is the only family where pivotal and silent come apart.
DRI-8's whole-group defect is fixed in code (`is_pivotal` walks every subset).
In the pair family the extra machinery did not filter.

### 7. Irreversible immunity is a code path, not a law.

`settle()` on irreversible, when not robust, falls back to `lookup_grouping`,
which is defined to ignore belief. Instrument arms therefore match the baseline
on `high_irreversible:correct_settlement` in every cell. The **oracle** does
move them (trio 1,283→1,714, 1,234→1,659, 1,331→1,744, 1,199→1,648). Belief
could still flip the robust branch; they measured 0/360 on development and
scoped the path out. A bait sequel that does not change this branch will "find"
the same zero.

### 8. Frozen labels that are no longer true.

`EXECUTION-CONFIG.json` `status` is still `preregistered-unexecuted` after a
completed confirmatory run. `test_config_is_frozen_scoped_and_sized` asserts
that string. The runner refuses any other status. The file that says it has not
been run is the file the run was pinned to.

`run_confirmatory.py`'s docstring says it pins "reused DRI-5, DRI-9 and DRI-3
files". It pins DRI-8, DRI-3, DRI-2, and this experiment.

### 9. Tests do not compare arms and do not catch 1–7.

`tests/test_dri9_protocol.py` is construction invariants on the development
salt: pins, rewrite-every-cut, subset pivotal, timing excluded from the ladder,
determinism, criterion logic on toy rows. No test asks whether the decoy emits
a marker. No test asks whether an all-underpowered result should fail. No test
reads `result.json`. A green protocol suite is compatible with every hole above.

## What the numbers actually are

Ladder critical-prevention shares, from `result.json`:

| Cell | Pair | Trio |
|---|---:|---:|
| pickup=0.5 jitter=0.1 | 0.153 | 0.186 |
| pickup=0.5 jitter=0.5 | 0.147 | 0.182 |
| pickup=0.9 jitter=0.1 | **0.276** | 0.238 |
| pickup=0.9 jitter=0.5 | 0.244 | 0.229 |

One cell over 0.25. All seven failures are `preventsEnoughOfCritical`.
Significance checks passed. That part of the write-up is honest.

Bait on the same cells: 0.360, 0.345, 0.699, 0.703 (pair) and 0.447, 0.459,
0.761, 0.768 (trio). Trio correct settlements 1,273→1,622 at pickup 0.9
jitter 0.1 is real. Pair family bait *loses* a few correct settlements
(2,077→2,056; 1,991→1,961) and stays above the 95% floor. Cite both.

## What would count as sorting this out

Do **not**:

- Open DRI-10 that only flips `method_under_test` to `bait` and draws a new salt
  from this generator.
- Declare bait supported from this record.
- Patch prose to call the decoy a harm test without planting markers.

Do:

1. Keep DRI-9-V1 **rejected**. The named method lost. That stands.
2. Retract "zero harm in the decoy" / "no harm" from `EVIDENCE-ALIGNMENT.md` and
   `CANONICAL-RECORDS.md` unless the sentence says the decoy emitted no markers.
3. If a bait confirmatory is still wanted, change the world first: the decoy
   (or a new family) must be able to carry the marker by leak or by a shared
   unmarked bait that is *not* the hidden component. Then name bait, freeze,
   new salt. Without that, the harm clause is still free.
4. Fix `evaluate_criterion` so an all-underpowered result is not `supported`.
5. Score lost correct settlements and false merges for every arm, or stop
   calling reflection/ablation "harm flags" as if they were checks.
6. Say irreversible is out of scope because `lookup_grouping` ignores belief,
   not because belief cannot move that path.
7. Add a protocol test that fails if `coincident_independents` emits zero
   markers while `marker_leak > 0`.

Until 2–3 happen, bait is a reported arm that won inside a toy built for it,
with a decoy that never showed it the toy. That is already the result. It is
not a reason to run the same experiment again.
