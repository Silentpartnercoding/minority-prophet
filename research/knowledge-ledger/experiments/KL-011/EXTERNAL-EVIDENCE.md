# KL-011 — adjacent external evidence, and what it does not discharge

Written 2026-09-15. **This record does not advance KL-011's state.** It exists
because a sibling programme obtained the kind of evidence KL-011's next gate
asks for, and the absence of a cross-reference caused that result to be
invisible from here for thirteen days.

## Why this file exists rather than a completion record

KL-011's next gate reads:

> A transport that is not of our own construction. This run crossed a process
> boundary through bytes we serialised with a codec we chose. The untested
> cases are a transport we do not control — a real queue, a real network, a
> second implementation reading the receipt — and F11's question of whether an
> independent reader reconstructs the same conclusion from the same bytes.

Both clauses have now been satisfied **for a different corpus, in a different
repository**. The temptation is to read that as discharging this gate. It does
not, and the reason is the rule this programme already enforces elsewhere:
evidence is admissible for the exact artifact it measured, and not for a
neighbouring one that shares a theme.

| | KL-011 | The externally executed corpus |
|---|---|---|
| Artifact | knowledge-ledger receipts; fixtures `confident-only`, `population` | Border A2A→MCP crossing cases |
| Population | 10 transactions, five stages, seven injections | 28 cases, native and bound lanes |
| Question | do roots, coverage, uncertainty, conclusion and the authorization boundary survive a crossing | does authority remain bound across an A2A→MCP translation |
| Repository | `minority-prophet` | `minority-prophet-border` |

Same family. Not the same bytes. **No independent party has read a KL-011
receipt.**

## What the external evidence actually is

Recorded here in full so a later reader does not have to rediscover it.

**1. Foreign transport — Border A2A-MCP-CROSSING-001 transport run, 2026-08-19.**
The identical frozen cases (`cases.json` sha256
`eea9a7c5ca0e0d90ca308401c9408f0187721c5edeb4a46bffaf2a0484ca12d1`, the digest
recorded before either lane existed) re-run with the A2A hop over HTTPS with
verified TLS, caller identity from a **Keycloak RS256 bearer token** checked
against JWKS for issuer and expiry, and the context built by the **A2A SDK's own
`DefaultServerCallContextBuilder`**. Three real principals (`agent-a`, `agent-b`,
`agent-c`) make the substitution case a genuinely authenticated different
principal rather than an unauthenticated request. Verdict unchanged: interesting.

Finding: a valid credential does **not** catch caller substitution, because the
substituting principal holds a perfectly good token that the mandate simply does
not name. Authentication and authorization separate exactly where the
experiment predicted.

**2. Independent execution by a separate implementation and operator —
`Heaviside479/handoffprobe#20`, closed 2026-09-02.**

The frozen 28-case v2 crossing package (merge commit
`09aca453f9d5e5552e4ed2cfbda2ed0b22e4d51a`, corpus sha256
`f7a72b5c1c0473080aff468d1af6b0500d035d6a00ebbfce1d2499a0897534fb`) was executed
by a different operator on a different stack — `@a2a-js/sdk` 1.1.0 and the MCP
TypeScript SDK 2.0.0, against this side's Python `a2a-sdk==1.1.2` and
`mcp==2.0.0`. All 28 cases in corpus order, 58 attempt-level evidence records,
an effect recorder outside the verifier, and the implementer's own observations
for caller, message, resolved task/context, MCP audience, tool and arguments.
Their statement, which is the load-bearing one: *no reference-fixture observed
row was used to fill observation gaps.* 26 discriminating cases; the native lane
reaches the effect, the bound lane refuses.

**The grade was withheld on first submission.** This side declined
`--confirmed-grade implementation_independent` against a specific gap: the
profile requires issuer-authenticated initial and resolved authority artifacts,
and an unkeyed digest alone is not an issuer signature. The implementer closed
it with Ed25519 over a domain-separated authority digest verified against a
pinned issuer identity and key ID, plus a non-issuer forgery negative control.
Re-verification reproduced `result.json` and `authority-authentication.json`
byte-for-byte against the archive, with 67 test files / 352 tests passing. The
`implementation_independent` and `green_eligible: true` outcomes are recorded in
the implementer's own public documentation.

Scope limit, stated by the implementer and carried here: the key material is
fixed RFC 8032 test-fixture material, so this is conformance evidence rather
than a production credential setup, and `green_eligible` applies to that frozen
profile.

## What this changes for KL-011, precisely

**Nothing about its state.** KL-011 remains `fixture-passed`, and its
`claimAllowed` is unamended.

What it changes is the cost of the remaining gate. The gate was previously
open against an unknown: whether an independent implementation and operator
could be found at all, and whether a frozen corpus plus an intake contract was
enough for one to execute against. Both are now answered by demonstration.
The remaining work is to run **KL-011's own receipts** through that same
arrangement, not to establish that the arrangement is possible.

## What would discharge the gate

An operator who is not this one, running an implementation that is not this
one, reading a KL-011 receipt and reconstructing the same conclusion from the
same bytes — with the reference row not used to fill their observation gaps,
and the grade withheld until any gap they leave is closed.

## Record-hygiene finding

The 2026-09-02 result was thirteen days old and invisible from this experiment,
which still listed both clauses as untested. This is the `stale-self-description`
family — PROV-005, ART-101, TEST-101, DOC-102, and the KL-011 blocker corrected
at RUN-20260807-6 — occurring for the first time **across repositories** rather
than within one. The within-repository instances were each caught by a review
that re-derived rather than re-read. No such review spans repositories, so this
one was caught by the owner's memory instead.

The fix is the same as every prior instance: records name their evidence, and
reviews re-derive rather than re-read. The scope is what is new.
