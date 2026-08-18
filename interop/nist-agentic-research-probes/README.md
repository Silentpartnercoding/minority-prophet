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

## What is NOT demonstrated

**The three existing probes have not been run on this corpus.** They are
LM-judge probes and require an OpenAI-compatible endpoint. No such run has been
performed, so this directory does not claim that faithfulness, completeness and
sufficiency score well here. It claims only that they are structurally unable to
see the derivation, which follows from their per-citation design.

This is the discriminating experiment and it is outstanding:

1. Ingest `corpus/` with NIST's pipeline.
2. Ask a question that pulls all three documents into one section.
3. Run the three probes unchanged.

**The result that supports a fourth probe:** all three score well while the root
count is 1. **The result that refutes it:** any of the three flags the
derivative citations. In that case one of the existing probes already covers
this and no fourth dimension is warranted — and that finding should be recorded
here rather than discarded.

Until that run happens, the argument above is structural, not empirical. A
proposal to NIST on this basis would be asserting a measurement nobody made,
which is the failure this project exists to catch.

## Provenance of the claims here

Verified at source: the repository exists, is public, is not archived, and its
probe documentation says what is quoted above. Not verified: any claim about
NIST's intentions, roadmap, or receptiveness. The repository's last push was
15 April 2026, so "ongoing" should not be assumed.
