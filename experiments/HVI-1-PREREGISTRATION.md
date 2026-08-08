# HVI-1 — Verifier independence under shared control

**Status: preregistered before implementation or confirmatory execution**

## Question

Can explicit creator, verifier, and controller provenance stop one controlling
party from manufacturing apparent independent evidence by multiplying names,
keys, services, or organizational labels?

## Boundary

This experiment tests declared or externally supported control relationships
inside a frozen synthetic model. It does not discover hidden common control.
A valid signature proves use of a key, not organizational independence. An
independence assessment supplies evidence; it never grants authority.

## Unit of independence

One supported evidence-producer control domain is one possible evidence root.
Accounts, keys, signatures, services, verifiers, and corporate labels are not
independence units. A receipt is eligible only when:

1. its evidence producer has supported controller provenance;
2. its verifier has supported controller provenance;
3. producer and verifier do not share a control domain; and
4. the verifier did not create or promote the evidence being verified.

Unknown or conflicting controller provenance produces `ESCALATE`. It is never
silently converted into an independent root.

## Frozen receipt contract

The candidate contract is `hvi1/independence-receipt.schema.json`. The
confirmatory implementation must reject unknown fields, malformed identifiers,
unsupported controller assertions, creator/verifier self-control, and a
verifier claiming to be the evidence producer. The contract does not attest
truth or authorization.

## Frozen synthetic worlds

The implementation commit must materialize this generator without changing
the configuration below:

- PRNG seeds `401–420` inclusive;
- `250` base worlds per seed;
- one binary proposition per world;
- six supported honest producer control domains, independently correct with
  probability `0.85`;
- one adversarial producer control domain, correct with probability `0.25`;
- independently controlled verifiers for eligible receipts; and
- deterministic stable identifiers derived from seed, world, and role.

Each base world produces these matched variants while preserving claim values:

1. `single`: one identity/key/service per producer;
2. `alias_2`: the adversarial controller appears under two identities;
3. `alias_8`: it appears under eight identities;
4. `alias_32`: it appears under thirty-two identities;
5. `key_rotation_8`: one adversarial identity rotates through eight keys;
6. `service_split_8`: one adversarial controller uses eight service and label combinations;
7. `self_verified_8`: eight receipts are created and verified under one controller;
8. `unknown_control_8`: eight receipts omit supported controller provenance;
9. `partial_shared_8`: eight identities map to exactly two supported producer control domains; and
10. `genuine_8`: eight receipts come from eight genuinely separate supported producer domains.

The matched representation variants may change multiplicity and metadata only.
They may not redraw truth or claims.

## Frozen methods

1. receipt head count;
2. unique-signing-key count;
3. unique-identity count;
4. scalar validator-score mean;
5. scalar validator-score median;
6. scalar validator-score median after fixed 10% symmetric clipping; and
7. control-domain-aware evidence-root aggregation.

Scores are frozen at `0.90` for syntactically valid signed receipts and `0.00`
otherwise. Score methods answer by score-weighted claim mass and do not infer
control. The control-domain method deduplicates eligible receipts by supported
producer control domain and returns `ESCALATE` on unknown or conflicting control.
Binary ties return `ABSTAIN` for every method.

## Metrics

- false-independent-root acceptance: accepted units beyond hidden producer
  control domains;
- supported-independent-root retention;
- decision error against synthetic truth;
- abstention and escalation rates;
- root-mass delta caused only by alias, key, service, or label multiplication;
- self-verification root mass; and
- paired decision-error difference at the control-aware method's answered
  worlds (matched abstention).

World-clustered bootstrap 95% confidence intervals use seed `20260807` and
exactly `10,000` resamples. Base worlds, not receipts or matched variants, are
the resampling unit.

## Frozen hypotheses

- **HVI-1a — representation invariance:** every `alias_*`, `key_rotation_8`,
  and `service_split_8` variant changes control-aware root mass by exactly zero.
- **HVI-1b — self-verification exclusion:** `self_verified_8` adds zero eligible
  independent roots in every world.
- **HVI-1c — uncertainty preservation:** `unknown_control_8` escalates in every
  world and never returns an affirmative independence assessment.
- **HVI-1d — genuine-root retention:** at least 95% of supported producer
  control domains in `genuine_8` remain distinct.
- **HVI-1e — false-root reduction:** on multiplicity variants, the upper bound
  of the paired bootstrap interval for the control-aware false-root rate minus
  the unique-signing-key rate is at most `-0.80`.
- **HVI-1f — matched decision preservation:** on worlds answered by the
  control-aware method, the upper bound of its paired decision-error difference
  from the best non-oracle baseline is at most `0.02`.

The primary HVI-1 claim is supported only if HVI-1a through HVI-1f all hold.
Every adverse, null, incomplete, or contradictory result must be retained.

## Conformance vectors

The frozen hand-written vectors are in `hvi1/conformance-vectors.json`. They
are specification examples, not confirmatory samples, and cannot be added to
the confirmatory metric totals.

## Integrity controls

- Confirmatory worlds cannot be inspected before this protocol is publicly committed.
- Thresholds, seeds, variants, and success rules cannot change after that commit.
- A discovered defect requires a versioned deviation; original output remains preserved.
- The runner records protocol and implementation commits, file hashes,
  environment, configuration, verdicts, and output hashes.
- Two clean detached-worktree runs must produce byte-identical scientific JSON.
- Observational timings are retained separately from byte-identical output.

