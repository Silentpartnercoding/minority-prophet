# Capability Tournament v1 — Results

Status: completed

Run date: 2026-08-11

Preregistered protocol: `977766b5e2bed77cf6bab948e56ab3fcb49c2a05`

Isolated runner: `9888f25970186fb219a0d193a192f8d26f53ede1`

Frozen manifest: `sha256:e65d843669b1a0ead2a468ed8f05a44f3d74cf6e8184c05d2f697e427a8ec4ff`

## Claim boundary — read before comparing scores

This is a **constructed conformance study**, not a Minority Prophet lift study.
Tournament A and B both receive the complete supplied lineage. Tournament C is
the deterministic canonical rule, not the same model augmented with Minority
Prophet output. Therefore A-to-B and B-to-C differences do not estimate
provenance gain, Minority Prophet gain, H1, H2, or H3.

The unit of replication is the generated case: **eight cases**. Each case has
16 related propositions, yielding 128 within-case dispositions. The 128 values
are not 128 statistically independent trials. There is one clean replicate per
model and lane, so the table is descriptive; it has no repeated-seed confidence
intervals or paired significance tests.

## Question

When the same models receive the same difficult, fully specified evidence graphs,
how do unaided reasoning and freely chosen tool use compare with fixed standard
methods and the canonical Minority Prophet root vote?

This is a capability and conformance test. It asks whether a contestant selects
the disposition supported by the greatest number of distinct evidence origins.
It does not test whether an origin is honest, independent in the real world, or
ultimately true.

## Frozen task

- Eight cases, 16 propositions per case, and 128 scored decisions per lane.
- The 16 dispositions within a case share one generated packet and are not
  treated as independent replications.
- Between 201 and 524 shuffled records per case.
- Every contestant receives the identical public packet.
- Packets expose immediate `parent_record_id` links. A null parent denotes a
  direct evidence origin.
- No contestant receives the hidden reference, a root map, a root count, or
  precomputed root IDs.
- Two cases are exact distinct-origin ties and require `ABSTAIN`.
- A copied lineage can contain hundreds of records but contributes one origin.

## Lanes

- **A — reasoning only:** one model invocation per case; tools forbidden.
- **B — tools available:** the same model and packet; shell, scripts, packages,
  and web search permitted. The model chooses whether and how to use them.
- **C — canonical Minority Prophet:** a deterministic adapter resolves every
  record's supplied parent chain to its null-parent origin, then calls the pinned
  canonical root-vote implementation.
- **Fixed baselines:** archived standard methods run without case-specific
  tuning.

The AI lanes used medium reasoning and ephemeral Codex CLI sessions. A temporary
contestant home prevented host or repository instructions from entering the
model-visible prompt. All 48 AI trials completed. A emitted zero tool events. B
made 78 audited shell calls, no web searches, no package installations, no
outside-path accesses, and no hidden-answer or canonical-code accesses.

## Primary results

| Contestant | Correct | Accuracy | Exact cases | Wall time | Input / output tokens | API list-price proxy |
|---|---:|---:|---:|---:|---:|---:|
| Minority Prophet root vote | **128/128** | **100.0%** | **8/8** | **18.7 ms** | 0 / 0 | $0 model cost |
| GPT-5.6 Terra — reasoning | 116/128 | 90.6% | 5/8 | 365.0 s | 300,475 / 16,746 | $0.890 |
| GPT-5.6 Sol — reasoning | 102/128 | 79.7% | 5/8 | 512.2 s | 300,694 / 25,952 | $2.237 |
| Standard cluster vote | 96/128 | 75.0% | 6/8 | 9.5 ms | 0 / 0 | $0 model cost |
| GPT-5.6 Sol — tools | 69/128 | 53.9% | 4/8 | 351.1 s | 1,101,609 / 12,559 | $2.418 |
| GPT-5.6 Terra — tools | 68/128 | 53.1% | 4/8 | 245.8 s | 1,097,326 / 9,151 | $1.021 |
| GPT-5.6 Luna — tools | 35/128 | 27.3% | 2/8 | 496.3 s | 1,933,985 / 20,412 | $0.809 |
| GPT-5.6 Luna — reasoning | 16/128 | 12.5% | 1/8 | 296.0 s | 289,024 / 13,697 | $0.371 |

The price column is not an actual bill. The run used subscription-backed CLI
access. It applies the official 2026-08-11 API list prices to recorded tokens,
including cached-token rates and the long-context multiplier where applicable:
[Sol](https://developers.openai.com/api/docs/models/gpt-5.6-sol),
[Terra](https://developers.openai.com/api/docs/models/gpt-5.6-terra), and
[Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna).

## Preregistered Claude extension

The same frozen manifest, packets, prompts, lanes, hidden reference, and
scoring rule were subsequently applied to Claude Opus, Sonnet, and Haiku. This
is labeled an extension rather than part of the initial GPT/Codex grid.

| Contestant | Lane | Protocol score | Raw answers | Exact cases | Invalid trials | Wall time | Tool events |
|---|---|---:|---:|---:|---:|---:|---:|
| Claude Opus 5 | A | 106/128 | 106/128 | 6/8 | 0/8 | 478.0 s | 0 |
| Claude Sonnet 5 | B | 32/128 | 74/128 | 2/8 (4 raw) | 5/8 | 1,609.1 s | 27 |
| Claude Sonnet 5 | A | 23/128 | 23/128 | 0/8 | 0/8 | 809.7 s | 0 |
| Claude Opus 5 | B | 0/128 | 96/128 | 0/8 (6 raw) | 8/8 | 365.0 s | 35 |
| Claude Haiku 4.5 | A | 0/128 | 0/128 | 0/8 | 0/8 | 1,058.6 s | 0 |
| Claude Haiku 4.5 | B | 0/128 | 10/128 | 0/8 | 8/8 | 2,154.9 s | 59 |

The protocol score applies the preregistered rule that a failed or
workspace-boundary-violating trial counts as incorrect. Raw answer accuracy is
retained so that answer capability and lane compliance are not conflated. One
Haiku B trial reached the frozen 600-second timeout.

Read the [full Claude extension result](capability-tournament-v1-claude-extension-results.md),
[extension preregistration](capability-tournament-v1-claude-extension.md),
[v1.1 instrumentation amendment](capability-tournament-v1-claude-extension-v1.1-amendment.md),
or [machine-readable summary](capability-tournament-v1-claude-extension-summary.json).

At 18.7 milliseconds for all 128 decisions, canonical C was approximately
19,500 times faster than the most accurate AI lane, Terra reasoning-only. This
is descriptive telemetry from different execution paths on one local machine,
not a controlled serving benchmark or a general latency, capacity, cost, or
linear-scaling claim.

## Fixed-method results

| Method | Correct | Accuracy | Exact cases | Total time |
|---|---:|---:|---:|---:|
| Minority Prophet root vote | **128/128** | **100.0%** | **8/8** | 18.7 ms |
| Cluster vote | 96/128 | 75.0% | 6/8 | 9.5 ms |
| TruthFinder | 17/128 | 13.3% | 0/8 | 95.4 ms |
| Head majority | 12/128 | 9.4% | 0/8 | 1.9 ms |
| Accu-lite | 12/128 | 9.4% | 0/8 | 732.8 ms |
| Confidence-weighted vote | 6/128 | 4.7% | 0/8 | 4.2 ms |
| Dawid–Skene | 0/128 | 0.0% | 0/8 | 323.1 ms |

The canonical source was pinned before execution:

- Repository commit: `41911af5b372dbeec8513581d6970abcda4dd166`
- `aggregation/root_vote.py` SHA-256:
  `74ccf33aafc6de3281dee253558934a47f338e254c6a2e4b322556ff0db4328e`
- Archived baseline SHA-256:
  `c80ea6579d7bbe6061dd73b1d03666c175241d80eac38447aca11c0e3d34e3dd`

## What happened

The stronger models usually discovered the important first step: trace parent
links, collapse descendants, and avoid counting copies as independent evidence.
They often changed the second step, however. Instead of counting each distinct
origin equally, they summed confidence, used confidence log-odds, introduced an
unstated decisiveness threshold, or favored the strongest lineage. Those choices
caused failures on thin margins and exact ties.

Tool access automated the selected method; it did not ensure that the selected
method matched the scoring invariant. Compared with reasoning-only, tools
reduced correct decisions for Sol from 102 to 69 and for Terra from 116 to 68.
Tools improved Luna from 16 to 35, but the resulting lane remained far below the
fixed root-counting methods.

Cluster vote was the strongest simpler baseline. It recovered all six non-tie
cases but did not represent the two required abstention cases. That makes it a
useful low-cost comparator rather than a substitute for the complete declared
rule.

## What the result supports

Within a complete, immutable lineage graph whose direct-origin semantics are
known, a small deterministic implementation can apply distinct-origin counting
and exact abstention more reliably and cheaply than asking an LLM to infer an
aggregation rule from the same evidence.

Here, “more reliably and cheaply” is restricted to exact conformance and the
observed telemetry for this frozen eight-case packet. It does not establish a
stable model ranking, a population effect, or production economics.

The result also supports separating two jobs:

1. An adapter establishes the lineage relation supplied to the evaluator.
2. The evaluator applies a transparent, deterministic decision rule.

## What the result does not support

- It does not prove that a null-parent origin is honest or independently
  controlled.
- It does not detect missing, forged, or falsely separated roots.
- It does not prove ultimate truth.
- It does not show that every LLM-assisted workflow is inferior; no lane gave an
  LLM the Minority Prophet result as a tool.
- It does not establish stable model rankings. Each model/lane has one clean
  replicate, and hosted model aliases may change.
- It does not estimate the causal value of provenance visibility: both A and B
  already received the complete lineage.
- It does not estimate Minority Prophet value-add: C is deterministic code, not
  the same model receiving a non-answer-leaking Minority Prophet analysis.
- It does not test H1, H2, or H3, and the displayed C-minus-B difference must
  not be reported as “Minority Prophet gain.”
- It does not provide 128 independent trials; the primary replication unit is
  eight generated cases with 16 correlated dispositions per case.
- It does not test incomplete, false, fabricated, stale, or adversarial
  provenance. The lineage semantics are complete and truthful by construction.
- C's perfect score is conformance to a reference deliberately defined by the
  same distinct-origin invariant, not independent empirical validation of that
  invariant.

Read the separate
[adversarial validity review](capability-tournament-v1-adversarial-review.md)
or the [machine-readable claim boundary](capability-tournament-v1-summary.json).

## Audit history

The earlier Hard Gauntlet is not pooled with this result because its lanes did
not receive equivalent evidence and its C lane was not the pinned canonical
implementation. Two rehearsal executions of this tournament were also excluded
after command audit found host-level instruction leakage into contestant
prompts. Neither rehearsal contributed to the table above. The final run used a
prompt-inspected temporary contestant home and passed the command audit stated
above.

## Next confirmatory work

1. Run a separately frozen causal study on identical worlds and model versions:
   A receives claims only; B receives the exact claims plus provenance; C
   receives the exact B context plus non-answer-leaking Minority Prophet
   analysis.
2. Repeat paired model/world/condition trials across frozen seeds, report
   case-level uncertainty, and test A-to-B and B-to-C changes directly.
3. Retain standalone deterministic C as a conformance control, but do not
   substitute it for the same-model AI-plus-Minority-Prophet condition.
4. Run a separately preregistered root-integrity benchmark where forged or
   colluding origins carry observable verification signals.
5. Run an empirical domain benchmark whose outcomes are measured independently
   of the aggregation rule.
