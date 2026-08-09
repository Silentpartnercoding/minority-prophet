# LIR-1E development reproduction

This package is a development-only threshold record, not confirmatory evidence.
It can be reproduced on the commissioning machine from the sealed private
requests, labels, responses, and receipts. A public clone intentionally lacks
those raw provider artifacts.

The response phase completed 60 of 60 calls on the first attempt: 48 Claude
Fable 5 calls and 12 GPT-5.6 calls. Both models copied their assigned synthetic
source token in every structurally valid response. Subscription use recorded no
incremental API-key charge; provider token counters are preserved separately by
model because their accounting fields are not directly interchangeable.

Run materialization twice into different directories, then run
`experiments/lir1/llm_echo/score_development.py` against each claims file with
the same private response, request, and construction-label files. Both public
result files had SHA-256:

`25939bac4ffcb55bdafe6100d7802c496d6d0f34e9ca6013b98811695334080e`

The selected parent threshold is `0.85`. It is frozen before any confirmatory
model request.
