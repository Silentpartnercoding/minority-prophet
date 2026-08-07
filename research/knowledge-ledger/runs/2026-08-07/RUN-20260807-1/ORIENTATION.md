# RUN-20260807-1 — Orientation record

UTC start: `2026-08-07T17:30:04Z`

## 1. Base commit selection

| Ref | Commit | Authoritative files + fixture (of 12) |
|---|---|---|
| `agent/knowledge-ledger-run-20260807-1` (HEAD, this run) | `887bd2f` | **12 / 12** |
| `agent/first-transmission` | `887bd2f` | 12 / 12 |
| `agent/master-loop-run-completion` | `d1e237d` | 12 / 12 |
| `github/main` | `335b34e` | **12 / 12** |
| `origin/main` | `88a3001` | 4 / 12 |

**Chosen base: `887bd2f`, tip of `agent/first-transmission`.**

Reason: it carries all eleven authoritative files plus
`interoperability/reference-receipt.json`, and it is the branch this worktree
was already created from, so the run does not begin by moving the tree it is
auditing. `agent/master-loop-run-completion` was an equally valid base by file
coverage; `887bd2f` was preferred only because the worktree already sat on it,
which keeps `git status --porcelain` empty at run start (verified: empty).

### Discrepancies against the prompt's stated starting conditions

The prompt instructed that these be verified rather than assumed. Three of its
claims are now out of date. None of them changed the run's scientific plan.

1. **"`github/main` carries 8 of the 11 authoritative files."** False as of this
   run. `github/main` has advanced to `335b34e` and carries **12 / 12**. The
   prompt's figure matched `7a56663` (PR #12), which was this worktree's stale
   remote-tracking ref before `git fetch github`. Recorded as `PROV-001`.
2. **"`origin/main` carries none."** False. `origin/main` (`88a3001`) carries 4
   of 12: `README.md`, `CANONICAL-RECORDS.md`, `EVIDENCE-ALIGNMENT.md`,
   `PROVENANCE-REQUIREMENTS.md`. It is still not a viable base.
3. **"neither `main` does [carry the program]."** No longer true for
   `github/main`. This invalidates the prompt's stated *reason* for basing the
   PR on `agent/first-transmission` — see §2.

## 2. The `887bd2f` / `335b34e` divergence

Confirmed by the operator mid-run and independently verified here.

```
git rev-list --left-right --count 335b34e...887bd2f
2	2
git merge-base 887bd2f 335b34e
1d1491e  Merge pull request #8 from .../agent/verifier-independence-invariant
```

Both sides advanced two commits past the common ancestor `1d1491e`:

| Side | Commits | Effect |
|---|---|---|
| base `887bd2f` | `0a35fe1` "Render the first transmission for human readers", `887bd2f` "Hold the human rendering to its own receipt" | **adds** `REFERENCE-RENDERING.md`, `render_transmission()` in `scripts/run_knowledge_transaction.py`, `tests/test_reference_rendering.py` |
| `github/main` `335b34e` | `c5497aa` "clarify decision-quality boundary", `335b34e` (merge of PR #16) | edits `README.md`, `RESEARCH-HYPOTHESES.md`, `app/globals.css`, `app/page.tsx`, `interoperability/README.md`, `tests/rendered-html.test.mjs` |

`git diff --stat 887bd2f 335b34e` touches 10 files. The reference-rendering work
exists **only** on the base; the decision-quality clarification exists **only**
on `github/main`.

Per the operator's instruction this divergence is recorded as constraint
`PROV-002` and is **not** rebased, squashed, or otherwise reconciled by this
run. Reconciling it is a separate scientific question and therefore a separate
PR, per the one-question-per-PR rule.

## 3. Publication blocker discovered during orientation

`agent/first-transmission` — the branch the prompt names as the PR base — **does
not exist on the `github` remote**:

```
git ls-remote --heads github refs/heads/agent/first-transmission   # no output
git ls-remote github | grep -c 887bd2f                             # 0
```

Neither the branch nor the base commit `887bd2f` is published. A draft PR
against `agent/first-transmission` therefore cannot be opened until that base
branch is pushed to `github` first. Recorded as `PROV-003`; the decision is
referred to the founder in `HANDOFF-v1.md` rather than taken unilaterally,
because publishing a base branch to a public repository is an outward-facing
act this run was not explicitly asked to perform.

The prompt's stated justification for avoiding `main` as the PR base ("a PR
based there would carry roughly twenty unrelated files") no longer holds:
`github/main` now carries the program, and a PR from this branch to
`github/main` would carry the two reference-rendering commits plus this run's
work — 10 pre-existing files of drift, not twenty. That is still a
one-question-per-PR violation, so the prompt's *conclusion* stands even though
its *reason* has expired.

## 4. Remote topology as verified

```
github  https://github.com/Silentpartnercoding/minority-prophet.git   (public GitHub)
origin  james@100.101.32.77:/Users/james/.../minority-prophet         (working copy over SSH)
```

Both are reachable. They are **not** interchangeable and every push command
emitted by this run names its remote explicitly.

A transient orientation error is recorded here for completeness: an early
`git config --get-regexp '^remote\.'` in a compound command returned only
`origin.*`, which led the agent to state that `github` was unconfigured. That
statement was wrong and was corrected within the same phase by
`git remote -v` and a successful `git ls-remote github`. No action was taken on
the incorrect reading.

## 5. Canonical checks reproduced before any change

Per master-loop step 1, all canonical checks were reproduced **before** any
behaviour was modified.

- `reference-conformance-001`: regenerated from committed inputs; receipt
  **byte-identical** to the committed `reference-receipt.json` under both
  `/Users/james/Development/.mp-runner-venv/bin/python` (3.14.6) and system
  `python3`; `REFERENCE-RENDERING.md` byte-identical.
- Committed receipt digest **verified in place**, not recomputed-and-compared:
  `verify_content_digest(committed) -> True`, and an independent recomputation
  that does not call the library helper agrees
  (`sha256:dede0197…c9e527`).
- Tamper detection: mutating `conclusion` and mutating `search.searched`
  each make `verify_content_digest` return `False`.
- `PYTHONPATH=. .../python -m pytest -q` -> **73 passed**, matching the
  prompt's last-verified state.

`reference-conformance-001` is a local conformance fixture. Reproducing it
establishes reproducibility, not truth, and it is not a cross-system result.

## 6. Earliest incomplete kernel

All twelve preregistrations are `"status": "incomplete-seed"`. Each carries 22
keys of which **14 are unpopulated**, identically across all twelve
experiments: **11 explicit nulls** —

`effectSize`, `failureCondition`, `frozenSeedsOrSplits`,
`invalidationCondition`, `population`, `protocolCommit`, `rootDefinition`,
`safetyBoundary`, `searchSpace`, `successCondition`, `uncertainty`

— plus **3 empty collections**: `artifacts`, `baselines`,
`secondaryEndpoints`.

The 11/3/14 split is stated exactly rather than approximated because an
approximate count of unpopulated preregistration fields is precisely the kind
of drift this program exists to catch: "about eleven" silently discarded the
three empty collections, which are unpopulated in substance even though they
are not `null` in JSON. Counts reported by this run are produced by
`scripts/audit_preregistrations.py`, not by inspection.

Every `STATUS.json` reads `state: seeded`, `nextGate: "complete and commit
preregistration"`.

**Earliest incomplete gate: KL-000.** Its own registry entry states that one
violation "blocks every downstream kernel", so it is a hard prerequisite for
KL-001..KL-011 and this run does not skip past it to a more impressive
demonstration.

## 7. Registry audit — see `REGISTRY-AUDIT.md`

Disagreements between `EXPERIMENT-REGISTRY.json`, `RESEARCH-METHOD.md`, and the
prompt's per-experiment directory requirement are recorded there and are **not**
silently repaired.
