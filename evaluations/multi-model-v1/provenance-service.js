import { timingSafeEqual } from 'node:crypto';
import { json } from './http-utils.js';
import { compileProvenanceProposal } from './provenance-receipt.js';

const REQUEST_SCHEMA = 'mp-provenance-service-request.v1';
const RESPONSE_SCHEMA = 'mp-provenance-service-response.v1';
const REQUEST_KEYS = new Set([
  'schema', 'challenge_id', 'dispatch_id', 'action_digest', 'decision_subject',
  'packet', 'proposal', 'grants_protected_action_authority'
]);

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
  for (const key of ['challenge_id', 'dispatch_id', 'action_digest', 'decision_subject']) {
    if (typeof value[key] !== 'string' || value[key].length === 0) return `invalid_${key}`;
  }
  if (!value.packet || typeof value.packet !== 'object' || Array.isArray(value.packet)) return 'invalid_packet';
  if (!value.proposal || typeof value.proposal !== 'object' || Array.isArray(value.proposal)) return 'invalid_proposal';
  if (value.grants_protected_action_authority !== false) return 'authority_boundary_violation';
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
    receipt = compileProvenanceProposal(value.packet, value.proposal);
  } catch {
    json(response, 422, { error: 'invalid_packet_or_proposal' });
    return true;
  }
  json(response, 200, {
    schema: RESPONSE_SCHEMA,
    challenge_id: value.challenge_id,
    dispatch_id: value.dispatch_id,
    action_digest: value.action_digest,
    decision_subject: value.decision_subject,
    output_role: 'verification_artifact',
    receipt,
    grants_protected_action_authority: false
  });
  return true;
}
