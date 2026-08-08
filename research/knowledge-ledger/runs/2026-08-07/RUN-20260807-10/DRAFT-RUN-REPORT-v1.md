# DRAFT RUN REPORT v1 — RUN-20260807-10

**All four pieces completed.** Suite 187 passing; KL-000 untouched at
v1.3.0; C11/C12 reproducing; four chains verifying; eleven kernels seeded;
nothing pushed.

## Piece 1 — flip_budget surfaced, receipt untouched — COMPLETED

`knowledge_ledger/presentation.py` computes `flip_budget = margin` (net
per-side root-gain units, Theorem 4) as a registered derived presentation
value (`KL-000/FLIP-BUDGET-PRESENTATION.md`). **CE-03 registered**: reported
beside `conversionsToReverse`, never instead — a conversion is two units of
net gain, so flip_budget alone overstates attacker cost ~2× — and the API
structurally has no lone-flip_budget presentation. **Pass condition met and
tested**: C11/C12 byte-identical with the module in use; evaluator and
package-init hashes unchanged; derivation verified on all twelve fixtures
and 2,000 enumerated receipts. The traceability map's one
receipt-contradicts-paper finding (RCP-101) is closed at the presentation
layer; R3's both-metrics promise now reads "tested" under the recomputing
enforcement.

## Piece 2 — paper v1.0.4 — COMPLETED

Three marked additions per the errata convention ([E6]–[E8] in
`papers/ERRATA.md`), v1.0.3 preserved byte-for-byte, no theorem, proof, or
result changed: **[E6]** every published result ran at **τ = 0** — the
scope condition TRC-101 found undeclared; **[E7]** search-ledger location
identifiers MUST be pairwise distinct — the paper's own thesis had a gap on
the search ledger, both implementations refused duplicates unprompted, and
I11 is now credited; **[E8]** Theorem 1 is proved and, in the evaluated
schema, only shadow-tested — one line where a reader of the theorem finds
it. (PPR-101, the |margin| notation, remains the owner's — not this run's
repair.)

## Piece 3 — conformance profile — COMPLETED

`research/knowledge-ledger/CONFORMANCE-PROFILE-v1.md`: the five
specification-local engineering rules (P1–P5: I4, I6, I7, I9, receipt
serialisation) with normative statements, why each is specification-local,
and the program evidence — including P4's honest note that I9's entire
evidence is adversarial. A cross-reference to internal tooling was written into the profile on an operator brief's instruction and REMOVED before any push (commit ce07daf): the profile is destined for public product repositories, and that reference described what the owner probes for in other projects rather than what this codebase guarantees. No substance was lost; each rule already carried its statement, its locality reason, and its KL-000 evidence.

## Piece 4 — LIN-000: Theorem 1 and Lemma 1 end-to-end — COMPLETED

Registered before implementation (`lineage/REGISTRATION.md`: declared
exhaustive bound **50,362** = Σ k!·2^k for k≤6, asserted before evaluation;
frozen seed 20260808 **with the draw schedule registered** — the F11
lesson). Result: **passed.**

- **Theorem 1**: zero violations across **23,952 + 975,782** valid single
  reparentings (exhaustive + 100,000 randomized worlds) — and the
  protection provably does **not** extend past its preconditions:
  root-set-breaking rewirings change verdicts in 3,194 / 20,789 worlds;
  side-consistency-breaking rewirings likewise. A test that only exercises
  the satisfied case cannot fail; these can and don't.
- **Lemma 1**: zero violations on all 5,912 + 54,548 side-consistent
  worlds; 44,450 + 45,452 side-inconsistent negative witnesses, including
  the pinned two-claim world exhibiting the paper's
  one-root-on-both-sides scope-note phenomenon.
- **Checker power**: both must-fail ablations caught (LB-shallow: 4,658 +
  40,452 worlds; LB-claimcount: 5,786 + 47,460).

Two of the paper's four theorems left this program untested this morning;
none do tonight — Lemma 1 and Theorem 1 via LIN-000 (annotated in the
traceability map; KL-000's own statuses unchanged), Theorems 2 and 3 via
KL-000 since v1.0.0. No kernel state advanced; the bound reached is the
bound declared.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
