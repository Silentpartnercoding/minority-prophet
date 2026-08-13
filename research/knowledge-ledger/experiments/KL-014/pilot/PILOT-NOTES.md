# KL-014 pilot notes — 2026-08-13

**EXPLORATORY PILOT. ONE CONTROL DOMAIN. NOT A RESULT.**

This answers nothing about HRI-1. It establishes feasibility, and it refuted one
of the directional expectations registered in `preregistration-v0.2.json` before
any data was retrieved. Both of those are worth having; neither is a finding
about the world.

## What was run

Nine claims, hand-retrieved, across three resolved propositions: two Nobel Prize
announcements and one sporting result included deliberately as a contrast case
where independent observation is plausible. Split factor computed under both
digest-construction rules pinned in v0.2, before retrieval.

| prop | claims | obs | D1 split | D2 split | no primary cited | meets declared minimum |
|---|---|---|---|---|---|---|
| P1 Nobel Physics | 4 | 1 | 4.00 | 3.00 | 50% | yes |
| P2 Nobel Chemistry | 2 | 1 | 2.00 | 2.00 | 50% | **no** |
| P3 Super Bowl LIX | 3 | 1 | 3.00 | 3.00 | 67% | **no** |

Only P1 met the declared minimum of four claims. P2 and P3 are shown for
structure and excluded from the primary tally. The shortfall is reported rather
than resolved by extending retrieval, per `stopRule`.

## The registered expectation that was refuted

v0.2 registered D2-cited-primary as tending to **minimal split** — "claims
resting on one primary source collapse to one root". On P1 it did not collapse
to one. It gave **three**.

The reason is the thing the pilot actually surfaced: **five of nine verified
claims (56%) cite no resolvable primary source at all.** D2 falls back to D1 for
each of those, so each becomes its own evidence root regardless of which digest
convention is adopted.

D1's registered expectation — maximal split, one root per issuer — held exactly.

## What that suggests, weakly

The digest convention was the parameter v0.2 was most worried about. On this
corpus it is not the binding constraint: the D1/D2 ratio on P1 is **1.33**, not
the factor of N that v0.2 anticipated. Choosing the more favourable rule moved
the split factor from 4.00 to 3.00 and no further.

What dominates instead is that most published claims do not identify their
underlying evidence in any resolvable way. A claim with no attribution is, to
the aggregator, indistinguishable from an independent observation — which is
CE-01 (`formal/COUNTEREXAMPLES.md`) and ledger item U2 appearing in real
published text rather than in a constructed witness.

If this survived a proper confirmatory run, the implication would be that
tightening `provenance/ROOT-IDENTITY.md`'s digest convention is not where the
leverage is. The leverage would be in refusing to mint a root for a claim that
cannot identify its evidence — which is an ingest policy question, not an
identity question.

**None of that is established here.** It is one pilot, on nine claims, and see
below.

## Why this cannot be a result

- **Corpus hand-picked.** Propositions were chosen by the analyst after seeing
  that coverage existed. Two of three are institutional announcements, the
  maximal-syndication case. Selection alone could produce these numbers.
- **Single control domain.** One agent under one operator did the retrieval, the
  attribution judgement and the computation. The inter-rater statistic is
  undefined, not merely unmeasured — there is one rater. AGENTS.md boundaries 2
  and 3.
- **Not blinded.** The sole labeller also computed the identities.
- **Below its own minimum.** One of three propositions qualified.
- **Corpus is "what was fetchable".** Six retrievals failed with 403, 406 or
  timeout. A corpus assembled from what a fetcher can reach is a selected
  corpus. Failures are recorded in `corpus-20260813.json`, not omitted.

## What a confirmatory run would need

Everything in `preregistration-v0.1.json` and `v0.2.json` that this pilot could
not supply: a declared corpus fixed before retrieval, at least 200 propositions,
three independent labellers blinded to the root identities, and an inter-rater
floor of 0.67 with stop-and-report on failure.

The pilot's contribution is narrow and specific: it shows the measurement is
mechanically possible, it shows the instrument distinguishes the two rules on
real text, and it says the fallback rate is the quantity worth powering the
study around — which was not obvious before, and which changes what a
confirmatory run should measure first.
