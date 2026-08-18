# KL-016 v0.2 — measured: most of a conjecture's citing literature is not independent

First measurement in this programme of evidence-root structure on **real
literature** rather than a generated world. Reproduce:

```sh
python3 .../src/identify_origins.py  --out RESULT-v0.2-gate1-origins.json
python3 .../src/root_ratio.py        --origins RESULT-v0.2-gate1-origins.json
python3 .../src/negative_control.py
```

## Gate 1 — three of seven cases are unassignable

| case | arm | origin identified |
|---|---|---|
| hirsch | refuted | ✅ Dantzig 1963 |
| hedetniemi | refuted | ✅ Hedetniemi 1966 |
| connes-embedding | refuted | ✅ Connes 1976 |
| sensitivity | proved | ✅ Nisan & Szegedy 1992 |
| borsuk | refuted | ❌ 1933, not in index |
| fermat | proved | ❌ **no publication exists** |
| poincare | proved | ❌ 1904, not in index |

The registered stop rule needs **three of four refuted** cases unassignable. One
is. **The experiment continues.**

`fermat` was registered *in advance* as a known-null: a conjecture from a
marginal note with no originating publication at all. It tests that the gate
reports unassignable instead of substituting a proxy. It did.

**The control arm collapsed, and no registered rule covers that.** Two of three
proved cases are unassignable, leaving three refuted against one proved. The
spec says the proved cases are "the only thing that can produce a result against
the hypothesis"; with one left, the refuted-versus-proved comparison — already
hypothesis-generating only — is **not interpretable**. This is a second gap in a
frozen spec, of the same kind as v0.1's missing threshold, and it is recorded
rather than patched.

## Primary endpoint — measured

`root_ratio` = distinct roots among pre-cutoff citing works ÷ raw count. A root
is a citing work that references **no other work in the same set**.

| case | arm | citers | roots | **root ratio** | derived |
|---|---|---:|---:|---:|---:|
| hirsch | refuted | 3,637 | 1,562 | **0.429** | 57% |
| hedetniemi | refuted | 88 | 26 | **0.295** | 71% |
| connes-embedding | refuted | 578 | 76 | **0.132** | 87% |
| sensitivity | proved | 84 | 25 | **0.298** | 70% |
| *random unrelated maths, same eras* | *control* | *84–200* | *all* | ***1.000*** | *0%* |

**Between 57% and 87% of the literature citing a conjecture descends from other
literature citing the same conjecture.** Against a negative control of 0%.

## The confound, checked rather than assumed

A work whose references the index does not record is a root **by default** —
`HRI1-BLOCKER-20260816.md`'s population, and it would appear here as spurious
independence. Measured: **zero blind roots in all four cases.**

The reason is structural and cuts both ways. To enter a citing set at all, the
index must already have parsed the work's references. So the confound is absent
**by construction** — and the flip side is that the measured population is the
reference-recording subpopulation only. Works whose references were never parsed
are **invisible here, not counted as roots**. The ratio describes the ~62% of
mathematics that records references, and says nothing about the rest.

## BL-060 negative control — satisfied

Size-matched random mathematics samples from the same eras, no citation
relationship to any conjecture: **root ratio 1.000, zero internal edges**, in all
four samples, seed fixed in advance.

So the measured ratios are a property of a conjecture's citing literature, not
of how mathematics cites in general. The instrument distinguishes the population
with the property from one without, which is what BL-060 demands.

## The comparison arm — a null on the only well-matched pair

`hedetniemi` (refuted) **0.295** against `sensitivity` (proved) **0.298**.

These are the two most comparable cases in the design: both resolved in 2019,
both with specific originating papers, both with ~85 pre-cutoff citers. Their
root ratios are indistinguishable.

**Registered in advance as hypothesis-generating only, and reported because a
null is a result.** It is weak evidence that root ratio does not track whether a
conjecture was later refuted — and with n=4, one arm reduced to a single case,
and no statistic permitted, it is nothing stronger than that.

## Construct validity — weak for two of the four

Citing the originating work is **not** the same as supporting the conjecture.

- **Strong proxy:** `hedetniemi` and `sensitivity`. Specific origin papers,
  small citing sets, cited largely because of the conjecture.
- **Weak proxy:** `hirsch` — the origin is Dantzig's *Linear Programming and
  Extensions*, a foundational textbook with 5,829 total citations, the vast
  majority nothing to do with the Hirsch conjecture. Its 0.429 largely measures
  the root structure of the linear-programming literature.
- **Weak proxy:** `connes-embedding` — a landmark classification paper cited for
  the classification. Its 0.132 is the most extreme value in the table and the
  least attributable to the conjecture.

This should have been caught when the case list was frozen. It was not, and the
per-case table is reported precisely so a reader can discount the two weak cases
rather than have them averaged in.

## Secondary endpoint — not run

The conditional-dependent versus confirming-evidence split requires two
labellers blinded to outcome, with κ ≥ 0.7. **No labelling was performed.** The
endpoint is open, not answered.

## What may be claimed

- The instrument runs on real literature and reproduces.
- A conjecture's citing literature is **substantially internally derived**
  (57–87%) where a matched unrelated sample is **not at all** (0%).
- Root collapse on this corpus is not an indexing artefact: zero blind roots.

## What may not be claimed

- Nothing about whether these conjectures were *believed* for dependent reasons.
  Citation is not endorsement, and two of four origins are cited mostly for
  other reasons.
- Nothing predictive. The refuted-versus-proved comparison is uninterpretable
  with one control, and its only matched pair is a null.
- Nothing about evidence-root identity corresponding to independent observation.
  That remains blocked by KL-014, and this measurement does not touch it.
- Nothing about the Riemann Hypothesis.
