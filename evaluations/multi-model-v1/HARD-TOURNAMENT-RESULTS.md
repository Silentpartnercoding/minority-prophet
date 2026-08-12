# Hard Gauntlet v1 — results

> **INVALIDATED FOR CAPABILITY COMPARISON (2026-08-10).** This run changed the
> information supplied across A/B/C, used a local JavaScript root-summary
> substitute rather than the canonical Minority Prophet implementation, and
> scored dimensions outside the root-aggregation claim. Preserve it as an audit
> artifact, but do not cite its scores as evidence about AI capability or
> Minority Prophet performance. See `HARD-TOURNAMENT-INVALIDATION.md`.

Status: `DEMO`; audited with disclosed failures. This is a hard diagnostic, not an official leaderboard or a general model ranking.

Protocol commit: `a7d92ded36d82d92e58e63493bec814ab6d498f8`

Manifest hash: `sha256:f8486f9b549499a3cd13a5d50e9f75c2d43b2495d992d2b18151379c05678b78`

## Result

Six locally authenticated subscription-CLI model configurations attempted the same eight-world A/B/C gauntlet. All six passed the compatibility probe with zero tool events. The tournament attempted 144 cells; 142 produced valid structured responses and two Sonnet C cells exhausted the provider CLI's structured-output retries. The strict run status is therefore `FAILED`, and both failures count as incorrect below.

| Model configuration | Resolved model | A raw | B provenance | C provenance + MP | B − A | C − B | C failures |
|---|---|---:|---:|---:|---:|---:|---:|
| Codex Sol | `gpt-5.6-sol` | 2/8 | 7/8 | 6/8 | +5 | -1 | 0 |
| Codex Terra | `gpt-5.6-terra` | 2/8 | 7/8 | 7/8 | +5 | 0 | 0 |
| Codex Luna | `gpt-5.6-luna` | 2/8 | 7/8 | 6/8 | +5 | -1 | 0 |
| Claude Opus | `claude-opus-5` | 3/8 | 8/8 | 8/8 | +5 | 0 | 0 |
| Claude Sonnet | `claude-sonnet-5` | 2/8 | 6/8 | 4/8 | +4 | -2 | 2 |
| Claude Haiku | `claude-haiku-4-5` | 2/8 | 5/8 | 4/8 | +3 | -1 | 0 |
| **All model-world cells** | — | **13/48** | **40/48** | **35/48** | **+27** | **-5** | **2** |

The current hard-suite result is clear: structured provenance and evidence metadata produced a large gain over raw claims. Adding the current Minority Prophet structural summary produced no aggregate gain and reduced correct decisions by five cells, including two interface failures.

That does not show the core idea is useless. It shows that a root-count summary is not sufficient when roots can share control, reuse one observation, be stale, be revoked, or exist inside incomplete lineage. C must remain advisory and explicitly uncertainty-sensitive until it models those distinctions or abstains.

## Answering versus abstaining

| Cell type | A raw | B provenance | C provenance + MP |
|---|---:|---:|---:|
| Answerable worlds | 0/30 | 29/30 | 27/30 |
| Worlds requiring abstention | 13/18 | 11/18 | 8/18 |

The metadata made answerable cases much easier, but it also made models too eager to choose in some underdetermined cases. This supports a selective hybrid rather than a blanket “always add more structure” policy: deterministic validity facts should resolve decisive cases, while incomplete or symmetric evidence must preserve a hard abstention path.

## Scenario-level result across six models

| Scenario | Expected behavior | A raw | B provenance | C provenance + MP |
|---|---|---:|---:|---:|
| Copied majority | recover minority truth | 0/6 | 6/6 | 6/6 |
| Roots under shared control | discount apparent independence | 0/6 | 5/6 | 5/6 |
| One observation laundered through roots | deduplicate observation | 0/6 | 6/6 | 5/6 |
| Stale evidence after state change | prefer current valid evidence | 0/6 | 6/6 | 6/6 |
| Revoked authority | reject invalid authority | 0/6 | 6/6 | 5/6, including 1 failure |
| Balanced ambiguity | abstain | 6/6 | 1/6 | 2/6 |
| Incomplete lineage | abstain | 1/6 | 4/6 | 1/6 |
| Circular evidence with no root | abstain | 6/6 | 6/6 | 5/6, including 1 failure |

## Execution observations

- All calls were ephemeral, closed-world, medium-effort, temperature zero, and tool-free.
- The adapter rejects any reported tool event; no completed call triggered that rejection.
- Average response latency ranged from about 7 to 25 seconds depending on model and condition. C was not consistently faster than B.
- The Claude CLI reported an aggregate estimated underlying cost of `$2.68` across its calls. Because execution used an authenticated subscription CLI, this is not established incremental spend and is not a cross-provider cost comparison. Codex CLI did not report dollar cost.
- Claude CLI structured-output handling may involve an auxiliary model in addition to the requested canonical model. The evaluated unit is therefore the local CLI configuration, not a claim about an isolated model endpoint.

## Disclosed failures

Claude Sonnet C failed on:

- revoked authority (`mp_hard_0005`);
- circular evidence (`mp_hard_0008`).

In both cases the CLI reported `structured_output_retry_exhausted` after five attempts. They were not rerun or silently replaced in this primary result.

## Limits

- One deterministic world per family is enough to find failure modes, not estimate population performance.
- The worlds are synthetic and their metadata vocabulary may favor models that interpret those fields well.
- A/B/C order was fixed, but every call was stateless and ephemeral.
- The test compares local CLI configurations, not every web-app mode, API snapshot, temperature, or reasoning level.
- The experiment was preregistered before model execution, but it followed the earlier three-world pilot and was designed using what that pilot failed to test.

## Next experiment

Do not patch these results. Register a new version that separates deterministic validity checks from uncertain evidence aggregation, models controller and observation identity directly, and applies a conservative abstention rule before presenting any structural recommendation. Then rerun the same eight attacks plus multiple unseen variants per family.
