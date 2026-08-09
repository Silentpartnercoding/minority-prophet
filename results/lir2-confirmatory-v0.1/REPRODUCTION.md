# LIR-2 confirmatory reproduction receipt

The protocol and candidate family were committed before development selection.
Threshold `0.75` was then frozen before the new seed was created. The new
36-case request and construction-label hashes were committed before model
execution, with zero case overlap against the LIR-1E confirmatory corpus.

All 180 model responses completed validly on their first attempt. Their
SHA-256 and the combined hash of all 180 private receipts were committed before
labels were opened.

Two independent materializations each produced 432 claims and 252 deterministic
descendants. Their claims SHA-256 was
`9ea76600051198e649edbcb5ba6d14c290be79ac4f7d3565e77a4a4b8cf89701`.
Two confirmatory scoring runs were byte-identical with result SHA-256
`f6d3b21fda332c429f76e23f9c2620b334c368b7a5d83cb1bcc09c89eef21e1c`.

Raw requests, labels, responses, and provider receipts remain private under
`artifacts/lir2/confirmatory/` and are bound by the canonical manifest.
