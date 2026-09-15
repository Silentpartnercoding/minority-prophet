# Knowledge-ledger research program

Status: **active research program.** Experiments have run, stopped, and failed;
the index below gives each one's recorded status. Only artifacts listed as
completed in the canonical registry may be described as results. Plans,
fixtures, expected outputs, simulations, and failed runs are not results.

## Start here

1. [`RESEARCH-METHOD.md`](RESEARCH-METHOD.md) defines the public method and claim rules.
2. [`EXPERIMENT-REGISTRY.json`](EXPERIMENT-REGISTRY.json) is the frozen seed registry for
   KL-000 to KL-011, pinned by `tests/test_knowledge_ledger_program.py`. It is a
   record of what was seeded, not a current status list. KL-012 onward are
   registered by their own frozen collection rules and are listed in the index below.
3. [`experiments/`](experiments/) contains versioned protocols, statuses, and results.
4. [`interoperability/`](interoperability/) contains reference conformance fixtures and cross-system acceptance criteria.
5. `knowledge_ledger.transaction` is a deliberately small reference evaluator.
6. [`CROSS-PROGRAMME-RECONCILIATION.md`](CROSS-PROGRAMME-RECONCILIATION.md) records
   gates that other series in this repository already answer. **Read it before
   concluding an experiment is blocked**: six gates in the KL-001..011 ladder
   describe work the DRI, H- and LIR-series have done, and the ladder does not
   know. [`GATE-COVERAGE.json`](GATE-COVERAGE.json) is its machine-readable form,
   enforced by `scripts/check_gate_coverage.py`.

## Experiment index

Compiled from each experiment's own status-bearing files on 2026-09-14. The
wording is quoted from those files; follow the link before citing anything.

| Experiment | Recorded status | Source |
|---|---|---|
| KL-000 | adversarial-passed | [`STATUS.json`](experiments/KL-000/STATUS.json) |
| KL-001 | fixture-passed | [`STATUS.json`](experiments/KL-001/STATUS.json) |
| KL-002 | seeded | [`STATUS.json`](experiments/KL-002/STATUS.json) |
| KL-003 | seeded | [`STATUS.json`](experiments/KL-003/STATUS.json) |
| KL-004 | seeded | [`STATUS.json`](experiments/KL-004/STATUS.json) |
| KL-005 | seeded | [`STATUS.json`](experiments/KL-005/STATUS.json) |
| KL-006 | seeded | [`STATUS.json`](experiments/KL-006/STATUS.json) |
| KL-007 | seeded | [`STATUS.json`](experiments/KL-007/STATUS.json) |
| KL-008 | seeded | [`STATUS.json`](experiments/KL-008/STATUS.json) |
| KL-009 | seeded | [`STATUS.json`](experiments/KL-009/STATUS.json) |
| KL-010 | seeded | [`STATUS.json`](experiments/KL-010/STATUS.json) |
| KL-011 | fixture-passed | [`STATUS.json`](experiments/KL-011/STATUS.json) |
| KL-012 | KL-012 — funding-cluster membership does not reproducibly predict token outcome | [`FINDING-KL012.md`](experiments/KL-012/FINDING-KL012.md) |
| KL-013 | v0.2 collection-rule-frozen, not run; v0.1 stopped on its own effectRequires (0 winners against a required 30) | [`COLLECTION-SPEC-v0.2.json`](experiments/KL-013/COLLECTION-SPEC-v0.2.json) |
| KL-014 | HRI-1 is blocked structurally, not for want of resources | [`HRI1-BLOCKER-20260816.md`](experiments/KL-014/HRI1-BLOCKER-20260816.md) |
| KL-015 | collection-rule-frozen; blocked through its declared dependency on HRI-1 | [`DECISION-20260813.md`](experiments/KL-014/DECISION-20260813.md) |
| KL-016 | v0.1 stopped-unanswerable-on-this-corpus; v0.2 primary-endpoint-measured; secondary endpoint not run | [`STATUS.json`](experiments/KL-016/STATUS.json) |
| KL-017 | KL-017 — stopped as not executable, before producing any number | [`FINDING-KL017-STOP.md`](experiments/KL-017/FINDING-KL017-STOP.md) |
| KL-018 | KL-018 — the registered endpoint passed, and its own control refuted it | [`FINDING-KL018.md`](experiments/KL-018/FINDING-KL018.md) |
| KL-019 | KL-019 — registered, never executed | [`STATUS.md`](experiments/KL-019/STATUS.md) |

**Renumbering.** KL-017, KL-018 and KL-019 were written on 12–13 August as
KL-014, KL-015 and KL-016 on the branch `agent/kl014-copytrade`, and renumbered
when they reached main on 2026-09-14 because main had already assigned those
numbers. Residue of the old numbers remains: the JSON keys `whyKL014Failed` and
`notInheritedFromKL014` in KL-018's spec refer to KL-017, `whyKL015Failed` in
KL-019's spec refers to KL-018, and the scripts read scratch data from `kl014/`
(KL-017) and `kl015/` (KL-018). Their preregistration pins are commits on that
branch and are not ancestors of main. Separately, the "KL-017" in
`experiments/KL-016/FEASIBILITY-v0.1.md` is a hypothetical follow-up written on
17 August, before the rescue, and is unrelated to the KL-017 above.

## Program invariants

- Copies never create independent evidence.
- Search coverage and evidential independence are separate quantities.
- Incomplete coverage never becomes proof of absence.
- One root cannot count on opposing sides.
- Root-flow units and adversary actions are reported separately.
- Uncertainty widens or produces abstention; it never creates permission.
- No safety-critical experiment controls a live medical, legal, governmental,
  financial, or autonomous decision.
- Every claimed result is reproducible from immutable inputs, code, environment,
  and a recorded commit.

## Current milestone

`reference-conformance-001` is a local conformance artifact. It demonstrates that four
searched locations out of five produce `not_established`, even when several
reports agree. It is not a cross-system result and is not evidence
that the method improves real-world truth recovery.
