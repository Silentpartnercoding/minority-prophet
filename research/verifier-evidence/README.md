# Negative vectors for draft-he-agentproto-verifier-evidence

Executable form of Appendix A of
`draft-he-agentproto-verifier-evidence-00`. Run:

```
python3 research/verifier-evidence/run_vectors.py     # writes results.json
python3 -m unittest tests.test_verifier_evidence      # 22 tests
```

`results.json` is deterministic: rerunning must produce a byte-identical file,
and a test asserts it.

## What each vector is

Every vector supplies a **positive population** and a **negative control**, and
runs two checks over both — one that cannot tell them apart and one that can.
**The pair is the evidence.** A vector that ran only the sound check would show
a check passing and demonstrate nothing; one that ran only the degenerate check
would show a check accepting everything and demonstrate nothing either.

| | what it shows | degenerate check | sound check |
|---|---|---|---|
| **V1** | a check reading too few fields | `implemented-unexercised` | `implemented` |
| **V2** | a probe reporting a constant | `implemented-unexercised` | `implemented` |
| **V3** | a one-sided endpoint and a silent system | see below | — |
| **V4** | a withheld record under a completeness claim | `unestablished` | `failed` / `established` |

**V3 is not recomputed here.** It is the frozen KL-005 first-gate probe, a
committed artifact with its own runner. `run_vectors.py` reads it and pins its
SHA-256. A second implementation of the same numbers would establish nothing
about the first.

**V4 is due to Iman Schrock**, from the IETF agentproto delegation-and-evidence
thread, 15 September 2026: withhold one of two uses while leaving every
disclosed signature and inclusion proof valid.

## A correction this package produced

`KL-005/REPRODUCE.md` says of the silent system: *"Under the two-sided score it
is last."* That is wrong by its own committed numbers.

Two-sided, lower is better: `root_aware` 0.533, `silent` 1.000,
`count_reports` 1.033. The silent system is **second of three**. What the
two-sided term actually does is remove silence from the winning set — it does
not make silence the worst available strategy, because a system that confirms
every false event scores worse.

The claim in the draft was corrected to match. `test_silent_is_not_last_under_two_sided`
now pins it so the prose and the numbers cannot drift apart again.

## What this package does not establish

- It is **illustrative, not a conformance suite**. Nothing here is a claim about
  any protocol, implementation, or deployment.
- V1, V2 and V4 are constructed fixtures, not observations of a deployed system.
  They demonstrate that the requirements have content and that a check can fail
  them; they are not evidence that any real check does.
- Only V3 rests on a prior frozen experiment. The other three were written for
  the draft.
- No independent party has run any of this. There is no interoperability claim
  and no second implementation.
