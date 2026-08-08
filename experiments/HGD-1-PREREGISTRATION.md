# HGD-1 — Graded dependence under shared sensor context

**Status: preregistered before confirmatory data inspection or execution**

## Question

Can an interval-valued account of partially shared evidence preserve genuinely
distinct measurements without treating collocated sensors as either wholly
independent or wholly identical?

## Boundary

HEO-1 distinguishes supported evidence origins. HGD-1 begins after those
origins are established and asks how much evidential separation remains when
origins share equipment, location, calibration, operator, model, or another
failure domain. Statistical similarity alone does not establish a dependency.
The experiment tests declared dependency structure and injected failures; it
cannot discover an undisclosed common cause, prove a measurement true, or
grant authority.

## Unit and output

Each observation has one origin and zero or more supported dependency
components. A component has a declared lower and upper shared-failure weight
in `[0, 1]`. Identical origins remain one root. Distinct origins with no shared
component remain separate. Partially overlapping origins produce an interval
of effective root mass rather than invented scalar certainty.

For a dependency component touching `n` origins with weight interval
`[w_low, w_high]`, its contribution reduces naive mass by between
`w_low * (n - 1)` and `w_high * (n - 1)`. Reductions from nested or overlapping
components are capped so effective mass remains in `[1, n]`. Unsupported,
conflicting, cyclic, or incomplete dependency records return `ESCALATE`.

## Track A — frozen synthetic model

- seeds `701–720` inclusive;
- `250` base worlds per seed;
- one binary event;
- eight sensors, each correct with probability `0.85` before injected failure;
- one adverse sensor, correct with probability `0.25`;
- stable identifiers derived from seed, world, and sensor role; and
- bootstrap seed `20260809` with exactly `10,000` world-clustered resamples.

Each base world yields matched variants:

1. `independent_8` — eight separate sensors and no shared component;
2. `duplicate_origin_8` — eight records from one origin;
3. `shared_station_8` — eight instruments under one station-wide component;
4. `two_station_4x4` — two independent station components;
5. `partial_calibration_8` — eight instruments sharing a calibration component
   with true injected weight `0.50`;
6. `nested_station_model` — station and downstream-model components overlap;
7. `unknown_overlap` — component strength is unsupported;
8. `forged_separation` — a shared component is omitted from an otherwise valid
   receipt; and
9. `common_mode_flip` — a declared component flips all attached observations.

## Track B — frozen observational stress test

The external sample is the US EPA Air Quality System 2025 daily PM2.5 FRM/FEM
archive for parameter `88101`. The frozen source URL is:

`https://aqs.epa.gov/aqsweb/airdata/daily_88101_2025.zip`

The archive will be downloaded only after this protocol has a public commit.
SHA-256, retrieval time, byte length, response headers, and the unmodified
archive will be recorded. Eligible pairs must share state, county, site,
parameter, date, sample duration, and units; have different POCs; have valid
numeric samples; and have no invalidating qualifier. AQS defines POC as the
identifier distinguishing instruments measuring the same parameter at one
site. The lexicographically first eligible site is the frozen development
sample and is excluded from confirmation. All remaining eligible site-years
form the confirmatory sample; no site may be selected by outcome.

For each pair, the unchanged measurements establish an observational baseline.
Frozen counterfactual shifts of `+5`, `+10`, and `+20` micrograms per cubic
meter are then applied to every POC within the same site-day dependency family.
The pre-injection site-day median is the counterfactual target. This tests
resistance to a known injected common-mode failure, not whether the historical
EPA values were correct and not whether collocation alone proves causal
dependence.

NOAA USCRN is reserved as a named replication target. NOAA documents three
thermometers per station, but the readily downloadable quality-controlled
products expose a combined air-temperature field. HGD-1 will not pretend that
field is three raw sensor streams.

## Frozen comparators

1. observation head count;
2. binary origin collapse;
3. binary dependency-family collapse;
4. fixed pairwise-correlation weighting from the development sample only;
5. declared midpoint weighting; and
6. interval-valued dependency accounting with conservative escalation.

Any decision whose result differs across the effective-mass interval returns
`ABSTAIN`. Missing dependency support returns `ESCALATE`. Neither state may be
converted to permission.

## Metrics

- true effective-root interval coverage in synthetic worlds;
- interval width;
- independent-origin retention;
- false-independent mass under common-mode failure;
- false-alarm and missed-event rates at matched answered coverage;
- abstention and escalation rates; and
- forged-separation acceptance.

## Frozen hypotheses

- **HGD-1a — extremes:** duplicate origins have mass `[1, 1]`; eight supported
  independent origins have `[8, 8]`.
- **HGD-1b — partial coverage:** at least 95% of synthetic partial-dependence
  worlds contain the true effective root mass in the reported interval.
- **HGD-1c — useful precision:** median interval width is below `2.0` roots in
  supported partial-dependence worlds.
- **HGD-1d — uncertainty preservation:** every `unknown_overlap` world
  escalates.
- **HGD-1e — common-mode safety:** at matched answered coverage, the upper
  bound of the paired false-confident-error difference versus head count is at
  most `-0.10` under declared common-mode flips.
- **HGD-1f — independent retention:** at least 95% of supported fully
  independent origins retain their full mass.
- **HGD-1g — observational direction:** on the frozen EPA counterfactuals,
  interval accounting has no higher false-confident-error rate than head count
  at every injected shift, with at least one shift lower by `0.05` or more.

The primary claim is supported only if HGD-1a through HGD-1g all hold. Null,
adverse, incomplete, and contradictory outcomes remain reportable.

## Integrity controls

- No confirmatory measurement value may be inspected before public commit.
- Source choice, eligibility, shifts, seeds, thresholds, metrics, and success
  rules cannot be tuned after inspection.
- A data manifest must distinguish documentation review from value inspection.
- The runner records protocol, source, and implementation hashes.
- Two detached-worktree runs must produce byte-identical scientific JSON.
- Timings remain separate observational output.

## Structural-feasibility amendment — before outcome analysis

After the first public commit, acquisition inspected the archive header, two
leading records, and structural counts only. No outcome distribution, method
comparison, injected result, or hypothesis result was computed. That inspection
showed two underspecified points that would make Track B non-falsifiable or
non-reproducible:

1. the daily archive has no qualifier column; and
2. a collocated family by itself supplies no outside reference against a
   site-wide common-mode shift.

This amendment restarts Track B before outcome analysis. The missing qualifier
is recorded as unavailable; rows are instead required to have a numeric daily
mean and positive observation count. Duplicate rows for one frozen group and
POC are collapsed deterministically by lexicographic full-row order.

Each collocated site-day is paired with the geographically nearest different
site having the same date, sample duration, units, and at least one valid POC.
Distance is Haversine distance over the archive coordinates; ties resolve by
state, county, site, then POC. The separate site must be within `100 km` or the
case is excluded. The collocated site is one declared full-dependence family;
the separate site is a second family. The pre-injection median across the two
families is the counterfactual target. Only the collocated family receives the
frozen shift.

The binary event threshold is fixed at `35.0` micrograms per cubic meter. A
method may answer only with effective lower mass of at least `2.0`; otherwise
it abstains. Track B reports results separately by sample duration and pooled,
and it must report coverage alongside error. HGD-1g additionally requires at
least `25%` answered coverage for interval accounting at every shift. These
rules supersede only the underspecified Track B mechanics above; Track A and
all other frozen hypotheses remain unchanged.
