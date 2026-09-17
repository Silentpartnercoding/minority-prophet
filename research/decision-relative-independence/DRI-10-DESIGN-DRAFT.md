# DRI-10 — a world that can reject bait

Status: **Frozen.** The preregistration is `experiments/dri10/PREREGISTRATION.md`,
protocol v1. This draft is not pinned.

## 1. Why this exists

DRI-9 rejected its named ladder and reported that bait cleared the floor
everywhere. The write-up then asked for a sequel that names bait and redraws
the same generator. That sequel is already sitting in `result.json`: flip
`method_under_test` to `bait` and the criterion returns supported, 65/65.

The deeper problem is the world. Hidden families *were* one unmarked shared
component; that component was marked; the decoy planted no markers. Bait
looked for the thing the generator planted on the group it was supposed to
find, and the harm clause never saw a token.

DRI-10 keeps DRI-9 rejected, names bait (the confirmatory that was deferred),
and splits **error component** from **marker carrier**.

## 2. What is independent of what

A source can share a hidden error and not carry the mark. It can carry a
shared mark and not share an error. Leak is a rate that applies to everyone
whose carrier is not the marked channel, including the old decoy.

| Family | Shared error | Marked channel | What bait should do if it is a detector |
|---|---|---|---|
| `marked_hidden_pair` | yes (pair) | that component | find them |
| `unmarked_hidden_pair` | yes (pair) | environmental token | mostly miss them, except leak |
| `common_carrier` | no | shared library | not collapse the library |
| `leaky_independents` | no | environmental token | not invent groups from leak |

`marked_hidden_pair` is a positive control, not the whole test. A method that
only passes there has passed DRI-9's world again.

## 3. Criterion, fail-closed

DRI-9's `evaluate_criterion` returns `supported` when every hidden cell is
underpowered. This one does not. No powered floor cell is a fail.

The 25% floor applies only to the positive control. The unmarked family is a
contrast: at leak 0.02, marked prevention must beat unmarked by 15 points, or
the mark is not the mechanism.

Harm includes the correct-settlement floor on both harm families, and a
library-collapse cap on `common_carrier` (0.1 false merges per campaign).
Prevention-without-harm is scored, not narrated.

## 4. What this will not do

- Rewrite DRI-9-V1.
- Claim independence of authorship. Same control domain, written after DRI-9
  was public.
- Run the confirmatory in the same commit as this draft. The salt is named
  and unread.
- Speak about irreversible decisions. `lookup_grouping` still ignores belief.

## 5. How to run

After the candidate record is committed:

```text
PYTHONPATH=. python -m experiments.dri10.run_confirmatory --output results/dri10-v1/result.json
```

Do not evaluate the confirmatory salt while editing this protocol.
