# LIR-2/PHEME fixed-method transfer

The preregistered joint transfer criterion is **rejected**.

At 40% hidden recorded edges, LIR-2 retained root-pair precision `1.0` but
recovered only `0.2020` recall, producing F1 `0.3362`. Root-count mean absolute
error was `5.5517`. The known LIR-1/PHEME-R2 comparator had recall `0.2256`, F1
`0.3680`, and root-count error `4.9310`, so the constructed-corpus LIR-2 gain did
not transfer and was slightly worse on these measures.

This negative result sharply limits the constructed findings: direct textual
and temporal grouping worked on controlled model echoes but did not reconstruct
the much looser recorded relationships in PHEME. Precision remained safe because
the method rarely merged unrelated roots; the failure was insufficient coverage.

PHEME edges are platform reply lineage, not causal evidence independence. The
result neither proves that better real-world inference is impossible nor permits
retuning this transfer into a confirmatory success.
