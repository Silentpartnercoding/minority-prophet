# RUN-20260807-1 — Orientation record

UTC start: `2026-08-07T17:30:04Z`

> **CORRECTION NOTICE — appended after operator verification, original text
> unaltered below.** Two statements in §1 and one in §4 rest on measurements
> that were taken against a deleted remote's surviving cache. The corrected
> account is in **§8**, appended at the end of this file. The original text is
> deliberately preserved in place: it is the record of what was believed at
> decision time, and the base commit was chosen under it. Rewriting it would
> destroy the evidence that a correction was needed. See constraints `PROV-001`
> (severity raised) and `PROV-005` (new).
>
> Superseded claims carry an inline **ᶜ⁸** marker, so a quoted line or a link
> landing mid-document arrives with its own correction attached rather than
> relying on the reader having seen this notice. The marker is the only
> addition to those lines; their wording is unchanged.

## 1. Base commit selection

| Ref | Commit | Authoritative files + fixture (of 12) |
|---|---|---|
| `agent/knowledge-ledger-run-20260807-1` (HEAD, this run) | `887bd2f` | **12 / 12** |
| `agent/first-transmission` | `887bd2f` | 12 / 12 |
| `agent/master-loop-run-completion` | `d1e237d` | 12 / 12 |
| `github/main` | `335b34e` | **12 / 12** ᶜ⁸ |
| `origin/main` | `88a3001` | 4 / 12 |

ᶜ⁸ This row was measured **after** the operator restored the deleted `github`
remote, so the figure is correct — but every `github/*` measurement taken
earlier in this run came from a surviving cache of a deleted remote and was
silently two commits stale. See §8.

**Chosen base: `887bd2f`, tip of `agent/first-transmission`.** ᶜ⁸

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
   remote-tracking ref before `git fetch github`. ᶜ⁸ Recorded as `PROV-001`.

   ᶜ⁸ **The stated cause is wrong.** The ref was not merely unfetched — the
   `github` remote had been **deleted** from the clone while its tracking refs
   survived, so no fetch would have refreshed it and no error was raised. See
   §8 and constraint `PROV-005`.
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
origin  <user>@<host>:$HOME/.../minority-prophet         (working copy over SSH)
```

Both are reachable. They are **not** interchangeable and every push command
emitted by this run names its remote explicitly.

A transient orientation error is recorded here for completeness: an early
`git config --get-regexp '^remote\.'` in a compound command returned only
`origin.*`, which led the agent to state that `github` was unconfigured. That
statement was wrong and was corrected within the same phase by
`git remote -v` and a successful `git ls-remote github`. No action was taken on
the incorrect reading. ᶜ⁸

> ᶜ⁸ **This entire paragraph is the error it claims to record.** The first
> reading was *correct*: `github` genuinely was not configured at that moment.
> The operator added the remote between the two observations. The agent saw a
> real state change and misfiled it as its own measurement error. See §8 and
> constraint `PROV-006`.

## 5. Canonical checks reproduced before any change

Per master-loop step 1, all canonical checks were reproduced **before** any
behaviour was modified.

- `reference-conformance-001`: regenerated from committed inputs; receipt
  **byte-identical** to the committed `reference-receipt.json` under both
  `$HOME/Development/.mp-runner-venv/bin/python` (3.14.6) and system
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

---

## 8. Correction: the `github` remote was deleted, not misread

Appended after the operator independently verified the base-selection question
and supplied the mechanism. Sections 1–7 above are unaltered.

### What actually happened

The `github` remote had been **deleted from this clone**, while five of its
remote-tracking refs under `refs/remotes/github/*` survived. A deleted remote
with surviving refs is not a broken state that announces itself:

- `git remote -v` correctly listed only `origin`;
- `git branch -r` still listed `github/main` and four others;
- `github/main` still **resolved cleanly**, to `7a56663` — two commits stale;
- a file-presence check against it returned **8 / 11** with no error, no
  warning, and no indication that the ref was a cache rather than a remote.

The operator's `8 of 11` figure in the run prompt was measured that way. It was
a faithful measurement **of a cache**, reported as a measurement of the remote.

### Correction to §4 of this document

§4 records a "transient orientation error" in which the agent stated that
`github` was unconfigured and then, on observing `git remote -v` list it,
concluded the earlier statement had been wrong.

**That self-correction was itself wrong.** The first observation was accurate:
at the time it was taken, `github` genuinely was not a configured remote. The
operator ran `git remote add github` and `git fetch --prune` between the two
observations. The world changed; the measurement did not err.

The agent saw `X`, then `not X`, and concluded it had mismeasured — when the
correct inference was that the state had changed underneath it. Nothing in a
single clone's git output distinguishes those two cases after the fact. This is
recorded because attributing a genuine state change to one's own measurement
error is a failure mode that *silently discards a real event*, and it is
strictly harder to detect than an ordinary mistake: the agent's second reading
agreed with reality, so the incident looked resolved.

### Corrected measurement

Taken by the operator after `git remote add github` + `git fetch --prune`:

| Ref | Commit | Authoritative files |
|---|---|---|
| `github/main` | `335b34e` | **11 / 11** |
| `origin/main` | `88a3001` | 4 / 11 |

Base `887bd2f` is **not** an ancestor of `github/main`; the two diverge by two
commits each way. This agrees with the independent measurement in §2, which was
taken after the remote was restored and is therefore unaffected.

### Why the base is being kept

Rebasing onto `github/main` is **declined**. The reasoning:

1. `ORIENTATION.md`, `environment-lock.txt`, and `git-status-before.txt` are
   already committed against `887bd2f`. Rebasing would silently invalidate a
   committed provenance record in order to repair a base that does not affect
   KL-000 at all.
2. KL-000 tests `knowledge_ledger/transaction.py`, which is **byte-identical**
   on both sides of the divergence. The evaluator hash frozen in the
   preregistration is valid against either base.
3. The divergence is already recorded as `PROV-002`. A recorded divergence is a
   finding; a rebased-away divergence is a deleted one.

The base-selection *rationale* in §1 rested on a false premise — that no `main`
carried the program. The premise is now known false and the **decision is
unchanged**, for the independent reasons above. A right decision reached partly
through a wrong premise is still worth flagging, because the premise could have
justified a wrong decision just as easily.

### `FIRST-TRANSMISSION.md` has never existed

Verified independently on both refs:

```
git ls-tree -r --name-only 887bd2f | grep -i 'first.transmission'   # no match
git ls-tree -r --name-only 335b34e | grep -i 'first.transmission'   # no match
```

The first-transmission render (`0a35fe1`) and its correction (`887bd2f`) exist
only on this run's unmerged base. What they produced is
`REFERENCE-RENDERING.md`, whose first line reads `# Reference Conformance
Rendering` — correctly titled as the reference rendering it is. No artifact in
this repository claims the First Transmission title, and this run creates none.

### Governing prompt for this run

A corrected prompt exists as **v3**,
`sha256:4bf92221f371cf55b67112f885d4c0b2496843a0ba19acc4d403d25fd117173f`,
recorded here on the operator's statement. It was **not read** by this run and
is not present in the operator's `run-inputs/` directory as seen from this
worktree.

**v2 remains authoritative for RUN-20260807-1**, as captured byte-exactly at
`inputs/PROMPT.txt`, `sha256:729bfb70…5ccb`. v3 exists so the remote-cache error
does not propagate to the next run. Re-reading instructions from a prompt
revised mid-run would make this run's governing instruction unreconstructible
after the fact.
