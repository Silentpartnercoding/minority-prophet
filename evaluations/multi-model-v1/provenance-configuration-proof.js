import { hashObject } from './src/lib/hash.js';
import { inferProvenance } from './provenance-inference.js';

function rootsFor(documents, parents) {
  const root = (id, path = new Set()) => {
    if (path.has(id) || !parents.has(id)) return id;
    return root(parents.get(id), new Set(path).add(id));
  };
  return Object.fromEntries(documents.map((document) => [document.document_id, root(document.document_id)]));
}

function normalize(value) {
  return value.toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
}

export function exactTextAutoCollapse(packet) {
  const sorted = [...packet.documents].sort((a, b) => a.published_at.localeCompare(b.published_at) || a.document_id.localeCompare(b.document_id));
  const parents = new Map();
  for (let i = 0; i < sorted.length; i += 1) {
    const parent = sorted.slice(0, i).find((candidate) => normalize(candidate.content) === normalize(sorted[i].content));
    if (parent) parents.set(sorted[i].document_id, parent.document_id);
  }
  return rootsFor(packet.documents, parents);
}

export function ambiguityPair() {
  const documents = Array.from({ length: 6 }, (_, index) => ({
    document_id: `ambiguous_doc_${index + 1}`,
    url: `https://reports.example/ambiguous_doc_${index + 1}`,
    publisher: `Independent Outlet ${index + 1}`,
    published_at: new Date(Date.UTC(2026, 8, 1, 0, index)).toISOString(),
    content: 'Standard inspection complete. Aster is the usable route.'
  }));
  const packet = { world_id: 'mp_nonidentifiable_packet', question: 'How many independently originating observations support Aster?', documents };
  const copied = Object.fromEntries(documents.map((document) => [document.document_id, documents[0].document_id]));
  const independent = Object.fromEntries(documents.map((document) => [document.document_id, document.document_id]));
  return {
    packet,
    copy_world: { ...packet, hidden: { root_by_document: copied } },
    independent_world: { ...packet, hidden: { root_by_document: independent } },
    public_packet_hash: hashObject(packet)
  };
}

function pairs(rootByDocument) {
  const ids = Object.keys(rootByDocument).sort();
  const result = new Set();
  for (let i = 0; i < ids.length; i += 1) for (let j = i + 1; j < ids.length; j += 1) if (rootByDocument[ids[i]] === rootByDocument[ids[j]]) result.add(`${ids[i]}|${ids[j]}`);
  return result;
}

function classificationAccuracy(actual, predicted) {
  const ids = Object.keys(actual);
  const actualPairs = pairs(actual); const predictedPairs = pairs(predicted);
  let correct = 0; let total = 0;
  for (let i = 0; i < ids.length; i += 1) for (let j = i + 1; j < ids.length; j += 1) {
    const key = [ids[i], ids[j]].sort().join('|');
    correct += Number(actualPairs.has(key) === predictedPairs.has(key)); total += 1;
  }
  return correct / total;
}

export function evaluateAmbiguityConfigurations() {
  const pair = ambiguityPair();
  const conservative = inferProvenance(pair.packet).inferred_root_by_document;
  const aggressive = exactTextAutoCollapse(pair.packet);
  const conservativeCopy = classificationAccuracy(pair.copy_world.hidden.root_by_document, conservative);
  const conservativeIndependent = classificationAccuracy(pair.independent_world.hidden.root_by_document, conservative);
  const aggressiveCopy = classificationAccuracy(pair.copy_world.hidden.root_by_document, aggressive);
  const aggressiveIndependent = classificationAccuracy(pair.independent_world.hidden.root_by_document, aggressive);
  return {
    public_packet_hash: pair.public_packet_hash,
    configurations: {
      confidence_gated_review: {
        copy_accuracy: conservativeCopy,
        independent_accuracy: conservativeIndependent,
        paired_mean_accuracy: (conservativeCopy + conservativeIndependent) / 2
      },
      exact_text_auto_collapse: {
        copy_accuracy: aggressiveCopy,
        independent_accuracy: aggressiveIndependent,
        paired_mean_accuracy: (aggressiveCopy + aggressiveIndependent) / 2
      }
    }
  };
}
