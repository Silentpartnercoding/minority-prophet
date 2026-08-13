# Closed-world real-model pilot

Status: **DEMO — not eligible for the official leaderboard**

Run: `cli-pilot-v4:3:gpt-5.6-sol:sonnet`

The pilot used three deterministically generated majority-copying worlds. Each world was evaluated under the same three conditions by the authenticated Codex and Claude subscription CLIs. Provider tools, retrieval, web access, and repository context were disabled or audited. All 18 expected trials completed, all responses parsed, world hashes matched, and the verification gate passed.

| Runtime | Raw claims | + provenance | + Minority Prophet |
|---|---:|---:|---:|
| GPT-5.6-sol through Codex CLI | 0/3 | 3/3 | 3/3 |
| Claude Sonnet 5 through Claude CLI | 0/3 | 3/3 | 3/3 |

This result shows a clear provenance effect in this small scenario family. It does **not** show additional truth-recovery lift from Minority Prophet beyond raw provenance: Condition C minus Condition B was zero for both runtimes.

The pilot did show a directional response-efficiency difference:

| Runtime | Provenance average | Minority Prophet average |
|---|---:|---:|
| Codex CLI | 11.88 s · 201 output tokens | 7.31 s · 150 output tokens |
| Claude CLI | 19.21 s · 1,876 output tokens | 16.02 s · 1,728 output tokens |

Those timing and token differences are descriptive only. Three worlds are too few for an efficiency claim, CLI system-context overhead differs substantially between providers, and Claude's provider-reported cost estimate was slightly higher under Condition C despite the shorter response. A fair cost comparison requires direct, version-pinned API adapters or a separately calibrated runtime-overhead model.

The next high-value test is not more copies of this easy lineage world. It is a preregistered harder set where raw provenance is available but difficult to interpret: partial correlation, multiple roots on both sides, missing or forged edges, cycles, temporal conflicts, and calibrated abstention cases. That is where Minority Prophet can either demonstrate value beyond provenance or fail honestly.
