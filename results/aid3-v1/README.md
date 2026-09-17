# AID-3 v1 confirmatory result

**Outcome: not supported.** 17 of 23 checks failed. Two executions semantically
identical. 7,200 campaigns.

This is the adversarial review's world — submitted as PR #214, authored against
the **pre-repair** policy — run against the **repaired** policy merged as #216.
The criteria are AID-1's five, verbatim, as the reviewer's scoring implements
them. Every edit I made to their submission is listed in
[`AID-3-REGISTRATION-NOTE.md`](../../research/attested-independence/AID-3-REGISTRATION-NOTE.md).

It exists because I ran AID-1 and AID-2 against worlds written by subagents I
spawned, while this world sat open, frozen and green in CI since 35 minutes
before AID-1's run. That was the weakest part of both records.

## 1. The suppression is total, and the repair did not touch it

`minority_suppression`: the true side is two witnesses who cannot attest; the
false side is two device-attested, verified attesters. The ladder ties 2–2 and
abstains.

| Arm | α = 0.0 | α = 0.5 | α = 1.0 |
|---|---|---|---|
| `ladder` | abstains, claim survives 4800 | 4800 | 4800 |
| `attested_declared_only` | 4800 | 4800 | 4800 |
| `refuse_all_unrecorded` | 4800 | 4800 | 4800 |
| **`attested`** | **false settlement 4800 of 4800** | **4800** | **4800** |

Contrary-claim survival goes **4800 → 0** at every adoption rate. Every other
arm abstains and the claim lives; the policy settles against it in every
decision. Criterion 5 fails in all three cells, and by its own terms that fails
the experiment outright.

This is the finding the repair does not reach. Removing the completeness
short-circuit changed nothing here, because the asymmetry is not about
completeness: the false side has backing, the true side cannot obtain any, and
deflating the unattested is exactly what the policy is for.

## 2. Prevention is zero, because the policy trades one wrong answer for another

`hidden_source` is DR3's case, laid out so that collapsing the hidden pair turns
a 3–2 settlement into a 1–2 settlement *the other way* — not an abstention.

| α | ladder silent | prevented | policy silent | unneeded |
|---:|---:|---:|---:|---:|
| 0.0 | 1051 | **0** | 1051 | 0 |
| 0.5 | 1032 | **0** | 1032 | 0 |
| 1.0 | 1020 | **0** | 1020 | 0 |

Prevented is zero at every rate, and the policy's silent count equals the
ladder's exactly. Traced on one decision: the ladder counts 3–2 and settles
true; the repaired policy collapses the hidden pair to 1–2 and settles **false**;
the theatre arm keeps the old short-circuit and settles true at 3–2. The
reference for that decision is `abstain`, so both the ladder and the policy are
wrong on it — in opposite directions.

So the policy is not inert here. It correctly collapses the hidden pair, and the
world is built so that collapsing it produces a different wrong answer rather
than a right one. Criterion 1 fails in all three powered cells, on both the 40%
floor and the significance test.

## 3. The backing machinery reads as ornamental under this criterion

`adversary_attests`: copies always declare `REALITY` and complete ancestry, with
no backing and no holdable identity.

| α | ladder silent | `attested` silent | `attested_declared_only` silent |
|---:|---:|---:|---:|
| 0.0 | 1043 | 1043 | 1043 |
| 0.5 | 1033 | 1033 | 1033 |
| 1.0 | 1040 | 1040 | 1040 |

Criterion 3 requires the theatre arm to be *strictly worse* than the policy.
The counts are identical, so it fails in all three cells.

**This one deserves care.** The two arms do behave differently on individual
decisions — the trace in section 2 shows the theatre arm taking the
short-circuit the repaired policy refuses. They arrive at the same *number* of
silent false settlements by different routes. The criterion counts outcomes, not
mechanisms, so under its wording the backing machinery is not doing measurable
work in this family. That is a statement about the criterion as much as about
the policy, and it was written before the repair existed.

## 4. Cost, and the flat adoption curve

| Family | α = 0.0 | α = 0.5 | α = 1.0 |
|---|---|---|---|
| `honest_unattestable` correct settlements | 4800 → **0** | 4800 → **0** | 4800 → **0** |
| `robust_correct` | 4792 → 4792 | 4787 → 4787 | 4795 → 4795 |
| `mixed_attestation` | 3944 → 3117 | 3921 → 3146 | 3934 → 3147 |

Where nobody can attest, the policy discards **every** correct settlement at
every rate — 4800 unneeded abstentions per cell — and prevents nothing.
Criterion 2 fails there and in `mixed_attestation`. Where everyone is backed
(`robust_correct`) it matches the ladder exactly and costs nothing, which is the
one place it behaves as intended.

**The adoption curve is flat, as predicted before the run.** `world.py` sets
`ancestry_complete = adopted`, so α *is* the completeness tick, and a policy
that no longer honours completeness is insensitive to it. The registration note
recorded this prediction in advance; the numbers confirm it. A flat curve here
is the repair working, not the world failing.

## 5. Failure counts

| Check | Failed / total |
|---|---:|
| `preventsEnoughOfCritical` (criterion 1) | 3 / 3 |
| `significantlyFewerSilent` (criterion 1) | 3 / 3 |
| `costBound` (criterion 2) | 2 / 6 |
| `materiallyWorseThanAttested` (criterion 3) | 3 / 3 |
| `cheaperThanRefuseAll` (criterion 4) | 3 / 3 |
| `doesNotSuppress` (criterion 5) | 3 / 3 |

3 powered comparisons, 0 underpowered. The two criterion-2 passes are
`robust_correct` and the families where no benefit was possible.

## 6. What the repair did and did not change

The reviewer's world was built around the completeness short-circuit, and their
own construction test asserted that two unbacked witnesses ticking the box are
granted independence. **That test now asserts the opposite, and passes** — the
repair closed the hole they aimed at. Their `declared_only` arm keeps the old
control flow inline, so the contrast is preserved and scored.

What the repair did not change is everything in section 1. The hole is shut; the
suppression is untouched.

## Run

- **Scope:** criterion on reversible decisions; adoption curve reported, not a
  pass mark.
- **Size:** 7,200 campaigns, 12 decisions each; 6 families, 3 adoption rates,
  `FABRICATION` error class.
- **Reproducibility:** two executions identical, SHA-256
  `1f6be8d016f8b2fc0f4bd2175a6891e3e02ccebc0d05c81b25d28e9570e6aba2`.
- **Output:** `result.json`, SHA-256
  `bf31b3c4abedf5fc7d46c816490c91edbfdef4250730007b819ae9f80296f94e`.
- **Campaign manifest:** SHA-256
  `16e033afbfbd19031f3dff13aa4255bc9a3008b249230a237d93401b14f4d46b`.
- **When:** 2026-09-17, 11:48:36 to 11:49:02 UTC.
- **Environment:** CPython 3.12.13 on macOS arm64, commit
  `f5792b123dceaa1b7a142ced0c396a965bf9cd90`. `dirtyWorktree: true` because the
  shell redirect created this directory's `run-stdout.txt` before the run
  sampled git status; the guarantee that matters is the pin check, which
  verified all ten frozen inputs including the policy at `116d290f…`.

## What this does not establish

- **Not independent validation.** The reviewer operates under the same owner.
  This is author separation, which is what AID-1 and AID-2 lacked, not an
  outside replication.
- **Not that the criteria are right.** Criterion 3 counts outcomes and cannot
  see that two arms reached the same total by different mechanisms. Criterion 4
  compares against an arm that abstains on everything unrecorded.
- **Not a real-world cost.** Every rate is a dial in a generator, and the census
  in `experiments/aid1/` found zero records in this estate stating any depth.
- **Not a verdict on the repair.** The repair demonstrably closed the
  short-circuit; this world shows that closing it does not address the
  suppression, which is a different defect.
