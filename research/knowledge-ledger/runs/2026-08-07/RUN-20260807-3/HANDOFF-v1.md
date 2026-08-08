# HANDOFF v1 — RUN-20260807-3

Everything needed to review, reproduce, or resume. No hidden state.

## Where the work is

```
worktree  $HOME/Development/minority-prophet-first-transmission
branch    agent/knowledge-ledger-run-20260807-1   (continued)
base      0b6614f  (RUN-20260807-2's closing commit)
head      the closing-packet commit carrying this file
window    2026-08-07T20:48:15Z -> END-UTC.txt
```

## Commits, in order

| SHA | What |
|---|---|
| `2f81b9e` | run open: all seven IND-20260807-2 claims verified; LEAK-101 traced to the registration's own prediction table |
| `d51ead6` | IND-20260807-2 evidence imported by copy with provenance + conformance record |
| `7e9e55f` | **registration commit** — protocol v1.2.0 (R5.1 receipt object, R5.2 absolute margin), C11 re-pin + C12 |
| `461bfbf` | Amendment 1 (member-count typo, pre-execution; preregistration untouched) + v1.2.0 sidecar |
| `bc67075` | execution support (schema/reason/limits + canonical-string comparison) + 12 permanent tests |
| `a7f4d37` | **result commit** — v1.2.0 confirmatory, `passed`, nothing moved: counts, conclusions, or bytes |
| `d29904b` | STATUS: conclusion-function conformance established; next gate IND-20260807-3 |
| *(head)* | closing packet |

No commit amended, no history rewritten. All three registration chains verify:

```bash
P=research/knowledge-ledger/experiments/KL-000
for v in "" "-v1.1.0" "-v1.2.0"; do
  test "$(git log -1 --format=%H -- $P/preregistration$v.json)" = "$(cat $P/PROTOCOL-COMMIT$v.txt)" \
    && echo "chain$v intact"
done
```

## Reproduce the science

```bash
cd research/knowledge-ledger/experiments/KL-000
python3 src/run_kl000.py --phase all --preregistration preregistration-v1.2.0.json \
    --out results --label reproduction-v1.2.0
```

Expected values in `REPRODUCE-v1.2.0.md`; v1.0.0 and v1.1.0 paths unchanged
and still reproduce. Tests: 74 repo, 80 KL-000.

## Artifact hashes

```
inputs/PROMPT.txt (agent transcription, UNVERIFIED)  sha256:78157a926dea5b6fad9a1055044c283d205f6fd882364fa523a9ea5149064eee
KL-000/preregistration-v1.2.0.json                   sha256:3e9d117e04740947763578a60b55ab868016ff951a297c6ad9fc27eb36bfe215
KL-000/PROTOCOL-v1.2.0.md (post-Amendment-1)         sha256:09a7130bdd8f0ce0801db6ea20a9cf9ca6ca214a449dc18b1bed0c7ce2236e0d
KL-000/fixtures/v1.2.0/c11-canonical-digest.json     sha256:992e0c12aadb25baa2bd6d49b0b93cc7f30aff0c3944ec280ca1c215161831d5
KL-000/fixtures/v1.2.0/c12-margin-sign.json          sha256:d69c9e2402cadc4cc6ed168fe0a85b7eb5d258d173fa6453276c6731592e491d
KL-000/results/kl000-confirmatory-v1.2.0.json        sha256:0ce125057080cfb90f04f1772b79e9b89ffe828e0d580070941f1acb42cd36e9
evaluator under test (unchanged since v1.0.0)        sha256:15dfd50051ef5da3db13d8e591f58537325ee50aa4e3573914f86e4ff3a3e21f
imported: FINDINGS-v110.md                           sha256:c0aa3d62089331065c0a6af9cc626eac27342afbc912717e96c02263c86802e5
imported: kl000-independent-result-v110.json         sha256:465032f5fa34a2b5eff5693564f5c9c87a074c3a8980869251e42788a9512c79
package: kl000-v110-spec/PROTOCOL.md                 sha256:2ce181f3… (== registered PROTOCOL-v1.1.0.md — the LEAK-101 vector)
package: kl000-v110-spec/preregistration.json        sha256:6a95d024… (redacted variant)
```

## The draft PR — same fork as prior runs

**Nothing pushed, no PR opened.** PR body: `DRAFT-RUN-REPORT-v1.md`. The
run-1 delivery routes still apply; the cherry-pick list now spans three runs
of commits on this branch, and sidecar rebinding after any cherry-pick
applies to **all three** `PROTOCOL-COMMIT*.txt` files.

## Unresolved approvals

| # | Decision | Blocking |
|---|---|---|
| 1 | Publish base branch or cherry-pick onto `github/main` (unchanged from run 1) | the draft PR |
| 2 | **Commission IND-20260807-3** under the registered packaging requirements (BL-020; manifest, per-file screening in both number formats, resolvable paths, ideally a reference-free machine) | KL-000's next gate, KL-011, and the `verified-independent` promotion decision |
| 3 | v1.3.0 bundle (BL-021) — **after** #2 returns. Its I12 component is a **committed gate** (owner direction at this run's close; evidence in STATUS `committedGates`), not an optional item | specification loop |
| 4 | ~~Ratify R5.2 (margin absolute)~~ **RESOLVED post-close: owner ratified absolute** (`RATIFICATION-R5.2.md`). The IND-20260807-3 target is fully owner-endorsed and frozen | — |
| 5 | Confirm nothing is promoted yet | — |

Nothing in `EXPERIMENT-REGISTRY.json`, `CANONICAL-RECORDS.md`,
`PUBLIC-CLAIMS.md`, or the paper was touched.

## How another agent resumes

1. Read `DRAFT-RUN-REPORT-v1.md`, `CONSTRAINTS-v1.json`,
   `KERNEL-STATUS-SNAPSHOT-v1.json`; `NEXT-RUN-PROPOSAL-v1.md` is the next
   run.
2. Do **not** re-run confirmatories hoping for different numbers; do not
   execute IND-20260807-3 yourself; do not modify anything under
   `kl000-independent-spec/` or `kl000-v110-spec/`.
3. Do **not** claim "verified" or "verified-independent". Established so far
   (M17 discipline — name the object): evaluator partitioning and the
   complete conclusion function, across two implementations, qualified by
   LEAK-101. Untested: receipt bytes (I4/I6) — that is IND-20260807-3's
   question. Never comparable: randomized counts (F11).
4. v1.2.0 is frozen at `7e9e55f` (+ logged Amendment 1). Further repairs are
   v1.3.0, after the commission returns.
5. When preparing the IND-20260807-3 package, follow the registered
   packaging requirements (v1.2.0 `expectedIdenticalToRun1` note, STATUS
   nextGate, BL-022). The prediction table must not ship.

## Known-stale things a resumer will trip over

- `EXPERIMENT-REGISTRY.json` still reads `seeded-not-executed` for KL-000 —
  deliberate; promotion is a separate owner-reviewed commit.
- The v1.2.0 preregistration's `repairs[0].statement` prose says "ten
  top-level members" over the authoritative nine-entry `memberList`; the
  registration commit message repeats it. Both deliberate survivals of
  Amendment 1's discipline (the prereg is never edited; the error is
  documented in the protocol's amendment log).
- NAM-101 (baseline id spellings) is still open; the id map is now recorded
  in the v1.2.0 preregistration's `baselineIdNote`, and the comparison logs
  carry it inline.
- `kl000-independent-spec/` top level is still the v1.0.0 package — correct
  and deliberate (the operator delivered v1.1.0 as `kl000-v110-spec/`);
  don't "fix" it.
