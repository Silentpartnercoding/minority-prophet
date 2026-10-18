# Verifier-evidence review ledger

Document: `draft-he-agentproto-verifier-evidence-00`
Publication state: submitted and confirmed as an individual Internet-Draft on
October 17, 2026:
<https://datatracker.ietf.org/doc/draft-he-agentproto-verifier-evidence/>

This ledger distinguishes review, reproduction, and adoption. It is not a list
of endorsements.

## Review sequence

- **September 19, 2026 — scoped technical response.** Songbo identified EXR as
  directly relevant and treated CMP as the completeness/omission subcase,
  rather than as a solution to every independence question. The response also
  distinguished a principal-binding floor already present in the AgentProto
  work from the additional exercise and completeness records proposed here.
- **September 19, 2026 — bounded replay.** At repository commit
  `b4ee46924ebe8fd0bee38b4986a01229e859764b`, the author reran 28
  verifier-evidence tests and 38 related tests against byte-identical source
  vectors. The report described this as a **bounded source replay**, **not a
  second implementation or conformance result**.
- **September 26–27, 2026 — wording review.** Review focused on the EXR-1 and
  CMP-2 requirements. Two final wording changes were requested and incorporated.
- **September 28, 2026 — matching package.** XML, text, and HTML were sent as a
  matching set for parity review.
- **October 2, 2026 — parity review.** A named technical reviewer rerendered the
  received XML. The
  text was byte-identical, and the HTML document body matched apart from
  generator metadata and stylesheet material. The review found one
  reproducibility defect: the RFCXML did not contain an explicit date. The
  wording and parity review concluded at that point.
- **October 2, 2026 — date correction.** The author added the explicit
  September 27 date and rerendered with `xml2rfc` 3.34.1. The text remained
  byte-identical and the HTML body remained unchanged apart from generator
  metadata.

## Changes after the reviewed package

Only the following changes were made while preparing this local package on
October 17, 2026:

1. The missing date identified by parity review was first fixed to the reviewed
   September 27 date. The prepared package advances that explicit date to
   October 17, 2026 so the IETF submission preflight does not reject a stale
   document date. This changes generated header and expiration metadata, not
   the technical requirements.
2. `consensus="false"` was added as individual-submission metadata. It does not
   alter the proposal's technical requirements.
3. The informative principal-binding citation was updated from
   `draft-bu-agentproto-security-principal-binding-07` to
   `draft-bu-agentproto-security-principal-binding-08`, the current Datatracker
   revision checked on October 17, 2026. The cited section numbers remain
   present. The reference month was updated from September to October.

The current generated text is therefore not claimed to be byte-identical to
the September 28 attachment: its date metadata and citation revision are
intentionally current. The technical requirements and bounded
implementation-status language remain the reviewed text.

## What this record establishes

- Scoped technical and wording review occurred.
- A named reviewer checked XML/text/HTML parity and identified a concrete
  reproducibility defect, which was corrected.
- The repository contains a bounded replay of the author's own source and
  fixtures.

## What this record does not establish

- It is not a second implementation.
- It is not a conformance result.
- It is not an independently appraised CMP-1 or CMP-2 result.
- It is not approval, endorsement, working-group adoption, or an RFC decision.
