# HGD-2 — Activated-failure replication across environmental and software evidence

**Status: preregistered before confirmatory acquisition or execution**

## Why HGD-2 exists

HGD-1 preserved a rejected primary claim because its five-percentage-point
absolute endpoint exceeded the largest available baseline error. HGD-2 does
not rewrite HGD-1. It tests the same safety idea with base-rate-aware endpoints,
untouched controls, positive and negative failures, and a non-weather domain.

## Question

When a documented evidence family suffers a shared failure, can
dependency-aware interval accounting cut confidently wrong conclusions by at
least half while preserving ordinary performance when no failure is present?

## Public boundary

The experiment tests declared dependency families and controlled failures. It
does not infer hidden common control, establish historical sensor error,
certify any static analyzer, prove source code safe, or grant execution
authority. Abstention is recorded separately and cannot become permission.

## Frozen methods

1. observation head count;
2. unique-origin count;
3. binary dependency-family collapse;
4. declared midpoint weighting; and
5. interval-valued dependency accounting.

Methods answer only when effective lower mass is at least `2.0` and one side's
lower mass exceeds the other side's upper mass. Otherwise they abstain.
Unknown or conflicting dependency support escalates.

## Domain A — EPA collocated PM2.5 replication

HGD-2 reuses the archive and source commitment frozen by HGD-1:

`https://aqs.epa.gov/aqsweb/airdata/daily_88101_2025.zip`

It reuses HGD-1's deterministic site pairing, 100-km ceiling, development-site
exclusion, duplicate handling, and `35.0` micrograms-per-cubic-meter event
threshold. No new site or threshold may be selected by outcome.

Untouched controls use shift `0`. Confirmatory failures apply `-20`, `-10`,
`-5`, `+5`, `+10`, and `+20` to every POC in the collocated family only. The
separate-site family is unchanged. The pre-injection median remains the frozen
counterfactual target.

An **activated case** is defined independently of the interval method: the
injected failure changes head count from its untouched answer to an incorrect
answer. Results are reported for all cases, activated cases, shift direction,
and sample duration. This conditioning measures resistance when the trap is
actually active; untouched controls prevent abstention-only success.

## Domain B — NIST SARD software-analysis replication

The frozen source is NIST SARD test suite 101, “C Test Suite for Source Code
Analyzer — Secure v2”:

`https://samate.nist.gov/SARD/downloads/test-suites/2015-03-15-c-test-suite-for-source-code-analyzer-secure-vv2.zip`

NIST publishes archive SHA-256
`19b7059d067c093d078c6b34d1ec669ccd648aa5b8507ca3fb49d58324bb802b`
and 102 labeled good/bad cases. The archive will be acquired only after this
protocol has a public commit. Its unmodified hash, headers, file inventory, and
tool versions will be recorded before source inspection.

Eligible cases are accepted or candidate C/C++ source cases with an
unambiguous suite-provided good/bad label. Deprecated, mixed, unlabeled,
unbuildable, and duplicate-digest cases are excluded. Cases sort by archive
path. The first 20% within each label and CWE stratum are development-only;
the remaining 80% are confirmatory. No source is selected by a detector's
performance.

Seven frozen detector configurations form three declared families:

- **compiler frontend:** Apple Clang static analysis, warning baseline, and
  security-warning configuration;
- **Flawfinder:** risk thresholds 1 and 3; and
- **lexical rules:** dangerous-call and unchecked-input rule sets.

Exact commands, versions, raw outputs, exit status, and source digests are
recorded. A detector votes vulnerable when it emits at least one finding for
the case. Tool failure is `unknown`, never a clean vote.

Untouched controls use the original outputs. Controlled family failures are:

1. `false_negative` — every member of one family is forced clean on a labeled
   bad case;
2. `false_positive` — every member is forced vulnerable on a labeled good
   case; and
3. `stale_replay` — every member receives that family's deterministic output
   from the immediately preceding case in path order.

Each family and failure type is tested separately. An activated case is one
where the injected family failure changes head count from its untouched answer
to an incorrect answer. No mutation is described as a real tool defect.

## Frozen endpoints

For each domain and pooled across domains:

- false-confident-error rate on activated cases;
- relative risk versus head count with a paired 95% bootstrap interval;
- answered coverage on activated cases;
- untouched-control accuracy and answered coverage;
- calibration coverage and width of effective-root intervals; and
- abstention and escalation.

Bootstrap seed is `20260810`; exactly `10,000` resamples use the natural case
as the cluster. Domain results are never averaged before their individual
gates are evaluated.

## Frozen hypotheses

- **HGD-2a — activated EPA safety:** in both shift directions, interval
  accounting's activated false-confident-error relative risk versus head count
  has a 95% upper bound at most `0.50`.
- **HGD-2b — activated software safety:** across all three software failure
  types, the pooled activated relative-risk upper bound is at most `0.50`, and
  no family/failure cell has point relative risk above `0.75`.
- **HGD-2c — control accuracy:** in each domain, interval untouched-control
  accuracy is at least 95% of head-count accuracy.
- **HGD-2d — control coverage:** in each domain, interval untouched answered
  coverage is at least 95% of head-count coverage.
- **HGD-2e — attacked usefulness:** interval accounting answers at least 50%
  of activated cases in each domain.
- **HGD-2f — interval calibration:** at least 95% of frozen synthetic graded
  worlds contain true effective root mass, with median width below `2.0`.
- **HGD-2g — no silent uncertainty:** every unknown or conflicting dependency
  record escalates in conformance vectors.

The primary claim is supported only if HGD-2a through HGD-2g all pass.
Incomplete cells, zero activated cases, tool-acquisition failures, and adverse
results fail the affected hypothesis and remain public.

## Integrity controls

- Protocol and source commitments are public before confirmatory acquisition.
- Structural feasibility may be inspected only through a separately committed,
  explicit amendment before any detector outcome comparison.
- No threshold, family, exclusion, or endpoint changes after outcomes.
- Runner records protocol, data, implementation, and tool hashes.
- Two detached-worktree executions must produce byte-identical scientific
  JSON; timings remain separate.

## Structural-feasibility amendment — paired NIST source

After the initial public source commitment, archive inventory and manifest
labels were inspected without reading source content, running a detector, or
comparing any outcome. That inspection established that suite 101 contains
only the 102 `good` cases. Its NIST-published companion is suite 100, “C Test
Suite for Source Code Analyzer v2 — Vulnerable,” containing the corresponding
102 `bad` cases and explicit pair metadata.

Domain B therefore uses the paired union of suites 100 and 101. Suite 100 is
frozen at:

`https://samate.nist.gov/SARD/downloads/test-suites/2015-03-15-c-test-suite-for-source-code-analyzer-v2-vulnerable.zip`

NIST publishes SHA-256
`423f20e8ead850bf64cd93cd4a73dc1161d7b5bb6036328e16fc32e27d09f0d1`.
Only reciprocal pairs whose two manifests name each other and share a CWE are
eligible. Both members must be accepted or candidate, unambiguous, and
single-labeled. Development/confirmation splitting occurs by reciprocal pair,
within CWE, so a good/bad pair can never cross the boundary. This amendment
changes no detector, failure, metric, threshold, or success rule.
