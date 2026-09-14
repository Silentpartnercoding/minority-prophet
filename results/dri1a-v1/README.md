# DRI-1A preregistered candidate result

**Outcome:** the preregistered joint criterion was **not supported**.

This is the first bounded local run of the declared-policy arm of
decision-relative independence. It used all 8,192 frozen synthetic worlds. The
semantic result was identical across two executions:

```text
c63097e8ada155aba93e2ceb310dca771285114a2581998515a8fbdfa85487a2
```

The generated world manifest was:

```text
a940c3ea06f0b310c12a3cbb1c7d17ef805b93338f42334a9afe70e6a18199f1
```

The content SHA-256 of `result.json` when this record was captured was:

```text
ec8b2428f459af9f80b8372935d5d0eb1ed1d22aefc30aa0864ec00b55da4c6c
```

## Frozen lineage

- preregistration commit: `59c83ff948ddfccf279d8b07c16caba63ae1ddf6`
- frozen runner commit: `1b16f9ca62dd17cfde18701a237d85489dfa443b`
- preregistration SHA-256:
  `6f47faa5aaa3d856e7d9e990b40b086288a9d05507a2b7ec053f85ef720248ce`
- execution-config SHA-256:
  `42078e86815cd5b806e1a44f23aaff4b002f94af7193b5c422adf0c948bb7d1b`

The runner refuses changed protocol/config bytes. No failed criterion was tuned,
dropped, or rerun under a replacement threshold.

## Record classification

This result is **not canonical** under `CANONICAL-RECORDS.md`. The protocol and
runner were frozen before inspectable outcome metrics, but the pre-run package
did not include a lifecycle record, registered uncertainty intervals,
multiple-testing treatment, or the complete environment/intervention manifest
required for canonical promotion. Those omissions cannot be repaired after the
outcome is known. The result is preserved as an adverse candidate diagnostic
and is not added to the canonical registry or public-claims ledger.

## Primary results

| Method | Correct settlement | False settlement | Abstention | Minority-reversal recovery |
|---|---:|---:|---:|---:|
| Decision-relative oracle | 90.99% | 9.01% | 0.00% | 100.00% |
| Explicit rules engine | 90.99% | 9.01% | 0.00% | 100.00% |
| Agent headcount | 60.78% | 39.22% | 0.00% | 0.00% |
| Fixed machine | 68.32% | 31.68% | 0.00% | 24.97% |
| Fixed controller | 64.33% | 22.08% | 13.59% | 27.35% |
| Fixed evidence origin | 64.48% | 22.07% | 13.45% | 27.56% |
| Fixed upstream component | 56.51% | 3.26% | 40.23% | 32.77% |

The decision-relative policy improved correct settlement by 22.67 percentage
points over the best fixed-cut result and by 30.21 points over headcount. It
recovered all 2,475 registered minority-reversal worlds, while headcount
recovered none. A cut change was decision-material in 50.13% of worlds.

Those are descriptive outcomes, not a rescued primary claim.

## Why the joint criterion failed

The registered criterion required at least 15 percentage points lower false
settlement than **every** fixed cut, including after abstention matching.

- Reduction versus agent headcount: `30.21` points.
- Reduction versus fixed machine: `22.67` points.
- Reduction versus fixed controller: `13.07` points.
- Reduction versus fixed evidence origin: `13.06` points.
- Reduction versus fixed upstream component: `-5.75` points.

The last baseline was safer only in the narrow false-settlement sense because it
abstained on 40.23% of all worlds and made fewer correct settlements than every
other method. Its coarsest root policy erased both duplicated error and useful
independent evidence. This is exactly why false settlement cannot be interpreted
without decisiveness and missed-action cost.

Only agent headcount and fixed machine could match the oracle's zero abstention
with the frozen threshold search. The other fixed cuts remained 11.95–35.84
points away, so the abstention-matched joint condition correctly failed rather
than pretending the operating points were comparable.

## Latency

The deterministic Python path evaluated the selected cut plus all four
alternatives with these two-run timings:

| Run | p50 | p95 | p99 |
|---|---:|---:|---:|
| 1 | 0.139 ms | 0.449 ms | 0.673 ms |
| 2 | 0.138 ms | 0.435 ms | 0.685 ms |

This demonstrates that the graph/counting primitive itself does not require an
LLM and can fit a tactical path on this laptop. It is not a hard-real-time
guarantee: persistence, network transport, lineage acquisition, scheduling,
and production tail latency were not measured.

## What the result establishes

In the frozen world model, no one global collapse level preserved accurate
decisions across machine, controller, source-copying, and common-component
failure domains. Counting at the registered relevant cut preserved independently
rooted minority evidence without adopting a no-child-left-behind policy: the
minority won only when it represented the causal-root majority for that decision.

## What it does not establish

The rules engine scored perfectly because the failure domain was supplied and
the mapping was explicit. That is a wiring and runtime result, not evidence that
a model or human can identify the correct cut in unfamiliar cases. The data are
synthetic, erroneous roots were deliberately amplified, and the lineage was
ground truth. The run says nothing about field prevalence, self-reported roots,
joint failure domains, action authority, customer demand, or commercial value.

The next falsification gate is DRI-1B: externally authored, blinded cases in
which humans and models must select a cut without seeing outcome labels. Do not
build a runtime gate before that selection problem and real lineage availability
are measured.

## Procedural note

Before the frozen runner commit, a development unit test calculated the full
semantic loop once to assert determinism and rules/oracle equality. It printed no
outcome metrics, and no implementation or threshold was changed in response.
The test was then narrowed to a 128-world integrity sample before the runner was
committed. This is not a data-independence violation—the generator was already
preregistered and no result was observed—but it is recorded so the execution
history is complete.
