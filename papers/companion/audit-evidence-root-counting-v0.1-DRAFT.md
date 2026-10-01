# An Echo Is Not a Witness: Evidence-Root Counting for Agent Audit Records

**Status: DRAFT v0.2. Not submitted to the IETF. Not adopted by any working
group. Not deposited. No DOI.**

Drafted 2026-09-20 and updated 2026-10-01 as a standards-facing mapping of
existing Minority Prophet results. The submission-candidate RFCXML source and
generated renderings are in
[`papers/ietf/`](../ietf/README.md). This note proposes no change to the
published foundation paper.

---

## Abstract

An agent audit trail can contain many correctly signed records that ultimately
repeat one observation. Signatures establish who signed the records; they do
not establish that the records are independent evidence. This note maps the
Minority Prophet copy-invariance result onto audit records: records derived
from one declared evidence root contribute one unit of evidentiary support,
however many copies, relays, summaries, or re-signatures appear in the trail.

The proposal is deliberately narrow. An audit format should preserve enough
derivation information to count declared evidence roots, expose the basis on
which any roots were treated as distinct, and return **not established** when
that basis is missing. This controls recorded multiplicity. It does not prove
truth, causal independence, search completeness, or operational authority.

## 1. The seam

The active individual AUDIT architecture draft links user intent, delegation,
authorization, actions, and outcomes through distributed audit records.
Decision-record discussion around the proposed IETF AUDIT work also asks
whether an authorization decision leaves a signed, checkable audit artifact.
The August 2026 individual draft *Signed Decision Records for Agent
Authorization: Disclosures, Entry Emission, and Ordering Evidence* requires
artifacts for allow, deny, and other states a relying party may need to reason
about. Its
accompanying implementation notes identify a remaining failure: some requests
that cannot be canonicalized leave no record at all.

That is a **record-completeness** problem. Minority Prophet addresses a
different problem that begins after records exist: **evidence-counting
correctness**. If five records repeat one source, the trail contains five
records and one declared evidence root. The first number measures artifacts;
the second measures the support represented by those artifacts.

Both checks are needed:

1. **Completeness:** did each committed attempt produce the required terminal
   artifact, including a refusal when a normal decision record could not be
   encoded?
2. **Counting:** do copied or transformed records preserve their derivation so
   they cannot manufacture additional evidentiary weight?

Passing either check does not imply passing the other.

The counting problem is already on the public AgentProto record: a September
2026 charter-review comment states that a record containing multiple
attestations does not thereby establish multiple units of support. That comment
announced an individual draft in preparation; it did not establish AgentProto
adoption or make audit-record semantics part of its charter.

### Separate verification dimensions

| Dimension | Question answered | What success does not establish |
| --- | --- | --- |
| Authenticity and integrity | Did the identified signer produce these unchanged bytes? | Truth, completeness, causation, or independent support |
| Recomputation | Does the stated result follow from the available inputs and named procedure? | Fresh external state or complete inputs |
| Freshness | Was an external fact current at the claimed time? | Causal use or evidence multiplicity |
| Completeness | Did every attempt in a separately committed scope produce the required record? | That present records are independent evidence |
| Precedence or effect | Did a decision precede and govern an action, or did the claimed effect occur? | More than one underlying observation |
| Evidence multiplicity | How many declared evidence-provenance roots support the proposition? | Truth, absolute independence, or authority to act |

## 2. Candidate audit rule

For a named proposition and a declared class of error, an audit report that
states an evidence count should:

1. identify the terminal records included in the report;
2. identify the declared derivation root or roots reached from each record;
3. state the rule and evidence used to treat roots as distinct for that class
   of error;
4. count each distinct qualified root once, regardless of the number of
   descendant records; and
5. report the evidence-root count as **not established** when the derivation or
   distinction basis is unavailable.

A repeated, relayed, translated, summarized, or re-signed statement does not
become new evidence merely because a new actor, model, process, key, or record
carried it. A separate signature authenticates a signer. It does not, by
itself, establish a separate evidence root.

The proposed machine-checkable invariant is:

> Adding a same-side record with a declared parent does not change the set of
> evidence roots, the root count, or the root-count verdict.

This is the audit-facing form of the published recorded-copy invariance result.
It is conditional on the declared lineage and root boundary being correct.

## 3. Minimal record mapping

This note does not propose a complete wire format. A format can support the
rule with four logical items, whether carried inline or by digest reference:

| Item | Purpose |
| --- | --- |
| `proposition_id` | Binds records to the same question before any count is compared. |
| `assertion` | Records the side supported by the artifact. |
| `derivation_parent_ids` | Prevents a recorded copy from appearing as a new root. |
| `root_basis_ref` | Points to the declared basis and error class used to qualify and distinguish roots. |

The count is computed from the distinct declared roots reached under the cited
qualification and distinction rule, not from record identifiers, signer
identifiers, agent identifiers, or public keys. If `root_basis_ref` is absent
or cannot support the claimed distinction, the report should expose that
limitation rather than silently promote each record to a root.

## 4. Completeness remains a separate commitment

No set of present records can prove, by itself, that a required record is
missing. A checker needs a separately committed finite set of expected attempts
or another independently auditable scope boundary. Without that commitment,
silence is **unverifiable**, not a successful completeness check.

A companion fixture in `Silentpartnercoding/agent-security-verifier-matrix`
freezes three attempts and checks their signed terminal artifacts. Its decisive
case removes the refusal record for an unencodable request. The remaining
signatures and hash chain still verify, but the separately frozen attempt
manifest makes the omission a violation. That fixture tests completeness; it
also exercises the narrow declared-root copy case, but it is not a general
implementation of this note or a conformance claim for another implementation
or draft.

The fixture is public at merge revision
`7114ae58bdc2efb13417e4624762f8f9b1ff6ba4`. It includes the external attempt
commitment, the terminal-deletion counterexample, and the declared-root
photocopy cases. It is supporting implementation evidence, not an IETF
conformance claim or an independent implementation of another draft.

## 5. What the foundation establishes

The published Minority Prophet foundation proves, for finite side-consistent
claim graphs with declared roots:

- **recorded-copy invariance:** appending a same-side claim with an existing
  parent preserves root counts, margin, and verdict;
- **root-preserving lineage immunity:** changing non-root lineage while
  preserving assertions and the root set preserves the verdict; and
- **majority non-invariance:** ordinary head counting can be reversed by adding
  copies.

The proofs establish behavior of the counting rule under their assumptions.
They do not establish that a deployment discovered every copy or chose the
correct root boundary.

## 6. What is not claimed

- A declared root is not automatically true, authentic, qualified, or causally
  independent.
- Different organizations, people, agents, prompts, models, hosts, keys, or
  signatures do not by themselves establish distinct evidence roots.
- A root count is not a probability and does not grant permission to act.
- A derived-record graph does not establish that discovery was complete.
- The symmetric root-count verdict is not the right instrument for universal
  or existential claims, where the two sides have different logical force.
- This note is not an IETF working-group product and does not claim endorsement
  by the authors of related individual drafts.

The strongest safe statement from an incomplete provenance check is **no
dependence trace was found**, not **these sources are independent**.

## 7. Proposed evaluation

A minimal interoperability exercise should publish frozen inputs and expected
outcomes for at least these cases:

1. one root, five direct copies: root count remains one;
2. two separately qualified roots plus any number of copies: root count remains
   two;
3. two signatures over the same source observation: root count remains one;
4. unknown or unsupported derivation: count is not established; and
5. an expected attempt with no terminal record: completeness violation, even
   when every present signature verifies.

The first four test evidence counting. The fifth tests record completeness.
Reporting them as separate verdicts prevents a valid signature or complete log
from being mistaken for independent evidentiary support.

## References

1. James He, *The Minority Prophet Property: Copy-Invariant Evidence
   Aggregation in Rooted Claim Graphs*, archival record and versions,
   <https://doi.org/10.5281/zenodo.21965712>.
2. Bradley B, *Signed Decision Records for Agent Authorization: Disclosures,
   Entry Emission, and Ordering Evidence*, Internet-Draft work in progress,
   <https://datatracker.ietf.org/doc/draft-bradleyb-audit-decision-records/>.
3. Bradley B, implementation receipt notes at frozen revision
   `f2efb313d113149c6ddc9656307a605a7619f8ea`,
   <https://github.com/11-11AI/execution-governance/blob/f2efb313d113149c6ddc9656307a605a7619f8ea/docs/RECEIPTS.md>.
4. Agent-to-Agent Protocol working-group mailing-list discussion, 24 August
   2026,
   <https://mailarchive.ietf.org/arch/msg/agentproto/ujxE1J-394TnVw9gXmT1h2TeMew/>.
5. Mirja Kuehlewind and Henk Birkholz, *An Architecture for Auditing Agent
   Delegation and Interactions*, Internet-Draft work in progress,
   <https://datatracker.ietf.org/doc/draft-kuehlewind-audit-architecture/>.
6. J S He, AgentProto charter-review comment on evidence limits and copy
   counting, 19 September 2026,
   <https://mailarchive.ietf.org/arch/msg/agentproto/N8CtuCJ5jYeEv4F4vKn9ybnKwDw/>.
7. *Audit Refusal Completeness and Declared Evidence-Root Fixture*, frozen at
   `7114ae58bdc2efb13417e4624762f8f9b1ff6ba4`,
   <https://github.com/Silentpartnercoding/agent-security-verifier-matrix/tree/7114ae58bdc2efb13417e4624762f8f9b1ff6ba4/experiments/audit-refusal-completeness-001>.
