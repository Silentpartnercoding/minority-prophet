# U1 — what counts as one evidence root

**Status: proposed closure.** The definitional question is answered; one
residual exposure remains and is bounded rather than solved.

## Why every previous attempt failed

The question was always asked as *"find the equivalence relation on sources."*
That framing cannot succeed. Ancestry is transitive and unbounded — every claim
descends from earlier claims without end — so any relation of the form "shares
an ancestor" has a transitive closure that swallows the corpus.

Concretely, the case that broke the previous definition: `A` shares provenance
with `B`, `B` shares *different* provenance with `C`, `A` and `C` share nothing.
An equivalence relation must be transitive, so all three collapse into one
lineage. Effective count 1. The truthful answer is 2 — `A` and `C` are
genuinely independent witnesses.

Scale that up and `N_eff → 1` across any connected corpus. The aggregator
becomes maximally conservative and refuses to believe anything, which is the
`FalseDenyRate` failure the canon programme exists to prevent.

**The error was demanding an equivalence relation at all.** Dependence between
witnesses is not an equivalence. It is not transitive, and forcing transitivity
on it is what destroyed the count.

## The borrowed doctrine

Criminal and tort law faced the identical structure and did not solve it by
tracing harder.

**Cause-in-fact** — the but-for chain — is unbounded and transitive. Everything
has infinite ancestry; on that test the manufacturer of the ship that carried
the timber is a cause of the fire.

**Proximate cause** is a *declared cut*. Beyond a certain remoteness the chain
stops carrying liability — not because causation stopped, but because
responsibility did. And the cut has an operative mechanism: `novus actus
interveniens`, an intervening independent act that breaks the chain.

The transplant is exact:

> Two sources descending from a common ancestor are still **independent
> witnesses** if each re-established the claim through a channel that does not
> pass through that ancestor.

Shared ancestry is cause-in-fact. It is necessary for dependence and not
sufficient. What makes ancestry *matter* — the proximity the owner's framing
asks for — is the absence of an intervening re-derivation.

## The formal consequence

If dependence is a graph relation relative to a proposition rather than an
equivalence, the count is not a quotient. It is a **maximum independent set**:
the largest set of witnesses no two of which are proximately dependent.

`N_eff = max { |S| : S ⊆ Sources, no two members of S proximately dependent }`

Three properties, each checked:

**1. It generalizes the old definition rather than replacing it.** When
dependence really is transitive the graph is a disjoint union of cliques, a
maximum independent set picks exactly one member per clique, and the count is
the number of classes — the quotient answer. Machine-checked as
`RootIdentity.clique_indep_one`.

**2. It gives the right answer where the quotient failed.** On the `A—B—C` path
it returns 2. Machine-checked as `RootIdentity.path_indep_two` and pinned in
`tests/test_root_identity.py`.

**3. It cannot over-report relative to the dependence graph it is given.** Any
independent set holds at most one member per true lineage, so the count is
bounded by the number of real lineages present. Machine-checked as
`RootIdentity.independent_card_le_lineages`.

## How the cut is decided in practice

The doctrine needs an operative test for "was there an intervening
re-derivation?", and the test is already MP's: **the trout in the milk**.

Two sources that re-derived a claim independently will not share the ancestor's
*idiosyncratic errors*. Two sources where one copied the other will. A shared
idiosyncratic marker has no innocent explanation, so it is treated as decisive
and **overrides any provenance record claiming re-derivation**. The content
outranks the paperwork — the record is what an adversary controls.

This is expansion `E1` from `ASSAYER.md` doing exactly the work it was named
for: leaving the metadata and entering the substance.

## Novelty

Per `PROGRAM.md`, stated before it can be misread as a discovery.

- Proximate cause and `novus actus interveniens`: tort doctrine, centuries old.
- Blocking a dependence path by conditioning on an intervening variable:
  d-separation (Pearl).
- Counting independent observations under shared ancestry: phylogenetic
  independent contrasts (Felsenstein 1985); effective sample size (Kish 1965).
- Maximum independent set in a conflict graph: standard combinatorics.

**Verdict: `NOVEL COMBINATION`.** No component is ours. The composition —
a remoteness cut decided by content-level error correlation, counted as a
maximum independent set, reported under a no-positive-absence rule — is, as far
as the audit found, not standard. It should be published as a combination and
never as a discovery.

## What remains open, stated plainly

**The residual exposure is detection, not counting.** An adversary who launders
the provenance record *and* scrubs the shared idiosyncratic markers removes
edges from the graph, and a sparser graph admits a *larger* independent set. The
count then over-reports independence relative to reality.

This is pinned as a deliberately uncomfortable test —
`test_ATTACK_laundered_provenance_inflates_the_count` — which asserts that three
copies with erased ancestry are counted as 3.

No counting rule closes this. Only detection does, and per `ASSAYER.md` A5
detection can only ever report *"no dependence trace was found."* The residual
is what **R3 margin sufficiency** exists to absorb: require a margin above
`N_eff` rather than trusting `N_eff` itself. U1 and R3 were always the same
problem seen from two ends.

**Two owner decisions remain**, both smaller and far more defensible than the
original question:

1. **What qualifies as an intervening re-derivation?** This must be published in
   advance under `A3` and fixed before the sample is drawn. It is a judgment
   call, but a narrow and auditable one.
2. **Exact or greedy?** Maximum independent set is NP-hard in general. The
   greedy pass is always a *lower* bound — conservative in the safe direction —
   and both are implemented. At realistic witness counts exact is affordable.

## Verdict on U1

The definitional question — *what counts as one root* — is answered: **a root is
a witness whose chain to any shared ancestor is cut by an intervening
independent re-derivation, and roots are counted as a maximum independent set
over the proximate-dependence graph.**

The empirical question — *can we detect when the cut is faked* — is not
answered, is not answerable in the positive direction, and is bounded by R3.
That is the honest boundary, and it is a much better place to stand than an
undefined term.
