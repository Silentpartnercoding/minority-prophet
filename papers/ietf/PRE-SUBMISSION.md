# Pre-submission record

Document: `draft-he-audit-evidence-root-counting-00`  
Intended status: Informational  
Stream: IETF individual submission  
IETF 127 upload cutoff: November 2, 2026 at 23:59 UTC

## Prepared in this repository

- RFCXML v3 source with the individual-draft boilerplate.
- Generated paginated text and HTML renderings.
- A pinned `xml2rfc` build environment and repeatable build targets.
- A verification-dimensions table that separates authenticity, recomputation,
  freshness, completeness, precedence/effect, and evidence multiplicity.
- Explicit limitations: a declared root is not automatically true or
  independent; replay is not an independent implementation; the rule cannot
  detect omitted provenance.
- A permanent supporting-fixture reference at matrix merge revision
  `7114ae58bdc2efb13417e4624762f8f9b1ff6ba4`.

## Mechanical preflight

- [x] `make ietf-check` passes in the prepared worktree.
- [x] `make verify` passes in the prepared worktree.
- [x] IETF `idnits` 3.1.0 reports the RFCXML source nit-free in submission
      mode.
- [x] Generated text stays within the RFCXML renderer's pagination and line
      constraints.
- [x] The cited AUDIT architecture and signed-decision-record drafts still name
      revisions `-01` and `-00`, respectively.
- [ ] The rendered author block is correct.
- [x] The Datatracker has no conflicting draft name as of October 1, 2026.

## Human-only submission steps

These steps are deliberately not automated or completed here:

1. Confirm that the public author line should read `James He, Independent`,
   with `jsiyuanhe@gmail.com`, Yorba Linda, California, and
   `https://minorityprophet.org/`.
2. Confirm the IPR disclosure answer presented by the IETF submission tool.
3. Review the final text and HTML as the named author.
4. Upload the XML or generated text through the IETF Datatracker submission
   tool and complete its email confirmation.
5. After a Datatracker URL exists, decide whether and where to announce it.

The draft must not be described as adopted by AgentProto, AUDIT, or any other
IETF working group.
