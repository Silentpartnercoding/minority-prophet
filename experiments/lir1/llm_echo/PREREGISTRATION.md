# LIR-1E preregistration — controlled multi-agent echo corpus

**Status:** protocol frozen before case generation, provider requests, response
inspection, inference, or scoring.

## Purpose

LIR-1E supplies the `constructed_exact` corpus required by the LIR-1 primary
hypothesis. It asks whether observable answer text, time, exposed links, and
mutation inheritance can recover known record ancestry when a group of model
answers contains independent observations, a shared evidence source, direct
copies, and mutated copies.

This is a lineage experiment, not a claim that language models possess
independent judgment. A source packet is a controlled record root. It is not a
proxy for everything in a model's pretraining or for causal independence in
the physical world.

## Frozen design

### Cases and split

- Generate exactly 48 fictional micro-world cases: 12 development and 36
  confirmatory.
- The development and confirmatory cases use separate randomly generated
  seeds. Their SHA-256 commitments are registered before any case is opened.
- A case contains a fictional entity, one factual question, three separately
  worded source packets supporting the constructed true value, and one source
  packet supporting a constructed false value.
- Tokens used for entities, values, and source wording are synthetic. The task
  must be answerable from the supplied packet without outside knowledge.
- No case may cross splits. No confirmatory case may be inspected before the
  execution configuration, parser, and thresholds are frozen.

### Response roles per case

Each case produces these records:

1. three model responses, each exposed to a different true source packet;
2. two model responses exposed to the same false source packet;
3. one exact programmatic copy of a selected false-source response; and
4. six deterministic programmatic mutations descended from that copy.

The result is three true evidence roots and one false evidence root. The false
root has nine records once the two responses that share its packet, the exact
copy, and six mutations are counted. Raw record majority should therefore
favor the false value when every required record is valid; collapsing by the
four declared evidence roots should favor the true value 3–1.

The two model responses that see the false packet share an evidence root but
neither is declared the direct parent of the other. The exact copy and its
mutations have direct parents because those transformations are performed and
logged by the harness.

### Model assignment cells

The registered execution amendment must bind exact provider and model IDs to:

- `same_model_disjoint`: at least two true packets answered by the same model;
- `different_family_disjoint`: at least one true packet answered by a different
  model family from another true-packet answer; and
- `same_model_same_source`: both false-packet responses answered independently
  by the same model with identical source bytes and prompt bytes.

“Disjoint” refers only to the supplied source packets. It does not establish
independent pretraining, provider infrastructure, or physical observation.
“Same source” establishes a declared shared retrieval dependency, not direct
answer copying.

### Prompt and response contract

Every model call receives only its assigned source packet and a fixed prompt:

> Using only the source packet, answer the question. Return one JSON object
> with exactly `answer`, `confidence`, and `explanation`. Copy the answer token
> exactly. `confidence` is a number from 0 through 1. Do not use outside
> knowledge.

Required generation settings are temperature `0`, no tools, no web access, no
memory, and no inter-agent messages. If a provider does not support a seed, the
receipt records `seed: null`. The exact system prompt, user prompt, source
bytes, parameters, request time, response bytes, provider, exact model ID, and
provider request ID when available are logged.

Malformed responses receive one mechanically identical retry. Both attempts
remain in the private audit log. A second malformed response marks that role
missing; it is not hand-corrected. A case with any missing required role is
excluded and counted. Fewer than 30 complete confirmatory cases fails the LIR-1
primary hypothesis.

### Copy and mutation controls

Copy and mutation records are created locally after the two false-source model
responses exist. They do not consume model calls.

- The exact copy duplicates the selected origin response's answer and
  explanation bytes.
- Each mutated copy preserves the asserted answer but applies one frozen,
  deterministic surface transformation: clause reorder, synonym map, wrapper
  addition, explanation truncation, punctuation normalization, or combined
  synonym-and-wrapper transformation.
- The transformation ID, input SHA-256, output SHA-256, direct parent, and root
  are stored in the sealed construction labels.

No mutation may introduce a new fact or change the asserted answer.

## Isolation and evidence boundary

The run uses three non-overlapping views:

1. **public request view** — case and role IDs, prompts, synthetic source bytes,
   request parameters, model assignments, timestamps, and cryptographic hashes;
2. **inference feature view** — response text, time, public actor/model metadata,
   and only those links selected for the perturbation level; and
3. **sealed evaluation view** — constructed truth, evidence root, direct parent,
   transformation log, split seed, and all label-only fields.

The inference process must not read the sealed evaluation view, generator seed,
construction plan, filenames encoding labels, or provider conversations outside
the recorded response. An automated boundary test must fail if any label-only
key enters the feature view.

Before execution, the repository records hashes for the protocol, generator,
schemas, prompt template, execution configuration, and sealed case inventory.
Raw provider responses, credentials, provider receipts, and unrevealed labels
remain under `artifacts/lir1/llm_echo/`, which is excluded from Git. A public
result may contain sanitized responses and labels only after scoring is closed.

## Execution amendment required before model calls

The amendment must freeze:

- exact provider and model identifiers for every assignment cell;
- account or runner identity without publishing credentials;
- per-call settings and whether deterministic seeds are supported;
- maximum calls, input tokens, output tokens, and dollar spend;
- retry and outage rules;
- execution window and clock source;
- response redistribution policy;
- development threshold selection procedure; and
- hashes of both sealed inventories.

Changing any frozen item requires a dated deviation before affected responses
are inspected. Provider unavailability does not permit silent substitution.

## Primary analysis

The primary analysis is the existing LIR-1 registered analysis on the 36
confirmatory cases at 40% deterministic hidden edges:

- hidden-parent precision, recall, and F1;
- root-pair precision, recall, and F1;
- root-count mean absolute error;
- raw-majority, declared-collapse, and inferred-collapse truth accuracy;
- declared advantage survival with its registered undefined-denominator rule;
- coverage and abstention; and
- 10,000 case-cluster bootstrap resamples with seed `20260808`.

Thresholds are selected only on the 12 development cases. Confirmatory labels
remain sealed until the threshold and output hashes are committed.

## Diagnostic analyses

Report separately, without rescuing the primary result:

- exact-copy versus each mutation transformation;
- same-model/same-source versus same-model/disjoint-source versus
  different-family/disjoint-source pairs;
- performance at every registered hiding fraction;
- no-text and no-time ablations;
- malformed, refused, missing, and retried response counts; and
- token use, provider-reported cost where available, elapsed model time, and
  local computation time.

No model-family comparison is interpreted causally unless assignment was
randomized and all other call conditions were identical.

## Success and failure

The success and failure conditions are exactly those in the parent LIR-1
preregistration. At 40% hiding, the lower case-bootstrap 95% bound for declared
advantage survival must exceed 0.25 and root-pair F1 must be at least 0.60.

Failure, exclusion, provider refusal, cost overrun prevention, and adverse
results are publishable results. They are never replaced by a cleaner rerun.

## What this experiment cannot establish

Even a successful result would not prove that:

- textual difference means causal independence;
- model families are independent witnesses;
- a shared source caused two model outputs to resemble one another;
- the constructed source packets resemble every real information ecosystem;
- inferred lineage is authentication, content truth, or a blockchain; or
- Minority Prophet can discover an absent source outside its searched universe.

It would show only how much known record-root structure this frozen inference
method recovers in this controlled, auditable setting.
