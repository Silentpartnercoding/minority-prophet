# Methodology notes — RUN-20260807-10

M1–M30 in force. One addition.

## M31 — Derived values are surfaced at the presentation layer; frozen bytes are never the place for new information

The paper promised flip_budget "with every verdict"; the receipt is
byte-frozen by two pinned fixtures and a cross-implementation agreement.
The resolution was neither to break the pins nor to leave the promise
unmet: a registered derivation at the presentation layer, computed from a
member already present, with the pass condition that the pins still hold —
proven, not assumed. The general rule: when a registered artifact is
byte-frozen, new information derivable from it belongs in a derived layer
with its derivation registered; only underivable information justifies the
full re-registration cost of moving frozen bytes (that remains BL-026/
BL-037's deliberate path). CE-03 shows the second half of the discipline:
a derived value that can mislead alone (units!) is registered WITH its
pairing constraint, structurally enforced.
