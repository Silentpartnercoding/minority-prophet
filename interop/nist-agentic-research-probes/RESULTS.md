# Measurement: what NIST's three probes score on this corpus

Run 18 August 2026. Judge model `gpt-4.1`. NIST's probe code unmodified.
Raw verdicts in `probe-results.json`; runner in `run_probes.py`.

## Result

| Probe | Mean score | Verdicts below full marks |
|---|---|---|
| Citation faithfulness | **0.82** | 2 partially supported, 1 not supported |
| Citation completeness | **0.95** | 2 minor omission |
| Citation sufficiency | **0.86** | 3 minor overreach, 1 significant overreach |

Eleven citation instances per probe, 33 verdicts, **zero parse errors**.

Meanwhile the root count over the same three citations is **1**
(`independence_demo.py`).

The discriminating experiment predicted in the previous README has been run and
the answer is the one that supports a fourth dimension: the three probes score
the section well while the evidence-root analysis shows a single root.

## The sharper finding, which is not the one predicted

The prediction was that the probes are *structurally unable to see* the
derivation. That turns out to be too strong, and the real result is more
interesting.

**8 of the 33 rationales explicitly discuss derivation.** The judges write
things like:

> "The source fully supports the assertion that the trade press article is a
> secondary source that derives its data from the original Meridian note and did
> not conduct independent measurements."

So the judges *read* the derivation. The corpus states it plainly and they
report it back.

**And not one of the nine deductions is because of it.** Every verdict below
full marks is a scope mismatch inside a single citation — a detail absent from
that particular source, or a sentence mentioning "review literature" when the
cited source is the trade press. None says the three citations are one
observation, because no probe has a verdict that could say it.

The accurate claim is therefore narrower and worse:

> A judge can notice derivation and still not act on it, because every probe
> scores one citation against one source. The number of independent sources is
> not a quantity any of the three produces.

Awareness without a place to put it. That is a harder problem than blindness,
because adding a fourth judge does not fix it on its own — the dimension has to
exist in the output.

## Honest weaknesses in this measurement

- **One judge model, one run.** `gpt-4.1` at temperature 0. No repeats, so no
  variance estimate. A different judge might score differently.
- **The report section was not written by NIST's generator.** Their report
  pipeline sends `reasoning_effort` alongside `temperature`
  (`exhaustive_scanner.py:104`, `pipeline.py:115`); OpenAI's reasoning models
  reject a non-default temperature and its chat models reject
  `reasoning_effort`, so the generator cannot run against the public OpenAI API
  without editing NIST's code. The generator was written for their internal
  `gpt-oss-120b` endpoint. **The probes are unaffected and unmodified** —
  `probes/_judge.py::call_judge` sends only model, messages, temperature and
  `response_format`. The section was written by `gpt-4.1` from the same three
  documents.
- **The section is unusually careful.** It states outright that the secondary
  sources derive from the original. A sloppier report would give the probes more
  to catch. This makes the corpus a *weak* test in one direction and a strong
  one in another: even when the derivation is spelled out in the text, no probe
  converts it into a finding.
- **Probes are rate-limit sensitive.** The first attempt returned 11 of 11
  `PARSE_ERROR` on completeness. That was not the judge failing but HTTP 429 —
  the dispatcher fires all judge calls concurrently and exceeded a 30k
  tokens-per-minute account limit. Recorded because a mean score of 0.0 from
  rate limiting looks exactly like a mean score of 0.0 from disagreement, and
  anyone reproducing this should check `num_parse_error` before reading a mean.

## What would still refute the fourth-probe case

A probe or verdict category in the current three that lowers a score *because*
sources share a root. Nothing in these 33 verdicts does, but the search was over
one corpus and one judge.
