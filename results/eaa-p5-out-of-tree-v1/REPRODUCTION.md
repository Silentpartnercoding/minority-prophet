# EAA-P5 public verification boundary

From the repository root, verify that the imported files still match their
manifest and that the frozen interpretation remains intact:

```bash
python -m pytest tests/test_eaa_p5_out_of_tree.py
```

This verifies the public packet; it does not rerun the scientific computation.
The full harness used pinned dependencies, development-only calibration,
untouched synthetic confirmation seeds, and a disjoint NIST Juliet packet in a
separate repository. That complete record is retained outside this repository.

A future public computational replication must be registered as a new run. It
must commit its protocol, implementation, source lock, candidate, confirmation
sample rule, and thresholds before inspecting confirmatory outcomes. Importing
this result does not retroactively turn it into a repository-native rerun.
