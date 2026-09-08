# Placement — what belongs where, and what was superseded

Written after reading the shipped architecture rather than inferring it. Three
placement calls in this programme were made from mechanical proxies — keyword
frequency, import graphs — and all three were wrong. This file records the real
division of labour and re-places every canon artifact against it.

## The architecture that already exists

Four components, documented in
`research/decision-relative-independence/README.md` and composed in the private
`minority-prophet-stack`:

| component | owns |
|---|---|
| **Border** | binds authority, declaration, destination policy, and **human control** to one exact action; emits a signed admission receipt |
| **Minority Prophet** | analyses evidence structure. Returns `TRUE / FALSE / ABSTAIN` and **no authority** |
| **Gate** | interprets authenticated evidence and controls runtime consequence: `proceed / block / escalate / request_evidence` |
| **Strategic governor** | declares failure domain, cut, **sufficiency threshold**, consequence, stopping rule |

`minority-prophet-stack` composes them into a hash-chained decision timeline
across Border → MP → Gate → runtime, with a credentialless shadow observer that
records would-be outcomes while attempting zero effects.

**MP has no human path and should not acquire one.** It emits `ABSTAIN`, an
epistemic state, not `ESCALATE`, an action. Gate decides *that* a human is
needed; Border decides *which* human may act. Neither half works alone.

## Human control is already modelled, and better than assumed

`border/admission.py` — *"Fail-closed admission binding for declarations,
authority, policy, and human control."*

- `requires_human_approval` on the policy, `override_permitted` alongside it
- a signed `human-control/v1` event with three modes: `approval`, `override`,
  `manual_control`
- signature verification on that event, plus `human_is_authorized(control)`,
  which fails closed with *"human lacks authority for this intervention"*

The human is an authenticated party with a signed intervention record and their
own authority check — not an escalation target. A human approving something they
are not authorised for is refused exactly like a bad issuer.

## Re-placement

| artifact | placement | status |
|---|---|---|
| `Responsiveness.lean` | **minority-prophet** | reasons in `margin` / `rootSet`; repairs `Margin.lean` |
| `RootIdentity.lean`, `U1-PROXIMATE-ROOTS.md` | **minority-prophet** | closes CE-08; MP's register cites them |
| `independence_axes.py`, `root_vote.py`, `root_registry.py` | **minority-prophet** | MP's own aggregator and issuance |
| `proximity.py`, `root_identity.py`, `targets.py`, `rungs.py`, `independent_set.py` | **minority-prophet** (`canon/`) | reference implementations of what is plumbed into `aggregation/` |
| `NarrowGate.lean` | **minority-prophet** Lean development | Gate's `FORMAL.md` forbids restating proofs; Gate gets a pointer row, not a copy |
| the depth/identity vocabulary | **minority-prophet-gate**, blocked on #115 | filed as gate issue #22 |
| `precedent.py` | **retracted** | superseded — see below |
| `narrow_gate.py` | **retracted as a proposal** | superseded — see below |

## Retractions

**`precedent.py` is superseded.** It proposed a three-outcome gate with
dominance-based precedent replacing a sufficiency threshold. The shipped Gate
already has *four* outcomes, escalates on abstention and on thin margins with
the comment *"no independent evidence is a reason to ask a human, never a reason
to proceed"*, fails closed when a theorem's precondition does not hold, and
prices attacks in forged and compromised roots. Border carries the signed human
record the proposal lacked entirely.

The dominance model is also not an improvement on `min_flip_budget`: a scalar
threshold on a priced attack budget is simpler, and Gate applies it only on the
proceed path while escalating rather than blocking on a thin margin. The claim
that a threshold could be eliminated was wrong — and in any case sufficiency is
the strategic governor's, not Gate's.

**`narrow_gate.py` is superseded as a proposal.** Deny-by-default, bounded
undertaking, receipts and at-most-once are all present in Gate's `decide()` and
Border's admission binding, in stronger form. It is retained only as the
executable form of the audited laws — the record of how the rules were derived.

Both files stay in the tree with a retraction header. Deleting them would remove
the evidence that this programme re-derived shipped work, which is the finding.

## What survives as genuinely additive

1. **`NarrowGate.lean`.** Gate's design is right and nothing proves its shape is
   necessary. The theorem shows safety is trivially satisfiable by a gate that
   admits nothing, so controlled invariance buys liveness rather than safety.
   This bears directly on two open production blockers in the stack's
   `FAILURE-MATRIX.md` — revocation provider and durable replay store, both
   *"fail closed and alert, not implemented"* — because fail-closed-everywhere
   is exactly the configuration the theorem warns about.

2. **The witness-depth gap.** Border authenticates who speaks; Gate authenticates
   the envelope; nothing in the chain distinguishes a source that looked from one
   that read. Gate classifies with two values — anything without `derived_from`
   is a `root`, a "fresh observation" — so an attacker inflates their position by
   omitting a field rather than forging one. Filed as
   `minority-prophet-gate#22`, blocked on #115.

## Lesson recorded

Three placement errors in one session, each from substituting a cheap proxy for
reading the thing: keyword frequency put the gate work in Border; an import graph
nearly split `RootIdentity.lean` out of the repository whose ledger cites it; and
not reading `FORMAL.md` nearly duplicated a proof into a repository that
explicitly refuses copies to prevent drift.

The proxy is fast and it was wrong every time.
