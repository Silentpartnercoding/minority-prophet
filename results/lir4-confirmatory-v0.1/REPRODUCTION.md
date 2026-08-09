# LIR-4 reproduction receipt

The attack protocol and final-unused-case selector were committed at `e90105d`
before the holdout was materialized. The private input digest and frozen scorer
were committed at `41dd992` before scoring.

Two executions produced byte-identical result files with SHA-256
`19ce697b29484725b04ff5dde153962dd1d62fffe5eb3760f24c963af0b97ce6`.
The private normalized input is bound by SHA-256
`974df303ea8c489060b281260abde10e7b59f6525fcd2943e8c7138c99ddfe15`
and case-set SHA-256
`f36868482c6fdf729876886c1ab0251dc998d5adec02762f4669b808eecabfbe`.

After locally acquiring and materializing the prerequisite PHEME records, run:

```bash
python -m experiments.lir4.materialize \
  --source artifacts/lir1/pheme/extracted/all-rnr-annotated-threads \
  --exclude-from artifacts/lir1/pheme/pheme-pilot.jsonl \
    artifacts/lir1/pheme/pheme-r2.jsonl \
    artifacts/lir3/pheme-development.jsonl \
    artifacts/lir3/pheme-confirmatory.jsonl \
  --output artifacts/lir4/pheme-holdout.jsonl \
  --inventory results/lir4-pheme-v0.1/inventory.json --cap 5000

python -m experiments.lir4.score_confirmatory \
  --source artifacts/lir4/pheme-holdout.jsonl \
  --output results/lir4-confirmatory-v0.1/result.json
```

Tweet text, identities, and normalized rows remain local. The code, inventory,
aggregate result, and hashes are public.
