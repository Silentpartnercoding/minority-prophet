# DRAFT RUN REPORT v1 — RUN-20260807-9

The provenance break is verified, corrected in the record, and closed by an
enforced traceability rule. The plain counts the brief demanded:

**Of the paper's 14 in-scope claims, KL-000 fully tests 6 and partially
tests 4; 4 are untested. Of KL-000's 19 normative rules, 7 have no paper
basis** (declared specification-local with reasons; 6 more are partial
derivations). One place the receipt **contradicts** the paper. All counts
are machine-checked against the map's entries, not asserted.

## The finding, verified then extended

Both briefed facts held: the paper's §3 defines the aggregator ("returns 1
if |S₁| > |S₀|, 0 if reversed, **abstaining on ties**"), and no KL-000
specification of any version cites the paper (zero occurrences,
grep-verified). The audit found the break is **wider than briefed**: §3 also
defines *"The **margin** is ||S₁| − |S₀||"* — explicitly absolute — and
Theorem 4 [E2] publishes *"reversal costs ⌊margin/2⌋+1"*, the exact
`conversionsToReverse` formula the record calls "reverse-engineered, defined
nowhere".

## The determinations, with quotes

- **R1: settled by the paper.** Ties abstain; minorities take the opposing
  verdict. The "could defensibly have gone the other way" characterisation
  was false as to derivability — the rule was derivable, the specification
  package severed the chain, and the 22,440-world divergence was one
  implementation contradicting a published definition. Corrected in
  PROTOCOL-v1.1.0.md **Amendment 1**, registered text preserved. The
  implementer's reading remains defensible *given the package it received* —
  which is the point.
- **R5.2: settled by the paper** (margin defined absolute). Corrected in
  PROTOCOL-v1.2.0.md **Amendment 3**. Bonus: **F4 settled for decisive
  worlds** by Theorem 4 [E2]; the margin-0/empty-ledger edge stays outside
  the theorem and the implementer's objection stands exactly there.
- **A1: genuinely open in the paper** — the RUN-8 owner-decision
  characterisation **survives** the audit. **A2: stays an owner decision**,
  now with paper evidence recorded beside it (§3's verdict function has no
  coverage input; §8 imposes coverage on absence only — the registered
  reading matches; the alternative has no paper basis).
- No behaviour changed anywhere: provenance only, appended never rewritten,
  all four chains verifying after.

## What was built

**TRC-101** (registered, `schemas/traceability-TRC-101.md`): every
normative rule cites the paper — *with a verbatim quote at the citation
site* — or declares itself specification-local with a reason.

**The map** (`KL-000/TRACEABILITY-v1.3.0.json`), both directions. Notable
entries: I12 now cites the definitions it enforces (the R1/R5.2 correction
in enforceable form); I7 is declared as a strictly weaker shadow of
Theorem 1, not a test of it; the previously undeclared τ=0
no-abstention-threshold simplification is declared for the first time.
Untested paper claims, named: the abstention threshold, Lemma 1, Theorem 1
(both need a lineage-bearing schema), and **R1 root integrity** (declared
out of scope since v1.0.0; the ADV-002/004/006 gap). **The contradiction:**
§6 R3 promises `flip_budget` and `conversions_to_reverse` "both are
surfaced with every verdict" — KL-000's receipt has never carried
`flip_budget`. SCH-005 recorded this against RESEARCH-DIRECTION; the map
traces it to its paper root. Repair is digest-moving and the owner's
(BL-040, joining the BL-026/BL-037 family).

**Enforcement** (`tests/test_traceability.py`, 55 checks): citation-or-
declaration for every rule; verbatim-quote verification against the paper's
bytes — **which caught two of this run's own paraphrased quotes on first
execution**; completeness against the registered invariant list; explicit
status for every paper claim; summary counts recomputed, never trusted
(the DOC-102 lesson mechanized).

## For the owner, not repaired here

A paper notation finding (PPR-101): Theorem 4's T5-correction writes
"|margin| > k" — bars on a quantity §3 already defines as absolute. Minor,
internal to the paper, owner's to fix or leave.

## What did not move

Suite **172 passed** (124 inherited + 48 new; 7 skips are the quote-checker
passing over specification-local entries, by design); KL-000
`adversarial-passed` at v1.3.0; eleven kernels `seeded`; four chains
verify; no canonical record, PUBLIC-CLAIMS, or paper edit; nothing pushed.
The first-transaction gate remains **NOT REACHED**.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
