# HANDOFF v1 — RUN-20260807-1

Everything needed to review, reproduce, or resume. No hidden state.

## Where the work is

```
worktree  $HOME/Development/minority-prophet-first-transmission
branch    agent/knowledge-ledger-run-20260807-1
base      887bd2f  (agent/first-transmission)
head      8d1bc31
window    2026-08-07T17:30:04Z -> 2026-08-07T18:20:59Z
```

Worktree clean at start and at end (`git-status-before.txt`,
`git-status-after.txt`, both empty).

## Commits, in order

| SHA | What |
|---|---|
| `6600dc7` | orientation + registry audit; adds `scripts/audit_preregistrations.py` |
| `72f45cc` | authoritative prompt bytes replace the agent transcription; opens `CONSTRAINTS-v1.json` |
| `c977347` | **protocol commit** — KL-000 preregistration v0.2, protocol v1.0.0, 10 fixtures |
| `38fc0cb` | orientation correction: the `github` remote was deleted, not misread |
| `db55b53` | implementation: generator, invariant checker, baselines, red-team suite |
| `3ac618f` | **result commit** — confirmatory execution, passed |
| `74c6561` | result correction: bucket fail-closed causes, baselines on the full set |
| `8d1bc31` | next gates for KL-001..KL-011; snapshot test replaced by its invariant |

`3ac618f` was briefly amended into `1b0ce02` and that was **reverted**;
`3ac618f` is an ancestor of HEAD again and its superseded outputs are retained
under `KL-000/results/superseded/`. See `PROV-007`.

## The draft PR — needs your decision first

**No PR has been opened and nothing has been pushed.** Two facts block the
prescribed route:

1. `agent/first-transmission` **does not exist on `github`**, and neither does
   `887bd2f`. The prompt's PR base is unpublished (`PROV-003`).
2. Publishing a base branch to a public repository is outward-facing and was not
   explicitly requested, so it is your call, not mine.

### Recommended: cherry-pick onto `github/main`

Keeps one scientific question per PR. The delivered diff carries KL-000 and this
run's provenance, and does **not** carry `0a35fe1`/`887bd2f` (the
first-transmission render and its correction), which are unrelated to KL-000 and
belong in their own PR.

Already validated: KL-000 was reproduced from base `github/main` `335b34e` with
an exact match, so the cherry-pick target is known good.

```bash
cd $HOME/Development/minority-prophet-first-transmission
git fetch github --prune
git worktree add /tmp/kl000-pr -b agent/kl-000-conformance github/main
cd /tmp/kl000-pr
git cherry-pick 6600dc7 72f45cc c977347 38fc0cb db55b53 3ac618f 74c6561 8d1bc31
PYTHONPATH=. python3 -m pytest -q                                    # expect 74 passed
PYTHONPATH=. python3 -m pytest research/knowledge-ledger/experiments/KL-000/tests -q   # expect 54 passed
git push github agent/kl-000-conformance
gh pr create --draft --repo Silentpartnercoding/minority-prophet \
  --base main --head agent/kl-000-conformance \
  --title "KL-000: dual-ledger conformance reaches adversarial-passed" \
  --body-file research/knowledge-ledger/runs/2026-08-07/RUN-20260807-1/DRAFT-RUN-REPORT-v1.md
```

**After cherry-picking, `PROTOCOL-COMMIT.txt` will be stale.** It records
`c977347`, the registration commit on *this* branch; the cherry-pick creates a
new SHA for the same content. Fix on the PR branch before pushing:

```bash
git log -1 --format=%H -- research/knowledge-ledger/experiments/KL-000/preregistration.json \
  > research/knowledge-ledger/experiments/KL-000/PROTOCOL-COMMIT.txt
git commit -am "Rebind KL-000 protocol sidecar to the cherry-picked registration commit"
```

Then re-verify the M1 chain:

```bash
P=research/knowledge-ledger/experiments/KL-000
test "$(git log -1 --format=%H -- $P/preregistration.json)" = "$(cat $P/PROTOCOL-COMMIT.txt)" \
  && echo "preregistration unedited since registration"
```

This is a genuine tension between a clean single-question PR and an immutable
commit binding, and it is resolved in favour of recording both SHAs rather than
pretending the history is linear. Do not "fix" it by editing
`preregistration.json`; its `protocolCommit` stays `null` by design.

### Alternative, if you prefer preserving exact history

```bash
git push github agent/first-transmission           # publishes the base
git push github agent/knowledge-ledger-run-20260807-1
gh pr create --draft --repo Silentpartnercoding/minority-prophet \
  --base agent/first-transmission --head agent/knowledge-ledger-run-20260807-1 \
  --title "KL-000: dual-ledger conformance reaches adversarial-passed" \
  --body-file research/knowledge-ledger/runs/2026-08-07/RUN-20260807-1/DRAFT-RUN-REPORT-v1.md
```

No SHA remapping, no stale sidecar. Costs publishing a second branch.

**Name the remote explicitly in every push.** `github` is the public repository;
`origin` is a working copy on another machine over SSH. A bare `git push` may
publish nothing, or publish to the wrong place.

## Reproduce the science

```bash
cd research/knowledge-ledger/experiments/KL-000
python3 src/run_kl000.py --phase all --out results --label reproduction
```

~95s, stdlib only, no network. Expected values and the exact comparison script
are in `REPRODUCE.md`. Verified working from base `github/main`.

## Artifact hashes

```
inputs/PROMPT.txt (authoritative)   sha256:729bfb70f39916e320f6bcb248febb273e4a1d832f6de9356b0e34940b2f5ccb
KL-000/preregistration.json         sha256:5204e6400e0b90d5ed1f127c548050e4469ad65739b6213e21976f6446bcaaa5
KL-000/PROTOCOL.md                  sha256:dea9649f95e18769cf6c59b6f9a2e969c73caecef60294218f9a1d4ccf948a14
results/kl000-confirmatory.json     sha256:0b73541a49bc4ec30c0e756d1d5c100270d857cf29e9a00dd1168b7a1d5ae1b0
results/kl000-reproduction.json     sha256:33cf35e9828ff4ea42fb0c3951012534fc2735690ee84e3d09b17ef533923206
results/kl000-effective-sample.json sha256:08ecd9f28c296e7755e47064b51d80082500d16881a51d279faeb982be1cbabf
evaluator under test                sha256:15dfd50051ef5da3db13d8e591f58537325ee50aa4e3573914f86e4ff3a3e21f
```

The confirmatory and reproduction documents differ only in `label`,
`environment`, and two `elapsedSeconds` values, so their digests differ by
design. The comparison in `REPRODUCE.md` is the equality check, not the hashes.

## Unresolved approvals

| # | Decision | Blocking |
|---|---|---|
| 1 | Publish base branch, or cherry-pick onto `github/main`? | the draft PR |
| 2 | Commission the independent reimplementation (`BL-001`), and with what isolation? | KL-000's next gate **and** KL-011 |
| 3 | Fix `ADV-001` before or after KL-011? | schema sequencing; either order has a cost |
| 4 | Schema v0.2 for shared dependency (`BL-003`)? | KL-006 and KL-008 substantively |
| 5 | Confirm nothing is promoted yet | — |

Nothing in `CANONICAL-RECORDS.md`, `EVIDENCE-ALIGNMENT.md`, `PUBLIC-CLAIMS.md`,
or the paper was touched. Promotion is a separate commit after your review.

## How another agent resumes

1. Read `DRAFT-RUN-REPORT-v1.md`, then `CONSTRAINTS-v1.json`, then
   `KERNEL-STATUS-SNAPSHOT-v1.json`.
2. `NEXT-RUN-PROPOSAL-v1.md` is the next run, fully specified.
3. Do **not** re-run KL-000's confirmatory phase hoping for a different number.
   It is deterministic; re-running is reproduction, and re-running to search for
   a preferred answer is forbidden.
4. Do **not** claim First Transmission or Candidate First Transmission. Neither
   is earned. KL-011 was never eligible to run.
5. The governing prompt for *this* run is `inputs/PROMPT.txt` (v2). A corrected
   **v3** exists —
   `sha256:4bf92221f371cf55b67112f885d4c0b2496843a0ba19acc4d403d25fd117173f` —
   and governs the *next* run. It was deliberately not read here.

## Known-stale things a resumer will trip over

- `EXPERIMENT-REGISTRY.json` still reads `"status": "seeded-not-executed"`.
  KL-000 is now `adversarial-passed`. **Not updated deliberately**: the registry
  is a canonical record, and canonical registries are updated only in a separate
  promotion commit after the evidence satisfies the existing rules. It is not
  an oversight.
- `research/knowledge-ledger/README.md` still calls `reference-conformance-001`
  the current milestone. Still true — it remains a local conformance artifact,
  and KL-000 does not displace it as a *cross-system* claim, because KL-000 is
  not one.
- Eleven preregistrations remain schema v0.1 and cannot satisfy
  `RESEARCH-METHOD.md` however fully populated (`SCH-001`, `BL-009`).
