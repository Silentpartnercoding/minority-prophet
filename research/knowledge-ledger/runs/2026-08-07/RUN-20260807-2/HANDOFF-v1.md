# HANDOFF v1 — RUN-20260807-2

Everything needed to review, reproduce, or resume. No hidden state.

## Where the work is

```
worktree  $HOME/Development/minority-prophet-first-transmission
branch    agent/knowledge-ledger-run-20260807-1   (continued from RUN-20260807-1)
base      cc1d494  (RUN-20260807-1's closing commit)
head      the closing-packet commit carrying this file
window    2026-08-07T19:49:58Z -> END-UTC.txt
```

Worktree clean at start (`git-status-before.txt` holds only this run
directory's own creation) and at end (`git-status-after.txt`).

## Commits, in order

| SHA | What |
|---|---|
| `544ea1e` | run open: orientation, prompt capture (agent-transcription, marked unverified), verification of the reimplementation and operator-note claims |
| `226a9f2` | independent-implementation evidence imported by copy, with provenance + comparison record |
| `1a8256f` | **registration commit** — protocol v1.1.0, preregistration, fixture C11 (v1.0.0 untouched) |
| `cc18ce6` | execution support: `--preregistration`, digest-pinned fixtures, I11/R2 admissibility path, 14 permanent tests, v1.1.0 sidecar |
| `ddf4025` | **result commit** — v1.1.0 confirmatory, `passed`, every number identical to RUN-20260807-1 |
| `a477a07` | KL-000 STATUS: next gate = independent re-run against v1.1.0 |
| *(head)* | closing packet |

No commit was amended; no history was rewritten (M6 discipline held).

## Reproduce the science

```bash
cd research/knowledge-ledger/experiments/KL-000
python3 src/run_kl000.py --phase all --preregistration preregistration-v1.1.0.json \
    --out results --label reproduction-v1.1.0
```

~90 s, stdlib only, no network. Expected values and the comparison snippet are
in `REPRODUCE-v1.1.0.md`; the v1.0.0 path (`REPRODUCE.md`, no
`--preregistration` flag) is unchanged and still reproduces.

Registration chains (both must print their confirmation):

```bash
P=research/knowledge-ledger/experiments/KL-000
test "$(git log -1 --format=%H -- $P/preregistration.json)"        = "$(cat $P/PROTOCOL-COMMIT.txt)"        && echo "v1.0.0 chain intact"
test "$(git log -1 --format=%H -- $P/preregistration-v1.1.0.json)" = "$(cat $P/PROTOCOL-COMMIT-v1.1.0.txt)" && echo "v1.1.0 chain intact"
```

## Artifact hashes

```
inputs/PROMPT.txt (agent transcription, UNVERIFIED)  sha256:6a0e1945d9eb78ef8a24951a5eddc676ee384def60e99d645a17a11a881f08f7
KL-000/preregistration-v1.1.0.json                   sha256:e9458f71e6ae9f5f3cf4ea64afe2b225f650e526915bd5f5e54791b4c7570bbf
KL-000/PROTOCOL-v1.1.0.md                            sha256:2ce181f3894d284cba9ecd4edf8897da0c767d4aa49b75473c80a2067390075c
KL-000/fixtures/v1.1.0/c11-canonical-digest.json     sha256:b598152908e4e75f3ff1f48af1d14e9f3345647e480cc1cf4f12094b3d6aab3f
KL-000/results/kl000-confirmatory-v1.1.0.json        sha256:cf39d579f06a48e71bbaba195d48223dc81699b66e7ab532a129a0faa2a1c048
evaluator under test (unchanged from v1.0.0)         sha256:15dfd50051ef5da3db13d8e591f58537325ee50aa4e3573914f86e4ff3a3e21f
imported: impl-rs FINDINGS.md                        sha256:af6b38376e497c22028b53da21272a28e0271013dbc783e6443c352dffe699ad
imported: impl-rs kl000-independent-result.json      sha256:c271443fedee400b9db6d357a3d65f9f53b4591b7377f29ae90390f2ef7e2f4e
```

## The draft PR — needs your decision, same fork in the road as run 1

**No PR has been opened and nothing has been pushed** (as instructed). The
PR body is `DRAFT-RUN-REPORT-v1.md`. RUN-20260807-1's two delivery routes
(HANDOFF-v1 there, "The draft PR" section) still apply, now with eight more
commits on the same branch; run 1's cherry-pick list extends to include
`544ea1e 226a9f2 1a8256f cc18ce6 ddf4025 a477a07` + the packet commit, and
the sidecar-rebinding step applies to **both** `PROTOCOL-COMMIT.txt` and
`PROTOCOL-COMMIT-v1.1.0.txt` after any cherry-pick. Expect 74 repo tests and
68 KL-000 tests.

## Unresolved approvals

| # | Decision | Blocking |
|---|---|---|
| 1 | Publish base branch, or cherry-pick onto `github/main`? (unchanged from run 1) | the draft PR |
| 2 | **Commission the independent re-run against v1.1.0** (BL-013): clean machine, artifacts-as-roles package | KL-000's next gate and KL-011 |
| 3 | v1.2.0 repair bundle (BL-014..BL-018) — **sequenced after #2**; the commission target must not move | specification loop |
| 4 | Owner decisions embedded in future repairs: margin sign, empty-ledger `conversionsToReverse` (F4/F5) | BL-015 |
| 5 | Confirm nothing is promoted yet | — |

Nothing in `EXPERIMENT-REGISTRY.json`, `CANONICAL-RECORDS.md`,
`PUBLIC-CLAIMS.md`, or the paper was touched.

## How another agent resumes

1. Read `DRAFT-RUN-REPORT-v1.md`, then `CONSTRAINTS-v1.json`, then
   `KERNEL-STATUS-SNAPSHOT-v1.json`; `NEXT-RUN-PROPOSAL-v1.md` is the next
   run.
2. Do **not** re-run either confirmatory hoping for different numbers; both
   are deterministic and re-running to search for a preferred answer is
   forbidden.
3. Do **not** execute the independent implementation or modify anything under
   `$HOME/Development/kl000-independent-spec/` — its untouched state
   is the evidence. In-repo copies with digests live in
   `KL-000/results/independent/`.
4. Do **not** claim "verified", "verified-independent", First Transmission,
   or Candidate First Transmission. None is earned. The two implementations
   demonstrably disagreed under v1.0.0 and their v1.1.0 agreement is
   untested.
5. v1.1.0 is frozen at `1a8256f`. If you believe a fifth repair is needed,
   that is v1.2.0, a new registration — after the commission returns.

## Known-stale things a resumer will trip over

- `EXPERIMENT-REGISTRY.json` still reads `"status": "seeded-not-executed"`
  for KL-000 — deliberate, promotion is a separate owner-reviewed commit
  (unchanged from run 1).
- `REPRODUCE.md`'s expected-values tables still describe the fixture phase as
  ten controls; true under the default v1.0.0 invocation it documents. The
  v1.1.0 invocation is documented in `REPRODUCE-v1.1.0.md`.
- The registered baseline ids and the runner's report keys differ in spelling
  (NAM-101); any machine comparison needs the id map shown in
  `logs/v110-vs-run1-comparison.txt`.
- RUN-20260807-1's `NEXT-RUN-PROPOSAL-v1.md` proposed diffing both evaluators
  over a shared frozen world stream; the commission that actually ran
  compared result documents instead (world streams were independently
  derived and matched by count and decomposition). The world-by-world diff
  remains available as extra assurance if the owner wants it — the
  independent implementation's `worldStreamHash` makes it cheap to arrange
  in the v1.1.0 re-run.
