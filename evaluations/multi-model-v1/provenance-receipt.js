import { hashObject } from './src/lib/hash.js';
import { inferProvenance } from './provenance-inference.js';

export const LINEAGE_PROPOSAL_SCHEMA = Object.freeze({
  type: 'object',
  additionalProperties: false,
  required: ['schema', 'links', 'unresolved_document_ids', 'summary'],
  properties: {
    schema: { const: 'mp-lineage-proposal.v1' },
    links: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        required: ['child_document_id', 'parent_document_id', 'confidence', 'evidence_types'],
        properties: {
          child_document_id: { type: 'string' },
          parent_document_id: { type: 'string' },
          confidence: { type: 'number', minimum: 0, maximum: 1 },
          evidence_types: { type: 'array', items: { enum: ['explicit_citation', 'distinctive_shared_detail', 'exact_text_match', 'high_lexical_overlap', 'publisher_relationship'] } }
        }
      }
    },
    unresolved_document_ids: { type: 'array', items: { type: 'string' } },
    summary: { type: 'string' }
  }
});

const TOP_KEYS = new Set(['schema', 'links', 'unresolved_document_ids', 'summary']);
const LINK_KEYS = new Set(['child_document_id', 'parent_document_id', 'confidence', 'evidence_types']);
const EVIDENCE_TYPES = new Set(['explicit_citation', 'distinctive_shared_detail', 'exact_text_match', 'high_lexical_overlap', 'publisher_relationship']);

function schemaErrors(proposal) {
  const errors = [];
  if (!proposal || typeof proposal !== 'object' || Array.isArray(proposal)) return ['proposal_not_object'];
  if (proposal.schema !== 'mp-lineage-proposal.v1') errors.push('invalid_schema_version');
  for (const key of Object.keys(proposal)) if (!TOP_KEYS.has(key)) errors.push(`unexpected_top_level_field:${key}`);
  if (!Array.isArray(proposal.links)) errors.push('links_not_array');
  if (!Array.isArray(proposal.unresolved_document_ids)) errors.push('unresolved_document_ids_not_array');
  if (typeof proposal.summary !== 'string') errors.push('summary_not_string');
  else if (proposal.summary.length > 1000) errors.push('summary_too_long');
  if (Array.isArray(proposal.links) && proposal.links.length > 1000) errors.push('too_many_links');
  for (const [index, link] of (Array.isArray(proposal.links) ? proposal.links : []).entries()) {
    if (!link || typeof link !== 'object' || Array.isArray(link)) { errors.push(`link_not_object:${index}`); continue; }
    for (const key of Object.keys(link)) if (!LINK_KEYS.has(key)) errors.push(`unexpected_link_field:${index}:${key}`);
    if (typeof link.child_document_id !== 'string') errors.push(`invalid_child_id:${index}`);
    if (typeof link.parent_document_id !== 'string') errors.push(`invalid_parent_id:${index}`);
    if (!Number.isFinite(link.confidence) || link.confidence < 0 || link.confidence > 1) errors.push(`invalid_confidence:${index}`);
    if (!Array.isArray(link.evidence_types) || link.evidence_types.some((type) => !EVIDENCE_TYPES.has(type))) errors.push(`invalid_evidence_types:${index}`);
    else if (new Set(link.evidence_types).size !== link.evidence_types.length) errors.push(`duplicate_evidence_type:${index}`);
  }
  return errors;
}

function safeRootGroups(inference) {
  return inference.root_groups.map((group) => ({
    root_document_id: group.root_document_id,
    document_ids: [...group.document_ids]
  }));
}

export function compileProvenanceProposal(packet, proposal) {
  const inputHash = hashObject(packet);
  const proposalHash = hashObject(proposal);
  const errors = schemaErrors(proposal);
  const inference = inferProvenance(packet);
  const knownIds = new Set(packet.documents.map((document) => document.document_id));
  const candidates = new Map(inference.candidate_links.map((link) => [`${link.child_document_id}|${link.parent_document_id}`, link]));
  const reviewLinks = [];
  const rejectedLinks = [];
  const seen = new Set();

  if (!errors.length) {
    for (const link of proposal.links) {
      const key = `${link.child_document_id}|${link.parent_document_id}`;
      let rejection = null;
      if (seen.has(key)) rejection = 'duplicate_link';
      else if (!knownIds.has(link.child_document_id) || !knownIds.has(link.parent_document_id)) rejection = 'unknown_document_id';
      else if (link.child_document_id === link.parent_document_id) rejection = 'self_parent';
      seen.add(key);
      const observed = candidates.get(key);
      if (!rejection && !observed) rejection = 'no_deterministically_observed_support';
      if (!rejection && observed.action === 'reject') rejection = 'deterministic_policy_rejected';
      if (rejection) rejectedLinks.push({ child_document_id: link.child_document_id, parent_document_id: link.parent_document_id, reason: rejection });
      else if (observed.action === 'review') reviewLinks.push({ child_document_id: link.child_document_id, parent_document_id: link.parent_document_id, model_confidence: link.confidence, observed_score: observed.score, observed_reasons: observed.reasons });
      // Collapse-grade observations are already present in inference.accepted_links;
      // the model cannot elevate, rewrite, or duplicate them in the trusted receipt.
    }
    for (const id of proposal.unresolved_document_ids) if (!knownIds.has(id)) errors.push(`unknown_unresolved_document_id:${id}`);
  }

  const acceptedLinks = errors.length ? [] : inference.accepted_links.map((link) => ({
    child_document_id: link.child_document_id,
    parent_document_id: link.parent_document_id,
    observed_score: link.score,
    observed_reasons: link.reasons
  }));
  const base = {
    schema: 'mp-provenance-receipt.v1',
    compiler_version: 'mp-provenance-receipt-compiler-v1',
    status: errors.length ? 'REJECTED' : rejectedLinks.length || reviewLinks.length || inference.provenance_warnings.length ? 'REVIEW_REQUIRED' : 'ACCEPTED',
    input_hash: inputHash,
    proposal_hash: proposalHash,
    accepted_links: acceptedLinks,
    review_links: errors.length ? [] : reviewLinks,
    rejected_links: rejectedLinks,
    provenance_warnings: inference.provenance_warnings,
    validation_errors: errors,
    root_groups: errors.length ? packet.documents.map((document) => ({ root_document_id: document.document_id, document_ids: [document.document_id] })) : safeRootGroups(inference),
    claim_clusters: errors.length ? [] : inference.claim_clusters,
    ground_truth_included: false,
    answer_included: false
  };
  return { ...base, receipt_hash: hashObject(base) };
}

export function parseAndCompileProvenanceProposal(packet, raw) {
  if (raw && typeof raw === 'object') return compileProvenanceProposal(packet, raw);
  if (typeof raw !== 'string' || raw.length > 1_000_000) return compileProvenanceProposal(packet, raw);
  try {
    return compileProvenanceProposal(packet, JSON.parse(raw));
  } catch {
    // No fence stripping, substring extraction, or repair model: malformed
    // transport is preserved as a rejected proposal rather than guessed into
    // a trusted receipt.
    return compileProvenanceProposal(packet, raw);
  }
}
