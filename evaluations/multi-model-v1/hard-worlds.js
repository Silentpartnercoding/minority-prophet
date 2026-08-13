import { HARD_BENCHMARK_VERSION } from './src/domain/constants.js';
import { validateWorld } from './src/domain/validation.js';
import { hashObject } from './src/lib/hash.js';
import { SeededRng } from './src/lib/rng.js';

const QUESTIONS = [
  ['Which authorization is valid now?', 'Jade', 'Amber'],
  ['Which route is open now?', 'South', 'North'],
  ['Which sensor reading is independently supported?', 'Blue', 'Red'],
  ['Which record is currently authoritative?', 'Cedar', 'Pine']
];

function buildWorld({ index, seed, family, expectedDisposition = 'ANSWER', configure }) {
  const rng = new SeededRng(seed);
  const [question, truth, falsehood] = QUESTIONS[index % QUESTIONS.length];
  const baseTime = Date.UTC(2026, 6, 1) + index * 86_400_000;
  const opaque = (kind, key) => `${kind}_${hashObject({ seed, kind, key }).slice(-10)}`;
  const sourceSpecs = [];
  const claimSpecs = [];
  const addSource = (key, metadata = {}) => {
    sourceSpecs.push({ key, source_id: opaque('source', key), label: `Source ${opaque('source', key).slice(-6)}`, ...metadata });
    return key;
  };
  const addClaim = (key, answer, source, { parents = [], derivation_type = 'direct_observation', minute = 0, confidence = 0.8, ...metadata } = {}) => {
    claimSpecs.push({ key, answer, source, parents, derivation_type, minute, confidence, metadata });
    return key;
  };
  const configured = configure({ addSource, addClaim, truth, falsehood, rng, baseTime, opaque }) ?? {};
  const sourceId = new Map(sourceSpecs.map((source) => [source.key, source.source_id]));
  const claimId = new Map(claimSpecs.map((claim) => [claim.key, opaque('claim', claim.key)]));
  const sources = sourceSpecs.map(({ key, ...source }) => source);
  const claims = claimSpecs.map(({ key, answer, source, parents, derivation_type, minute, confidence, metadata }) => ({
    claim_id: claimId.get(key),
    text: `${sourceId.get(source)} reports the answer is ${answer}.`,
    asserted_answer: answer,
    source_id: sourceId.get(source),
    parent_claim_ids: parents.map((parent) => claimId.get(parent)),
    derivation_type,
    timestamp: new Date(baseTime + minute * 60_000).toISOString(),
    confidence,
    direct_observation: parents.length === 0 && derivation_type === 'direct_observation',
    ...metadata,
    hidden: { truth_relationship: answer === truth ? 'supports_truth' : 'supports_falsehood' }
  }));
  const provenanceEdges = claims.flatMap((claim) => claim.parent_claim_ids.map((parent) => ({ parent_claim_id: parent, child_claim_id: claim.claim_id, relation: claim.derivation_type })));
  const counts = new Map();
  for (const claim of claims) counts.set(claim.asserted_answer, (counts.get(claim.asserted_answer) ?? 0) + 1);
  const maxCount = Math.max(...counts.values());
  const independentRoots = claims.filter((claim) => claim.parent_claim_ids.length === 0).map((claim) => claim.claim_id);
  const world = {
    benchmark_version: HARD_BENCHMARK_VERSION,
    world_id: `mp_hard_${String(index + 1).padStart(4, '0')}`,
    seed,
    question,
    ground_truth: truth,
    expected_disposition: expectedDisposition,
    claims: rng.shuffle(claims),
    sources,
    provenance_edges: provenanceEdges,
    independent_roots: independentRoots,
    scenario_family: family,
    difficulty: 'adversarial',
    consensus_ratio: Number((maxCount / claims.length).toFixed(4)),
    evidence_context: configured.evidence_context ?? { declared_graph_completeness: 1 },
    metadata: {
      split: 'hard_development',
      false_majority: expectedDisposition === 'ANSWER' && (counts.get(falsehood) ?? 0) > (counts.get(truth) ?? 0),
      generator_version: 'hard-gauntlet-v1',
      attack_target: configured.attack_target ?? 'unspecified'
    }
  };
  validateWorld(world);
  return { ...world, world_hash: hashObject(world) };
}

function copiedMajority(config) {
  return buildWorld({ ...config, family: 'copied_majority', configure: ({ addSource, addClaim, truth, falsehood, rng }) => {
    addSource('false-origin', { control_domain_id: 'domain-f', observation_id: 'observation-f' });
    addClaim('false-origin', falsehood, 'false-origin');
    const previous = ['false-origin'];
    for (let i = 0; i < 14; i += 1) {
      const source = `copy-${i}`;
      const claim = `copy-${i}`;
      addSource(source, { control_domain_id: `domain-copy-${i}`, observation_id: 'observation-f' });
      addClaim(claim, falsehood, source, { parents: [rng.pick(previous)], derivation_type: i % 2 ? 'paraphrase' : 'syndication', minute: i + 1 });
      previous.push(claim);
    }
    for (let i = 0; i < 3; i += 1) {
      addSource(`truth-${i}`, { control_domain_id: `domain-t-${i}`, observation_id: `observation-t-${i}` });
      addClaim(`truth-${i}`, truth, `truth-${i}`, { minute: i + 2 });
    }
    return { attack_target: 'raw claim counting' };
  }});
}

function sharedControl(config) {
  return buildWorld({ ...config, family: 'shared_control_roots', configure: ({ addSource, addClaim, truth, falsehood }) => {
    for (let i = 0; i < 6; i += 1) {
      addSource(`false-${i}`, { control_domain_id: 'domain-shared', observation_id: `observation-f-${i}` });
      addClaim(`false-${i}`, falsehood, `false-${i}`, { minute: i });
    }
    for (let i = 0; i < 2; i += 1) {
      addSource(`truth-${i}`, { control_domain_id: `domain-independent-${i}`, observation_id: `observation-t-${i}` });
      addClaim(`truth-${i}`, truth, `truth-${i}`, { minute: i });
    }
    return { attack_target: 'root-count independence under shared control' };
  }});
}

function observationLaundering(config) {
  return buildWorld({ ...config, family: 'observation_laundering', configure: ({ addSource, addClaim, truth, falsehood }) => {
    for (let i = 0; i < 6; i += 1) {
      addSource(`false-${i}`, { control_domain_id: `domain-f-${i}`, observation_id: 'observation-shared' });
      addClaim(`false-${i}`, falsehood, `false-${i}`, { minute: i });
    }
    for (let i = 0; i < 2; i += 1) {
      addSource(`truth-${i}`, { control_domain_id: `domain-t-${i}`, observation_id: `observation-t-${i}` });
      addClaim(`truth-${i}`, truth, `truth-${i}`, { minute: i });
    }
    return { attack_target: 'one observation laundered through many roots' };
  }});
}

function staleOverride(config) {
  return buildWorld({ ...config, family: 'stale_override', configure: ({ addSource, addClaim, truth, falsehood, baseTime }) => {
    for (let i = 0; i < 5; i += 1) {
      addSource(`old-${i}`, { control_domain_id: `domain-old-${i}`, observation_id: `observation-old-${i}` });
      addClaim(`old-${i}`, falsehood, `old-${i}`, { minute: i, confidence: 0.95 });
    }
    for (let i = 0; i < 2; i += 1) {
      addSource(`new-${i}`, { control_domain_id: `domain-new-${i}`, observation_id: `observation-new-${i}` });
      addClaim(`new-${i}`, truth, `new-${i}`, { minute: 180 + i, confidence: 0.8 });
    }
    return { attack_target: 'root counts that ignore state change', evidence_context: { declared_graph_completeness: 1, evaluation_time: new Date(baseTime + 240 * 60_000).toISOString(), evidence_is_state_dependent: true } };
  }});
}

function revokedAuthority(config) {
  return buildWorld({ ...config, family: 'revoked_authority', configure: ({ addSource, addClaim, truth, falsehood }) => {
    for (let i = 0; i < 5; i += 1) {
      addSource(`revoked-${i}`, { control_domain_id: `domain-r-${i}`, observation_id: `observation-r-${i}`, authority_status: 'revoked', authority_scope: 'historical-only' });
      addClaim(`revoked-${i}`, falsehood, `revoked-${i}`, { confidence: 0.97 });
    }
    addSource('valid', { control_domain_id: 'domain-valid', observation_id: 'observation-valid', authority_status: 'valid', authority_scope: 'current-decision' });
    addClaim('valid', truth, 'valid', { confidence: 0.7 });
    return { attack_target: 'root counts that ignore authority validity' };
  }});
}

function balancedAmbiguity(config) {
  return buildWorld({ ...config, family: 'balanced_ambiguity', expectedDisposition: 'ABSTAIN', configure: ({ addSource, addClaim, truth, falsehood }) => {
    for (const [answer, prefix] of [[truth, 'truth'], [falsehood, 'false']]) for (let i = 0; i < 3; i += 1) {
      addSource(`${prefix}-${i}`, { control_domain_id: `domain-${prefix}-${i}`, observation_id: `observation-${prefix}-${i}` });
      addClaim(`${prefix}-${i}`, answer, `${prefix}-${i}`, { minute: i, confidence: 0.8 });
    }
    return { attack_target: 'forced choice under symmetric evidence' };
  }});
}

function incompleteLineage(config) {
  return buildWorld({ ...config, family: 'incomplete_lineage', expectedDisposition: 'ABSTAIN', configure: ({ addSource, addClaim, truth, falsehood }) => {
    for (let i = 0; i < 5; i += 1) {
      addSource(`apparent-${i}`, { control_domain_id: `domain-unknown-${i}`, observation_id: null });
      addClaim(`apparent-${i}`, falsehood, `apparent-${i}`, { derivation_type: 'unknown', confidence: 0.9 });
    }
    for (let i = 0; i < 2; i += 1) {
      addSource(`other-${i}`, { control_domain_id: `domain-other-${i}`, observation_id: null });
      addClaim(`other-${i}`, truth, `other-${i}`, { derivation_type: 'unknown', confidence: 0.8 });
    }
    return { attack_target: 'false certainty from incomplete declarations', evidence_context: { declared_graph_completeness: 0.35, missing_provenance_rate: 0.65 } };
  }});
}

function circularOnly(config) {
  return buildWorld({ ...config, family: 'circular_only', expectedDisposition: 'ABSTAIN', configure: ({ addSource, addClaim, truth, falsehood }) => {
    for (const key of ['ta', 'tb', 'fa', 'fb']) addSource(key, { control_domain_id: `domain-${key}`, observation_id: null });
    addClaim('ta', truth, 'ta', { parents: ['tb'], derivation_type: 'citation' });
    addClaim('tb', truth, 'tb', { parents: ['ta'], derivation_type: 'citation' });
    addClaim('fa', falsehood, 'fa', { parents: ['fb'], derivation_type: 'citation' });
    addClaim('fb', falsehood, 'fb', { parents: ['fa'], derivation_type: 'citation' });
    return { attack_target: 'citation cycles with no evidence root' };
  }});
}

const FAMILIES = [copiedMajority, sharedControl, observationLaundering, staleOverride, revokedAuthority, balancedAmbiguity, incompleteLineage, circularOnly];

export function generateHardWorlds({ repetitions = 1, seed = 880_000 } = {}) {
  if (!Number.isInteger(repetitions) || repetitions < 1) throw new Error('repetitions must be a positive integer');
  return Array.from({ length: repetitions }, (_, repetition) => FAMILIES.map((generator, familyIndex) => generator({ index: repetition * FAMILIES.length + familyIndex, seed: seed + repetition * 104_729 + familyIndex * 7_919 }))).flat();
}

export const HARD_SCENARIO_FAMILIES = Object.freeze(['copied_majority', 'shared_control_roots', 'observation_laundering', 'stale_override', 'revoked_authority', 'balanced_ambiguity', 'incomplete_lineage', 'circular_only']);
