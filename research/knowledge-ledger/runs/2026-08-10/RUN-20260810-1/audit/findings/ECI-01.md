# ECI-01 — a green run does not exclude a verifier that ignores what it verifies

**Identifier:** ECI-01
**Classification:** ASSURANCE WEAKNESS
**Severity:** medium — no false documented claim, but a real gap between what the
green result establishes and what an adopter will read it as
**Affected commit:** epistemic-ci `6870233b5e0d`
**Type:** composition / claim scope. Not code, not configuration.

## Claim affected

README: *"Epistemic CI is a small, vendor-neutral meta-validation gate for
computational research. It tests the verification path before anyone treats a
green check as evidence. In plain language: it is a test for the tests."*

The narrower per-check statements are accurate and are **not** falsified here.
Vacuous Test says it plants *"every **declared** source or input defect"*, which
is exactly what it does.

## Minimal reproduction

`raw-artifacts/eci-A1-declared-mutation-blindness/`. Four files matter:

`verify.py` — the verification path, materially defective by construction:

    text = pathlib.Path("fixture.txt").read_text()
    if not text.strip():
        sys.exit(1)          # only checks the file is non-empty
    sys.exit(0)              # never reads VERDICT

`check.py` — the same defect on the generated-output path.

`.epistemic-ci.json` declares one mutation per check, each of which empties the
file. Both are caught, because an empty file is the one thing these verifiers
detect.

## Expected and observed

Run: `epistemic-ci run --root <pkg> --config .epistemic-ci.json`

    vacuous-test               pass
    executable-pass-condition  pass
    observation-surface        pass
    final-artifact-binding     pass
    OVERALL                    PASS

Then, on the same package:

    fixture.txt: "VERDICT: PASS" -> "VERDICT: FAIL"
    verify.py exit=0            (accepts a FAIL verdict as passing)

    results/result.json: {"verdict":"PASS"} -> {"verdict":"FAIL"}
    check.py  exit=0            (accepts a FAIL result as passing)

So a fully green Epistemic CI run is compatible with a verification path that
never reads the verdict it exists to verify.

## Why the existing checks miss it

**Mutation selection is author-controlled and unconstrained.** Vacuous Test
proves the verifier catches the defects the author *chose to declare*. An author
who declares only defects their verifier happens to catch gets a green check that
carries no information about the defects it does not.

Nothing in the tool measures whether the declared mutation set is representative,
non-trivial, or related to the property under verification. The check cannot
distinguish "this verifier is sound" from "this author declared easy mutations".

The other three checks do not close it. Executable Pass Condition has the same
author-controlled mutation list. Observation Surface constrains provenance, not
verifier semantics. Final Artifact Binding constrains artifact integrity after
the fact.

## Practical impact

Bounded. This is not a vulnerability and nobody is attacked by it. It matters at
adoption: a project can obtain a green "test for the tests" badge while its
verification path is vacuous in exactly the way the tool is named for. The
README's *"What it does not prove"* section hedges the scientific claim but does
not say **the green result is only as good as the declared mutations**, which is
the operative limit.

## Smallest regression test

A check that the declared mutation set is non-trivial cannot be written in
general — it requires knowing which defects matter, which is the thing under
study. The tractable version, and the one this programme has already adopted
elsewhere:

> require each declared mutation to be classified **equivalent** or
> **behaviour-changing** against the artifact under verification, and fail when
> every declared mutation is equivalent or when the declared set is empty.

That is BL-058 Amendment 2 in the research repository, applied here.

## The result that matters more than the finding

This is the **same defect the research repository found in its own immunity
ablation on the same day** (`FINDING-BL058B.md`): mutation selection determines
what you learn, and a checker that catches the mutations you chose says nothing
about the ones you did not. Two independently written codebases, same blind spot.

That recurrence is stronger evidence than either instance. It suggests the defect
is a property of mutation-based assurance as practised here, not of either
implementation.

## Status

NO COUNTEREXAMPLE to any documented claim. Recorded as an assurance weakness and
a documentation gap, not as a defect in the implementation.
