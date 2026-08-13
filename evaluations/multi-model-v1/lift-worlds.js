import { LIFT_BENCHMARK_VERSION } from './src/domain/constants.js';
import { validateWorld } from './src/domain/validation.js';
import { hashObject } from './src/lib/hash.js';
import { SeededRng } from './src/lib/rng.js';

const QUESTIONS = Object.freeze([
  ['Which emergency route is usable now?', 'Aster', 'Birch'],
  ['Which sensor bank is reporting the current state?', 'Cobalt', 'Dune'],
  ['Which archive contains the operative record?', 'Elm', 'Flint'],
  ['Which inspection result should govern?', 'Garnet', 'Harbor'],
  ['Which sample is supported by direct observations?', 'Indigo', 'Juniper'],
  ['Which channel reflects the present system state?', 'Kestrel', 'Lumen']
]);

function buildWorld({ index, seed, family, expectedDisposition = 'ANSWER', configure }) {
  const rng = new SeededRng(seed);
  const [question, first, second] = QUESTIONS[index % QUESTIONS.length];
  const truth = rng.next() < 0.5 ? first : second;
  const falsehood = truth === first ? second : first;
  const baseTime = Date.UTC(2026, 7, 1) + index * 86_400_000;
  const opaque = (kind, key) => `${kind}_${hashObject({ seed, kind, key }).slice(-12)}`;
  const sourceSpecs = [];
  const claimSpecs = [];
  const addSource = (key, metadata = {}) => {
    sourceSpecs.push({ key, source_id: opaque('source', key), label: `Source ${opaque('source', key).slice(-6)}`, ...metadata });
    return key;
  };
  const addClaim = (key, answer, source, { parents = [], derivation_type = 'direct_observation', minute = 0, confidence = 0.8 } = {}) => {
    claimSpecs.push({ key, answer, source, parents, derivation_type, minute, confidence });
    return key;
  };
  const configured = configure({ addSource, addClaim, truth, falsehood, rng, baseTime }) ?? {};
  const sourceId = new Map(sourceSpecs.map((source) => [source.key, source.source_id]));
  const claimId = new Map(claimSpecs.map((claim) => [claim.key, opaque('claim', claim.key)]));
  const sources = sourceSpecs.map(({ key, ...source }) => source);
  const claims = claimSpecs.map(({ key, answer, source, parents, derivation_type, minute, confidence }) => ({
    claim_id: claimId.get(key),
    text: `${sourceId.get(source)} reports the answer is ${answer}.`,
    asserted_answer: answer,
    source_id: sourceId.get(source),
    parent_claim_ids: parents.map((parent) => claimId.get(parent)),
    derivation_type,
    timestamp: new Date(baseTime + minute * 60_000).toISOString(),
    confidence,
    direct_observation: parents.length === 0 && derivation_type === 'direct_observation',
    hidden: { truth_relationship: answer === truth ? 'supports_truth' : 'supports_falsehood' }
  }));
  const provenanceEdges = claims.flatMap((claim) => claim.parent_claim_ids.map((parent) => ({ parent_claim_id: parent, child_claim_id: claim.claim_id, relation: claim.derivation_type })));
  const headCounts = new Map();
  for (const claim of claims) headCounts.set(claim.asserted_answer, (headCounts.get(claim.asserted_answer) ?? 0) + 1);
  const independentRoots = claims.filter((claim) => claim.parent_claim_ids.length === 0).map((claim) => claim.claim_id);
  const maxCount = Math.max(...headCounts.values());
  const world = {
    benchmark_version: LIFT_BENCHMARK_VERSION,
    world_id: `mp_lift_${String(index + 1).padStart(5, '0')}`,
    seed,
    question,
    ground_truth: truth,
    expected_disposition: expectedDisposition,
    claims: rng.shuffle(claims),
    sources: rng.shuffle(sources),
    provenance_edges: rng.shuffle(provenanceEdges),
    independent_roots: independentRoots,
    scenario_family: family,
    difficulty: 'adversarial',
    consensus_ratio: Number((maxCount / claims.length).toFixed(4)),
    evidence_context: configured.evidence_context ?? { declared_graph_completeness: 1, state_dependent: false },
    metadata: {
      split: 'candidate_development',
      false_majority: expectedDisposition === 'ANSWER' && (headCounts.get(falsehood) ?? 0) > (headCounts.get(truth) ?? 0),
      generator_version: 'epistemic-lift-worlds-v1',
      replication_unit: 'world'
    }
  };
  validateWorld(world);
  return { ...world, world_hash: hashObject(world) };
}

function copiedMajority(config) {
  return buildWorld({ ...config, family: 'copied_majority', configure: ({ addSource, addClaim, truth, falsehood, rng }) => {
    addSource('false-root', { control_domain_id: 'cd-f', observation_id: 'obs-f', display_reputation: 0.88 });
    addClaim('false-root', falsehood, 'false-root', { confidence: 0.91 });
    const prior = ['false-root'];
    const copies = rng.int(28, 46);
    for (let i = 0; i < copies; i += 1) {
      addSource(`copy-${i}`, { control_domain_id: `cd-copy-${i}`, observation_id: 'obs-f', display_reputation: Number((0.55 + rng.next() * 0.4).toFixed(2)) });
      addClaim(`copy-${i}`, falsehood, `copy-${i}`, { parents: [rng.pick(prior)], derivation_type: i % 3 === 0 ? 'summary' : i % 2 ? 'paraphrase' : 'syndication', minute: i + 1, confidence: Number((0.78 + rng.next() * 0.2).toFixed(2)) });
      prior.push(`copy-${i}`);
    }
    for (let i = 0; i < 3; i += 1) {
      addSource(`truth-${i}`, { control_domain_id: `cd-t-${i}`, observation_id: `obs-t-${i}`, display_reputation: Number((0.35 + rng.next() * 0.25).toFixed(2)) });
      addClaim(`truth-${i}`, truth, `truth-${i}`, { minute: rng.int(1, copies), confidence: Number((0.65 + rng.next() * 0.18).toFixed(2)) });
    }
  }});
}

function sharedControl(config) {
  return buildWorld({ ...config, family: 'shared_control_roots', configure: ({ addSource, addClaim, truth, falsehood, rng }) => {
    const apparentRoots = rng.int(9, 15);
    for (let i = 0; i < apparentRoots; i += 1) {
      addSource(`false-${i}`, { control_domain_id: 'cd-shared', observation_id: `obs-f-${i}`, display_reputation: Number((0.7 + rng.next() * 0.28).toFixed(2)) });
      addClaim(`false-${i}`, falsehood, `false-${i}`, { minute: i, confidence: Number((0.82 + rng.next() * 0.16).toFixed(2)) });
    }
    for (let i = 0; i < 3; i += 1) {
      addSource(`truth-${i}`, { control_domain_id: `cd-independent-${i}`, observation_id: `obs-t-${i}`, display_reputation: Number((0.35 + rng.next() * 0.25).toFixed(2)) });
      addClaim(`truth-${i}`, truth, `truth-${i}`, { minute: i + 2, confidence: Number((0.62 + rng.next() * 0.18).toFixed(2)) });
    }
  }});
}

function observationLaundering(config) {
  return buildWorld({ ...config, family: 'observation_laundering', configure: ({ addSource, addClaim, truth, falsehood, rng }) => {
    const apparentRoots = rng.int(8, 13);
    for (let i = 0; i < apparentRoots; i += 1) {
      addSource(`false-${i}`, { control_domain_id: `cd-f-${i}`, observation_id: 'obs-shared', display_reputation: Number((0.68 + rng.next() * 0.3).toFixed(2)) });
      addClaim(`false-${i}`, falsehood, `false-${i}`, { minute: i, confidence: Number((0.8 + rng.next() * 0.18).toFixed(2)) });
    }
    for (let i = 0; i < 3; i += 1) {
      addSource(`truth-${i}`, { control_domain_id: `cd-t-${i}`, observation_id: `obs-t-${i}`, display_reputation: Number((0.35 + rng.next() * 0.28).toFixed(2)) });
      addClaim(`truth-${i}`, truth, `truth-${i}`, { minute: i + 3, confidence: Number((0.6 + rng.next() * 0.2).toFixed(2)) });
    }
  }});
}

function temporalStaleness(config) {
  return buildWorld({ ...config, family: 'temporal_staleness', configure: ({ addSource, addClaim, truth, falsehood, rng, baseTime }) => {
    const oldRoots = rng.int(7, 12);
    for (let i = 0; i < oldRoots; i += 1) {
      addSource(`old-${i}`, { control_domain_id: `cd-old-${i}`, observation_id: `obs-old-${i}`, display_reputation: Number((0.7 + rng.next() * 0.28).toFixed(2)) });
      addClaim(`old-${i}`, falsehood, `old-${i}`, { minute: i, confidence: Number((0.86 + rng.next() * 0.12).toFixed(2)) });
    }
    for (let i = 0; i < 3; i += 1) {
      addSource(`current-${i}`, { control_domain_id: `cd-current-${i}`, observation_id: `obs-current-${i}`, display_reputation: Number((0.38 + rng.next() * 0.25).toFixed(2)) });
      addClaim(`current-${i}`, truth, `current-${i}`, { minute: 225 + i, confidence: Number((0.64 + rng.next() * 0.18).toFixed(2)) });
    }
    return { evidence_context: { declared_graph_completeness: 1, state_dependent: true, evaluation_time: new Date(baseTime + 240 * 60_000).toISOString(), freshness_window_minutes: 60 } };
  }});
}

function prestigeAttack(config) {
  return buildWorld({ ...config, family: 'prestige_attack', configure: ({ addSource, addClaim, truth, falsehood, rng }) => {
    addSource('prestige-root', { control_domain_id: 'cd-prestige', observation_id: 'obs-prestige', display_reputation: 0.99 });
    addClaim('prestige-root', falsehood, 'prestige-root', { confidence: 0.99 });
    const prior = ['prestige-root'];
    for (let i = 0; i < 18; i += 1) {
      addSource(`prestige-copy-${i}`, { control_domain_id: `cd-pc-${i}`, observation_id: 'obs-prestige', display_reputation: Number((0.8 + rng.next() * 0.18).toFixed(2)) });
      addClaim(`prestige-copy-${i}`, falsehood, `prestige-copy-${i}`, { parents: [rng.pick(prior)], derivation_type: i % 2 ? 'citation' : 'paraphrase', minute: i + 1, confidence: Number((0.88 + rng.next() * 0.1).toFixed(2)) });
      prior.push(`prestige-copy-${i}`);
    }
    for (let i = 0; i < 3; i += 1) {
      addSource(`field-${i}`, { control_domain_id: `cd-field-${i}`, observation_id: `obs-field-${i}`, display_reputation: Number((0.18 + rng.next() * 0.2).toFixed(2)) });
      addClaim(`field-${i}`, truth, `field-${i}`, { minute: 12 + i, confidence: Number((0.58 + rng.next() * 0.16).toFixed(2)) });
    }
  }});
}

function paraphraseDepth(config) {
  return buildWorld({ ...config, family: 'paraphrase_depth', configure: ({ addSource, addClaim, truth, falsehood, rng }) => {
    addSource('false-origin', { control_domain_id: 'cd-origin', observation_id: 'obs-origin', display_reputation: 0.78 });
    addClaim('false-origin', falsehood, 'false-origin', { confidence: 0.9 });
    let parent = 'false-origin';
    const depth = rng.int(22, 34);
    for (let i = 0; i < depth; i += 1) {
      addSource(`layer-${i}`, { control_domain_id: `cd-layer-${i}`, observation_id: 'obs-origin', display_reputation: Number((0.5 + rng.next() * 0.45).toFixed(2)) });
      addClaim(`layer-${i}`, falsehood, `layer-${i}`, { parents: [parent], derivation_type: i % 3 === 0 ? 'translation' : i % 2 ? 'summary' : 'paraphrase', minute: i + 1, confidence: Number((0.74 + rng.next() * 0.23).toFixed(2)) });
      parent = `layer-${i}`;
    }
    for (let i = 0; i < 3; i += 1) {
      addSource(`truth-${i}`, { control_domain_id: `cd-t-${i}`, observation_id: `obs-t-${i}`, display_reputation: Number((0.32 + rng.next() * 0.3).toFixed(2)) });
      addClaim(`truth-${i}`, truth, `truth-${i}`, { minute: 10 + i, confidence: Number((0.6 + rng.next() * 0.2).toFixed(2)) });
    }
  }});
}

function balancedConflict(config) {
  return buildWorld({ ...config, family: 'balanced_conflict', expectedDisposition: 'ABSTAIN', configure: ({ addSource, addClaim, truth, falsehood, rng }) => {
    for (const [answer, prefix] of [[truth, 'left'], [falsehood, 'right']]) for (let i = 0; i < 4; i += 1) {
      addSource(`${prefix}-${i}`, { control_domain_id: `cd-${prefix}-${i}`, observation_id: `obs-${prefix}-${i}`, display_reputation: Number((0.45 + rng.next() * 0.4).toFixed(2)) });
      addClaim(`${prefix}-${i}`, answer, `${prefix}-${i}`, { minute: i, confidence: Number((0.62 + rng.next() * 0.25).toFixed(2)) });
    }
  }});
}

function incompleteProvenance(config) {
  return buildWorld({ ...config, family: 'incomplete_provenance', expectedDisposition: 'ABSTAIN', configure: ({ addSource, addClaim, truth, falsehood, rng }) => {
    for (const [answer, prefix, count] of [[truth, 'left', 4], [falsehood, 'right', 9]]) for (let i = 0; i < count; i += 1) {
      addSource(`${prefix}-${i}`, { control_domain_id: null, observation_id: null, display_reputation: Number((0.45 + rng.next() * 0.5).toFixed(2)) });
      addClaim(`${prefix}-${i}`, answer, `${prefix}-${i}`, { derivation_type: 'unknown', minute: i, confidence: Number((0.68 + rng.next() * 0.28).toFixed(2)) });
    }
    return { evidence_context: { declared_graph_completeness: 0.35, missing_provenance_rate: 0.65, state_dependent: false } };
  }});
}

const FAMILIES = Object.freeze([copiedMajority, sharedControl, observationLaundering, temporalStaleness, prestigeAttack, paraphraseDepth, balancedConflict, incompleteProvenance]);
export const LIFT_SCENARIO_FAMILIES = Object.freeze(['copied_majority', 'shared_control_roots', 'observation_laundering', 'temporal_staleness', 'prestige_attack', 'paraphrase_depth', 'balanced_conflict', 'incomplete_provenance']);

export function generateLiftWorlds({ repetitions = 4, seed = 1_730_000 } = {}) {
  if (!Number.isInteger(repetitions) || repetitions < 1) throw new Error('repetitions must be a positive integer');
  return Array.from({ length: repetitions }, (_, repetition) => FAMILIES.map((generator, familyIndex) => generator({ index: repetition * FAMILIES.length + familyIndex, seed: seed + repetition * 104_729 + familyIndex * 7_919 }))).flat();
}
