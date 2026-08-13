# Provenance Discovery v1 — DEMO result

Status: **COMPLETED DIAGNOSTIC — not a verified or public benchmark**

## Execution record

- Frozen protocol commit: `51240e818e46aa137afb2bb81d03f655e2a6b094`
- Complete-matrix runner commit: `bacaf9dac8928a8595c8879ed8796307666c7fc1`
- Manifest: `sha256:570f1ee0dd78b0cb109af3c4e8533a7ae4a54aa976c1df319706c679725317b1`
- Report: `sha256:a1b53d2fbc9a3bab5e4c66800350552dcb163f88b17121f750d20a29878bfccc`
- 48/48 model cells completed; 24 worlds each for GPT-5.6 Sol and Claude Sonnet.
- No model parse failures.

The initial execution exposed a scheduler bug that assigned half the matrix to
each provider. Its report was correctly marked `INCOMPLETE`. Commit
`bacaf9d` fixed only cross-product scheduling and added an exact-once matrix
test. The frozen worlds, prompts, endpoints, and inference thresholds did not
change; the run resumed the missing cells.

## Results

| Contestant | Same-origin precision | Recall | F1 | Downstream truth recovery | Mean time/world |
| --- | ---: | ---: | ---: | ---: | ---: |
| GPT-5.6 Sol | 100.00% | 91.67% | 95.24% | 100.00% | 10.55 s |
| Claude Sonnet | 100.00% | 90.63% | 94.64% | 100.00% | 10.83 s |
| MP confidence-gated candidate | 66.67% | 66.67% | 66.67% | 66.67% | 0.81 ms |
| EXP008 heuristic comparator | 90.32% | 100.00% | 94.92% | 0.00% | 0.12 ms |

The MP candidate was exact on all 16 worlds containing its supported signals
and deliberately made no same-origin claims on the other eight. This produces
100% F1 on explicit citation, syndication marker, distinctive-detail
laundering, and deceptive-citation families; the lower macro score includes
the no-claim families rather than hiding them.

Claude reported `$0.694247` for all 24 calls. The local Codex adapter reported
no billable price, so GPT cost is **unavailable**, not zero. Token telemetry is
retained in the local checkpoint.

## Post-run validity audit

The preregistered abstention interpretation for `generic_boilerplate` and
`opaque_paraphrase` is invalid. Those reports repeated exact wording at
one-minute intervals, while the independent reports used unique serial details
and direct-observer language. Both models cited those observable clues. The
families are not information-theoretically opaque, even though the
deterministic candidate intentionally does not use broad semantic similarity.

Accordingly:

- same-origin precision/recall/F1 remain valid against the synthetic hidden
  graph;
- the claimed "appropriate abstention" label for those eight worlds must not
  be used;
- the result demonstrates a useful speed/coverage tradeoff, not real-world
  provenance discovery;
- a rigorous opacity test needs identical public packets paired with different
  hidden lineage graphs, proving that no method can distinguish them from the
  supplied evidence.

The EXP008 comparator also demonstrates why pairwise F1 cannot stand alone. It
merged the copied branch correctly but also merged three genuinely independent
truthful observations. That small number of false-positive pairs forced a
downstream tie in every world, despite a 94.92% F1.

## Supported determination

Use a cascade:

1. deterministically auto-collapse direct citations and distinctive shared
   observations;
2. require integrity review for contradictory, future, or unknown citations;
3. escalate unresolved paraphrase/semantic cases to a model;
4. abstain when competing lineage graphs remain observationally equivalent.

This is a development result only. Nothing from this run is authorized for the
verified leaderboard or the public website.
