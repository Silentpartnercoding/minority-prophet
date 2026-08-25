# Benchmark

The public benchmark generates deterministic copied-majority worlds and scores
aggregation methods against hidden binary truth.

```bash
python -m benchmark --worlds 500 --seed 7
```

- [`SPECIFICATION.md`](SPECIFICATION.md) defines the task, generation regime,
  metrics, controls, and interpretation boundary.
- [`world.py`](world.py) generates the synthetic worlds.
- [`evaluate.py`](evaluate.py) computes the metrics.
- [`decision-relative-independence-v0.1.json`](decision-relative-independence-v0.1.json)
  contains constructed falsification fixtures, not a benchmark result.

Synthetic performance does not establish real-world lineage recovery or truth
discovery. See the [research map](../docs/research/README.md) for protocols and
preserved outcomes.
