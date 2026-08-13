import { CONDITIONS, LIFT_BENCHMARK_VERSION, PROMPT_VERSION } from './src/domain/constants.js';
import { assertNoHiddenLabels, publicWorld } from './src/domain/validation.js';
import { hashObject } from './src/lib/hash.js';
import { analyzeEvidence } from './mp.js';
import { buildLiftPrompt } from './lift-prompts.js';
import { RESPONSE_SCHEMA } from './response-schema.js';

export { RESPONSE_SCHEMA } from './response-schema.js';

export function buildPrompt(world, condition) {
  if (world.benchmark_version === LIFT_BENCHMARK_VERSION) {
    return buildLiftPrompt(world, condition);
  }
  const visibleWorld = publicWorld(world, condition);
  const mpOutput = condition === CONDITIONS.MINORITY_PROPHET ? analyzeEvidence({ claims: visibleWorld.claims, sources: visibleWorld.sources, provenance_edges: visibleWorld.provenance_edges, context: visibleWorld.evidence_context ?? {} }) : null;
  const systemPrompt = `Evaluate the conflicting reports and select the best-supported answer using only the supplied information. Return concise JSON matching the supplied schema; do not provide private chain-of-thought. Prompt version: ${PROMPT_VERSION}.`;
  const conditionText = condition === CONDITIONS.BASELINE ? 'Evaluate the supplied reports. Abstain when the supplied evidence cannot justify either answer.' : condition === CONDITIONS.PROVENANCE ? 'Declared derivation relationships and evidence metadata are supplied. Use them critically, and abstain when the evidence cannot justify either answer.' : 'Declared derivation relationships, evidence metadata, and a provider-independent evidence-structure analysis are supplied. The analysis does not contain a ground-truth label and may be incomplete or misleading when declared metadata is incomplete; use it critically and abstain when warranted.';
  const payload = { instruction: conditionText, world: visibleWorld, ...(mpOutput ? { minority_prophet_analysis: mpOutput } : {}), response_schema: RESPONSE_SCHEMA };
  assertNoHiddenLabels(payload);
  return { condition, systemPrompt, messages: [{ role: 'user', content: JSON.stringify(payload) }], tools: [], payload, system_prompt_hash: hashObject(systemPrompt), user_prompt_hash: hashObject(payload), provenance_graph_hash: hashObject(world.provenance_edges), minority_prophet_output_hash: mpOutput ? hashObject(mpOutput) : null };
}
