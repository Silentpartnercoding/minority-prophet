# LIR-1 mechanics fixture v0.1

**Status:** software-mechanics check only. This is not the registered LLM echo
corpus, not a real-world dataset, and not a result for any LIR-1 hypothesis.

The fixture contains 40 deterministic copied-false-majority cases. It verifies
that the common schema, leakage-safe feature projection, nested edge hiding,
parent inference, root reconstruction, and three aggregation paths execute
end to end.

At 40% edge hiding, exact direct-parent F1 is 0.665625 while root-pair F1 is
1.0 and root-count mean absolute error is 0.0. This difference is expected in
the fixture: when a direct link is hidden, the baseline can attach a copy to a
nearby sibling copy and miss the immediate parent while still recovering the
correct root family. Minority Prophet needs the root family for copy collapse;
the immediate transmission path is a separate, harder target.

Across this intentionally easy fixture, majority accuracy is 0.0 and both the
declared and inferred root-collapse paths are 1.0 at every hidden fraction.
Those values only prove that the harness behaves as designed on its own test
data. They carry no external-validity claim.

Reproduce:

```bash
python3 -m experiments.lir1.run_boundary \
  --output results/lir1-mechanics-v0.1/result.json
python3 -m unittest tests.test_lir1
```

Scientific output is canonical JSON with no timing or host fields, allowing
byte comparison across clean executions.
