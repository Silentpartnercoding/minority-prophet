# LIR-3 reproduction receipt

The protocol and method grid were committed at `ea4d230` before development
selection. The selected author-only configuration and sealed holdout digest were
then committed at `f52e171` before confirmatory scoring.

Two executions produced byte-identical result files with SHA-256
`358fb278c139b55dcb8ee40c6f1370504627a0a0ff3504844223f595cbd7a10f`.
The private normalized holdout is bound by SHA-256
`4a66b3bd48865c8a05d6167417d283ef3ad6ea46aef44aa18436a9ea2db5e1c0`
and case-set SHA-256
`d03ac90910866ba5ad65b95c54dc8edac0789e55b62fd1293b50e2470a1ab2eb`.

From a repository containing the locally acquired PHEME archive and prior local
PHEME normalized files, reproduce the public record with:

```bash
python -m experiments.lir3.pheme_provenance \
  --source artifacts/lir1/pheme/extracted/all-rnr-annotated-threads \
  --exclude-from artifacts/lir1/pheme/pheme-pilot.jsonl artifacts/lir1/pheme/pheme-r2.jsonl \
  --development-output artifacts/lir3/pheme-development.jsonl \
  --confirmatory-output artifacts/lir3/pheme-confirmatory.jsonl \
  --inventory results/lir3-pheme-v0.1/inventory.json --cap 5000

python -m experiments.lir3.tune \
  --source artifacts/lir3/pheme-development.jsonl \
  --output results/lir3-development-v0.1/result.json

python -m experiments.lir3.score_confirmatory \
  --source artifacts/lir3/pheme-confirmatory.jsonl \
  --development-result results/lir3-development-v0.1/result.json \
  --output results/lir3-confirmatory-v0.1/result.json
```

Normalized tweet records remain private because Twitter retains content rights.
The public inventory, code, aggregate result, and hashes are sufficient to check
identity and deterministic reproduction without redistributing those records.
