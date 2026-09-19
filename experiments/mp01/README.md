# MP.01 — False Consensus

Six synthetic agents answer one question. Five support Answer A and one supports
Answer B. The five Answer A claims look like a majority until their declared
ancestry is reconstructed:

```text
claim-a1 ─┬─> claim-a2 ─> claim-a4
          └─> claim-a3 ─> claim-a5

claim-b1
```

The fixture therefore contains five votes for A and one for B, but only one
recorded evidence root for each answer. The correct epistemic action is not to
declare B true. It is to preserve the minority, abstain, and request another
independent source.

Run it:

```sh
python -m experiments.mp01.run_mp01
```

The output is deterministic and must match
`public/research/mp01-canonical-demo.json`. This is a synthetic demonstration
of dependence collapse under declared ancestry. It does not infer copying from
unstructured material and it does not establish a real-world truth claim.

