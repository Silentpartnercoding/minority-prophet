# HANDOFF v1 — RUN-20260807-4 (final run of the program)

Everything needed to review, reproduce, deliver, or someday resume. No
hidden state.

## Where the work is

```
worktree   /Users/james/Development/minority-prophet-first-transmission
branch     agent/knowledge-ledger-run-20260807-1
base       ecb2b45  (RUN-20260807-3 close + R5.2 ratification)
head       the closing-packet commit carrying this file
PR branch  agent/kl-000-conformance @ 11eb204  (rebuilt this run; worktree
           /Users/james/Development/minority-prophet-kl000-pr; UNPUSHED)
window     2026-08-07T22:19:15Z -> END-UTC.txt
```

## Commits of this run

| SHA | What |
|---|---|
| `3fc619f` | run open: all eight IND-3 claims verified (R5.2 ablation reproduced exactly: 38,760 / 0 / C12-only); result-artifact header defect found; kernel audit clean |
| `897ec6d` | IND-20260807-3 evidence imported with provenance: both digests reproduce; mechanistic finding recorded |
| `7629d37` | final KL-000 record: I12 gate with both ablations, A1/A2 recorded undecided, Amendment 2, FINAL-RECORD.md |
| *(head)* | closing packet |

On the PR branch: 31 program commits cherry-picked onto `github/main`
(`335b34e`) plus the sidecar rebind commit → head `11eb204`. The previous
stale head `cc9635e` (run-1-era) is recoverable via reflog in the
`minority-prophet-kl000-pr` worktree.

## Registration chains — both SHA sets

| Registration | Run branch (original) | PR branch (cherry-picked) |
|---|---|---|
| v1.0.0 | `c977347…` | `9a1b5f5b1…` |
| v1.1.0 | `1a8256f…` | `7ddd5dd75…` |
| v1.2.0 | `7e9e55f…` | `379bd926e…` |

All six sidecar checks verified this run. The preregistration files are
byte-identical on both branches; only the commit SHAs differ, which is the
recorded, expected consequence of cherry-picking (run-1's M1 discussion).

## Test expectations — measured, not projected (M21)

| Tree | repo root | KL-000 |
|---|---|---|
| run branch | **74 passed** | **80 passed** |
| PR branch (main base) | **63 passed** | **80 passed** |

The 11-test difference is `tests/test_reference_rendering.py` (10) plus one
program test — they belong to the run branch's *base* (`887bd2f`,
first-transmission render), not to this program, and do not exist on
`github/main`. Run-1's HANDOFF projected 74 for the cherry-picked branch;
that projection was wrong (TEST-101). 63 is correct and was executed.

## To deliver the PR — owner's commands, nothing run

```bash
cd /Users/james/Development/minority-prophet-kl000-pr
git log --oneline github/main..HEAD | wc -l          # expect 32
PYTHONPATH=. python3 -m pytest -q                    # expect 63 passed
PYTHONPATH=. python3 -m pytest research/knowledge-ledger/experiments/KL-000/tests -q   # expect 80 passed

# The closing-packet commits made after the rebuild are not yet on this
# branch; bring them over first (provenance-only; the range form covers all
# of them, including the handoff-finalisation commit):
git cherry-pick 7629d37..agent/knowledge-ledger-run-20260807-1

git push github agent/kl-000-conformance
gh pr create --draft --repo Silentpartnercoding/minority-prophet \
  --base main --head agent/kl-000-conformance \
  --title "KL-000: cross-implementation conformance, with its limits measured" \
  --body-file research/knowledge-ledger/runs/2026-08-07/RUN-20260807-4/DRAFT-RUN-REPORT-v1.md
```

The PR body (the run report) carries the LEAK-101 qualification and the
unenforced-decision finding in its first screen, as instructed — they are in
the claim, not an appendix.

## Decisions that are yours

| # | Decision | Notes |
|---|---|---|
| 1 | Push and open the draft PR | commands above; everything local is ready and tested |
| 2 | **Schedule I12 / v1.3.0** | the sole committed gate (STATUS `committedGates`), evidence 22,440 / 38,760 / 0 / 0, exact pass condition attached. The program's state cannot honestly advance without it |
| 3 | **Decide A2** (presence and coverage) | 19,152 worlds, 17.3% of receipts, both readings recorded in STATUS `permanentLimits`. The program did not reach this decision and did not take it at close |
| 4 | Decide A1 (absence with empty evidence), the margin rename (`rootCountGap` / `majoritySide`), and `conversionsToReverse` at the empty ledger | all digest-moving if taken; belong in one version together |
| 5 | Any future commission: withhold the conclusion distribution (LEAK-102/H3), screen every shipped file, and — the one condition never met in three IND runs — a machine that does not hold the reference | the implementer's own §7 item 8: three runs of self-reported abstention is not one run of enforced abstention |
| 6 | Promotion | EXPERIMENT-REGISTRY.json still reads `seeded-not-executed` for KL-000; CANONICAL-RECORDS.md, PUBLIC-CLAIMS.md and the paper untouched by all four runs. Promotion is a separate commit after your review, as it always was |

## How anyone resumes

1. Read `KL-000/FINAL-RECORD.md` first — it is the program's consolidated
   claim at strength. Then this packet's `DRAFT-RUN-REPORT-v1.md`,
   `CONSTRAINTS-v1.json`, `KERNEL-STATUS-SNAPSHOT-v1.json`.
2. The claim discipline is in STATUS `claimAllowed`/`claimNotAllowed` and is
   final: conformance by object (M17), qualified by LEAK-101, capped by
   SPEC-112. **"Verified" is not licensed. The first-transaction gate is NOT
   REACHED.**
3. Do not modify anything under `kl000-independent-spec/`, `kl000-v110-spec/`
   or `kl000-v120-spec/`. The IND-3 result's header metadata is known-stale
   (ART-101); identity comes from `FINDINGS-v120.md` and the re-verification.
4. Eleven kernels are seeded with exact next gates (audited this run, none
   advanced). KL-011's prerequisites are substantively met and nothing about
   it is registered or executed.
5. The v1.2.0 preregistration's prose retains two known inert errors ("ten
   top-level members", "all nine non-contentDigest members") preserved under
   the immutability rule and documented in the protocol's amendment log.
