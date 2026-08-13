import { hashObject } from './src/lib/hash.js';
import { SeededRng } from './src/lib/rng.js';

export const CAPABILITY_VERSION = '1.0.0-capability';
export const CAPABILITY_SEED = 2_026_081_000;
export const PROPOSITIONS = 16;

const FAMILY_SPECS = Object.freeze([
  { family: 'single_copy_swarm', roots: 15, correctRoots: 10, swarm: [170, 2, 1] },
  { family: 'distributed_copy_swarms', roots: 15, correctRoots: 9, swarm: [85, 55, 34, 21] },
  { family: 'confidence_theatre', roots: 15, correctRoots: 10, swarm: [140, 50], confidenceTrap: true },
  { family: 'thin_root_margin', roots: 15, correctRoots: 8, swarm: [190, 70, 25] },
  { family: 'mixed_vector_swarms', roots: 17, correctRoots: 10, swarm: [110, 89, 55, 34] },
  { family: 'high_volume_thin_margin', roots: 19, correctRoots: 10, swarm: [240, 120, 60] },
  { family: 'balanced_root_tie', roots: 16, correctRoots: 8, swarm: [180, 90, 45], tie: true },
  { family: 'balanced_root_tie_high_volume', roots: 18, correctRoots: 9, swarm: [260, 130, 65, 32], tie: true }
]);

function balancedTruth(rng) {
  return rng.shuffle(Array.from({ length: PROPOSITIONS }, (_, index) => index % 2 === 0 ? 'A' : 'B'));
}

function opposite(value) { return value === 'A' ? 'B' : 'A'; }

function opaque(seed, kind, ...parts) {
  return `${kind}_${hashObject({ seed, kind, parts }).replace(/^sha256:/, '').slice(0, 12)}`;
}

function buildWorld(spec, index, seed) {
  const rng = new SeededRng(seed);
  const truth = balancedTruth(rng);
  const rootVectors = Array.from({ length: spec.roots }, () => Array(PROPOSITIONS).fill(null));

  for (let proposition = 0; proposition < PROPOSITIONS; proposition += 1) {
    // Root zero is deliberately wrong and later receives the largest copy swarm.
    // The remaining supporting roots are chosen without semantic labels in IDs.
    const candidates = rng.shuffle(Array.from({ length: spec.roots - 1 }, (_, offset) => offset + 1));
    const correct = new Set(candidates.slice(0, spec.correctRoots));
    for (let root = 0; root < spec.roots; root += 1) {
      rootVectors[root][proposition] = correct.has(root) ? truth[proposition] : opposite(truth[proposition]);
    }
  }

  const records = [];
  let sequence = 0;
  for (let root = 0; root < spec.roots; root += 1) {
    const copies = root < spec.swarm.length ? spec.swarm[root] : rng.int(1, 5);
    const lineage = [];
    for (let copy = 0; copy < copies; copy += 1) {
      const recordId = opaque(seed, 'c', root, copy);
      const supports = rootVectors[root].filter((value, proposition) => value === truth[proposition]).length;
      const misleading = supports < PROPOSITIONS / 2;
      const confidence = spec.confidenceTrap
        ? (misleading ? 0.99 : 0.56 + rng.next() * 0.08)
        : (misleading ? 0.92 + rng.next() * 0.07 : 0.62 + rng.next() * 0.18);
      records.push({
        record_id: recordId,
        parent_record_id: copy === 0 ? null : rng.pick(lineage),
        sequence,
        answers: rootVectors[root],
        confidence: Number(confidence.toFixed(4))
      });
      lineage.push(recordId);
      sequence += 1;
    }
  }

  const publicPacket = {
    benchmark_version: CAPABILITY_VERSION,
    case_id: `cap_${String(index + 1).padStart(3, '0')}`,
    instructions: {
      task: 'Determine the best-supported disposition for each proposition and return them in order.',
      dispositions: ['A', 'B', 'ABSTAIN'],
      field_semantics: 'parent_record_id names the immediate evidence record from which a record derives. A null parent marks a direct evidence origin. The supplied lineage graph is fully specified and immutable.'
    },
    proposition_ids: Array.from({ length: PROPOSITIONS }, (_, proposition) => opaque(seed, 'p', proposition)),
    records: rng.shuffle(records)
  };
  const reference = truth.map((value, proposition) => {
    const countA = rootVectors.filter((answers) => answers[proposition] === 'A').length;
    const countB = spec.roots - countA;
    return countA === countB ? 'ABSTAIN' : (countA > countB ? 'A' : 'B');
  });
  if (spec.tie && !reference.every((value) => value === 'ABSTAIN')) throw new Error(`${spec.family} did not produce ties`);
  if (!spec.tie && !reference.every((value, proposition) => value === truth[proposition])) throw new Error(`${spec.family} root reference diverged from constructed key`);

  return {
    public_packet: { ...publicPacket, packet_hash: hashObject(publicPacket) },
    hidden_key: {
      case_id: publicPacket.case_id,
      family: spec.family,
      reference,
      roots: spec.roots,
      records: records.length
    }
  };
}

export function generateCapabilityWorlds({ seed = CAPABILITY_SEED } = {}) {
  return FAMILY_SPECS.map((spec, index) => buildWorld(spec, index, seed + index * 104_729));
}

export function capabilityManifest(worlds = generateCapabilityWorlds()) {
  const manifest = {
    version: CAPABILITY_VERSION,
    seed: CAPABILITY_SEED,
    cases: worlds.map(({ public_packet: packet, hidden_key: hidden }) => ({
      case_id: packet.case_id,
      family: hidden.family,
      packet_hash: packet.packet_hash,
      propositions: packet.proposition_ids.length,
      roots: hidden.roots,
      records: hidden.records
    }))
  };
  return { ...manifest, manifest_hash: hashObject(manifest) };
}
