# EXP010 — Root identifiability ladder

**Status: preregistered; confirmatory execution is authorized only from a
committed frozen runner**

EXP010 tests where evidence-root identification becomes possible and where it
remains impossible. It does **not** assume that Minority Prophet, signatures,
agent identities, semantic similarity, or attestation can discover genuine
causal independence from claims alone.

The formal aggregator remains conditional: it counts the roots supplied to it.
EXP010 studies the separate observation boundary that supplies those roots.

## Question

For a frozen class of causal claim histories, what information must an
observation interface expose before a method can distinguish independent
acquisition from copying, replay, or a hidden common source?

The target is an operational root relation under a stated threat model, not
universal epistemic independence. A successful source receipt establishes only
that a designated provider recorded a particular acquisition event under the
provider assumptions. It does not prove truth, competence, absence of collusion,
or independence from every unobserved cause.

## Identifiability boundary

For every paired case, the generator creates two hidden causal worlds with:

- different true root sets or root partitions; and
- identical observations at one or more lower interface levels.

Any deterministic classifier receiving an identical projection must return the
same answer in both worlds. If the correct root relation differs, it must be
wrong in at least one. This paired construction is the primary impossibility
witness; it is stronger than observing that a particular heuristic performs
poorly.

Randomized classifiers do not escape the boundary. They may distribute their
error differently, but identical observation distributions cannot identify
which hidden causal world produced a case without an additional assumption or
channel.

## Frozen vocabulary

- **True root:** a generator-known acquisition event with no causal parent in
  the modeled evidence flow.
- **Recorded root:** a claim with no parent recorded by the evaluated interface.
- **Operational root:** a root accepted under the explicit policy of an
  interface level.
- **Same-root relation:** two records descend from the same generator-known
  acquisition event.
- **Root integrity:** agreement between an operational root set and the hidden
  causal root set within the frozen threat model.
- **Source receipt:** a provider-signed statement binding a source-event ID,
  acquisition challenge, payload digest, issuer, and time window.

“Independent” is never inferred merely from different names, keys, signatures,
services, network locations, wording, or model instances.

## Interface ladder

Each higher level contains the lower level's fields plus the listed channel.

### L0 — Claim projection

Assertion and payload only. Direct copies, independent convergence, and hidden
common-source descendants can be observationally identical.

### L1 — Authenticated actor projection

L0 plus stable actor identifier and actor signature. This authenticates the
actor key; it does not prove distinct control or distinct evidence.

### L2 — Declared lineage projection

L1 plus self-declared parent IDs and citations. Honest declarations expose
recorded copying. Omission and false declaration remain possible.

### L3 — Policy-constrained registry projection

L2 plus authenticated issuance, per-identity quotas, freshness, replay
protection, and append-only tombstones. This constrains root manufacture per
identity and prevents specific registry failures. It still cannot detect an
undisclosed common upstream source or coordinated distinct identities.

### L4 — Source-bound acquisition receipt

L3 plus a provider receipt binding:

- `source_event_id`;
- a verifier challenge or nonce;
- raw evidence digest;
- acquisition time window;
- source/provider identifier; and
- capture/issuer identifier.

Within an honest-provider regime, records carrying the same source-event ID are
not counted as independent acquisitions. Distinct capture receipts count as
distinct only where the protocol assigns distinct capture opportunities.

L4 imports provider honesty and correct event canonicalization. A compromised
provider can manufacture apparently independent receipts. EXP010 must exhibit
that failure rather than describe L4 as universal proof of independence.

### L5 — Generator oracle

The hidden causal parent and root IDs. This is an upper-bound diagnostic, not a
deployable method.

## Paired causal cases

Every confirmatory seed contains all of the following case families:

1. independent observations that converge on the same assertion and payload;
2. direct copying with an honest parent declaration;
3. direct copying with an omitted or false parent declaration;
4. paraphrase, summary, translation, or format conversion from one root;
5. multiple actors consuming one hidden upstream feed;
6. replay of one acquisition under a fresh claim or actor identity;
7. Sybil identities under one control boundary;
8. valid distinct acquisitions by one actor;
9. honest source receipts with copied descendants; and
10. compromised-source receipts that manufacture distinct apparent events.

At least one pair in each applicable family must remain byte-identical after
projection at L0, L1, L2, or L3 while its true root relation differs. The runner
must verify this property before scoring any estimator.

## Frozen generator and schedule

The protocol uses:

- development seeds `1–20`, which may be inspected while implementing;
- confirmatory seeds `401–420`, which must remain untouched until the protocol
  and implementation are committed;
- exactly `200` paired templates per seed, scheduled as twenty repetitions of
  each case family in the listed order;
- two hidden worlds per template;
- eight binary propositions per world;
- exactly twenty-four claim records per world;
- six true acquisition roots in the independent member and five in the copied
  member of each pair; and
- `4,000` world pairs (`8,000` worlds) in total.

The final implementation must derive every random choice from an explicit local
PRNG instance. No network service, language model, embedding service, wall-clock
time, or mutable external dataset may participate in the canonical run.

## Methods

1. **All-claims-as-roots:** every record is independent.
2. **Actor-key roots:** one root per authenticated actor key.
3. **Declared lineage:** follow self-declared parent links.
4. **Registry policy:** declared lineage plus L3 issuance and replay controls.
5. **Source-receipt lineage:** group records by valid L4 acquisition receipt and
   then follow recorded descendants.
6. **Generator oracle:** use hidden causal parents and roots.

Each method is scored at its native minimum interface: all-claims at L0,
actor-key at L1, declared lineage at L2, registry policy at L3, source receipt
at L4, and oracle at L5. An interface-dependent method presented with a lower
level must abstain rather than import hidden fields.

No semantic or behavioral heuristic may be described as proving independence.
If a heuristic is later added, it is an inference comparator and must report
abstention and false-merger rates separately.

## Metrics

For every method, interface level, and case family report:

- true-root precision, recall, and F1;
- same-root pairwise precision, recall, and F1;
- root inflation and root deflation;
- root-set symmetric-difference error where claim IDs make the sets directly
  comparable;
- oracle-root-verdict agreement;
- false reversal of an oracle-root verdict;
- abstention or unverifiable rate; and
- minority-truth recovery only as a secondary, generator-scoped measure.

For verdict analysis, report the hidden oracle margin `m` and estimated root-set
error `k`. The empirical record must separately tabulate `k < m`, `k = m`, and
`k > m`; it must not relabel `k` as a count of attacker actions.

## Primary hypotheses

### H10-1 — Lower-interface non-identifiability

For each declared indistinguishable pair at L0–L3, the runner verifies that the
projected inputs are byte-identical and the correct root relation differs. The
result is supported only if every required pair passes both checks. This is a
construction check, not a claim that every possible L0–L3 world is ambiguous.

### H10-2 — Honest-receipt operational sufficiency

In the honest-provider regime, source-receipt lineage must have zero false-root
acceptances for direct copy, paraphrase, replay, Sybil, and shared-feed cases,
with the exact one-sided 95% binomial upper bound below `0.005`. When the
observed error count is zero, the runner uses `1 - 0.05^(1/n)` rather than a
degenerate all-zero bootstrap interval. The frozen error opportunity is the
target copied relation in the copied member of case families 2 through 7 and
9: `2,800` opportunities in total.

### H10-3 — Independent-acquisition preservation

In the honest-provider regime, source-receipt lineage must preserve at least
`0.99` of generator-distinct acquisition roots, with the 95% lower confidence
bound at least `0.985`. The frozen opportunity is the target independent
relation in the independent member of the first nine case families: `3,600`
opportunities. For an all-success record, the one-sided exact lower bound is
`0.05^(1/n)`; otherwise the runner reports the exact binomial lower bound.

### H10-4 — Compromised-provider boundary

When the source provider is allowed to issue valid-looking receipts for invented
source events, at least one paired causal family must remain indistinguishable at
L4. This is an expected limitation result. Failure to demonstrate it would mean
the attack construction is incomplete, not that compromised providers are safe.

### H10-5 — Margin translation

For the shipped aggregator implementation, no estimated verdict may differ from
the oracle-root verdict in an applicable case where assertions are unchanged,
both worlds are side-consistent, and the directly measured total root-set
symmetric-difference error satisfies `k < m`. Cases violating a theorem
precondition are reported separately and cannot support H10-5. This is an
implementation bridge to the compiled margin theorem, not new mathematical
evidence. The check covers each method at its native interface, every
proposition, and both worlds; a method with no `k < m` applicable cases is
reported as uninformative and cannot independently support the hypothesis.

## Confidence intervals

Non-boundary empirical proportions use world-pair-clustered bootstrap 95%
percentile intervals. The pair, not an individual claim or proposition, is the
resampling unit. Zero-error upper and all-success lower bounds use the exact
binomial rules specified in H10-2 and H10-3. The bootstrap seed is `20261029`
and the resample count is exactly `10,000`.

Exact construction and conformance checks report counts and violations rather
than confidence intervals.

## Failure interpretation

- H10-1 failure means the paired generator did not establish the claimed
  observational equivalence.
- H10-2 or H10-3 failure means the L4 operational contract or its implementation
  does not preserve roots under its own stated honest-provider regime.
- H10-4 failure means the experiment did not successfully model provider
  compromise.
- H10-5 failure indicates an implementation/specification mismatch requiring a
  counterexample before any result is promoted.

No outcome establishes universal root integrity. Even complete support would
show only that a source-receipt policy works in the frozen provider-neutral
harness under the stated honest-provider assumptions, while explicitly failing
under a compromised provider.

## Promotion controls

- Commit and timestamp the final protocol before confirmatory execution.
- Never use seeds `401–420` for debugging, threshold selection, or fixture
  repair.
- Preserve all outcomes, including null and adverse results.
- Record protocol commit, implementation commit, source hashes, configuration,
  environment, and output hashes.
- Require two clean detached-worktree executions with byte-identical scientific
  JSON.
- Keep runtime diagnostics outside the deterministic scientific record.
- Scientific JSON uses schema `minority-prophet.exp010-result.v1`; runtime
  diagnostics use `minority-prophet.exp010-diagnostics.v1`.
- Update `CANONICAL-RECORDS.md`, `PUBLIC-CLAIMS.md`, and the paper only after the
  verification record exists.

## Interpretation boundary

EXP010 is designed to falsify overclaims about root detection. Its strongest
possible positive conclusion is conditional:

> Under a specified source-receipt policy and honest-provider threat model, the
> implementation preserved operational acquisition roots across the frozen
> cases.

It can never justify:

> Minority Prophet discovered genuine independence from claims, identities,
> signatures, or language alone.
