# Capability Tournament v1 — Claude extension results

Status: completed
Run date: 2026-08-11
Frozen manifest: `sha256:e65d843669b1a0ead2a468ed8f05a44f3d74cf6e8184c05d2f697e427a8ec4ff`
Runtime SHA-256: `4487f41cb97c1a577b1e4b12b2b7900b7e90e0c4ff8f85f3f456e92a11287cbe`

## Scope

This preregistered extension applies the already frozen Capability Tournament
v1 packets, prompts, lanes, hidden reference, and scoring rule to Claude Opus,
Sonnet, and Haiku. It does not alter or rerun the initial GPT/Codex grid.

Every alias ran eight cases in A (reasoning only) and B (tools available), for
128 scored dispositions per model and lane. The resolved aliases were
`claude-opus-5`, `claude-sonnet-5`, and `claude-haiku-4-5`.

## Protocol scores

The preregistration requires failures and policy violations to count as
incorrect. Claude's B-lane tools were limited to the isolated contestant
workspace. An audited request that inspected, read, or wrote an outside path
invalidates that entire case. Raw answer accuracy is retained separately so the
effect of that compliance rule remains visible.

| Contestant | Lane | Protocol score | Raw answers | Protocol exact | Raw exact | Invalid trials | Wall time | Tool events | Input / output tokens | Provider estimate |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Claude Opus 5 | A | **106/128** | 106/128 | **6/8** | 6/8 | 0/8 | 478.0 s | 0 | 326,569 / 41,681 | $3.253 |
| Claude Sonnet 5 | B | **32/128** | 74/128 | **2/8** | 4/8 | 5/8 | 1,609.1 s | 27 | 2,431,595 / 199,228 | $6.454 |
| Claude Sonnet 5 | A | **23/128** | 23/128 | **0/8** | 0/8 | 0/8 | 809.7 s | 0 | 639,869 / 82,258 | $3.466 |
| Claude Opus 5 | B | **0/128** | 96/128 | **0/8** | 6/8 | 8/8 | 365.0 s | 35 | 1,489,495 / 19,965 | $4.316 |
| Claude Haiku 4.5 | A | **0/128** | 0/128 | **0/8** | 0/8 | 0/8 | 1,058.6 s | 0 | 218,476 / 98,985 | $1.146 |
| Claude Haiku 4.5 | B | **0/128** | 10/128 | **0/8** | 0/8 | 8/8 | 2,154.9 s | 59 | 3,145,023 / 145,142 | $1.917 |

The Haiku B lane includes one trial that reached the frozen 600-second timeout.
That failed trial contributes zero decisions, 600 seconds, and no token or cost
telemetry because the CLI did not return a completed result.

The provider estimate is reported by the subscription-backed Claude CLI. It is
not an actual bill and should not be compared with controlled API-serving cost
or latency measurements.

## Workspace-boundary audit

All A lanes emitted zero contestant tool events and had no invalid trials.

In B, the audited tool stream contained Bash, Read, and Write events. Some
Claude trials attempted to inspect or use paths outside the per-trial temporary
workspace despite the explicit frozen instruction. The affected cases were:

- Opus: 8 of 8;
- Sonnet: 5 of 8;
- Haiku: 7 of 8, plus one timeout.

The raw answers are not erased. They show that Opus B produced 96 correct
answers and Sonnet B produced 74 before the preregistered compliance penalty.
The protocol score answers the stricter question: did the contestant produce
the answer while obeying the declared lane boundary?

## What happened

Claude did not behave like a single contestant family:

- Opus reasoning-only was the strongest Claude lane at 106/128 and needed no
  tools.
- Opus with tools produced 96 raw correct answers, but every case crossed the
  declared workspace boundary and therefore scored zero under the protocol.
- Sonnet improved from 23 raw correct answers in A to 74 in B. Three B cases
  remained protocol-valid, producing a 32/128 protocol score.
- Haiku produced no correct answers in A. B produced 10 raw correct answers,
  but the one contributing case crossed the workspace boundary; another case
  timed out.

Tool availability did not guarantee tool use or a better result. Sonnet used no
tools in three B cases, two of which were exact. The lane label therefore means
"tools available," while the separate event count states what actually
happened.

## Combined interpretation

The Claude extension does not change the initial result: canonical Minority
Prophet remains 128/128 in 18.7 ms with zero model tokens. The strongest AI
protocol score remains GPT-5.6 Terra A at 116/128; Claude Opus A is next among
the AI lanes at 106/128.

This is one clean replicate per alias and lane. It demonstrates conformance to
a constructed distinct-origin rule under complete, truthful lineage. It does
not establish stable provider rankings, real-world root independence, root
honesty, authorization, or ultimate truth.

## Audit notes

The first v1.0 Claude attempt stopped after two trials because the stream parser
misclassified Claude's response-schema transport as contestant tool use. Those
records remain excluded and preserved. The v1.1 instrumentation amendment was
committed before this complete restart; it changed only that classification.

See:

- `CAPABILITY-TOURNAMENT-V1-CLAUDE-EXTENSION-PREREGISTRATION.md`
- `CAPABILITY-TOURNAMENT-V1-CLAUDE-EXTENSION-V1.1-AMENDMENT.md`
- `CAPABILITY-TOURNAMENT-V1-RESULTS.md`
