# KL-016 feasibility — the ancestry this experiment consumes is largely not recorded

Measured before any case was scored, so the registered invalidation condition is
evaluated against a number rather than an impression. Reproduce:

```sh
python3 research/knowledge-ledger/experiments/KL-016/src/reference_coverage_probe.py
```

Raw output: `FEASIBILITY-v0.1-probe.json`. Source: OpenAlex `has_references`,
field Mathematics.

## What was measured

The share of works in each case's era recording **any** reference. A work
recording none is a root by default. That is precisely the population
`KL-014/HRI1-BLOCKER-20260816.md` identifies as carrying the over-count — and
the population in which this experiment's method has nothing to consume.

| case | cutoff | era | works | record references |
|---|---|---|---:|---:|
| li-crossing | 1914 | 1910–1918 | 10,234 | **5.5%** |
| polya | 1958 | 1954–1962 | 48,047 | 33.9% |
| euler-sum-of-powers | 1966 | 1962–1970 | 100,578 | 42.6% |
| mertens | 1985 | 1981–1989 | 201,588 | 57.3% |
| *modern ceiling* | 2010 | 2005–2015 | 949,560 | *62.6%* |

## Three findings, one of which was not expected

**1. li-crossing is not runnable.** At 5.5%, roughly nineteen of every twenty
works in Littlewood's era record no ancestry at all. There is no lineage to
recover, so nothing about lineage-aware aggregation can be tested on it. This
was the registered risk and it is confirmed at the low end of expectation.

**2. There is a ceiling, and it is 62.6%.** No era can exceed what the index
records today. So a case is not weak by being below 100%; it is weak by being
far below the ceiling. On that reading mertens (57.3%) is essentially at the
modern rate and polya/euler sit at roughly half to two-thirds of it.

**3. Mathematics is the BEST-documented field measured, not the worst.** This
contradicts the working assumption — including the one stated when a
biomedical follow-on corpus was proposed — that modern applied literature would
supply better ancestry. It does not:

| field | 1990–1999 | 2005–2015 |
|---|---:|---:|
| Mathematics | 57.0% | **62.6%** |
| Physics & Astronomy | 57.1% | 57.4% |
| Biochemistry & Molecular Biology | 54.7% | 54.2% |
| Medicine | 41.2% | 47.6% |
| Psychology | 36.4% | 38.7% |

A KL-017 justified by *"post-1980 science has better ancestry data than old
mathematics"* is justified by a false premise. The premise was measured and is
false. Whatever case is made for a second corpus, it cannot be that one.

This is consistent with the repository's headline measurement (46.2% of 60.8M
2015–2024 articles record no ancestry) and refines it: the no-ancestry share is
strongly field-dependent, and mathematics is on the favourable end.

## The gap this probe exposes in the frozen spec

`COLLECTION-SPEC-v0.1.json` says the experiment stops if ancestry "cannot be
reconstructed" for three or more of the four refuted cases. **It never defines
what that means numerically.** One case is plainly out at 5.5% and one plainly
in at 57.3%; polya and euler decide whether the stop rule fires, and there is no
registered threshold to decide them by.

That is a defect in the specification, not in the data. It must be fixed by an
**owner-set threshold, registered before any case is scored** — the same
discipline as KL-001's 15% ceiling, which was fixed before the population it
would be tested against existed. Choosing it after seeing which cases clear it
is choosing the result.

The spec is frozen and is **not edited**. The threshold is registered as an
amendment sidecar, in the same way `PROTOCOL-COMMIT` sidecars bind commits
without editing the protocol.

## What this does not say

It does not say polya or euler will fail. Field-wide reference coverage is a
screening instrument: it can rule a case out cheaply and cannot rule one in. The
pre-cutoff literature of a specific conjecture may be far better or far worse
recorded than its era's average, and only the case-level collection will show
which. This probe was run to avoid spending that collection on a case already
known to be empty.
