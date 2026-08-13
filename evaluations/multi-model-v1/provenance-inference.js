import { hashObject } from './src/lib/hash.js';

const DETAIL = /field detail (?:was |“)?[“\"]([^”\"]+)[”\"]/i;
const URL = /https:\/\/reports\.example\/(doc_[a-f0-9]+)/ig;
const ANSWER = /\b(Aster|Birch|Cobalt|Dune|Elm|Flint|Garnet|Harbor)\b/i;
const ACCEPT_THRESHOLD = 0.78;
const REVIEW_THRESHOLD = 0.5;

function published(document) {
  return Date.parse(document.published_at);
}

function answer(document) {
  return document.content.match(ANSWER)?.[1]?.toLowerCase() ?? null;
}

function marker(document) {
  return document.content.match(DETAIL)?.[1]?.trim().toLowerCase() ?? null;
}

function distinctive(value) {
  if (!value) return false;
  const compact = value.replace(/[^a-z0-9]/g, '');
  return compact.length >= 12 && (/\d{5,}/.test(value) || /[a-z].*\d|\d.*[a-z]/i.test(value));
}

function citedIds(document) {
  return [...document.content.matchAll(URL)].map((match) => match[1]);
}

function normalizedText(document) {
  return document.content.toLowerCase()
    .replace(/https?:\/\/\S+/g, ' ')
    .replace(/[^a-z0-9]+/g, ' ')
    .trim();
}

function lexicalOverlap(left, right) {
  const a = new Set(normalizedText(left).split(' ').filter((token) => token.length > 2));
  const b = new Set(normalizedText(right).split(' ').filter((token) => token.length > 2));
  const union = new Set([...a, ...b]);
  if (!union.size) return 0;
  return [...a].filter((token) => b.has(token)).length / union.size;
}

function scoreCandidate(child, parent) {
  const reasons = [];
  const childAnswer = answer(child);
  const parentAnswer = answer(parent);
  const sameAnswer = Boolean(childAnswer && childAnswer === parentAnswer);
  const citesParent = citedIds(child).includes(parent.document_id);
  const sharedMarker = marker(child) && marker(child) === marker(parent);
  const markerIsDistinctive = sharedMarker && distinctive(marker(child));
  const exactText = normalizedText(child) === normalizedText(parent);
  const overlap = lexicalOverlap(child, parent);

  if (citesParent && !sameAnswer) {
    return { score: 0.2, reasons: ['explicit_citation', 'assertion_conflict'], action: 'reject' };
  }
  if (citesParent) reasons.push('explicit_citation');
  if (markerIsDistinctive) reasons.push('distinctive_shared_detail');
  else if (sharedMarker) reasons.push('generic_shared_detail');
  if (exactText) reasons.push('exact_text_match');
  else if (overlap >= 0.8) reasons.push('high_lexical_overlap');
  if (sameAnswer) reasons.push('same_asserted_answer');

  // A citation or high-entropy shared observation is sufficient to propose a
  // collapse. Agreement on the answer and temporal proximity are deliberately
  // not sufficient: independent witnesses can agree and publish close in time.
  let score = citesParent ? 0.99
    : markerIsDistinctive ? 0.94
      : exactText ? 0.65
        : overlap >= 0.8 ? 0.55
          : sharedMarker ? 0.45 : 0;
  if (score && !sameAnswer) score = Math.min(score, 0.2);
  return {
    score,
    reasons,
    action: score >= ACCEPT_THRESHOLD ? 'collapse' : score >= REVIEW_THRESHOLD ? 'review' : 'reject'
  };
}

function resolveRoots(documents, parentByDocument) {
  const roots = new Map();
  const root = (id, path = new Set()) => {
    if (roots.has(id)) return roots.get(id);
    if (path.has(id) || !parentByDocument.has(id)) return id;
    const value = root(parentByDocument.get(id), new Set(path).add(id));
    roots.set(id, value);
    return value;
  };
  return Object.fromEntries(documents.map((document) => [document.document_id, root(document.document_id)]));
}

function groups(rootByDocument) {
  const values = new Map();
  for (const [documentId, rootId] of Object.entries(rootByDocument)) {
    if (!values.has(rootId)) values.set(rootId, []);
    values.get(rootId).push(documentId);
  }
  return [...values.entries()].map(([root_document_id, document_ids]) => ({
    root_document_id,
    document_ids: document_ids.sort()
  }));
}

function exactClaimClusters(documents) {
  const values = new Map();
  for (const document of documents) {
    const fingerprint = normalizedText(document);
    if (!values.has(fingerprint)) values.set(fingerprint, []);
    values.get(fingerprint).push(document.document_id);
  }
  return [...values.entries()].filter(([, documentIds]) => documentIds.length > 1).map(([fingerprint, documentIds]) => ({
    cluster_id: hashObject({ basis: 'exact_normalized_text', fingerprint }),
    basis: 'exact_normalized_text',
    document_ids: documentIds.sort(),
    evidential_independence: 'unresolved'
  }));
}

export function inferProvenance(packet) {
  const sorted = [...packet.documents].sort((a, b) => published(a) - published(b) || a.document_id.localeCompare(b.document_id));
  const byId = new Map(packet.documents.map((document) => [document.document_id, document]));
  const parents = new Map();
  const candidateLinks = [];
  const selectedLinks = [];
  const provenanceWarnings = [];
  for (const child of packet.documents) {
    for (const citedId of citedIds(child)) {
      const cited = byId.get(citedId);
      if (!cited) provenanceWarnings.push({ document_id: child.document_id, cited_document_id: citedId, warning: 'unknown_citation_target' });
      else if (published(cited) >= published(child)) provenanceWarnings.push({ document_id: child.document_id, cited_document_id: citedId, warning: 'non_prior_citation' });
      else if (answer(child) && answer(cited) && answer(child) !== answer(cited)) provenanceWarnings.push({ document_id: child.document_id, cited_document_id: citedId, warning: 'citation_assertion_conflict' });
    }
  }
  for (let position = 0; position < sorted.length; position += 1) {
    const child = sorted[position];
    const candidates = sorted.slice(0, position).map((parent) => ({
      child_document_id: child.document_id,
      parent_document_id: parent.document_id,
      ...scoreCandidate(child, parent)
    })).filter((candidate) => candidate.score > 0).sort((a, b) => b.score - a.score || a.parent_document_id.localeCompare(b.parent_document_id));
    candidateLinks.push(...candidates);
    const best = candidates[0];
    if (best?.action === 'collapse') {
      parents.set(child.document_id, best.parent_document_id);
      selectedLinks.push(best);
    }
  }
  const rootByDocument = resolveRoots(packet.documents, parents);
  const review = candidateLinks.filter((candidate) => candidate.action === 'review');
  const nextAction = provenanceWarnings.length > 0
    ? 'integrity_review_required'
    : selectedLinks.length > 0 ? 'auto_collapse' : 'semantic_review_required';
  return {
    engine_version: 'mp-provenance-inference-candidate-v2.1',
    policy: { accept_threshold: ACCEPT_THRESHOLD, review_threshold: REVIEW_THRESHOLD, answer_agreement_alone_can_collapse: false },
    candidate_links: candidateLinks,
    accepted_links: selectedLinks,
    review_links: review,
    provenance_warnings: provenanceWarnings,
    next_action: nextAction,
    inferred_parent_by_document: Object.fromEntries(parents),
    inferred_root_by_document: rootByDocument,
    root_groups: groups(rootByDocument),
    claim_clusters: exactClaimClusters(packet.documents),
    unresolved_document_ids: packet.documents.filter((document) => !parents.has(document.document_id)).map((document) => document.document_id).sort(),
    evidence_coverage: selectedLinks.length / Math.max(1, packet.documents.length - 1)
  };
}

// A faithful conceptual port of EXP008's answer-agreement + time + citation
// heuristic. EXP008 used eight-answer vectors; on one-answer documents its
// agreement signal is intentionally exposed as much less discriminating.
export function inferProvenanceExp008Comparator(packet) {
  const sorted = [...packet.documents].sort((a, b) => published(a) - published(b) || a.document_id.localeCompare(b.document_id));
  const parents = new Map();
  for (let position = 0; position < sorted.length; position += 1) {
    const child = sorted[position];
    let best = null;
    let bestScore = 0.55;
    for (const parent of sorted.slice(0, position)) {
      const agreement = Number(Boolean(answer(child) && answer(child) === answer(parent)));
      const minutes = Math.max(0, (published(child) - published(parent)) / 60_000);
      const citation = Number(citedIds(child).includes(parent.document_id));
      const score = 0.55 * agreement + 0.25 * Math.exp(-minutes / 5) + 0.2 * citation;
      if (score > bestScore) { best = parent.document_id; bestScore = score; }
    }
    if (best) parents.set(child.document_id, best);
  }
  const rootByDocument = resolveRoots(packet.documents, parents);
  return {
    engine_version: 'exp008-inference-comparator-js-v1',
    inferred_parent_by_document: Object.fromEntries(parents),
    inferred_root_by_document: rootByDocument,
    root_groups: groups(rootByDocument)
  };
}

export function decideFromInferredRoots(packet, inference) {
  const byId = new Map(packet.documents.map((document) => [document.document_id, document]));
  const counts = new Map();
  for (const root of new Set(Object.values(inference.inferred_root_by_document))) {
    const value = byId.get(root)?.content.match(ANSWER)?.[1] ?? null;
    if (value) counts.set(value, (counts.get(value) ?? 0) + 1);
  }
  const ordered = [...counts.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
  const tie = ordered.length < 2 || ordered[0][1] === ordered[1][1];
  const noObservableLineage = Array.isArray(inference.accepted_links) && inference.accepted_links.length === 0;
  const abstain = tie || noObservableLineage;
  return {
    answer: abstain ? '' : ordered[0][0],
    abstain,
    abstention_reason: tie ? 'root_support_tie' : noObservableLineage ? 'no_observable_lineage' : null,
    root_support: Object.fromEntries(ordered),
    evidence_coverage: inference.evidence_coverage ?? null
  };
}
