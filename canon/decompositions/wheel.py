"""The pu-erh flavour wheel, decomposed with the primitive.

The prose account is `canon/WHEEL-WORKED-EXAMPLE.md`. This is the same reading
expressed as data, so the claim "this instrument cannot record its own refutation"
becomes a property something can assert about rather than a paragraph.

The wheel is a research artifact whose vocabulary sits on a national standard.
The standards are identified (GB/T 14487-2017 for the sensory vocabulary, from
SAC/TC339); the specific figure is not. The AUTHORITY layer therefore stays
`IMPLIED` rather than becoming `STATED`, because knowing which standard the words
came from is not the same as citing the diagram that ordered them.
"""

from __future__ import annotations

from canon.decomposition import Cell, Decomposition, Fill, Layer

WHEEL = Decomposition(
    subject="pu-erh flavour wheel (Monascus purpureus fermentation)",
    cells=(
        Cell(Layer.BOUNDARY, Fill.STATED,
             "One tea type under one named fermentation, from raw to finished."),
        Cell(Layer.COORDINATES, Fill.STATED,
             "Five sectors and no others: aroma, taste, appearance, soup colour, "
             "tea residue."),
        Cell(Layer.OBSERVABLES, Fill.STATED,
             "One permitted descriptor per cell, from a closed list per sector."),
        Cell(Layer.OPERATIONALISATIONS, Fill.STATED,
             "A 42-unit fermentation clock sampled at seven points, with physical "
             "reference samples at the rim so a taster calibrates against the "
             "object rather than the word."),
        Cell(Layer.CLAIMS, Fill.STATED,
             "A tasting note: one descriptor per sector at a sampled time."),
        Cell(Layer.EVIDENCE_LINEAGE, Fill.UNEXAMINED),
        Cell(Layer.MECHANISM, Fill.IMPLIED,
             "A causal trajectory, asserted by the ordering rather than announced: "
             "aroma advances fresh, floral fruity, ripe fruity, fruit-fungus, "
             "fungus-stale; soup colour green-yellow through to brownish-red. The "
             "least visible of the fused layers and the only one that can be wrong "
             "in an interesting way."),
        Cell(Layer.AUTHORITY, Fill.IMPLIED,
             "The vocabulary is standardised: GB/T 14487-2017, Tea vocabulary for "
             "sensory evaluation, from the National Tea Standardization Technical "
             "Committee SAC/TC339. The wheel itself is a research artifact built on "
             "that vocabulary and its specific citation is not recovered, so the "
             "words have an authority and the ordering does not yet."),
        Cell(Layer.INVARIANTS, Fill.IMPLIED,
             "The rim's physical reference samples are the one invariant: they hold "
             "the vocabulary to something outside the vocabulary, so two tasters can "
             "in principle disagree about a tea rather than about a word."),
        Cell(Layer.FALSIFIERS, Fill.EMPTY,
             finding="No cell exists for a tea that departs from the asserted "
                     "trajectory, so departure produces no evidence rather than "
                     "contrary evidence. The instrument cannot record its own "
                     "refutation, and nothing downstream can distinguish a process "
                     "that behaved from one whose misbehaviour had nowhere to go. "
                     "This is ASSAYER A4: a gate that cannot reject is not a gate."),
    ),
)
