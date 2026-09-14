import { buildLiftPrompt, publicLiftWorld } from './lift-prompts.js';
import { RESPONSE_SCHEMA } from './response-schema.js';
import { CONDITIONS, LIFT_PROMPT_VERSION } from './src/domain/constants.js';
import { assertNoHiddenLabels } from './src/domain/validation.js';
import { hashObject } from './src/lib/hash.js';

export const REAL_CONDITIONS = Object.freeze({
  RAW: CONDITIONS.BASELINE,
  PROVENANCE: CONDITIONS.PROVENANCE,
  NEUTRAL_INDEX: 'C_NEUTRAL_ROOT_INDEX',
  MINORITY_PROPHET: 'D_MINORITY_PROPHET'
});

function neutralRootIndex(visibleWorld) {
  const childIds = new Set(visibleWorld.provenance_edges.map((edge) => edge.child_claim_id));
  const sources = new Map(visibleWorld.sources.map((source) => [source.source_id, source]));
  return {
    method: 'mechanical extraction of claims with no incoming provenance edge',
    roots: visibleWorld.claims
      .filter((claim) => !childIds.has(claim.claim_id))
      .map((claim) => {
        const source = sources.get(claim.source_id) ?? {};
        return {
          claim_id: claim.claim_id,
          asserted_answer: claim.asserted_answer,
          source_id: claim.source_id,
          derivation_type: claim.derivation_type,
          timestamp: claim.timestamp,
          direct_observation: claim.direct_observation,
          control_domain_id: source.control_domain_id ?? null,
          observation_id: source.observation_id ?? null
        };
      })
      .sort((left, right) => left.claim_id.localeCompare(right.claim_id))
  };
}

export function buildRealTestPrompt(world, condition) {
  if (condition === REAL_CONDITIONS.RAW) return buildLiftPrompt(world, CONDITIONS.BASELINE);
  if (condition === REAL_CONDITIONS.PROVENANCE) return buildLiftPrompt(world, CONDITIONS.PROVENANCE);
  if (condition === REAL_CONDITIONS.MINORITY_PROPHET) {
    return { ...buildLiftPrompt(world, CONDITIONS.MINORITY_PROPHET), condition };
  }
  if (condition !== REAL_CONDITIONS.NEUTRAL_INDEX) throw new Error(`Unsupported real-test condition ${condition}`);

  const visibleWorld = publicLiftWorld(world, CONDITIONS.PROVENANCE);
  const systemPrompt = `Evaluate the conflicting reports using only the supplied information. Return concise JSON matching the supplied schema; do not provide private chain-of-thought. Prompt version: ${LIFT_PROMPT_VERSION}.`;
  const instruction = 'Select the best-supported answer. Abstain when the supplied evidence cannot justify either answer.';
  const basePayload = { instruction, world: visibleWorld, response_schema: RESPONSE_SCHEMA };
  const payload = { ...basePayload, neutral_root_index: neutralRootIndex(visibleWorld) };
  assertNoHiddenLabels(payload);
  return {
    condition,
    systemPrompt,
    messages: [{ role: 'user', content: JSON.stringify(payload) }],
    tools: [],
    payload,
    system_prompt_hash: hashObject(systemPrompt),
    user_prompt_hash: hashObject(payload),
    epistemic_base_hash: hashObject(basePayload),
    provenance_graph_hash: hashObject(world.provenance_edges),
    minority_prophet_output_hash: null,
    mp_tool_contract_hash: null
  };
}
