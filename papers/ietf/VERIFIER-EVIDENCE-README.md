# AgentProto verifier-evidence Internet-Draft package

This package contains the source and generated renderings for individual
Internet-Draft revision `draft-he-agentproto-verifier-evidence-01`. Revision
`-01` was submitted and confirmed on October 18, 2026, following revision
`-00` on October 17, 2026:

<https://datatracker.ietf.org/doc/draft-he-agentproto-verifier-evidence/>

It is not a working-group document and does not claim AgentProto adoption or
reviewer endorsement.

The document proposes two distinct reporting obligations for agent-protocol
verifier results:

- EXR records whether a verifier has actually reached each declared rejecting
  or unverifiable path, the rule or condition reached, and whether an absent
  result is reachable-unexercised or shadowed-unreachable.
- CMP records the domain over which completeness is claimed and the basis for
  detecting material-party omission.

The implementation-status section distinguishes a bounded source replay, an
externally authored reader, a separately written reader under the author's
project control, and an external MUSUBI appraisal. None is promoted into an
independent proof of the underlying protocol.

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

Mailing-list outreach is intentionally outside this package.
