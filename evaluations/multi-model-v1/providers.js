import { CONDITIONS } from './src/domain/constants.js';

function payloadFrom(request) { return JSON.parse(request.messages.at(-1).content); }
function choose(claims, rootsOnly) {
  const candidates = rootsOnly ? claims.filter((claim) => (claim.parent_claim_ids ?? []).length === 0) : claims;
  const counts = new Map();
  for (const claim of candidates) counts.set(claim.asserted_answer, (counts.get(claim.asserted_answer) ?? 0) + 1);
  return [...counts.entries()].sort((a, b) => b[1] - a[1])[0][0];
}

export class DeterministicAdapter {
  constructor(model) { this.provider = 'deterministic'; this.model = model; this.version = model; }
  async runModel(request) {
    const payload = payloadFrom(request);
    const world = payload.world;
    const rootsOnly = request.condition === CONDITIONS.MINORITY_PROPHET || (this.model === 'lineage-reasoner-v1' && request.condition === CONDITIONS.PROVENANCE);
    const answer = choose(world.claims, rootsOnly);
    const evidence = world.claims.filter((claim) => claim.asserted_answer === answer && (!rootsOnly || (claim.parent_claim_ids ?? []).length === 0)).map((claim) => claim.claim_id).slice(0, 6);
    const assessment = rootsOnly ? 'Independent roots outweigh copied descendants.' : 'The most frequently asserted answer has the largest apparent support.';
    const raw = { answer, confidence: rootsOnly ? 0.84 : 0.78, abstain: false, reasoning_summary: assessment, evidence_used: evidence, independence_assessment: assessment };
    return { raw, provider_request_id: `det_${this.model}_${request.seed}`, usage: { input_tokens: Math.ceil(JSON.stringify(payload).length / 4), output_tokens: Math.ceil(JSON.stringify(raw).length / 4), cached_tokens: 0 }, cost_usd: 0, execution_ms: 0, model_version: this.version };
  }
}
