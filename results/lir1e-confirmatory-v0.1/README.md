# LIR-1E confirmatory result

The preregistered primary criterion is **supported** in the 36-case controlled
echo corpus at 40% hidden direct edges and fixed threshold `0.85`.

Raw majority was wrong on all 36 constructed cases. Declared evidence-root
collapse was correct on all 36. Inferred collapse answered 25 cases, was correct
on 21 of those 25 (`0.84`), and abstained on 11. Its declared-advantage survival
was `0.84`; the 10,000-sample case-bootstrap 95% interval was
`0.6818–0.9615`. Root-pair F1 was `0.8309`, with precision `1.0` and recall
`0.7106`.

The result supports recovery of useful constructed record-root groupings under
this frozen setup. It does not prove causal evidence independence, general
truth discovery, or performance on uncontrolled real-world sources. Selective
coverage is material: the inferred method answered 25 of 36 cases.

Exact hidden-parent recovery remained weak (`F1 0.3204`). No-text and no-time
ablations each lost the truth-recovery advantage, indicating that this baseline
needed both textual and temporal evidence under the registered threshold.
