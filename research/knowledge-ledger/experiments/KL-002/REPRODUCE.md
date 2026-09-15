# Reproducing KL-002's first gate

## Status of this output: UNREGISTERED PROBE

This is **not a result**. It lives in `probe/`, not `results/`, and the
experiment's state stays `seeded`.

The protocol's completion route requires the registration to be committed
*before* confirmatory inspection. This check was run first, so registering it
now and calling the outcome a result would be back-dating a registration after
seeing the answer -- the defect DRI-7 exists to name. Its function is to
**inform** the registration that has not been written yet.

The repository's own `test_no_experiment_claims_progress_without_the_evidence_for_it`
refused an earlier version of this work that placed these files under
`results/`. That refusal was correct and is recorded here rather than worked
around.

```
python3 run_first_gate.py        # writes probe/first-gate.json; exit 1 = gate does not hold
python3 -m pytest tests -q
```

No network, no inference, no randomness. Every number is a total function of
`fixtures/laundered-source.json` and the two root rules in `src/roots.py`.

## What this establishes

**The gate does not hold.** Twenty paraphrases of one false source produce
**twenty** roots under byte identity, not one. ADV-004 predicted this; it is now
measured rather than asserted.

The consequence, stated as an inequality rather than a rate: a **false** claim
laundered through twenty paraphrases reaches confidence `0.99999999996`, while a
**true** claim carried by three genuinely independent sources reaches `0.973`.
The false claim outscores the true one, with no adversary present — only a
paraphrase pipeline and a root rule that reads bytes.

## What it does not establish

- **No rate, and none is derivable.** The population is authored. Per KL-001's
  DESIGN-v0.4, a rate over an authored population is a generator setting read
  back, so this reports an enumerated table (`inflationTable`) instead.
- **`declared_origin` holding at one root is not a solution.** It relocates the
  trust assumption from the text to the declaration. ADV-001's under-declared
  search space is untouched: nothing here detects an origin that lies.
- Nothing about agent behaviour. No model was run. This is the check the
  protocol says comes *before* any metered inference.

## Next

The preregistration proper — accuracy, Brier score, confident-error, abstention,
root error, tokens, cost and latency — still requires founder authorization for
paid inference. This gate was the part that did not.
