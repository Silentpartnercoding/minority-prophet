# AgentProto Datatracker Submission Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish the reviewed verifier-evidence package under the confirmed author identity, upload its RFCXML as an individual Internet-Draft, and prepare a narrow AgentProto introduction without claiming working-group adoption.

**Architecture:** Treat the RFCXML as the source of truth, regenerate the text and HTML deterministically, and bind all three files in the submission manifest. Keep Git publication, Datatracker upload, email confirmation, and later working-group introduction as separate state transitions with explicit identity checks.

**Tech Stack:** RFCXML v3, `xml2rfc` 3.34.1, pytest, Git/GitHub, IETF Datatracker.

**Spec:** `papers/ietf/VERIFIER-EVIDENCE-SUBMISSION-CHECKLIST.md`

## Global Constraints

- Public author identity is `James Siyuan He`, `Independent`, `jsiyuanhe@gmail.com`.
- Document remains an IETF individual submission with `consensus="false"`.
- Upload does not imply AgentProto or AUDIT adoption.
- The bounded source replay is not a second implementation or a conformance result.
- Exact sender/account identity must be verified before any submission or external message.
- No AgentProto mailing-list or GitHub introduction is sent without a separate reviewed draft.

## Review Focus

- XML, text, HTML, and manifest could drift after the author-name edit; deterministic regeneration and hash tests must fail closed.
- Datatracker could be authenticated under the wrong account; verify the registered email before upload.
- The submission form could frame the draft as a working-group document; preserve individual-submission status.
- The IPR answer could exceed the author's knowledge; record only the author's confirmed good-faith answer.
- A later introduction could overclaim reviewer endorsement or adoption; keep it scoped to the open questions and runnable evidence.

---

### Task 1: Bind the confirmed author identity

**Files:**
- Modify: `tests/test_agentproto_verifier_evidence_draft.py`
- Modify: `papers/ietf/draft-he-agentproto-verifier-evidence-00.xml`
- Modify: `papers/ietf/draft-he-agentproto-verifier-evidence-00.txt`
- Modify: `papers/ietf/draft-he-agentproto-verifier-evidence-00.html`
- Modify: `papers/ietf/verifier-evidence-submission-manifest.json`
- Modify: `papers/ietf/VERIFIER-EVIDENCE-SUBMISSION-CHECKLIST.md`

**Interfaces:**
- Consumes: the user's confirmed full name, independent affiliation, email, and completed full-paper review.
- Produces: a deterministic, hash-bound submission package bearing the confirmed identity.

- [ ] **Step 1: Add a failing author-metadata test**

Assert that the RFCXML author has `fullname="James Siyuan He"`, `initials="J. S."`, `surname="He"`, organization `Independent`, and email `jsiyuanhe@gmail.com`.

- [ ] **Step 2: Run the focused test and verify the old `J. S. He` value fails**

Run: `PYTHONPATH=. .venv-agentproto/bin/python -m pytest -q tests/test_agentproto_verifier_evidence_draft.py`
Expected: FAIL on the full-name assertion.

- [ ] **Step 3: Update the RFCXML source and author checklist**

Set the full name to `James Siyuan He`; record the user's completed rendered-paper review and confirmed good-faith IPR answer while leaving upload and email-confirmation items open.

- [ ] **Step 4: Regenerate the renderings and update manifest byte counts and SHA-256 values**

Run: `make agentproto-draft`, then update the three manifest records from the generated files.

- [ ] **Step 5: Verify the focused package and repository**

Run: `make agentproto-check && make verify`
Expected: all commands exit 0 with no package drift or failing tests.

- [ ] **Step 6: Commit the author-confirmed package**

Commit the plan, test, source, regenerated renderings, checklist, and manifest with a factual submission-preparation message.

### Task 2: Publish the prepared source to GitHub

**Files:**
- No additional repository files.

**Interfaces:**
- Consumes: Task 1's verified commit plus the three previously prepared local commits.
- Produces: `origin/main` at the verified local commit.

- [ ] **Step 1: Recheck branch, remote, clean status, and ahead/behind count**

Run: `git status --short --branch && git remote -v && git log --oneline origin/main..main`
Expected: branch `main`, intended `Silentpartnercoding/minority-prophet` remote, clean worktree, and only reviewed local commits ahead.

- [ ] **Step 2: Push the explicitly authorized main branch**

Run: `git push origin main`
Expected: remote advances to the verified local commit.

- [ ] **Step 3: Verify the remote ref**

Run: `git ls-remote origin refs/heads/main`
Expected: remote SHA equals local `HEAD`.

### Task 3: Upload the individual Internet-Draft

**Files:**
- Upload: `papers/ietf/draft-he-agentproto-verifier-evidence-00.xml`

**Interfaces:**
- Consumes: Task 2's public source and the user's Datatracker account.
- Produces: a pending Datatracker submission and confirmation email, or a precise authentication/form blocker.

- [ ] **Step 1: Reconcile the submission in Master Relationships and verify the authenticated Datatracker identity**

Record the pre-contact check and verify the account's registered email is `jsiyuanhe@gmail.com`; do not substitute another identity.

- [ ] **Step 2: Upload the verified RFCXML as an individual submission**

Use `https://datatracker.ietf.org/submit/`; preserve the document name, author block, Informational intent, and non-working-group status.

- [ ] **Step 3: Answer the IPR prompt with the author's confirmed good-faith answer**

State that the author is not aware of undisclosed relevant intellectual property; do not convert that into a legal guarantee.

- [ ] **Step 4: Stop at the confirmation email if owner action is required**

Report the exact destination address and requested action without handling credentials or inventing completion.

### Task 4: Prepare the AgentProto introduction path

**Files:**
- No external message is sent in this task.

**Interfaces:**
- Consumes: the permanent Datatracker URL from Task 3.
- Produces: a short introduction draft tied to existing AgentProto questions and implementation evidence.

- [ ] **Step 1: Select the existing technical thread instead of opening with a generic announcement**

Introduce the draft as a proposed answer to the verifier exercise/completeness questions already raised around negative tests, omission detection, and same-party evidence.

- [ ] **Step 2: Draft a three-part message for owner review**

State: what the draft proposes (EXR and CMP), what evidence exists (negative fixtures and bounded replay), and what concrete feedback is requested (requirement placement, terminology, and whether to incorporate the obligations into an existing WG draft).

- [ ] **Step 3: Keep adoption as a later group decision**

Do not ask readers to endorse the whole research programme; ask whether the two narrow requirements solve a real gap and where they belong.
