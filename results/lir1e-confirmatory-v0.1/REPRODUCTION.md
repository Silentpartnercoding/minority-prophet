# LIR-1E confirmatory reproduction receipt

The confirmatory protocol, fixed threshold, request inventory, models, limits,
and scorer were committed before the first model request. After 180 of 180
responses completed validly on their first attempt, their SHA-256 and the
combined hash of 180 private receipts were committed before construction labels
were opened.

Two separate materialization directories were created from the sealed private
requests, responses, and construction labels. Each produced 432 claims and 252
programmatic descendant records. Both claims files had SHA-256
`5ffff9f790b9849574ed3648ccb88674e0884e97a8432c7af34ec57c31e19084`.

The frozen confirmatory scorer ran independently against both materializations.
Both output files were byte-identical with SHA-256
`ab95001c69a337e6d5baa5c90a8927ec0b61c138bb3790f9dfb48a3e9a227f3d`.

The raw requests, responses, labels, and provider receipts remain private under
`artifacts/lir1/llm_echo/confirmatory/`. Their public commitments permit an
authorized audit but intentionally do not publish provider response text or
hidden construction material.
