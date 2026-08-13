import { publicLiftWorld } from './lift-prompts.js';
import { MP_TOOL_CONTRACT_HASH, MP_TOOL_DEFINITION } from './mp-tool-v2.js';
import { RESPONSE_SCHEMA } from './response-schema.js';
import { CONDITIONS } from './src/domain/constants.js';
import { assertNoHiddenLabels } from './src/domain/validation.js';
import { hashObject } from './src/lib/hash.js';

export const LIVE_TOOL_CONDITIONS = Object.freeze({
  BASELINE: CONDITIONS.BASELINE,
  PROVENANCE: CONDITIONS.PROVENANCE,
  PRECOMPUTED: CONDITIONS.MINORITY_PROPHET,
  OPTIONAL: 'D_LIVE_MP_OPTIONAL',
  REQUIRED: 'E_LIVE_MP_REQUIRED'
});

export function buildLiveToolPrompt(world, condition) {
  if (![LIVE_TOOL_CONDITIONS.OPTIONAL, LIVE_TOOL_CONDITIONS.REQUIRED].includes(condition)) {
    throw new Error(`Not a live-tool condition: ${condition}`);
  }
  const visibleWorld = publicLiftWorld(world, CONDITIONS.PROVENANCE);
  const required = condition === LIVE_TOOL_CONDITIONS.REQUIRED;
  const toolInput = {
    claims: visibleWorld.claims,
    sources: visibleWorld.sources,
    provenance_edges: visibleWorld.provenance_edges,
    context: visibleWorld.evidence_context ?? {}
  };
  const systemPrompt = 'Evaluate the conflicting reports using only the supplied information and the explicitly provisioned read-only Minority Prophet tool. Do not use files, shell, network, web search, or any other tool. Return concise JSON matching the supplied schema; do not provide private chain-of-thought. Prompt version: live-mcp-prompts-v1.';
  const payload = {
    instruction: required
      ? 'Call analyze_evidence_structure exactly once with the supplied tool_input. After receiving its result, select the best-supported answer. Abstain when the evidence cannot justify either answer.'
      : 'You may call analyze_evidence_structure with the supplied tool_input when it would help. Select the best-supported answer and abstain when the evidence cannot justify either answer.',
    world: visibleWorld,
    tool_input: toolInput,
    provisioned_tool: {
      name: MP_TOOL_DEFINITION.name,
      contract_hash: MP_TOOL_CONTRACT_HASH,
      read_only: true
    },
    response_schema: RESPONSE_SCHEMA
  };
  assertNoHiddenLabels(payload);
  return {
    condition,
    systemPrompt,
    messages: [{ role: 'user', content: JSON.stringify(payload) }],
    payload,
    expected_tool_input_hash: hashObject(toolInput),
    system_prompt_hash: hashObject(systemPrompt),
    user_prompt_hash: hashObject(payload),
    epistemic_base_hash: hashObject({ instruction: payload.instruction, world: visibleWorld, response_schema: RESPONSE_SCHEMA }),
    provenance_graph_hash: hashObject(world.provenance_edges),
    mp_tool_contract_hash: MP_TOOL_CONTRACT_HASH
  };
}
