"""The decomposition primitive: take a bounded claim or artifact apart in ten layers.

The order is not cosmetic. You cannot name observables before a boundary is drawn,
and you cannot make claims before observables are turned into measurements. Each
layer is therefore only answerable once the one above it has been.

An unfilled layer is a **finding, not an omission**. `Layer.EMPTY` is a first-class
result meaning the artifact provides nothing at this layer, and it is reported
rather than skipped, because the classic failure this primitive exists to catch is
an instrument whose missing layer is invisible -- see `canon/WHEEL-WORKED-EXAMPLE.md`.

The four axes of `canon/EPISTEMIC-MODEL.md` are not replaced by the layers. They
classify what a thing *establishes*; the layers are a procedure for taking it
*apart*. One is a filing system, the other a scalpel, and the filing system works
better once you have cut. Each layer therefore declares which axis its content
bears on, so a decomposition can be read either way round.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum, StrEnum


class Layer(IntEnum):
    """Ordered. Lower layers must be answerable before higher ones are meaningful."""

    BOUNDARY = 0            # what phenomenon or domain is being enclosed
    COORDINATES = 1         # what dimensions are permitted to describe it
    OBSERVABLES = 2         # what can actually be detected
    OPERATIONALISATIONS = 3  # how detections become measurements and categories
    CLAIMS = 4              # what statements are made from them
    EVIDENCE_LINEAGE = 5    # where support originates, and how independent it is
    MECHANISM = 6           # what causal account is asserted
    AUTHORITY = 7           # who or what may declare, transform, or act on it
    INVARIANTS = 8          # what survives changing observer, partition, representation
    FALSIFIERS = 9          # what would force a legitimate update or reversal


class Axis(StrEnum):
    """The four axes of canon/EPISTEMIC-MODEL.md. Authorization is not among them."""

    STRUCTURE = "structure"
    ATTRIBUTION = "attribution"
    CORRESPONDENCE = "correspondence"
    DEPENDENCE = "dependence"


#: Which axis each layer's content bears on. Declared once, here, so a
#: decomposition can be read by layer or by axis without either being derived
#: from the other at call time.
LAYER_AXIS: dict[Layer, Axis] = {
    Layer.BOUNDARY: Axis.DEPENDENCE,
    Layer.COORDINATES: Axis.DEPENDENCE,
    Layer.OBSERVABLES: Axis.CORRESPONDENCE,
    Layer.OPERATIONALISATIONS: Axis.CORRESPONDENCE,
    Layer.CLAIMS: Axis.STRUCTURE,
    Layer.EVIDENCE_LINEAGE: Axis.STRUCTURE,
    Layer.MECHANISM: Axis.CORRESPONDENCE,
    Layer.AUTHORITY: Axis.ATTRIBUTION,
    Layer.INVARIANTS: Axis.STRUCTURE,
    Layer.FALSIFIERS: Axis.CORRESPONDENCE,
}


class Fill(StrEnum):
    """Why a layer holds what it holds. `EMPTY` and `UNEXAMINED` are not the same."""

    STATED = "stated"          # the artifact says this outright
    IMPLIED = "implied"        # present but unannounced; the decomposer names it
    EMPTY = "empty"            # the artifact genuinely provides nothing here
    UNEXAMINED = "unexamined"  # we did not look. Never a finding about the artifact


@dataclass(frozen=True)
class Cell:
    """One layer of one decomposition."""

    layer: Layer
    fill: Fill
    content: str = ""
    #: Why this is a finding rather than a gap in our reading. Required for EMPTY,
    #: because "the artifact has no falsifiers" and "we did not check" are the two
    #: answers this primitive exists to keep apart.
    finding: str = ""

    def __post_init__(self) -> None:
        if self.fill in (Fill.STATED, Fill.IMPLIED) and not self.content:
            raise ValueError(f"{self.layer.name}: {self.fill} requires content")
        if self.fill is Fill.EMPTY and not self.finding:
            raise ValueError(
                f"{self.layer.name}: EMPTY must carry a finding saying what its "
                "absence means. An unfilled layer is a finding, not an omission."
            )
        if self.fill is Fill.UNEXAMINED and self.finding:
            raise ValueError(
                f"{self.layer.name}: UNEXAMINED cannot carry a finding. Not looking "
                "establishes nothing about the artifact (ASSAYER A5)."
            )

    @property
    def axis(self) -> Axis:
        return LAYER_AXIS[self.layer]


@dataclass(frozen=True)
class Decomposition:
    """A bounded artifact taken apart. Every layer appears, filled or not."""

    subject: str
    cells: tuple[Cell, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        seen = [c.layer for c in self.cells]
        if len(seen) != len(set(seen)):
            raise ValueError("a layer appears twice")
        missing = [l for l in Layer if l not in seen]
        if missing:
            raise ValueError(
                "every layer must appear; skipping one hides exactly what this "
                f"primitive is for. Missing: {[l.name for l in missing]}"
            )

    def __getitem__(self, layer: Layer) -> Cell:
        return next(c for c in self.cells if c.layer == layer)

    def findings(self) -> tuple[Cell, ...]:
        """Layers the artifact genuinely does not supply. The point of the exercise."""
        return tuple(c for c in sorted(self.cells, key=lambda c: c.layer)
                     if c.fill is Fill.EMPTY)

    def unexamined(self) -> tuple[Cell, ...]:
        """Layers we did not look at. Reported separately and never as findings."""
        return tuple(c for c in sorted(self.cells, key=lambda c: c.layer)
                     if c.fill is Fill.UNEXAMINED)

    def by_axis(self, axis: Axis) -> tuple[Cell, ...]:
        return tuple(c for c in sorted(self.cells, key=lambda c: c.layer)
                     if c.axis is axis)

    def coverage(self) -> tuple[int, int]:
        """(layers the artifact supplies, layers examined). Never a single ratio:
        a ratio hides which layer is missing, and which one it is, is the finding."""
        examined = [c for c in self.cells if c.fill is not Fill.UNEXAMINED]
        supplied = [c for c in examined if c.fill is not Fill.EMPTY]
        return len(supplied), len(examined)

    def report(self) -> str:
        lines = [f"decomposition: {self.subject}", ""]
        for c in sorted(self.cells, key=lambda c: c.layer):
            lines.append(f"  {c.layer.name:<21} {c.fill.value:<11} [{c.axis.value}]")
            if c.content:
                lines.append(f"      {c.content}")
            if c.finding:
                lines.append(f"      FINDING: {c.finding}")
        s, e = self.coverage()
        lines += ["", f"  {s} of {e} examined layers supplied by the artifact"]
        if self.findings():
            lines.append("  empty, and each is a finding:")
            lines += [f"    {c.layer.name}" for c in self.findings()]
        if self.unexamined():
            lines.append("  unexamined, establishing nothing either way:")
            lines += [f"    {c.layer.name}" for c in self.unexamined()]
        return "\n".join(lines)


__all__ = ["Layer", "Axis", "Fill", "Cell", "Decomposition", "LAYER_AXIS"]
