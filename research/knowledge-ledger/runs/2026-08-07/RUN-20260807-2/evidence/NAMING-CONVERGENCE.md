# Naming convergence observed during the reimplementation

Operator note. Recorded while the run was in progress, before results existed,
so the observation cannot be adjusted to fit whatever the comparison shows.

Three identifiers in `impl-rs/src/main.rs` match the Python reference. They are
not equally interesting.

## Spec-derived — not evidence of anything

`conclusionDistribution`

`preregistration.json` lists a secondary endpoint as *"conclusion distribution
across enumerated worlds"*. Both implementations camelCased a phrase the spec
supplied. This is what shared requirements look like.

## Plausible convergence

`DECLARED_WORLD_COUNT`

`PROTOCOL.md` says the generator *"asserts this count before any invariant is
evaluated"*, and the word "declared" appears 28 times across the package. A
constant holding a declared world count, in the SCREAMING_SNAKE convention both
languages use, has few other plausible names. Weak evidence at most.

## Unexplained

`violationsByInvariant`

The phrase "violations by invariant" appears **zero** times in the spec package,
as does "by invariant" in any form. Two implementations independently selecting
that exact multi-word camelCase key, for an output field the specification never
names, is not a coincidence I would bet on.

I cannot presently distinguish:

- the implementer saw the reference despite the brief;
- the implementer saw `kl000-operator-notes/OPERATOR-DISCLOSURE.md`, which sat
  inside the package for 32 seconds and named the reference's language and
  module decomposition (operator error, documented in that file);
- genuine convergence on an obvious name that I am underestimating.

`atime` is disabled on this volume, so reads are not observable and this cannot
be settled by inspection after the fact.

## Why this may not damage the result

`violationsByInvariant` is a **reporting** choice, not a **semantic** one. The
reproduction gate exists to test whether an independently reasoning implementer
recovers the same meaning from the ten invariant definitions. A shared output
field name is a naming leak; it does not by itself indicate shared reasoning
about what an invariant means.

The finding that would matter is different: if the implementer's invariant
*semantics* track the reference in places where the specification is silent or
ambiguous, that is shared reasoning, and it is exactly what this gate was built
to detect. The implementer's own ambiguity notes are the place to look, because
they record where it had to choose a reading without guidance.

## What to do with this

State it in the run record. Do not treat the reproduction as void on this
evidence, and do not treat it as clean either. The defensible claim is:

> One output field name in the reimplementation matches the reference without a
> visible path from the specification. The invariant semantics were compared
> separately; see the ambiguity analysis.

For any future reimplementation, the fix is environmental rather than
procedural: run it on a machine that does not hold the reference at all.

---

## Addendum — the surrounding schema is not shared

Added after `impl-rs/results/smoke.json` appeared, still before any full-scale
comparison.

The two matching names sit inside an output schema that is otherwise the
implementer's own:

| implementer | reference |
|---|---|
| `exhaustiveSmall` | `phases.exhaustive` |
| `checker.violationsTotal` | `totalViolations` |
| `firstViolation` | `preservedViolations` |
| `worldsPerSecond` | `elapsedSeconds` |
| `worldStreamHash` | *(no equivalent)* |
| — | `worldsChecked`, `outOfDeclaredBounds`, `failClosedRejections` |

Two of roughly ten field names match, and one of those two was supplied by the
specification. An implementation produced by reading the reference would be
expected to carry the schema, not two words out of it. This materially weakens
the contamination reading of `violationsByInvariant`, without eliminating it.

`worldStreamHash` is worth noting separately: a digest over the generated world
stream, which the reference does not have and neither implementation was asked
for. It lets two runs demonstrate they enumerated *the same worlds* rather than
merely the same number of them — a stronger reproduction primitive than the
protocol requires, and evidence of independent design rather than transcription.

It also independently derived the exhaustive count: `exhaustiveSmall.worlds =
176120`, computed from the declared bounds rather than adopted from the
protocol's stated figure. Fixture and exhaustive violation totals are both 0.
The randomized phase in this artifact ran 2,000 worlds, not the preregistered
1,000,000 — it is labelled `smoke.json` and should not be read as a
confirmatory result.
