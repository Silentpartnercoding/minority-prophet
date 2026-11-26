# Using Minority Prophet

Choose the smallest surface that answers your question.

## Run the offline demo

From a Git checkout, with Make and Python 3.11+ installed, run `make demo`.
It requires no dependency installation or network calls. The
[check contract](../CHECK.md) distinguishes the citation illustration, bounded
immunity checks, archived-result consistency, and separate Lean proof build.
Use `make demo DEMO_PYTHON=/path/to/python3` to select an interpreter.

Only full development and site checks require Node (use `nvm use` to select
the version in `.nvmrc`) and `make setup`.

## See the idea

Visit [minorityprophet.org](https://minorityprophet.org/) for the public
explanation and interactive demo. Website source and local commands are in
[`website/`](../../website/).

## Run the Python benchmark

Requires a supported Python environment.

```bash
python -m pip install .
python -m benchmark --worlds 500 --seed 7
python -m experiments.los_inspired_v01
```

The benchmark reports metrics including truth accuracy, minority-truth
recovery, Brier score, abstention rate, and compute time. Synthetic accuracy is
not evidence of real-world provenance recovery.

## Run the read-only engine

The provider-neutral runtime exposes HTTP and MCP/stdio analysis surfaces.

```bash
npm --prefix evaluations/multi-model-v1 install
MP_ENGINE_ALLOW_INSECURE_LOCAL=1 \
  npm --prefix evaluations/multi-model-v1 exec mp-engine -- doctor
MP_ENGINE_ALLOW_INSECURE_LOCAL=1 \
  npm --prefix evaluations/multi-model-v1 exec mp-engine -- serve
```

Services can call `POST /v1/analyze`; agent runtimes can use `mp-engine mcp`.
Read [`evaluations/multi-model-v1/RUNTIME-README.md`](../../evaluations/multi-model-v1/RUNTIME-README.md)
for security, telemetry, and deployment limits.

The engine returns evidence-structure assessments, never a truth label or
authorization to take a protected action.

## Reproduce and verify

```bash
make setup
make verify
```

The full verification suite runs Python tests, integrity checks, website tests,
and runtime evaluation tests. Paper rendering has separate pinned dependencies:

```bash
make paper-setup
make paper-check
```

Before reproducing a named research result, follow its exact protocol, manifest,
and record rather than assuming the current environment recreates historical
conditions. Start at the [evidence map](../evidence/README.md).

## Integrate safely

- Treat a root count as an assessment under recorded lineage, not proof of
  causal independence.
- Preserve unknown ancestry as unknown.
- Keep authorization and action policy outside the analyzer.
- Keep hard real-time safety and reflex control independent of this runtime.
- Log the exact schema version, policy, inputs, and assessment used by a
  downstream decision.
