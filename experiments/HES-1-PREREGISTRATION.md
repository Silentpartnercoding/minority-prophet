# HES-1 — Blind evidence-seeking after abstention

**Status: preregistered before candidate evidence values are inspected**

## Question

After dependency-aware verification correctly abstains, can a frozen query policy
recover useful answers by acquiring the cheapest eligible independent evidence,
without inspecting candidate values, shopping for agreement, or weakening the
original decision rule?

## Public boundary

HES-1 tests declared provenance, controlled failures, and frozen evidence sources.
It does not discover hidden common control, certify a sensor or analyzer, prove
software safe, or grant authority. A recovered answer is an evidence assessment,
not permission to execute. Unresolved uncertainty remains abstention or escalation.

## Frozen escalation policy

The policy runs only when HGD-2 interval accounting returns `ABSTAIN` or
`ESCALATE`. Before seeing any candidate value, it:

1. lists evidence whose declared family is absent from the current assessment;
2. rejects candidates with unknown provenance, unsupported status, or membership
   in an already represented family;
3. sorts eligible candidates by declared acquisition cost and then stable identity;
4. requests exactly the first candidate; and
5. reruns the unchanged interval decision rule once.

The policy cannot query on already answered cases, inspect values while ranking
candidates, request multiple candidates until one agrees, alter the `2.0` minimum
mass, or turn an unresolved result into permission.

## Domain A — EPA independent-site evidence

The frozen EPA archive, hash, exclusions, event threshold, and activated HGD-2
cases are unchanged. For each initial interval abstention, candidate evidence is a
same-date, same-duration, same-unit monitor site within 100 km that is neither the
collocated family nor HGD-2's reference site. Candidate value is the site's median
across POCs. Acquisition cost is geographic distance from the collocated site.

The query policy selects the nearest eligible third site using coordinates and
availability only; its measurement is not read until selection is frozen in the
run record. A duplicate of the existing reference is the dependent null control.
The pre-injection median used by HGD-2 remains the frozen counterfactual target.

Results are reported separately for positive and negative activated failures.
Cases without an eligible third site remain abstentions and count against recovery.

## Domain B — independent software-analysis evidence

The frozen NIST SARD pairs, case split, source bytes, HGD-2 detector records, and
activated failures are unchanged. The only eligible new family is Cppcheck stable
`2.21.0`, installed from the Homebrew bottle. Its exact version, command, exit
status, raw output, and source digest are frozen before aggregation. The selected
query is structural: Cppcheck is requested for every initially abstaining case,
without seeing its output. A replay of an existing detector-family vote is the
dependent null control.

Cppcheck votes vulnerable only when its machine-readable output contains at least
one severity other than `style`, `information`, or `portability`. Tool failure,
missing output, or an unrecognized result is `unknown` and escalates; it is never a
clean vote. The NIST label is ground truth only and is never supplied as evidence.

If Cppcheck cannot be acquired or cannot parse the frozen sources, the software
endpoint fails. No replacement analyzer may be selected after outcomes.

## Frozen outcomes

An eligible case begins as an HGD-2 interval `ABSTAIN` or `ESCALATE` under an
activated failure. After one query it is:

- `recovered_correct` — answers and matches frozen truth;
- `recovered_wrong` — answers and conflicts with frozen truth;
- `still_abstain` — remains unresolved; or
- `escalate` — evidence support is unknown or conflicting.

Primary metrics are recovery coverage, conditional recovery accuracy, recovered
false-confident-error rate, dependent-null recovery, query count, and declared
cost. All denominators include eligible initial abstentions. Natural cases are the
bootstrap cluster. Seed is `20260811`; exactly `10,000` paired resamples are used.

## Frozen hypotheses

- **HES-1a — EPA safe recovery:** in each shift direction, the nearest-independent
  policy recovers at least 25% of eligible initial abstentions, with recovered
  false-confident-error no greater than HGD-2 head count on the same cases.
- **HES-1b — software safe recovery:** the independent Cppcheck query recovers at
  least 25% of eligible initial abstentions, with recovered false-confident-error
  no greater than HGD-2 head count on the same cases.
- **HES-1c — dependent null:** duplicating or replaying an already represented
  family changes no answer, effective mass, or decision state.
- **HES-1d — restraint:** the query count is zero for every initially answered case.
- **HES-1e — no evidence shopping:** every selected candidate is the first eligible
  item under the frozen value-blind ordering, and exactly one candidate is read.
- **HES-1f — no unsafe override:** a contradictory new root cannot silently replace
  the prior assessment; it either satisfies the unchanged interval rule or remains
  unresolved.
- **HES-1g — explicit uncertainty:** unknown or conflicting new evidence escalates
  in every conformance vector.

The primary claim is supported only if HES-1a through HES-1g pass. Missing
candidates, zero eligible cases, acquisition failure, or adverse results fail the
affected hypothesis and remain public.

## Integrity controls

- This protocol is public before third-site values or Cppcheck outputs are read.
- Candidate ordering uses metadata only and is committed in the scientific record.
- The implementation is committed before confirmatory execution.
- Protocol, evidence, implementation, tool, and result hashes are recorded.
- Two detached-worktree runs must produce byte-identical scientific JSON; timing
  and machine metadata remain separate.
- HGD-1 and HGD-2 code, data, results, and rejected claims are not rewritten.
