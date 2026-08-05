# EXP007A — optimizing adversary completion

Status: preregistered before execution

EXP007R faithfully established that the archived EXP007 optimizer was
unfinished. EXP007A is a new record that completes the intended adversarial
test without editing or replacing EXP007R.

## Question

Can a deterministic, budget-limited adversary find a heterogeneous mixture of
paraphrase, citation-forgery, sybil, and timing intensities that reduces
inferred evidence-root accuracy more than uniform attacks, and do its errors
concentrate in worlds with smaller honest evidence-root margins?

## Frozen model and attack space

The implementation is a repository-native parameterization of the archived
EXP003 synthetic world: one originator, six independent observers, forty
copiers, binary claims, token/citation/time lineage inference, and evidence-root
aggregation. It does not model real deployments.

The adversary chooses four continuous values in `[0, 1]`:

1. paraphrase probability per copied token;
2. probability of forging a citation to an independent observer;
3. probability that a copier presents as a citation-free sybil;
4. timing intensity, linearly moving the originator from time `10.0` to `0.5`.

A sybil receives an additional 0.8 paraphrase pressure on the probability mass
not already paraphrased. Copied claims retain their parent's assertion; the
attack targets lineage inference, not the hidden truth label.

## Frozen optimizer

- objective: minimize decided inferred-root accuracy;
- training set: 80 worlds generated with seed 101 for every candidate;
- exact budget: 45 unique candidate evaluations;
- search: three deterministic random restarts, each followed by fourteen
  coordinate proposals; step size 0.5 for proposals 1–8 and 0.25 for 9–14;
- proposal direction and starting points: PRNG seed 7007;
- if clipping creates a previously evaluated point, the active coordinate is
  deterministically advanced by `0.137 × (restart + 1)` modulo 1.0;
- a proposal replaces the incumbent only if accuracy is lower, with
  lexicographic parameter order breaking exact ties;
- the globally best observed candidate is selected using the same ordering.

No search parameter may be changed after execution begins.

## Comparators and holdout

The selected attack, no attack, uniform 0.5, and uniform 1.0 are evaluated on
ten untouched seeds 201–210, each with 150 worlds. These holdout worlds do not
participate in optimization.

## Frozen hypotheses

- H7A-1 (optimizer value): on holdout, the selected attack's mean accuracy is
  lower than both uniform 0.5 and uniform 1.0.
- H7A-2 (margin targeting): among decided holdout worlds under the selected
  attack, the mean honest margin is lower for incorrect than correct verdicts,
  with Welch's t statistic greater than 1.96.

The overall hypothesis is `supported` only if both conditions hold. Otherwise
it is `rejected`; missing correct/incorrect groups produce `inconclusive`.

## Required record

The canonical JSON output must include all 45 training evaluations, chosen
parameters, all per-seed holdout summaries, pooled margin statistics, both
hypothesis verdicts, the overall verdict, configuration, environment, source
SHA-256, protocol commit, and output SHA-256. A second clean invocation must
produce byte-identical scientific output. Adverse results must be retained.

Reproducing a synthetic attack does not demonstrate an exploit against any
external system and does not validate the paper's previously reported optimum.
