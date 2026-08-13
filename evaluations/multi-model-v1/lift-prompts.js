import { CONDITIONS, LIFT_PROMPT_VERSION } from './src/domain/constants.js';
import { assertNoHiddenLabels } from './src/domain/validation.js';
import { hashObject } from './src/lib/hash.js';
import { executeMinorityProphetTool, MP_TOOL_CONTRACT_HASH, MP_TOOL_DEFINITION } from './mp-tool-v2.js';
import { RESPONSE_SCHEMA } from './response-schema.js';

function withoutHidden(value) {
  return Object.fromEntries(Object.entries(value).filter(([key]) => key !== 'hidden'));
}

export function publicLiftWorld(world, condition) {
  const includeProvenance = condition !== CONDITIONS.BASELINE;
  const claims = world.claims.map((claim) => includeProvenance
    ? withoutHidden(claim)
    : { claim_id: claim.claim_id, text: claim.text, asserted_answer: claim.asserted_answer, source_id: claim.source_id });
  const sources = world.sources.map((source) => includeProvenance
    ? withoutHidden(source)
    : { source_id: source.source_id, label: source.label });
  const output = { benchmark_version: world.benchmark_version, world_id: world.world_id, question: world.question, claims, sources };
  if (includeProvenance) {
    output.provenance_edges = world.provenance_edges;
    output.evidence_context = world.evidence_context;
  }
  return output;
}

export function buildLiftPrompt(world, condition) {
  const visibleWorld = publicLiftWorld(world, condition);
  const systemPrompt = `Evaluate the conflicting reports using only the supplied information. Return concise JSON matching the supplied schema; do not provide private chain-of-thought. Prompt version: ${LIFT_PROMPT_VERSION}.`;
  const instruction = 'Select the best-supported answer. Abstain when the supplied evidence cannot justify either answer.';
  const basePayload = { instruction, world: visibleWorld, response_schema: RESPONSE_SCHEMA };
  let toolReceipt = null;
  if (condition === CONDITIONS.MINORITY_PROPHET) {
    const toolInput = { claims: visibleWorld.claims, sources: visibleWorld.sources, provenance_edges: visibleWorld.provenance_edges, context: visibleWorld.evidence_context ?? {} };
    const output = executeMinorityProphetTool(toolInput);
    toolReceipt = {
      tool_name: MP_TOOL_DEFINITION.name,
      tool_version: output.engine_version,
      read_only: true,
      input_hash: hashObject(toolInput),
      contract_hash: MP_TOOL_CONTRACT_HASH,
      output
    };
  }
  const payload = toolReceipt ? { ...basePayload, minority_prophet_tool_receipt: toolReceipt } : basePayload;
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
    minority_prophet_output_hash: toolReceipt ? hashObject(toolReceipt.output) : null,
    mp_tool_contract_hash: toolReceipt ? MP_TOOL_CONTRACT_HASH : null
  };
}
