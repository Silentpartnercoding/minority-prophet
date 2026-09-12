# The epistemic model

What any component of the stack establishes, and what none of them does.

Canonical copy. `invention-graph` carries a pointer to this file rather than a
second copy. Independent implementation; no third-party code, text or naming
was used.

Read alongside `canon/PLACEMENT.md`, which assigns the components: Border binds
authority and human control to one exact action, Minority Prophet analyses
evidence structure and holds no authority, Gate controls runtime consequence,
and the strategic governor sets the sufficiency threshold and stopping rule.

## A note on the word "axes"

`axes` is reserved for the independence vocabulary: `WitnessDepth`,
`Attestation`, `WitnessIdentity` and `DepthBasis`. Those are orthogonal,
measurable dimensions of a single source, shared as a wire contract with
`minority-prophet`.

The four below are not dimensions and nothing is measured along them. They are
questions a record either answers or does not, and one of them is a question
this model refuses. Calling both sets "the four axes" invited exactly the
confusion this paragraph exists to prevent.

## Four questions, and one thing that is not a question

**Structure** asks what the recorded topology is: roots, lineage, margin.
**Attribution** asks who or what produced an artifact.
**Correspondence** asks whether a claim matches the world. This model never
answers it, and must not be read as answering it.
**Dependence** asks what a result rests on that this model does not itself
establish, with deliberately unbounded terms named. See `ASSUMPTIONS.md`.

Authorization is not a fifth question. It sits downstream of all four, and it takes
two conditions that are each necessary and neither sufficient: a capability the
provider granted this actor, and enough attack-resistant independent evidence.
Evidence strength never creates permission, but it is a precondition for acting
rather than something authorization ignores. Holding only one condition leads
somewhere other than proceeding: capability with thin evidence is a reason to
collect more, and strong evidence without capability is a reason to ask a
human.

## Status is computed, never stored

`EpistemicStatus` is an ordered ladder: ungrounded, declared, observed,
derived, verified. The rungs are cumulative rather than parallel labels, and
`verified` means derived and then re-checked by someone other than the author.

It is deliberately not a field. `InventionEngine.epistemic_status` reads it off
the graph on demand, because a stored status is one that can drift from the
evidence, and that drift is the failure this codebase keeps hitting: a paper
reporting an optimum from a runner that returned nothing, a ledger citing a
proof from a file that does not compile.

This is why the ladder is not adopted as a claim field even though it is a
tidy vocabulary. Two existing enums already separate what the ladder merges:
`OriginType` records where a claim came from, `IndependenceBasis` records how
well that is known. Storing a single status on top of them would flatten a
distinction the graph already draws and create a third thing to disagree with
the other two.

## Identity, authority, and why they are separate

`IdentityRecord` answers who or what. It is not human-only: instruments,
datasets, software, models, agents and checkers all author things, and
treating only people as identities is how an unattributed pipeline output
inherits a person's credibility.

`AuthorityGrant` answers what that identity is entitled to do. It is a typed,
scoped capability with an action and a scope, both required, because an
unscoped capability is a trust flag wearing a type. Delegation may narrow and
may never widen. `is_authorized` matches exactly rather than by prefix, so a
capability cannot grow by string coincidence.

Nobody issues their own capability. Granting requires a granter who already
holds the grant capability for that exact scope, and who is not the recipient.
Seeding the first granter in a scope is the one exception, it may create only
the power to grant, it is refused once that scope already has a granter, and it
is recorded on the node so a seeded capability never looks like an issued one.

Capabilities are withdrawn, never deleted. `revoke_authority` tombstones a
grant so a decision taken while it was live still reads correctly afterwards,
and authorization skips tombstoned grants from that moment. Revoking takes the
same power as granting, or being the holder standing themselves down.

The last granter of a scope cannot be revoked. Appoint a successor first.
Removing the final one would freeze the scope, and the only escape hatch that
could unfreeze it is the same hatch an attacker would use.
`succession_risk` lists every scope whose granting power rests on one identity,
so a bus factor of one is visible before somebody leaves rather than after.

That leaves one thing the model cannot settle: who should hold the first grant.
Nothing inside a graph can establish that, so recovering a lost granter is an
out-of-band operation and is deliberately unavailable here. It belongs recorded
as an irreducible term rather than quietly relied upon.

Authority is never a reason to believe anything. A credentialed actor
declaring something leaves the claim exactly where the evidence puts it, and
there is a test that says so.

## Justification and domains

A `Justification` carries a transportable artifact digest, who asserted it,
and, separately, a checker's verdict. Those are different facts and are stored
in different fields. A verdict is refused unless it names the checker and a
replayable output digest, and a verdict from the asserter does not count as
independent checking.

Each `DomainRecord` carries its own ladder. One ladder spanning proof checking
and physical replication collapses back into the single score the structure
exists to replace, so the rungs belong to the domain.

## Independence has dimensions

`IndependenceDimension` records source, dataset, measurement, method,
implementation, model and verifier separately. Two teams running one
implementation over one dataset are independent in personnel and nothing else.
`declare_independence` refuses an empty dimension set, and
`replication_strength` counts only claims that are pairwise independent on
every dimension the caller requires, so the shared-everything case returns one.

## Typed parsing

`PropositionType` declares a shape and the kind of thing each slot accepts. A
`CandidateParse` is a reading offered by someone, possibly a language model,
and it records who proposed it and how they ranked it. `admit_parse` checks
arity and each argument's kind against the declared shape and rejects a
mismatch outright. The rank is never consulted, so a confident proposer cannot
talk an invalid reading past the check.

## Translations

A crossing between domains is a `TranslationRecord`, a node rather than an
edge, carrying its own method, who performed it and whether it was checked for
faithfulness. A chain running through three representations therefore shows as
three inspectable hops instead of one unexplained jump.

## Replacing, not editing

`supersede` records a replacement as a new claim plus an edge. Nothing is
rewritten in place, so a historical claim keeps saying what it said when it was
made.

## Capability, which is not a gate

`capability_decision` answers whether an identity holds a capability for an
action at a scope. It consults capabilities and nothing else. A fully verified
claim held by an identity with no capability is refused, and a merely declared
claim held by an identity with the capability is permitted. When a claim is
named the record reports its status and states that the status was not used.

It is deliberately not a decision layer. An action-neutral assessment, a
provider-owned authority policy and a runtime controller that binds and
enforces a single execution already exist elsewhere in the stack, and this does
not replace any of them. It emits no proceed, block or escalate verdict.

What it supplies is the input those policies were missing. Until now a policy
had nothing to key off except how strong the evidence was, which is the exact
collapse the separation exists to prevent: the code paths were separate while
the decision still came from evidence strength. A typed capability gives a
policy something else to read.

## The warranty certificate

`warranty(claim_id)` returns the whole backing: text and proposition, origin and
independence basis, computed status, evidence roots, parent claims,
justifications with each checker verdict and whether it was independent, what
the claim rests on, its irreducible terms, its independence dimensions against
other claims, what supersedes it, and which load-bearing assumptions are in
scope. Every field is read from the graph, so the question "why does this
system hold this?" is answerable without trusting any prose.

The certificate carries its own caveat: it reports what the graph records and
does not assert that the recorded structure is complete.

## Migration

`unmodelled_claims` lists claims carrying none of the newer structure, so the
backlog is visible rather than assumed empty. Migration here is additive
enrichment of existing records, not a rewrite.

## Filling it in

The barrier to a model like this is usually assumed to be that nobody would
complete the fields. That is not the situation here. Most of the answers are
already inside records the system retrieves and then discards on the way in. A
scholarly record arrives carrying authors, publisher, DOI and a reference list.
A recorded result arrives carrying a content digest and, where one ran, an
attestation verifier and receipt.

So the fields are derived by default and typed in only by exception:

- `identities_from_source` mints identity nodes from the authors, publisher and
  provider a retrieved record already names, and is idempotent.
- `justification_from_result` turns a recorded run into a justification, using
  the captured verifier and receipt as the checker verdict. Where no verifier
  was captured it records the justification without one, leaving the claim
  unverified rather than quietly promoting it.
- `shared_dependencies` reads two sources and returns the dimensions they
  demonstrably do not vary on: same DOI, shared authors, identical reference
  lists, same publisher.

That last one only ever subtracts. Detecting shared structure is evidence
against independence and is safe to infer. The reverse is not, so nothing here
ever declares two things independent on its own; `declare_independence` still
requires someone to assert it with dimensions named.

What genuinely cannot be derived is the assumption set. No provider metadata
says what a result rests on that nobody established. That is a human judgement,
and it is a small one in practice, because the load-bearing assumptions belong
to a programme and are stated once rather than per claim.

## What is not built

A full immutable layer and commit chain over the storage engine. The store is
append-only and content digests are carried on records, but layers, parent
pointers and a commit pipeline are not implemented. Nothing else from the
target model is outstanding.
