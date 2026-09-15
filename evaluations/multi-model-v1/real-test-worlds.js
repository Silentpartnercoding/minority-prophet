import { generateLiftWorlds } from './lift-worlds.js';
import { hashObject } from './src/lib/hash.js';
import { SeededRng } from './src/lib/rng.js';
import { validateWorld } from './src/domain/validation.js';

const CONTROL_FAMILIES = Object.freeze([
  'independent_truth_majority',
  'truthful_syndication',
  'current_truth_majority'
]);

function honestControl(base, index) {
  const seed = 4_900_000 + index * 104_729;
  const rng = new SeededRng(seed);
  const family = CONTROL_FAMILIES[index % CONTROL_FAMILIES.length];
  const truth = base.ground_truth;
  const falsehood = base.claims.find((claim) => claim.asserted_answer !== truth)?.asserted_answer;
  if (!falsehood) throw new Error(`Unable to derive the alternate answer for ${base.world_id}`);
  const baseTime = Date.UTC(2026, 7, 15) + index * 86_400_000;
  const opaque = (kind, key) => `${kind}_${hashObject({ seed, kind, key }).slice(-12)}`;
  const sources = [];
  const claims = [];

  const addSource = (key, metadata) => {
    const source_id = opaque('source', key);
    sources.push({ source_id, label: `Source ${source_id.slice(-6)}`, ...metadata });
    return source_id;
  };
  const addClaim = (key, answer, sourceId, { parent = null, derivation_type = 'direct_observation', minute = 0, confidence = 0.8 } = {}) => {
    const claim_id = opaque('claim', key);
    claims.push({
      claim_id,
      text: `${sourceId} reports the answer is ${answer}.`,
      asserted_answer: answer,
      source_id: sourceId,
      parent_claim_ids: parent ? [parent] : [],
      derivation_type,
      timestamp: new Date(baseTime + minute * 60_000).toISOString(),
      confidence,
      direct_observation: !parent && derivation_type === 'direct_observation',
      hidden: { truth_relationship: answer === truth ? 'supports_truth' : 'supports_falsehood' }
    });
    return claim_id;
  };

  if (family === 'independent_truth_majority') {
    for (let i = 0; i < 7; i += 1) {
      const source = addSource(`truth-${i}`, { control_domain_id: `cd-t-${i}`, observation_id: `obs-t-${i}`, display_reputation: Number((0.45 + rng.next() * 0.4).toFixed(2)) });
      addClaim(`truth-${i}`, truth, source, { minute: 10 + i, confidence: Number((0.68 + rng.next() * 0.2).toFixed(2)) });
    }
    for (let i = 0; i < 3; i += 1) {
      const source = addSource(`false-${i}`, { control_domain_id: `cd-f-${i}`, observation_id: `obs-f-${i}`, display_reputation: Number((0.45 + rng.next() * 0.4).toFixed(2)) });
      addClaim(`false-${i}`, falsehood, source, { minute: 10 + i, confidence: Number((0.68 + rng.next() * 0.2).toFixed(2)) });
    }
  } else if (family === 'truthful_syndication') {
    for (let i = 0; i < 5; i += 1) {
      const source = addSource(`truth-root-${i}`, { control_domain_id: `cd-t-${i}`, observation_id: `obs-t-${i}`, display_reputation: Number((0.42 + rng.next() * 0.4).toFixed(2)) });
      const root = addClaim(`truth-root-${i}`, truth, source, { minute: i, confidence: Number((0.66 + rng.next() * 0.22).toFixed(2)) });
      if (i < 3) {
        const copySource = addSource(`truth-copy-${i}`, { control_domain_id: `cd-copy-${i}`, observation_id: `obs-t-${i}`, display_reputation: Number((0.5 + rng.next() * 0.4).toFixed(2)) });
        addClaim(`truth-copy-${i}`, truth, copySource, { parent: root, derivation_type: 'syndication', minute: 20 + i, confidence: Number((0.7 + rng.next() * 0.2).toFixed(2)) });
      }
    }
    for (let i = 0; i < 3; i += 1) {
      const source = addSource(`false-${i}`, { control_domain_id: `cd-f-${i}`, observation_id: `obs-f-${i}`, display_reputation: Number((0.44 + rng.next() * 0.4).toFixed(2)) });
      addClaim(`false-${i}`, falsehood, source, { minute: 4 + i, confidence: Number((0.65 + rng.next() * 0.2).toFixed(2)) });
    }
  } else {
    for (let i = 0; i < 6; i += 1) {
      const source = addSource(`current-truth-${i}`, { control_domain_id: `cd-current-t-${i}`, observation_id: `obs-current-t-${i}`, display_reputation: Number((0.4 + rng.next() * 0.42).toFixed(2)) });
      addClaim(`current-truth-${i}`, truth, source, { minute: 210 + i, confidence: Number((0.65 + rng.next() * 0.22).toFixed(2)) });
    }
    for (let i = 0; i < 4; i += 1) {
      const source = addSource(`stale-false-${i}`, { control_domain_id: `cd-stale-f-${i}`, observation_id: `obs-stale-f-${i}`, display_reputation: Number((0.55 + rng.next() * 0.4).toFixed(2)) });
      addClaim(`stale-false-${i}`, falsehood, source, { minute: i, confidence: Number((0.76 + rng.next() * 0.2).toFixed(2)) });
    }
  }

  const provenance_edges = claims.flatMap((claim) => claim.parent_claim_ids.map((parent_claim_id) => ({ parent_claim_id, child_claim_id: claim.claim_id, relation: claim.derivation_type })));
  const independent_roots = claims.filter((claim) => claim.parent_claim_ids.length === 0).map((claim) => claim.claim_id);
  const headCounts = new Map();
  for (const claim of claims) headCounts.set(claim.asserted_answer, (headCounts.get(claim.asserted_answer) ?? 0) + 1);
  const maxCount = Math.max(...headCounts.values());
  const evidence_context = family === 'current_truth_majority'
    ? { declared_graph_completeness: 1, state_dependent: true, evaluation_time: new Date(baseTime + 240 * 60_000).toISOString(), freshness_window_minutes: 60 }
    : { declared_graph_completeness: 1, state_dependent: false };
  const world = {
    benchmark_version: base.benchmark_version,
    world_id: `mp_real_control_${String(index + 1).padStart(5, '0')}`,
    seed,
    question: base.question,
    ground_truth: truth,
    expected_disposition: 'ANSWER',
    claims: rng.shuffle(claims),
    sources: rng.shuffle(sources),
    provenance_edges: rng.shuffle(provenance_edges),
    independent_roots,
    scenario_family: family,
    difficulty: 'control',
    consensus_ratio: Number((maxCount / claims.length).toFixed(4)),
    evidence_context,
    metadata: {
      split: 'local_balanced_diagnostic',
      false_majority: false,
      correct_majority: true,
      generator_version: 'openrouter-real-controls-v1',
      replication_unit: 'world'
    }
  };
  validateWorld(world);
  return { ...world, world_hash: hashObject(world) };
}

export function realTestWorlds(repetitions = 2) {
  if (!Number.isInteger(repetitions) || repetitions < 1) throw new Error("repetitions must be a positive integer");
  const adversarial = generateLiftWorlds({ repetitions });
  const answerable = adversarial.filter((world) => world.expected_disposition === 'ANSWER');
  const controls = Array.from({ length: answerable.length }, (_, index) => honestControl(answerable[index], index));
  return [...adversarial, ...controls];
}

export { CONTROL_FAMILIES };
