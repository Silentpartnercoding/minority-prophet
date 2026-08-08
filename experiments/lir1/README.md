# LIR-1 — Lineage inference boundary

LIR-1 tests the open boundary left by Minority Prophet's declared-lineage
results: how much evidential value survives when ancestry must be inferred from
observable records rather than supplied as trusted metadata?

This track deliberately separates three questions:

1. **content truth** — whether a proposition is true;
2. **record descent** — whether one record descends from another; and
3. **evidence independence** — whether two records rest on causally distinct
   observations.

An observed retweet edge can answer the second question without proving the
third. A retraction can label a paper's status without proving the stance or
ancestry of every later citation. LIR-1 therefore records the basis and scope
of every label instead of calling all convenient labels “ground truth.”

The protocol is frozen in `PREREGISTRATION.md`. `DATASET-CATALOG.md` records
source feasibility and the permitted role of each dataset. Per-source
acquisition and labeling rules live under `data/`. No acquired raw data is
committed unless its license permits redistribution.

The controlled LLM echo sub-study is registered separately at
`llm_echo/PREREGISTRATION.md`. Its protocol and future public code live in that
directory; private seeds, labels, receipts, and raw model responses live under
the Git-ignored `artifacts/lir1/llm_echo/` boundary.

## Status

PHEME-R2 has a canonical boundary result under `results/lir1-pheme-r2-v0.1/`.
The controlled LLM echo study is preregistered. Its 12 development and 36
confirmatory cases have been generated and sealed; public hash commitments are
in `llm_echo/INVENTORY-COMMITMENTS.json`. No model has been called.
