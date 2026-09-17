# AID-3 — the reviewer's world, run against the repaired policy

**Status: registration note. Protocol frozen; not run when this was written.**

This experiment runs a world I did not write, against a policy I did, using
criteria frozen before either existed. The world is the adversarial review's,
submitted as PR #214 on 2026-09-17 at 07:23 UTC.

## 1. Why this exists, stated plainly

I ran AID-1 at 07:58 UTC — **35 minutes after the reviewer's world was already
open, frozen, and green in CI** — against a world written by a subagent I
spawned instead. I did the same for AID-2. Both records carry the line "same
control domain; not independent validation", and that line was doing more work
than it should have: a subagent of mine is author separation, but it is not the
reviewer with the track record of catching me. The review rejected bait on the
first honest test in DRI-10 and caught my selection error in DRI-11.

AID-3 corrects that omission. It is not a re-run of AID-1, whose record is
closed and stands.

## 2. What is under test, and why the answer should differ

The policy has been repaired since the reviewer's world was authored. The
repair merged as #216 removed the completeness short-circuit — the hole the
reviewer's preregistration names in section 10 and builds three families around.

So AID-3 asks a question AID-1 could not: **does the repair close the hole the
reviewer aimed at, on the reviewer's terms?**

Two consequences are predictable from the construction and are disclosed here
rather than discovered in the results:

- **`world.py` sets `ancestry_complete=adopted`.** The adoption rate α *is* the
  completeness tick. A policy that no longer honours completeness is largely
  insensitive to α, so the adoption curve should be close to flat. That is the
  repair working, not the world failing.
- **Hidden copies are `DECLARED` / `ANONYMOUS`**, so post-repair their
  admissible depth is `TEXT` and they cannot clear a fabrication divergence.
  The pair should now collapse at every α.

The family that remains a live trap is `minority_suppression`: the false side is
`DEVICE_ATTESTED` / `VERIFIED`, the true side is unattestable, and nothing in
the repair changes that asymmetry.

## 3. Every change I made to the reviewer's submission

The reviewer's world is theirs. These are mine, and they are mechanical:

| Change | Why |
|---|---|
| Package relocated `experiments/aid1/` → `experiments/aid3run/` | `experiments/aid1/` holds the AID-1-OBS census on main. 16 import and path references rewritten. |
| Record id `AID-1-V1` → `AID-3-V1` | `AID-1-V1` is already canonical. A closed record must not be re-registered. |
| Salts → `minority-prophet-aid3-*` | Reusing AID-1's confirmatory salt would run this on a draw already bound to a closed record. |
| Schema strings → `aid3` | Consistency with the new identifier. |
| Pin map re-derived | The reviewer's digests covered its own paths and the pre-repair policy. The new map pins the repaired policy at `116d290f…`. |
| `test_complete_box_...` inverted | It asserted the short-circuit grants independence. It no longer does. The inversion is the measurement; the docstring records what it previously pinned. |

**Not changed:** `world.py` byte-for-byte (`b5cb965a…`), the config's parameters,
all five criteria, the four arms, the scoring logic, and the reviewer's
descriptive prose. Where their documents still say "AID-1", those are their
words describing their construction, and restamping them with my experiment's
name would misrepresent authorship.

## 4. Criteria

AID-1's five, verbatim, as the reviewer's `scoring.py` implements them.
Unchanged, and deliberately not repaired — AID-2 established that criterion 2
is unsatisfiable where the world guarantees zero prevention and that criterion 4
is low-discrimination when the ceiling arm refuses everything. Both limitations
apply here and are reported with the result rather than fixed mid-flight, since
editing criteria the reviewer scored against would defeat the purpose of running
their world at all.

## 5. Disclosure

- Same control domain. The reviewer operates under the same owner; this is
  author separation, not A2-independent validation.
- The world was authored against the pre-repair policy. Two of its six families
  target a defect that no longer exists, and should read as no-ops.
- Development salt only until the candidate record is committed.
- No authority claim.
