import { timingSafeEqual } from 'node:crypto';
import { json } from './http-utils.js';
import { compileProvenanceProposal } from './provenance-receipt.js';

const REQUEST_SCHEMA = 'evidence-collector.request.v1';
const RESPONSE_SCHEMA = 'evidence-collector.response.v1';
const INPUT_SCHEMA = 'mp-provenance-service-input.v1';
const COLLECTOR_ID = 'minority-prophet:provenance-service';
const REQUEST_KEYS = new Set(['schema', 'dispatch', 'input', 'grants_protected_action_authority']);
const INPUT_KEYS = new Set(['schema', 'packet', 'proposal']);

function authorized(actual, token) {
  if (!token || typeof actual !== 'string') return false;
  const expected = Buffer.from(`Bearer ${token}`);
  const received = Buffer.from(actual);
  return expected.length === received.length && timingSafeEqual(expected, received);
}

async function readJson(request, maxBytes = 2_000_000) {
  const chunks = [];
  let size = 0;
  for await (const chunk of request) {
    size += chunk.length;
    if (size > maxBytes) throw new Error('request_too_large');
    chunks.push(chunk);
  }
  try {
    return JSON.parse(Buffer.concat(chunks).toString('utf8'));
  } catch {
    throw new Error('invalid_json');
  }
}

function validate(value) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return 'request_not_object';
  for (const key of Object.keys(value)) if (!REQUEST_KEYS.has(key)) return `unexpected_field:${key}`;
  if (value.schema !== REQUEST_SCHEMA) return 'invalid_schema';
  if (value.grants_protected_action_authority !== false) return 'authority_boundary_violation';
  const dispatch = value.dispatch;
  if (!dispatch || typeof dispatch !== 'object' || Array.isArray(dispatch)) return 'invalid_dispatch';
  for (const key of ['challenge_id', 'dispatch_id', 'action_digest', 'decision_subject']) {
    if (typeof dispatch[key] !== 'string' || dispatch[key].length === 0) return `invalid_dispatch_${key}`;
  }
  if (dispatch.grants_protected_action_authority !== false) return 'dispatch_authority_boundary_violation';
  if (!dispatch.route || dispatch.route.collector_kind !== 'epistemic_service' ||
      dispatch.route.output_role !== 'verification_artifact' ||
      dispatch.route.route_grants_protected_action_authority !== false) return 'invalid_epistemic_route';
  if (!Array.isArray(dispatch.requirements) || dispatch.requirements.length === 0) return 'invalid_requirements';
  for (const requirement of dispatch.requirements) {
    if (typeof requirement?.requirement_id !== 'string' || !Array.isArray(requirement.accepted_kinds) ||
        requirement.accepted_kinds.length === 0) return 'invalid_requirement';
  }
  const input = value.input;
  if (!input || typeof input !== 'object' || Array.isArray(input)) return 'invalid_input';
  for (const key of Object.keys(input)) if (!INPUT_KEYS.has(key)) return `unexpected_input_field:${key}`;
  if (input.schema !== INPUT_SCHEMA) return 'invalid_input_schema';
  if (!input.packet || typeof input.packet !== 'object' || Array.isArray(input.packet)) return 'invalid_packet';
  if (!input.proposal || typeof input.proposal !== 'object' || Array.isArray(input.proposal)) return 'invalid_proposal';
  return null;
}

export async function handleProvenanceServiceRoute(request, response, url, { provenanceToken }) {
  if (request.method !== 'POST' || url.pathname !== '/internal/provenance/compile') return false;
  if (!authorized(request.headers.authorization, provenanceToken)) {
    json(response, 401, { error: 'unauthorized' });
    return true;
  }
  let value;
  try {
    value = await readJson(request);
  } catch (error) {
    json(response, error.message === 'request_too_large' ? 413 : 400, { error: error.message });
    return true;
  }
  const validationError = validate(value);
  if (validationError) {
    json(response, 400, { error: validationError });
    return true;
  }
  let receipt;
  try {
    receipt = compileProvenanceProposal(value.input.packet, value.input.proposal);
  } catch {
    json(response, 422, { error: 'invalid_packet_or_proposal' });
    return true;
  }
  const forbidden = ['assertion', 'answer', 'correct_answer', 'ground_truth', 'recommended_answer'];
  if (receipt.answer_included !== false || receipt.ground_truth_included !== false ||
      forbidden.some((key) => Object.hasOwn(receipt, key))) {
    json(response, 500, { error: 'unsafe_receipt' });
    return true;
  }
  const items = value.dispatch.requirements.map((requirement) => ({
    requirement_id: requirement.requirement_id,
    evidence_kind: requirement.accepted_kinds[0],
    envelope: {
      ...receipt,
      attest: {
        origin: COLLECTOR_ID,
        subject: value.dispatch.decision_subject,
        evidence_kind: requirement.accepted_kinds[0]
      }
    }
  }));
  json(response, 200, {
    schema: RESPONSE_SCHEMA,
    challenge_id: value.dispatch.challenge_id,
    dispatch_id: value.dispatch.dispatch_id,
    collector_id: COLLECTOR_ID,
    status: 'completed',
    items,
    diagnostics: { receipt_status: receipt.status, compiler_version: receipt.compiler_version },
    grants_protected_action_authority: false
  });
  return true;
}
