import { hashObject } from './src/lib/hash.js';
import { SeededRng } from './src/lib/rng.js';

const ANSWERS = [['Aster', 'Birch'], ['Cobalt', 'Dune'], ['Elm', 'Flint'], ['Garnet', 'Harbor']];
export const DISCOVERY_FAMILIES = Object.freeze([
  'explicit_citation',
  'syndication_marker',
  'signature_laundering',
  'deceptive_citation',
  'generic_boilerplate',
  'opaque_paraphrase'
]);

function words(answer, marker, style, sourceUrl = '') {
  if (style === 'citation') return `Field bulletin: the usable route is ${answer}. The observation included field detail “${marker}”. Source: ${sourceUrl}.`;
  if (style === 'syndication') return `Update: ${answer} is the usable route. Witnesses recorded field detail “${marker}”. Distributed from ${sourceUrl}.`;
  if (style === 'signature') return `Local report identifies ${answer} as usable. Its distinctive field detail was “${marker}”.`;
  if (style === 'generic') return `Local report identifies ${answer} as usable. Its field detail was “standard checklist complete”.`;
  if (style === 'opaque') return `After reviewing conditions, correspondents identify ${answer} as the usable route.`;
  return `Direct observer reports that ${answer} is the usable route and records field detail “${marker}”.`;
}

function makeWorld(index, seed, family) {
  const rng = new SeededRng(seed);
  const [first, second] = ANSWERS[index % ANSWERS.length];
  const truth = rng.next() < 0.5 ? first : second;
  const falsehood = truth === first ? second : first;
  const originId = `doc_${hashObject({ seed, key: 'false-origin' }).slice(-10)}`;
  const originUrl = `https://reports.example/${originId}`;
  const falseMarker = `serial-${rng.int(100000, 999999)}-north`;
  const documents = [{
    document_id: originId, url: originUrl, publisher: 'Central Dispatch', published_at: '2026-08-01T00:00:00.000Z',
    content: words(falsehood, falseMarker, 'root'), asserted_answer: falsehood
  }];
  const hiddenParent = new Map([[originId, null]]);
  const hiddenRoot = new Map([[originId, originId]]);
  const truthIds = Array.from({ length: 3 }, (_, i) => `doc_${hashObject({ seed, key: `truth-${i}` }).slice(-10)}`);
  let previous = originId;
  for (let i = 0; i < 7; i += 1) {
    const id = `doc_${hashObject({ seed, key: `copy-${i}` }).slice(-10)}`;
    const style = family === 'explicit_citation' ? 'citation'
      : family === 'syndication_marker' ? 'syndication'
        : family === 'signature_laundering' || family === 'deceptive_citation' ? 'signature'
          : family === 'generic_boilerplate' ? 'generic' : 'opaque';
    const source = family === 'explicit_citation' || family === 'syndication_marker'
      ? `https://reports.example/${previous}`
      : family === 'deceptive_citation' ? `https://reports.example/${truthIds[i % truthIds.length]}` : '';
    const body = words(falsehood, falseMarker, style, source);
    documents.push({
      document_id: id, url: `https://reports.example/${id}`, publisher: `Outlet ${i + 1}`,
      published_at: new Date(Date.UTC(2026, 7, 1, 0, i + 1)).toISOString(),
      content: family === 'deceptive_citation' ? `${body} Claimed source: ${source}.` : body, asserted_answer: falsehood
    });
    hiddenParent.set(id, previous);
    hiddenRoot.set(id, originId);
    previous = id;
  }
  for (let i = 0; i < 3; i += 1) {
    const id = truthIds[i];
    const marker = `serial-${rng.int(100000, 999999)}-${['east', 'west', 'south'][i]}`;
    documents.push({
      document_id: id, url: `https://reports.example/${id}`, publisher: `Field Observer ${i + 1}`,
      published_at: new Date(Date.UTC(2026, 7, 1, 0, i + 2)).toISOString(),
      content: words(truth, marker, 'root'), asserted_answer: truth
    });
    hiddenParent.set(id, null);
    hiddenRoot.set(id, id);
  }
  const publicPacket = {
    world_id: `mp_discovery_${String(index + 1).padStart(4, '0')}`,
    question: 'Which route is supported by the greatest number of independently originating observations?',
    documents: rng.shuffle(documents)
  };
  const hidden = {
    ground_truth: truth,
    parent_by_document: Object.fromEntries(hiddenParent),
    root_by_document: Object.fromEntries(hiddenRoot)
  };
  return { ...publicPacket, family, seed, hidden, world_hash: hashObject({ publicPacket, family, seed, hidden }) };
}

export function generateDiscoveryWorlds({ repetitions = 4, seed = 8_120_026 } = {}) {
  return Array.from({ length: repetitions }, (_, repetition) => DISCOVERY_FAMILIES.map((family, familyIndex) => makeWorld(repetition * DISCOVERY_FAMILIES.length + familyIndex, seed + repetition * 65_537 + familyIndex * 7_919, family))).flat();
}

export function publicDiscoveryWorld(world) {
  return { world_id: world.world_id, question: world.question, documents: world.documents.map(({ asserted_answer: ignored, ...document }) => document) };
}
