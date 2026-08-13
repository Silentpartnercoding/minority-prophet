# Minority Prophet Epistemic Lift Candidate Study

Status: frozen candidate-development protocol before model execution. This is not an official or public leaderboard benchmark.

Frozen manifest hash: `sha256:27f03b6fa35938eb5c81fc3f255aac17aa523b7802e68f52d8fba6b8d2518b7f`

## Hypotheses

- H1: exposing provenance improves truth recovery under correlated false consensus.
- H2: Minority Prophet's deterministic evidence-structure analysis improves truth recovery beyond provenance alone.
- Null and adverse results are valid outcomes and will be retained.

## Controlled conditions

Every model receives the same frozen world once in each condition. The system prompt, question, answer schema, sampling settings, model configuration, and B/C provenance payload are held fixed.

- A — Baseline: claims and ordinary source labels; no ancestry or hint about correlation.
- B — Provenance: A plus complete declared ancestry, timestamps, control-domain and observation-origin metadata, and evidence context. No scoring or recommendation.
- C — Minority Prophet: exact B payload plus a read-only deterministic analysis receipt computed only from B-visible bytes. The receipt identifies structure, correlation, current evidence units, and uncertainty. It does not return the ground truth, a correct answer, or an action.

Condition order is counterbalanced across all six A/B/C permutations for every preregistered model. Provider tools, retrieval, files, and network access are disabled inside model calls.

## Frozen candidate set

- Generator seed: 1,730,000
- Worlds: 32
- Repetitions: four per family
- Families: copied majority, shared-control roots, observation laundering, temporal staleness, prestige attack, paraphrase depth, balanced conflict, and incomplete provenance
- Answerable false-consensus worlds: 24
- Appropriate-abstention worlds: 8
- Replication unit: world

This generated candidate set is public-development material and may be used to test plumbing. It is not a private, contamination-resistant evaluation set.

## Models and execution

- OpenAI Codex CLI: `gpt-5.6-sol`, medium reasoning
- Anthropic Claude CLI: `sonnet`, medium effort
- Temperature: 0
- Top-p: 1
- Maximum response tokens: 500
- One completed response per model/world/condition
- Maximum two attempts for a transport or formatting failure; failed attempts remain immutable

The authenticated subscription CLIs are used only as model transports. Their tools are disabled, and each trial runs in a fresh temporary directory.

## Endpoints and decision rule

The primary endpoint is the paired truth-recovery difference `C - B`, calculated separately for each preregistered model. The exact paired test uses discordant B/C outcomes.

The candidate study supports the operational H2 claim only if **each** preregistered model has:

- `C - B >= 0.15`; and
- exact two-sided paired `p < 0.05`.

Secondary outcomes include A-to-B provenance gain, A-to-C total gain, calibration, abstention quality, family breakdowns, and all individual paired transitions. Components remain visible; no composite score substitutes for the primary endpoint.

With 32 worlds, this study is sensitive only to a large lift. For example, six C-only improvements and no C regressions produce an exact two-sided sign-test p-value below 0.05. A smaller or noisier effect requires a later, larger held-out study.

## Integrity and invalidation

The run is not verified if any of these occur:

- world, system-prompt, or B/C base-payload hashes mismatch;
- hidden evaluator labels enter a prompt or tool input;
- the MP receipt appears outside C or its contract hash changes;
- provider tools or external retrieval are used;
- a preregistered model is substituted or omitted;
- expected cells remain incomplete after the allowed attempts;
- source records, raw responses, or failed attempts are lost;
- the manifest or scorer changes after execution begins.

No result from this candidate study may be represented as an official verified leaderboard result. A scientifically frozen v1 requires a larger hidden evaluation set, independent implementation audit, contamination controls, and a prospectively powered sample.
