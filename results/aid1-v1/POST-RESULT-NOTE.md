# AID-1 v1 — post-result note, 2026-09-17

**The verdict is unchanged: rejected, 61 of 111.** The arithmetic in
`result.json` stands, the manifest still names the exact bytes that were
measured, and the frozen protocol is untouched. What this note records is what
happened to the artifact under test *after* the run, and what that does and does
not establish.

## 1. The policy was repaired

AID-1 measured `aggregation/attested_independence.py` as shipped, with two
defects disclosed in the protocol before the confirmatory salt was touched. Both
are now repaired, on `research/aid2-repair`:

1. **The completeness clause is gone.** It granted independence when both
   witnesses declared their ancestry record complete. That asks a witness to
   certify an absence it cannot see, and honouring it reinstated the inference
   from silence the policy exists to refuse — relocated into someone else's
   mouth. `ancestry_complete` is still recorded and is not honoured.
2. **The identity guard is wired in.** `Witness.admissible` now routes through
   `IndependenceAxes.honoured_identity`, so an unreferenced self-declared bond
   is honoured as a bare claim of identity rather than buying `REALITY`.

A third change is additive: `witness_bounds` returns the range the record
supports — a lower bound counting only earned independence, an upper bound
counting independence wherever the record cannot rule it out — so a caller can
evaluate a decision at both ends and refuse when they disagree.

## 2. What the repair does to this world, on the development salt

**These are development-salt observations, not a confirmatory result.** They are
recorded so the repair's direction is visible; they are not a verdict and must
not be cited as one.

| Observation | As measured in AID-1 | After the repair |
|---|---|---|
| Contrary claims surviving in the minority family, α=1.0 | 0 of 24 | **24 of 24** |
| `baseline_already_right`, fabrication class, α=1.0 | settles | **settles nothing** |

The suppression is gone — and the mechanism matters. It is not the bounds
machinery, which these arms never call: they ask for a single count. It is gone
because the repair is strict on *both* sides. The attested majority is backed by
an artifact and a verified identity, which tops out at `METHOD`, so it cannot
clear a fabrication-class divergence either and stops crossing the threshold.
Symmetric strictness removed the asymmetry that caused the deletion.

The price moved in the other direction at the same time. Against fabrication,
fully attested honest witnesses now settle nothing, because only a device
attestation or a resolved bond reaches `REALITY`. That is defensible — a log
proves you did something, not that you stood in the room — and it is expensive.

## 3. What this note does not do

- **It does not promote the repair.** No criterion was re-evaluated, no
  confirmatory salt was run against the repaired policy, and the table above is
  two observations, not a result. A successor must be separately registered and
  run.
- **It does not change the verdict**, the result, the manifest, or the protocol.
- **It does not claim the structural fix is validated.** `witness_bounds` is the
  principled answer to the suppression, and this world cannot exercise it,
  because its arms request a point estimate. Validating it needs a world whose
  callers ask for the range.

## 4. The pins now refuse, which is correct

`experiments/aid1run/run_confirmatory.py` pins the artifact under test by
digest. The policy changed, so `verify_pins()` now refuses on the working tree.
That is the machinery working: a closed record names the bytes it measured, and
re-pinning it to whatever the policy became is the one thing the pins exist to
prevent. The runner's tests were repointed at the freeze commit
`ee88928e4ae70f1aea5969a910336795fb960da5`, where all sixteen pinned inputs
still match their recorded digests.

Four of the world author's protocol tests asserted the two defects and the
suppression. They were updated in place to assert the repaired behaviour, each
recording in its docstring what it previously pinned and why it changed. Git
holds the historical blobs at the freeze commit, and the canonical manifest
continues to bind them.
