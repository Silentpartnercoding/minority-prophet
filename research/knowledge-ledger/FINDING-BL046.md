# BL-046 — the three remaining shared quantities

Executed 2026-08-08, following XRP-101. Method as XRP-101: evaluate each
quantity in every repository that implements it, on identical inputs.

## First result: the premise was wrong, and I wrote it

BL-046 named three quantities as "shared across the same three
implementations". Checked rather than assumed, only **one** is:

| quantity | research | knowledge-ledger | Gate | comparable? |
|---|---|---|---|---|
| `immunity_applicable` | `aggregation/root_vote.py` | — | `aggregator.py`, `reconcile.py` | **yes** |
| T5 floor | `formal/` (Lean, proofs) | — | prose in `README.md` / `RELEASE-GATES.md`, and a test comment | no — not an implemented named quantity in Gate |
| `unbound_root_weight` | — | — | four Gate modules | no — Gate-local |

`unbound_root_weight` appears in this repository in exactly four files, and all
four are documents written on 2026-08-08 naming it as an unchecked shared
quantity. It has never been implemented here. I listed three shared quantities
without verifying any of them were shared — the same failure XRP-101 documents,
committed in the act of scheduling the fix for it.

**Rule.** "Shared" is a claim about two codebases and requires checking two
codebases. A backlog item asserting a comparison is possible is itself an
unverified claim.

T5 and `unbound_root_weight` are therefore closed as **not comparable**, not as
agreeing. Nothing was measured about them.

## Second result: `immunity_applicable` — flags agree, behaviour does not

Both implementations compute the flag the same way in substance. Research sets
it false when a root carries conflicting assertions (R2, side separation);
Gate sets it false when any lineage edge joins different assertion values. On
the cases tested the two coincide, because an edge joining different values puts
that edge's root on both sides.

What they do next is not the same.

    one conflicted root, nothing else
      research: verdict=abstain   immunity_applicable=False
      gate:     decision=None     immunity_applicable=False      agree

    conflicted root + three clean supporters
      research: verdict=abstain   immunity_applicable=False
      gate:     decision=True     immunity_applicable=False      DIVERGE

Research **fails closed**: a conflicting root is detected and the verdict
abstains, per CE-11, because resolving the conflict either way makes the result
depend on input order. Gate records the flag and **returns a decision anyway**.

And nothing consults it. `immunity_applicable` is written in two places in Gate
and read in none; `gate.py` never mentions it. So `decide()` can return
`proceed` on evidence for which Theorem 1 provides no guarantee — the flag that
says so travels in a diagnostics dictionary nobody opens.

## Why this matters more than a flag mismatch would

Gate's stated principle, from its own README: *"no independent evidence is a
reason to ask a human, never a reason to proceed"*. The paper's §7 is stronger:
consequential systems *"must ... escalate evidential uncertainty rather than
translate it into permission"*.

`immunity_applicable=False` is precisely evidential uncertainty of the kind the
theorem was supposed to remove. Gate translates it into permission. This is not
a case where the two implementations chose different defensible readings — it is
Gate contradicting its own documented commitment, silently, on the input class
where the guarantee is void.

The attack shape is unremarkable, which is what makes it worth fixing: anything
that puts one root on both sides — a compromised issuer signing both ways, a
buggy adapter, a replayed claim re-parented — voids the immunity guarantee, and
Gate proceeds.

## Disposition

`immunity_applicable` divergence: repair proposed to Gate, escalating rather
than proceeding when the flag is false. It is a behaviour change to a published
product and therefore owner-gated; it is not merged by this finding.

T5 floor and `unbound_root_weight`: closed as not comparable. If Gate's T5 floor
is intended to implement the paper's T5, that correspondence is undocumented in
both repositories and is a separate, real gap — recorded as **BL-047** rather
than folded into a finding it was not measured by.
