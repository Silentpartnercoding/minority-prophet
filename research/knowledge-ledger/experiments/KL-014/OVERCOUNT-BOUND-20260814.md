# Where the over-count bound is worst — 2026-08-14

Descriptive measurement, no hypothesis test. The rule was fixed before querying
and had no analytic freedom to abuse: **zero recorded references / all journal
articles**, sliced by field and by year. There is no threshold, no comparison
and no discarded slice.

## Why a bound and not an estimate

HRI-1 asks how badly the aggregator over-counts sources. A point estimate needs
ground truth on the true number of observations, which no corpus supplied and
which one control domain cannot label. A **bound** needs no ground truth.

A claim whose recorded ancestry is empty becomes an evidence root. In the
copy-dominant regime this programme exists for — `N` claims all descending from
one observation — each such claim appears as its own independent root. So with
`u` the share of claims recording no ancestry:

> **over-count factor ≥ u × N**

## By field, 2015–2024

| field | articles | zero recorded references | `u` |
|---|---:|---:|---:|
| Medicine | 11,068,422 | 3,636,308 | **32.9%** |
| Computer Science | 2,894,855 | 1,297,732 | **44.8%** |
| Engineering | 10,559,679 | 6,175,381 | **58.5%** |
| Economics, Econometrics & Finance | 1,585,240 | 927,252 | **58.5%** |
| Social Sciences | 8,980,918 | 5,772,886 | **64.3%** |
| Arts and Humanities | 3,008,859 | 2,230,605 | **74.1%** |

**The domain decides the damage, by a factor of 2.3.** A thousand claims
descending from one observation yield at least ~329 apparent independent roots in
medicine and at least ~741 in the humanities. Any deployment quoting a single
global figure is quoting the wrong one for whichever field it is actually in.

## By year, all fields

| year | `u` |
|---|---:|
| 2015 | 59.2% |
| 2017 | 56.6% |
| 2019 | 50.8% |
| 2021 | 37.5% |
| 2023 | **29.4%** |
| 2024 | 36.5% |

The floor is falling — roughly halving across the decade. The 2024 uptick is
most plausibly indexing lag rather than a reversal: recent works have had least
time for publishers to deposit reference lists. That is an interpretation, not a
measurement, and is marked as such.

Even at the best year measured, a thousand claims from one observation still
yield at least ~294 phantom roots.

## What this does and does not establish

**Does.** A floor on the over-count, at scale, across 60.8M articles, requiring
no labelling and no judgement. It holds whatever the true observation count is,
because it counts only claims that record no ancestry at all.

**Does not.** The typical case. This is a worst-case regime bound, and a corpus
where claims genuinely are independent would show no over-count at all despite
the same `u`. Nothing here estimates how often the copy-dominant regime obtains.

**Cause is mixed and mostly mundane.** Roughly half the zero-reference works
carry a DOI, so they are properly indexed and simply have no reference list
deposited. This is not a finding that half of science cites nothing. It does not
matter for the bound: the aggregator cannot tell a claim that cited nothing from
one whose citations were never recorded, and mints a root either way.

**Attribution gates are field-sensitive.** `EvidenceGraph(require_root_evidence=True)`
removes exactly this population. Its refusal rate should therefore be expected
near 33% on medical corpora and near 74% on humanities corpora, and a rate far
from the field's `u` is worth investigating before it is worth loosening.
