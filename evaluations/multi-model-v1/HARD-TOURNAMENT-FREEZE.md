# Hard Gauntlet v1 — preregistration

Status: preregistered development experiment. It is not an official leaderboard or a product-performance claim.

Frozen before model execution: 2026-08-10 (America/Los_Angeles)

## Question

Do raw model judgment, declared provenance, and declared provenance plus Minority Prophet behave differently when the evidence is designed to attack each method rather than flatter it?

## Fixed design

- Benchmark version: `0.2.0-hard-dev`
- Manifest hash: `sha256:f8486f9b549499a3cd13a5d50e9f75c2d43b2495d992d2b18151379c05678b78`
- Generator seed: `880000`
- Worlds: 8, one per scenario family
- Conditions: same-world A/B/C
  - A: claims without structured provenance or evidence metadata
  - B: the same claims plus declared provenance and evidence metadata
  - C: the same B record plus Minority Prophet structural analysis
- Tools, files, memory, MCP, retrieval, and network access: disabled and audited where the local CLI exposes events
- Temperature: 0
- Reasoning effort: medium
- Maximum response tokens: 500
- Result namespace: `DEMO`

The scenario families are copied majority, roots under shared control, one observation laundered through many roots, stale evidence after a state change, revoked authority, balanced ambiguity, incomplete lineage, and citation cycles with no root.

Five worlds require an answer. Three require abstention. Four are constructed so the current root-count recommendation ranks the wrong answer first. This is deliberate: Minority Prophet is under test, not treated as an oracle.

## Model grid

The compatibility probe will attempt these locally authenticated subscription CLI configurations:

- OpenAI Codex CLI: `gpt-5.6-sol`, `gpt-5.6-terra`, `gpt-5.6-luna`
- Anthropic Claude CLI: `opus`, `sonnet`, `haiku`

Every configuration that completes the closed-world structured-output probe will enter the tournament. A failed probe is recorded and excluded; it is not silently replaced. No API keys or paid API endpoints are used.

## Outcomes

Primary descriptive outcomes, reported per model and condition:

- total correct decisions out of 8;
- correct answers on the five answerable worlds;
- correct abstentions on the three abstention worlds;
- result by scenario family;
- paired B minus A and C minus B accuracy changes.

Efficiency telemetry is secondary and descriptive only: execution time, input/output tokens when reported, and provider-reported cost when present. Subscription execution does not establish incremental dollar cost.

## Interpretation rules

- C better than B means the current Minority Prophet output helped on this finite gauntlet.
- C equal to B means no measured accuracy benefit on this finite gauntlet.
- C worse than B means the current output harmed decisions and identifies a system defect or integration hazard.
- A strong showing does not prove provenance is useless; B or C must improve paired decisions to support a benefit claim here.
- Eight deterministic worlds are a hard diagnostic, not enough for population-level significance or a general model ranking.
- Parse failures and closed-world violations count as failed trials and remain visible.
- Results will not change the frozen worlds, expected dispositions, prompts, scoring rule, or model eligibility rule. Any remediation is a later experiment with a new version.

## Reproduction

```bash
npm test
npm run probe:models
npm run run:hard -- 1
```

The runtime state is immutable and resumable locally but intentionally ignored by Git. A sanitized report may be committed after verification.
