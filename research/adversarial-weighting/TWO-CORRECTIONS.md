# Two corrections, both from owner challenges, both checked in code

Neither of these came from the research plan. Both came from someone pushing back on
how the problem was described, and in both cases the pushback was right.

**Correction one: "just enforce that the box is not empty" is already done, and I
described the system as weaker than it is.**

`provenance/graph.py` refuses a parentless claim whose evidence names nothing
dereferenceable, raising `UnattributedRootError`, with the reason stated in the
exception itself: such a claim would contribute full evidential weight while
identifying nothing. There is real field data behind it. A pilot on published claims
found five of nine cited no resolvable primary source.

So the empty box is closed. **The gap is narrower and considerably harder.** Citing a
source and declaring an ancestor are two different fields, and filling the first does
not touch the second.

Five people read one paper. Each cites it honestly, with a real DOI. Every gate passes
and nobody lies.

| | |
|---|---|
| claims accepted | 5 |
| counted as independent roots | **5** |
| sources actually behind them | 1 |

Had each named the paper as an *ancestor* rather than as *evidence*, the count collapses
to one, which is correct. The two fields never speak to each other, so one paper becomes
as many roots as it has readers.

This is not the adversarial case. It is the honest case, and it is worse, because there
is nobody to catch.

**Correction two: I said a root means someone who looked at the world. It does not, and
the glossary already said so.**

`GLOSSARY.md` distinguishes an *evidence root*, grounded in an observation, from an
*evidence root (recorded)*, which is a node with no recorded ancestry, and adds the note
that this means no ancestry recorded rather than independently observed. The corpus drew
the distinction and my explanation collapsed it.

The owner's framing was the correct one: everything really does descend from a root, and
copies should collapse back to it. They do, when the descent is recorded. The failure is
never that a copy destroys a root. It is that an unrecorded copy **becomes** one.

**And one measured result that came from the same conversation, which refutes the
obvious alternative to a bond.**

The natural objection to requiring forfeiture is that reputation should do it for free:
lie, get downgraded, lose influence. Over enough rounds, punishment arrives.

It does not merely arrive late. **Reputation is worse than no defence at all**, and the
gap widens with the number of rounds.

| rounds | adversaries | no defence | reputation | bond |
|---|---|---|---|---|
| 2 | 5 | 0.468 | 0.520 | 0.020 |
| 5 | 5 | 0.461 | 0.848 | 0.018 |
| 20 | 5 | 0.471 | **1.000** | 0.018 |

Share of final verdicts the attacker corrupts. At twenty rounds, reputation hands them
every single one.

The mechanism is obvious once seen. Reputation concentrates weight on whoever has been
most consistently right. An honest source with real competence below one is sometimes
wrong and gets downgraded for it. A patient adversary who simply agrees until the round
that matters is never wrong, never downgraded, and rises. **A reputation system selects
for the attacker it exists to deter**, and a longer history is a larger reward for
patience.

Reputation is a weighting scheme, so it inherits every weighting failure already measured
here and contributes one of its own.

A bond works for exactly one reason, and it is not that it is harsher. It acts in the
round it is needed rather than the round afterwards.

Exploratory, not preregistered. Same generator caveats as the rest of this directory.
