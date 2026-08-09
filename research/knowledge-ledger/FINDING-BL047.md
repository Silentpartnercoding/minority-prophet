# BL-047 — Gate's "T5 floor" names a theorem it does not implement

Opened by RUN-20260808-2 when BL-046 found that T5 appears in both repositories
and had never been compared. Executed 2026-08-09.

## There is nothing to compare

Gate mentions a **T5 floor** three times — `README.md`, `RELEASE-GATES.md`, and a
docstring in `tests/test_config_invariants.py`. Searched for an implementation:

    grep -rn "floor|T5" minority_prophet/   ->   no matches

No variable, no function, no threshold by that name. The only threshold in the
product is `min_flip_budget`, the policy floor `decide()` compares
`flip_budget` against. So the question BL-047 was opened to ask — does Gate's T5
floor implement the paper's T5? — has the answer **no, because Gate implements
no T5 floor**.

That alone would be a documentation defect. The substantive finding is what
happens if a reader assumes `min_flip_budget` *is* the T5 floor, which the
prose invites: *"Matching bound roots determine `flip_budget` and the T5 safety
floor."*

## The paper's T5, in full

> If `W` and `W'` are side-consistent, have the **same assertions**, and their
> root sets differ by at most `k` elements in total, then a verdict with
> `|margin W| > k` survives unchanged; and one with `|margin W| ≥ k` cannot be
> reversed.

Two hypotheses. Side-consistency, and **equal assertions**. The second is not
decoration: `PROOFS.md` records it as *new and necessary*, with
`T5_needs_assert_fixed` compiling a witness where an identical root set — zero
root-set error — still flips a margin-2 verdict under a single side conversion.
The un-hypothesised version is **falsified as CE-02**.

## What that means for a deployer, measured

Five supporting roots against two opposing: margin 3. The natural reading of a
"T5 floor" is *"margin 3 > k, so k = 2 errors are survivable; set
`min_flip_budget = 2`."*

    A) k root-set errors that PRESERVE assertions  — T5's actual scope
       1 supporting root removed: margin 2, decision True
       2 supporting roots removed: margin 1, decision True     survives

    B) the same k, errors that CHANGE assertions   — compromise
       1 supporting root flipped: margin 1, decision True
       2 supporting roots flipped: margin 1, decision False    REVERSED

Same `k`. T5 holds in (A) and says nothing about (B), because (B) violates the
equal-assertions hypothesis. A deployer who sets a floor from T5 is protected
against the benign class — misattribution, a dropped or duplicated root — and is
exactly wrong about the adversarial one.

**This is XRP-101 reached by a second route.** That finding measured the same 2×
overconfidence through `flip_budget` versus `conversions_to_reverse`. Here it
arrives through a theorem name attached to a threshold the theorem does not
license. The first route was repaired in gate#7 by reporting both prices; this
one survives because the docs still borrow T5's authority for the wrong attack.

## Disposition

**Not "not comparable" — a real defect, repaired.** BL-046 closed T5 as
non-comparable because Gate implemented nothing by that name. That was accurate
and incomplete: an unimplemented theorem reference is not harmless when it is
the stated justification for a security threshold.

Gate's documentation is corrected to say what the threshold is (a policy floor
on `flip_budget`), what T5 actually covers (assertion-preserving root-set
error), and which number prices compromise (`conversions_to_reverse`). The
theorem name is no longer attached to a guarantee it does not give.

Nothing in Gate's behaviour changes; the defect was entirely in what the
documentation claimed the behaviour meant.

## The pattern, now three for three

Every audit of "the same name in two repositories" has found a real defect:

| audit | result |
|---|---|
| XRP-101 | `flip_budget` priced the wrong attack; ~2× overconfident |
| BL-046 | `immunity_applicable` computed correctly and read by nothing |
| BL-047 | `T5` named as a floor, implemented nowhere, licensing a threshold it does not cover |

A shared name is not a shared definition, and the gap is invisible from inside
either repository. This is the rule XRP-101 stated; three independent
confirmations is enough to stop treating it as a hypothesis.
