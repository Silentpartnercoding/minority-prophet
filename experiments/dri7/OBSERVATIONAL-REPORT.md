# DRI-7 — observational replication on an unauthored corpus

*Not a preregistration. This file is deliberately not named one; see section 2.*

**Status: OBSERVATIONAL. ANALYSIS ALREADY PERFORMED. Read section 2 before any
result below is cited.** This is not a frozen-then-run experiment in the sense of
DRI-1 through DRI-6, and presenting it as one would be a false claim about its
own evidence class.

Design context: the DRI series to date generates its own worlds. DRI-4's
generator, DRI-5's admissibility function and DRI-3's arms all produce lineage
records whose ground truth is known because the experiment authored it. That is
the right way to establish a mechanism and the wrong way to establish a rate: a
rate measured on an authored corpus reads back the setting that authored it.

DRI-7 supplies the arm the series lacks. It measures the same rules against a
corpus produced by six weeks of ordinary operation in a production job-control
plane, by processes with no knowledge of this experiment, for purposes unrelated
to it.

## 1. Identifier

DRI-7, observational, protocol v1.

## 2. What is not preregistered, stated first

The measurement in section 6 was computed **before** this document existed. The
corpus is historical: it was written between 2026-07-31 and 2026-09-15 and could
not have been withheld from the analyst, because the analyst found the effect
first and wrote the protocol afterwards.

Consequences, which no later reader should have to reconstruct:

- **No hypothesis was frozen before observation.** The null below is stated for
  completeness, not as a commitment made in ignorance of the outcome.
- **Analyst degrees of freedom are unbounded.** Corpus choice, rule definition
  and the checkable/unverifiable split were all fixed with the data visible.
- **The effect size cannot be treated as an estimate.** It is a description of
  one corpus on one host.

What survives that, and the reason the arm is worth having: the **direction** of
the DRI-6 result is reproduced on data nobody authored, and the record-only rule
is shown to be non-falsifiable by construction rather than merely inaccurate.
A non-falsifiability claim is robust to analyst freedom in a way a rate is not —
it is refuted by exhibiting a single record the rule rejects, and none exists.

## 3. Questions

1. **Detection.** On an unauthored corpus, how many silent failures does a
   record-only rule detect?
2. **Confirmation.** Does one dereference of the referent reduce them?
3. **Generality.** Does the answer depend on the referent being a git object, or
   does it hold for an unrelated identifier scheme?
4. **Addressing.** Of the failures a second look finds, how many are recoverable
   by content rather than by location?

## 4. Null hypothesis

Looking twice makes no difference to silent failures on an unauthored corpus.

## 5. Corpus

**Corpus A — recorded result commits.** Every job in the ledger of a private
production job-control plane carrying a `resultCommit` (in the job record or in its worker-exit receipt): a
40-character git object identifier written by a runner at completion, plus the
repository it was written in. n = 358.

**Corpus B — recorded QA artifacts.** From the same ledger, every verification
artifact carrying a
`sha256` and an absolute filesystem `reference`. n = 284. Independent of A in
mechanism: a filesystem path, not a git object, written by a different code path
for a different purpose.

**Neither corpus is distributed with this repository.** Both are private
operational records; what is published here is the method, the aggregates, and
the boundaries. `measure.py` runs against a ledger you supply.

Neither corpus was constructed for this experiment. Neither contains a planted
defect. Ground truth is established by dereference, not by generation.

## 6. Rules and results

Rules are cumulative. Each adds exactly one operation to the one before.

**Rule A — record-only.** Accept when the identifier is well formed and a
location is named. Nothing outside the record is consulted.

**Rule B — look twice.** Rule A, then dereference the referent once.

**Rule C — look by content.** For referents Rule B finds absent, search a
content-addressed store by hash rather than by location.

| | Corpus A (n=358) | Corpus B (n=284) |
| --- | ---: | ---: |
| Rule A accepts | 358 / 358 | 284 / 284 |
| Rule A detects | **0** | **0** |
| Rule B checkable on this host | 123 | 284 |
| Rule B finds absent | 102 / 123 = **0.829** | 284 / 284 = **1.000** |
| share of silent failures found only by looking twice | **1.000** | **1.000** |
| Rule C recoverable by content | not measured | 233 / 284 = **0.820** |
| genuinely unrecoverable | — | 51 |

## 7. Findings

**7.1 The record-only rule is not inaccurate; it is non-falsifiable.** It accepts
642 of 642 records across both corpora. This is not a low detection rate. No
input in either corpus can make it return false, because every record is
internally well formed — the defect is entirely outside what it inspects. A rule
whose outcome has only ever held one value has not been tested, whatever its
sample size.

**7.2 The DRI-6 direction reproduces on unauthored data.** DRI-6 reported that a
second look removes 68–100% of silent failures on generated worlds. Here it
removes 100% on both corpora, because the first look removes none. That is the
top of the generated band, reached on data with no author.

**7.3 The result does not depend on the identifier scheme.** Corpus B shares no
mechanism with Corpus A — different writer, different identifier, different
storage — and behaves identically under Rules A and B. What fails is reading the
record instead of the referent, not anything specific to git.

**7.4 Location was the wrong identifier, and content recovers most of it.** 82%
of Corpus B's absent referents are retrievable by content hash from a store that
was already present. They were never lost; they were addressed by a path that did
not survive. This is a direct argument for content addressing made from failure
data rather than from design preference, and it is new to the series.

## 8. Mechanism, recorded so the corpus is not mistaken for a sample

Corpus A's absences have a single known cause. Runners execute in
`git clone --shared`, so objects a worker writes live only inside a disposable
clone and are destroyed with it, while the identifier survives in the ledger and
nothing re-checked it. Twelve sampled absent identifiers were confirmed absent
from all 51 repositories on the host.

This is genuine unrecorded dependence at operational scale, not a fixture. It is
also **one** mechanism. A second corpus with a different cause would test
generality further than Corpus B does, since B shares the same disposability.

## 9. Negative control: the same disease, wearing different clothes

Section 7.1 found a check that can only return one value because it reads the
record instead of the referent. The same ledger contains the other way to build
one.

`attempt_leases` holds 2,299 rows and **0** are missing a job or a worker. That
is a real table doing real work, and it is genuinely clean. Seven further tables
— `workflow_runs`, `node_runs`, `artifacts`, `edge_transitions`, `evaluations`,
`owner_decisions`, `outcomes` — hold **0 rows each**, so a check aimed at any of
them also returns zero defects, for the opposite reason.

Point an extractor at those eight and it reports a sound control plane. The
report is true. It is also worth nothing, because *zero defects over zero rows*
and *zero defects over 2,299 rows* print identically, while 102 absent referents
sit in a ninth table nobody opened.

So the series' claim generalizes past record-only checking. What makes a check
untested is that **its outcome never varies** — whether because it inspects the
wrong thing (7.1) or because there is nothing to inspect (here). Two rules
follow, and they are the transferable part of DRI-7:

- **Report the denominator.** A pass rate without one is not a measurement.
- **Audit a check's outcome distribution, not its pass rate.** Rule A is
  single-valued over 642 records. That is visible without knowing the correct
  answer to a single one of them, and it is what should have raised the alarm
  before anyone dereferenced anything.

## 10. Boundaries

- **235 of Corpus A is unverifiable, not clean.** Those records name repositories
  absent from this host. The 0.829 is a rate over what one machine can
  dereference. Another host yields a different denominator, and treating
  unverifiable as failure would convert machine visibility into a false negative.
- **One host, one control plane, six weeks.** Not a population estimate.
- **Identical hashes are not proof of copying.** Constant or empty outputs match
  too, which is why cross-record identical pairs concentrate in a small number of
  distinct contents.
- **Corpora A and B are not fully independent.** Both are written by the same
  runner family into the same disposable workspace. They are independent in
  identifier scheme and code path, not in root cause.

## 11. What would refute this

Exhibit one record in either corpus that Rule A rejects. That is sufficient to
refute 7.1, and it is the claim on which the others rest.
