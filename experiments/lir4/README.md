# LIR-4 — provenance degradation envelope

LIR-4 attacks the identity field that made LIR-3 work. It uses only remaining
unused PHEME cases and freezes missingness, collision, and deliberate cross-root
misbinding before scoring. See `PREREGISTRATION.md`.

The 400-case confirmatory run rejected graceful degradation: at 50% missing
reply identity, recall fell to `0.4329` while precision remained `1.0`. The
cross-root safety diagnostic was preregisteredly underpowered. See
`results/lir4-confirmatory-v0.1/`.
