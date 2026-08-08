# HANDOFF v1 — RUN-20260807-5

The gate run: I12 registered, implemented, and passed at its exact
registered surfaces. **The program is closed again, with no committed gate
outstanding.**

## Where the work is

```
worktree   $HOME/Development/minority-prophet-first-transmission
branch     agent/knowledge-ledger-run-20260807-1
base       ffbdb60  (RUN-20260807-4's final commit)
head       see DELIVERY-RECORD.md (post-close addendum; the closing sequence
           below explains why the head is recorded there)
PR branch  agent/kl-000-conformance — rebuilt AFTER this packet's closing
           commits so the range covers them; head + verification in
           DELIVERY-RECORD.md. UNPUSHED.
window     2026-08-07T22:45:21Z -> END-UTC.txt
```

## Commits of this run

| SHA | What |
|---|---|
| `29cb63f` | run open: deliberate reopening for the committed gate; design decisions stated |
| `08f8703` | **registration commit** — protocol v1.3.0, I12, the two registered ablations |
| `dedadbd` | implementation: I12 in the checker, ablation module, runner phase, 8 tests |
| `27e745c` | **result commit** — v1.3.0 confirmatory passed; ablations at exactly 22,440 / 38,760 |
| `ab22789` | STATUS gate paid; FINAL-RECORD appended; A1/A2 stay open |
| *(then)* | closing packet, END-UTC, delivery record — see DELIVERY-RECORD.md |

## Registration chains

All four verified this run on the run branch; PR-branch SHAs in
DELIVERY-RECORD.md after the rebuild.

```bash
P=research/knowledge-ledger/experiments/KL-000
for v in "" "-v1.1.0" "-v1.2.0" "-v1.3.0"; do
  test "$(git log -1 --format=%H -- $P/preregistration$v.json)" = "$(cat $P/PROTOCOL-COMMIT$v.txt)" \
    && echo "chain$v intact"
done
```

## Test expectations — measured (M21)

Run branch: **74 root + 88 KL-000**. PR branch (main base): **63 root + 88
KL-000** (the 11-test root difference is the base-only render suite,
TEST-101).

## To deliver — the owner's command, nothing run

The PR branch is rebuilt from `github/main` with the range
`887bd2f..agent/knowledge-ledger-run-20260807-1`, covering **every** program
commit including this run's closing commits, with all four sidecars rebound
and tests run (verification in DELIVERY-RECORD.md). What remains is
exactly:

```bash
cd $HOME/Development/minority-prophet-kl000-pr
git push github agent/kl-000-conformance
gh pr create --draft --repo Silentpartnercoding/minority-prophet \
  --base main --head agent/kl-000-conformance \
  --title "KL-000: cross-implementation conformance, with its limits measured" \
  --body-file research/knowledge-ledger/runs/2026-08-07/RUN-20260807-5/DRAFT-RUN-REPORT-v1.md
```

The PR body carries, in the body itself: the by-object claim strengths (full
enumeration for the conclusion function; two pinned receipts for the
canonical form), the LEAK-101 qualification with its origin, I12's result
with the ablation numbers, A1/A2 open with world counts, and the
NOT-REACHED first-transaction gate with the eleven seeded kernels.
**Publication requires your review of that exact public text.**

## Decisions that are yours

| # | Decision |
|---|---|
| 1 | Push and open the draft PR (above) |
| 2 | Decide A2 (19,152 worlds) and A1 (4 worlds) — still open by instruction |
| 3 | `verified-independent` promotion — I12 removed the enforcement objection; the independent implementation has not run against v1.3.0 (its checker is its own; its v1.2.0 conformance evidence is undisturbed) |
| 4 | Any future commission (IND v1.3.0 re-run; fourth implementation on a reference-free machine) under LEAK-101/LEAK-102 packaging rules |
| 5 | The digest-moving bundle (margin rename / `majoritySide`, F4) if ever wanted |
| 6 | Promotion into canonical records — untouched by all five runs |

## Known-stale items

- REPRODUCE.md's whole-document equality one-liner is stale for fresh
  reproductions (VER-101; the checker now carries I12 and baseline reports
  two new fields). Field-level checks in the versioned REPRODUCE documents
  are operative. The registered v1.0.0 document is not edited.
- `EXPERIMENT-REGISTRY.json` still reads `seeded-not-executed` for KL-000 —
  deliberate, as in every prior run.
- The v1.2.0 preregistration's two inert prose miscounts remain preserved
  and documented.

## How anyone resumes

Read `KL-000/FINAL-RECORD.md` (including its RUN-20260807-5 addendum),
then this packet. The claim discipline in STATUS is final. Do not modify
anything under the three external `kl000-*` directories. **The
first-transaction gate is NOT REACHED; eleven kernels remain seeded; the
program is closed with no committed gate outstanding.**
