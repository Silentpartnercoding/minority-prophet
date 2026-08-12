# Capability Tournament v1 — preregistration

Status: frozen before any model execution.

Frozen: 2026-08-10 (America/Los_Angeles)

## Question

When every contestant receives the same difficult evidence graph, can an AI
recover the best-supported dispositions by reasoning alone, can a tool-using AI
do so more reliably or efficiently, and how do both compare with conventional
methods and the canonical Minority Prophet root vote?

This is a finite lineage-aggregation contest. It is not a test of ultimate
truth discovery.

## Identical challenge

- Generator seed: `2026081000`
- Cases: 8
- Propositions per case: 16
- Total scored dispositions per contestant: 128
- Manifest hash: `sha256:e65d843669b1a0ead2a468ed8f05a44f3d74cf6e8184c05d2f697e427a8ec4ff`
- Every lane consumes the exact same immutable `public_packet` bytes.
- Records expose only their immediate `parent_record_id`; no contestant is
  supplied a hidden root list or precomputed root count.
- Parent links are complete, acyclic, and fixed by construction. A null parent
  is an unambiguous direct origin.
- No fake roots, missing lineage, root-control inference, freshness, revocation,
  authority, or external-world verification is scored.
- IDs and answer labels are opaque and counterbalanced.

Difficulty comes only from in-scope operations: 201–524 shuffled records per
case, deep/broad copy trees, deceptive confidence, distributed copy swarms,
thin distinct-root margins, 16 simultaneous propositions, and exact root ties.

## Contestants

### A — AI reasoning only

The model receives the complete packet inline. Shell, files, retrieval, web,
MCP, and all other tools are disabled. Any tool event invalidates that trial.

### B — the same AI with tools

The same model receives the identical packet. It may use live web search, a
shell, scripts, calculations, installed tools, or install a method if the
isolated environment permits it. The packet is also placed in its ephemeral
working directory for computation. Tool calls and commands are audited. It is
not told about Minority Prophet and receives no Minority Prophet output.

### C — canonical Minority Prophet

The identical raw packet enters a deterministic public adapter that follows the
supplied parent links to their null-parent origins. The derived root IDs then
enter the pinned canonical `aggregation/root_vote.py` implementation. C is not
given a hidden root map.

Pinned canonical repository commit:
`41911af5b372dbeec8513581d6970abcda4dd166`

Pinned `aggregation/root_vote.py` SHA-256:
`74ccf33aafc6de3281dee253558934a47f338e254c6a2e4b322556ff0db4328e`

### Conventional fixed methods

- record head-count majority;
- confidence-weighted record vote;
- Dawid–Skene;
- TruthFinder-style iterative reliability;
- dependency-discounted Accu-style voting;
- near-identical answer-vector cluster vote.

The reference implementations are pinned at canonical commit
`41911af5b372dbeec8513581d6970abcda4dd166`; `exp008_shootout.py` SHA-256 is
`c80ea6579d7bbe6061dd73b1d03666c175241d80eac38447aca11c0e3d34e3dd`.

## Model grid

Initial matched grid using locally authenticated subscription CLI execution:

- `gpt-5.6-sol`
- `gpt-5.6-terra`
- `gpt-5.6-luna`

A and B use the same exact model and medium reasoning effort. Each call is
ephemeral and stateless. Additional providers require an equally isolated and
auditable tool lane and must be reported as an extension, not silently mixed
into the initial grid.

## Output and scoring

Each contestant returns exactly 16 values from `A`, `B`, or `ABSTAIN` plus a
brief method description. The frozen reference is the distinct-origin support
disposition constructed before execution; exact ties require `ABSTAIN`.

Primary:

- correct dispositions out of 128;
- exact cases out of 8;
- accuracy on answerable and tied propositions;
- parse/tool-policy failures, counted incorrect and retained.

Efficiency:

- elapsed wall time;
- input, output, and cached tokens when reported;
- tool event count and tool types;
- provider-reported cost when available;
- a clearly labeled list-price proxy when actual incremental cost is not
  available;
- correct dispositions per second and per million tokens.

No result may be described as proving ultimate truth, root legitimacy, or
performance outside the frozen complete-lineage competition.

## Invalid predecessor

Hard Gauntlet v1 is preserved but invalid for this comparison because it varied
the information supplied across conditions, used a substitute implementation,
and tested out-of-scope dimensions. Its results cannot be pooled with this run.
