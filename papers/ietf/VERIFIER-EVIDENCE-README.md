# AgentProto verifier-evidence Internet-Draft package

This package prepares the reviewed individual Internet-Draft
`draft-he-agentproto-verifier-evidence-00` for a possible Datatracker upload.
It is **not submitted**, is not a working-group document, and does not claim
AgentProto adoption or reviewer endorsement.

The document proposes two distinct reporting obligations for agent-protocol
verifier results:

- EXR records whether a verifier has actually produced its rejecting outcome.
- CMP records the domain over which completeness is claimed and the basis for
  detecting material-party omission.

The included implementation-status section is deliberately narrow. It records
a bounded source replay, not a second implementation or conformance result.

## Build and check

From the repository root:

```text
make agentproto-draft
make agentproto-check
```

The targets use the pinned environment in `requirements-agentproto.txt` and
regenerate the text and HTML from the RFCXML source. The check also compares
the generated files, runs the package-contract tests, and scans for unresolved
placeholders.

Before any handoff, also run:

```text
make verify
```

## Review and submission records

- `VERIFIER-EVIDENCE-REVIEW-LEDGER.md` states what outside review did and did
  not establish, and itemizes the transparent post-review edits.
- `verifier-evidence-submission-manifest.json` binds the current source and
  renderings by byte count and SHA-256 digest.
- `VERIFIER-EVIDENCE-SUBMISSION-CHECKLIST.md` separates completed mechanical
  work from the decisions and confirmations that remain with the author.

Submission and mailing-list outreach are intentionally outside this package.
