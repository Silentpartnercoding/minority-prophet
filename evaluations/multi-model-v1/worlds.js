import { BENCHMARK_VERSION } from './src/domain/constants.js';
import { validateWorld } from './src/domain/validation.js';
import { hashObject } from './src/lib/hash.js';
import { SeededRng } from './src/lib/rng.js';

const QUESTIONS = [['Which evacuation route is open?','North','South'],['Which reservoir sensor is functioning?','Alpha','Beta'],['Which archive contains the signed record?','East','West'],['Which bridge passed the latest inspection?','Cedar','Pine'],['Which sample contains the target mineral?','Quartz','Slate']];

export function generateMajorityCopyingWorld({ seed, index = 0, benchmarkVersion = BENCHMARK_VERSION }) {
  const rng = new SeededRng(seed);
  const [question, truth, falsehood] = QUESTIONS[index % QUESTIONS.length];
  const truthfulRoots = rng.int(2, 4);
  const falseCopies = rng.int(12, 22);
  const baseTime = Date.UTC(2026, 0, 1) + index * 86_400_000;
  const sources = [];
  const claims = [];
  const opaqueId = (kind, ordinal) => `${kind}_${hashObject({ seed, kind, ordinal }).slice(-10)}`;
  const addSource = ({ hidden }) => {
    const sourceId = opaqueId('source', sources.length + 1);
    sources.push({
      source_id: sourceId,
      label: `Source ${sourceId.slice(-6)}`,
      prestige: Number((0.3 + rng.next() * 0.6).toFixed(2)),
      hidden
    });
    return sourceId;
  };
  const addClaim = ({ answer, sourceId, parents = [], derivation = 'direct_observation', minute, confidence }) => {
    const claimId = opaqueId('claim', claims.length + 1);
    claims.push({ claim_id: claimId, text: `${sourceId} reports the answer is ${answer}.`, asserted_answer: answer, source_id: sourceId, parent_claim_ids: parents, derivation_type: derivation, timestamp: new Date(baseTime + minute * 60_000).toISOString(), confidence, direct_observation: parents.length === 0, hidden: { truth_relationship: answer === truth ? 'supports_truth' : 'supports_falsehood' } });
    return claimId;
  };
  const falseRootSource = addSource({ hidden: { reliability: 0.42, benchmark_role: 'false_root' } });
  const falseRoot = addClaim({ answer: falsehood, sourceId: falseRootSource, minute: 0, confidence: 0.86 });
  const priorFalse = [falseRoot];
  for (let copy = 0; copy < falseCopies; copy += 1) {
    const sourceId = addSource({ hidden: { reliability: 0.5, benchmark_role: 'copy' } });
    const claimId = addClaim({ answer: falsehood, sourceId, parents: [rng.pick(priorFalse)], derivation: rng.next() > 0.35 ? 'syndication' : 'paraphrase', minute: copy + 1, confidence: Number((0.72 + rng.next() * 0.24).toFixed(2)) });
    priorFalse.push(claimId);
  }
  const truthfulClaimIds = [];
  for (let root = 0; root < truthfulRoots; root += 1) {
    const sourceId = addSource({ hidden: { reliability: 0.88, benchmark_role: 'truth_root' } });
    truthfulClaimIds.push(addClaim({ answer: truth, sourceId, minute: rng.int(0, falseCopies + truthfulRoots + 2), confidence: Number((0.68 + rng.next() * 0.18).toFixed(2)) }));
  }
  const provenanceEdges = claims.flatMap((claim) => claim.parent_claim_ids.map((parent) => ({ parent_claim_id: parent, child_claim_id: claim.claim_id, relation: claim.derivation_type })));
  const world = { benchmark_version: benchmarkVersion, world_id: `mp_world_${String(index + 1).padStart(6, '0')}`, seed, question, ground_truth: truth, claims: rng.shuffle(claims), sources, provenance_edges: provenanceEdges, independent_roots: [falseRoot, ...truthfulClaimIds], scenario_family: 'majority_copying', difficulty: falseCopies >= 18 ? 'hard' : 'medium', consensus_ratio: Number(((falseCopies + 1) / claims.length).toFixed(4)), metadata: { split: 'development', false_majority: true, generator_version: 'majority-copying-v1' } };
  validateWorld(world);
  return { ...world, world_hash: hashObject(world) };
}

export function generateDevelopmentWorlds({ count = 25, seed = 41_000, benchmarkVersion = BENCHMARK_VERSION } = {}) { return Array.from({ length: count }, (_, index) => generateMajorityCopyingWorld({ seed: seed + index * 7919, index, benchmarkVersion })); }
