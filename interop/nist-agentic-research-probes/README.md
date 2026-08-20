# Evidence independence as a fourth probe dimension

A fixture and an argument. Nothing here has been sent to NIST, and nothing here
asks NIST to adopt Minority Prophet.

## The system this is about

NIST's `usnistgov/agentic-research-evaluation-probes` runs deep research over a
local document corpus and scores every citation with three LM-judge probes:

| Probe | Direction | Question |
|---|---|---|
| Faithfulness | anti-hallucination | Does the source say what the text claims? |
| Completeness | anti-cherry-picking | Did the text capture the source's full message? |
| Sufficiency | anti-overreaching | Does the source carry the burden the claim requires? |

Read from the repository and its `docs/probes.md` on 18 August 2026. The probe
registry is extensible by design: `@register_probe`, a documented `ProbeFunc`
signature, and stated conventions for adding a dimension.

## The claim being tested

`docs/probes.md` states that the three probes "form a mutually exclusive,
collectively exhaustive evaluation of how a citation is used."

All three are **per-citation**. Each judge is shown one source passage and one
citing sentence. That is a property of the implementations, not a guess: each
resolves a single `[^N]` marker to a single chunk before calling the judge.

A judge that sees one citation at a time cannot observe a relation *between*
citations. So it cannot observe that three cited documents descend from one
observation. Each of the three is faithful, complete and sufficient on its own,
and the report still presents one observation as three.

This is not a defect in the probes. It is a dimension outside the unit they
evaluate.

Their architecture already admits the fix: `ProbeFunc` receives the section's
full `list[Finding]`, and `SectionVerdict` exists for per-section probes. A
fourth probe fits without rebuilding anything.

## The corpus

`corpus/` holds three documents.

| File | What it is |
|---|---|
| `01-root-observation.md` | One measurement, one array, one site. States its own limits. |
| `02-derivative-trade-press.md` | Trade-press report of that measurement. States it made no measurement. |
| `03-derivative-review.md` | Review summarising the same figure. States it made no measurement. |

Each derivative names its source in its own text, so the derivation is declared
by the documents rather than inferred by us. A report citing all three has three
citations and one observation.

The documents are deliberately honest. None misquotes, none drops the caveats,
none overreaches. They are written so that the three existing probes *should*
score them well — that is the point.

## What is demonstrated

```sh
python3 interop/nist-agentic-research-probes/independence_demo.py
```

Deterministic, no model, no network:

```
  counting citations : 3 supporting sources
  counting roots     : 1 supporting root (MIL-2291)
  weakest basis      : declared
```

The independence side of the proposed dimension needs no judge.

## The discriminating experiment — run, see `RESULTS.md`

Run on 18 August 2026 with NIST's probe code unmodified, judge `gpt-4.1`:

| Probe | Mean score |
|---|---|
| Citation faithfulness | 0.82 |
| Citation completeness | 0.95 |
| Citation sufficiency | 0.86 |

Root count over the same three citations: **1**. That is the outcome that
supports a fourth dimension, and it was named in advance.

**One claim above needed correcting.** An earlier version of this file said the
probes are *structurally unable to see* the derivation. That is too strong. 8 of
the 33 verdict rationales explicitly discuss it — the judges read the derivation
and report it back. What none of them do is act on it: every deduction is a
scope mismatch inside a single citation, because each probe scores one citation
against one source and no probe emits a count of independent sources.

The accurate statement is narrower and less comfortable: a judge can notice
derivation and still have nowhere to put it. `RESULTS.md` carries the evidence,
the weaknesses, and what would still refute the case.

## Provenance of the claims here

Verified at source: the repository exists, is public, is not archived, and its
probe documentation says what is quoted above. Not verified: any claim about
NIST's intentions, roadmap, or receptiveness. The repository's last push was
15 April 2026, so "ongoing" should not be assumed.
