"""Source weight, decomposed with the primitive.

`canon/U3-WHAT-TRANSFERS.md` argues that weighted roots break several things at
once. This asks the narrower question the decomposition primitive is for: taken
apart layer by layer, what does the *shipped* notion of a source weight actually
supply, and which layers are empty?

The subject is `aggregation/baselines.py::weighted_vote`, because that is the only
weighting this repository ships. It is a **baseline**, and its naivety is
deliberate: it exists to represent what a reasonable person would do and to be
beaten. Decomposing it is therefore not an accusation. It is the cheapest way to
see which layers any *serious* weighting would have to fill, since the baseline
fills none of them and still looks plausible.

Three layers come back empty, and each empty layer is a requirement on whatever
replaces it.
"""

from __future__ import annotations

from canon.decomposition import Cell, Decomposition, Fill, Layer

WEIGHT = Decomposition(
    subject="source weight, as shipped in aggregation/baselines.weighted_vote",
    cells=(
        Cell(Layer.BOUNDARY, Fill.STATED,
             "One source's claim to count for more than one unit, on one "
             "proposition, at one moment."),

        Cell(Layer.COORDINATES, Fill.STATED,
             "Two, immediately multiplied into one: declared confidence times "
             "supplied competence. The product is the only thing downstream sees, "
             "so the two are unrecoverable once combined. At least six distinct "
             "quantities are commonly meant by 'weight' -- expertise, stake at "
             "risk, historical accuracy, recency, calibration, reputation -- and "
             "this admits two and reports neither."),

        Cell(Layer.OBSERVABLES, Fill.IMPLIED,
             "Nothing about a weight is detected. Confidence is self-reported and "
             "competence is handed in by the caller. Both are DECLARED on the "
             "DepthBasis ladder, whose own comment in "
             "aggregation/independence_axes.py reads: '\"I was there.\" Free, "
             "therefore worthless alone.' The observable is the "
             "number, and the number is the claim."),

        Cell(Layer.OPERATIONALISATIONS, Fill.STATED,
             "Clamp each factor to [0, 1], multiply, sum per side. A negative "
             "weight is silently clamped to zero, which audit/falsify.py records "
             "as an implementation decision with no formal justification."),

        Cell(Layer.CLAIMS, Fill.STATED,
             "A verdict, plus a mass per side."),

        Cell(Layer.EVIDENCE_LINEAGE, Fill.EMPTY,
             finding="A weight arrives with no provenance and no independence "
                     "story. Nothing records who set it, from what, or whether two "
                     "sources' weights were set by the same party -- which would "
                     "make them dependent in exactly the sense U1 is about. This "
                     "baseline de-duplicates nothing at all, which is why it loses; "
                     "but even aggregation/root_vote.py, which does de-duplicate "
                     "claims by root, has no notion of de-duplicating weights by "
                     "the party that assigned them."),

        Cell(Layer.MECHANISM, Fill.IMPLIED,
             "Asserted by the multiplication and never argued: that confidence and "
             "competence are independent, that each correlates with correctness, "
             "and that their product is the right combination rather than a min, a "
             "max, or a floor. Three claims in one operator."),

        Cell(Layer.AUTHORITY, Fill.EMPTY,
             finding="Anyone who can submit a claim can set its weight, and no "
                     "capability is checked. Under canon/EPISTEMIC-MODEL.md "
                     "authorization needs a granted capability and enough "
                     "independent evidence; a self-assigned weight has neither and "
                     "is nonetheless load-bearing on the verdict."),

        Cell(Layer.INVARIANTS, Fill.IMPLIED,
             "One is known broken. A zero-weight root is counted at full strength "
             "by the formal aggregator and at zero here, so the same corpus yields "
             "two verdicts depending on which aggregator reads it. Recorded in "
             "audit/falsify.py::weight_boundary_probe."),

        Cell(Layer.FALSIFIERS, Fill.EMPTY,
             finding="No observation makes this scheme report that a weight was "
                     "wrong. A source can be confidently and competently wrong "
                     "every time and its weight never moves, because nothing reads "
                     "outcomes back. This is the wheel's defect in a second "
                     "instrument: the cell does not exist, so departure produces no "
                     "evidence rather than contrary evidence."),
    ),
)
