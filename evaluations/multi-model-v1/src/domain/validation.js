import { CONDITIONS } from './constants.js';
export function assert(condition, message) { if (!condition) throw new Error(message); }
export function validateWorld(world) {
  const required = ['benchmark_version','world_id','seed','question','ground_truth','claims','sources','provenance_edges','independent_roots','scenario_family','difficulty','consensus_ratio','metadata'];
  for (const field of required) assert(field in world, `World missing ${field}`);
  assert(Array.isArray(world.claims) && world.claims.length > 0, 'World requires claims');
  const claimIds = new Set(world.claims.map((claim) => claim.claim_id));
  assert(claimIds.size === world.claims.length, 'Claim IDs must be unique');
  for (const claim of world.claims) { for (const field of ['claim_id','text','asserted_answer','source_id','parent_claim_ids','derivation_type','timestamp','direct_observation','hidden']) assert(field in claim, `Claim ${claim.claim_id} missing ${field}`); for (const parent of claim.parent_claim_ids) assert(claimIds.has(parent), `Unknown parent ${parent}`); }
  return world;
}
export function publicWorld(world, condition) {
  const includeProvenance = condition !== CONDITIONS.BASELINE;
  const claims = world.claims.map(({ hidden, parent_claim_ids, derivation_type, direct_observation, timestamp, confidence, ...claim }) => includeProvenance
    ? { ...claim, parent_claim_ids, derivation_type, direct_observation, timestamp, confidence }
    : { claim_id: claim.claim_id, text: claim.text, asserted_answer: claim.asserted_answer, source_id: claim.source_id });
  const sources = world.sources.map(({ hidden, prestige, ...source }) => includeProvenance
    ? source
    : { source_id: source.source_id, label: source.label });
  const output = { benchmark_version: world.benchmark_version, world_id: world.world_id, question: world.question, claims, sources };
  if (includeProvenance) {
    output.provenance_edges = world.provenance_edges;
    if (world.evidence_context) output.evidence_context = world.evidence_context;
  }
  return output;
}
export function assertNoHiddenLabels(payload) { const serialized = JSON.stringify(payload); for (const forbidden of ['ground_truth','truth_relationship','is_correct','correct_answer']) assert(!serialized.includes(`\"${forbidden}\"`), `Hidden label leaked: ${forbidden}`); }
export function validateParsedResponse(value) { assert(value && typeof value === 'object', 'Response must be an object'); assert(typeof value.answer === 'string', 'Response answer must be a string'); assert(Number.isFinite(value.confidence) && value.confidence >= 0 && value.confidence <= 1, 'Confidence must be in [0,1]'); assert(typeof value.abstain === 'boolean', 'abstain must be boolean'); assert(typeof value.reasoning_summary === 'string', 'reasoning_summary must be a string'); assert(Array.isArray(value.evidence_used), 'evidence_used must be an array'); assert(typeof value.independence_assessment === 'string', 'independence_assessment must be a string'); return value; }
