import { LIFT_MP_ENGINE_VERSION } from './src/domain/constants.js';
import { hashObject } from './src/lib/hash.js';

export const MP_TOOL_DEFINITION = Object.freeze({
  name: 'analyze_evidence_structure',
  description: 'Read-only deterministic analysis of supplied claim ancestry, control domains, observation origins, freshness, and missing provenance. It never returns a correct answer or grants authority.',
  input_schema: {
    type: 'object',
    additionalProperties: false,
    required: ['claims', 'sources', 'provenance_edges', 'context'],
    properties: {
      claims: { type: 'array' },
      sources: { type: 'array' },
      provenance_edges: { type: 'array' },
      context: { type: 'object' }
    }
  }
});

export const MP_TOOL_CONTRACT_HASH = hashObject(MP_TOOL_DEFINITION);

function traceClaim(claimId, parents, memo, path = new Set()) {
  if (memo.has(claimId)) return memo.get(claimId);
  if (path.has(claimId)) return { roots: new Set(), cycle: true };
  const direct = parents.get(claimId) ?? [];
  if (direct.length === 0) {
    const result = { roots: new Set([claimId]), cycle: false };
    memo.set(claimId, result);
    return result;
  }
  const nextPath = new Set(path).add(claimId);
  const traced = direct.map((parent) => traceClaim(parent, parents, memo, nextPath));
  const result = {
    roots: new Set(traced.flatMap((item) => [...item.roots])),
    cycle: traced.some((item) => item.cycle)
  };
  if (!result.cycle) memo.set(claimId, result);
  return result;
}

function currentAt(timestamp, context) {
  if (!context.state_dependent) return true;
  const evaluation = Date.parse(context.evaluation_time ?? '');
  const observed = Date.parse(timestamp ?? '');
  const windowMs = Number(context.freshness_window_minutes ?? 0) * 60_000;
  if (!Number.isFinite(evaluation) || !Number.isFinite(observed) || windowMs <= 0) return false;
  return observed <= evaluation && observed >= evaluation - windowMs;
}

function stableUnique(values) {
  return [...new Set(values.filter((value) => value !== null && value !== undefined && value !== ''))].sort();
}

export function analyzeEvidenceV2({ claims, sources, provenance_edges, context = {} }) {
  const sourceById = new Map(sources.map((source) => [source.source_id, source]));
  const claimById = new Map(claims.map((claim) => [claim.claim_id, claim]));
  const parents = new Map(claims.map((claim) => [claim.claim_id, []]));
  for (const edge of provenance_edges) {
    if (parents.has(edge.child_claim_id) && claimById.has(edge.parent_claim_id)) parents.get(edge.child_claim_id).push(edge.parent_claim_id);
  }
  const memo = new Map();
  const traces = new Map(claims.map((claim) => [claim.claim_id, traceClaim(claim.claim_id, parents, memo)]));
  const rootIds = stableUnique([...traces.values()].flatMap((trace) => [...trace.roots]));
  const answers = stableUnique(claims.map((claim) => claim.asserted_answer));
  const clusters = new Map();
  for (const claim of claims) {
    const trace = traces.get(claim.claim_id);
    const key = trace.cycle ? `cycle:${[...trace.roots].sort().join('+')}` : [...trace.roots].sort().join('+') || `unresolved:${claim.claim_id}`;
    if (!clusters.has(key)) clusters.set(key, []);
    clusters.get(key).push(claim.claim_id);
  }

  const rootRecords = rootIds.map((rootId) => {
    const claim = claimById.get(rootId);
    const source = sourceById.get(claim?.source_id);
    return {
      root_claim_id: rootId,
      asserted_answer: claim?.asserted_answer ?? null,
      source_id: claim?.source_id ?? null,
      control_domain_id: source?.control_domain_id ?? null,
      observation_id: source?.observation_id ?? null,
      current: currentAt(claim?.timestamp, context),
      direct_observation: claim?.direct_observation === true,
      timestamp: claim?.timestamp ?? null
    };
  });

  const supportByAnswer = answers.map((asserted_answer) => {
    const answerClaims = claims.filter((claim) => claim.asserted_answer === asserted_answer);
    const answerClaimIds = new Set(answerClaims.map((claim) => claim.claim_id));
    const roots = rootRecords.filter((root) => root.asserted_answer === asserted_answer);
    const currentRoots = roots.filter((root) => root.current && root.direct_observation);
    const controls = stableUnique(currentRoots.map((root) => root.control_domain_id));
    const observations = stableUnique(currentRoots.map((root) => root.observation_id));
    const knownCurrentRoots = currentRoots.filter((root) => root.control_domain_id && root.observation_id);
    const evidenceUnits = Math.min(knownCurrentRoots.length, controls.length, observations.length);
    return {
      asserted_answer,
      raw_claim_count: answerClaims.length,
      lineage_root_count: roots.length,
      current_direct_root_count: currentRoots.length,
      distinct_control_domain_count: controls.length,
      distinct_observation_count: observations.length,
      current_evidence_unit_count: evidenceUnits,
      cycle_affected_claim_count: answerClaims.filter((claim) => traces.get(claim.claim_id)?.cycle).length,
      unresolved_claim_count: answerClaims.filter((claim) => traces.get(claim.claim_id)?.roots.size === 0).length,
      supporting_claim_ids: [...answerClaimIds].sort()
    };
  });

  const unitCounts = supportByAnswer.map((item) => item.current_evidence_unit_count);
  const maxUnits = Math.max(0, ...unitCounts);
  const maxCount = unitCounts.filter((count) => count === maxUnits).length;
  const graphCompleteness = Number(context.declared_graph_completeness ?? (provenance_edges.length ? 1 : 0));
  const rootsMissingControl = rootRecords.filter((root) => !root.control_domain_id).length;
  const rootsMissingObservation = rootRecords.filter((root) => !root.observation_id).length;
  const cycleClaims = claims.filter((claim) => traces.get(claim.claim_id)?.cycle).map((claim) => claim.claim_id).sort();
  const abstentionSignals = [];
  if (graphCompleteness < 0.8) abstentionSignals.push({ type: 'DECLARED_GRAPH_INCOMPLETE', value: graphCompleteness });
  if (rootsMissingControl || rootsMissingObservation) abstentionSignals.push({ type: 'ROOT_IDENTITY_INCOMPLETE', roots_missing_control: rootsMissingControl, roots_missing_observation: rootsMissingObservation });
  if (maxUnits === 0) abstentionSignals.push({ type: 'NO_RESOLVED_CURRENT_EVIDENCE_UNITS' });
  if (maxUnits > 0 && maxCount > 1) abstentionSignals.push({ type: 'STRUCTURAL_SUPPORT_TIE', tied_answer_count: maxCount, evidence_units_each: maxUnits });

  const correlationWarnings = [];
  for (const [ancestry_key, claim_ids] of clusters.entries()) if (claim_ids.length >= 3) correlationWarnings.push({ type: 'SHARED_ANCESTRY', ancestry_key, claim_ids: [...claim_ids].sort(), claim_count: claim_ids.length });
  for (const control of stableUnique(rootRecords.map((root) => root.control_domain_id))) {
    const roots = rootRecords.filter((root) => root.control_domain_id === control);
    if (roots.length >= 2) correlationWarnings.push({ type: 'SHARED_CONTROL_DOMAIN', control_domain_id: control, root_claim_ids: roots.map((root) => root.root_claim_id).sort(), root_count: roots.length });
  }
  for (const observation of stableUnique(rootRecords.map((root) => root.observation_id))) {
    const roots = rootRecords.filter((root) => root.observation_id === observation);
    if (roots.length >= 2) correlationWarnings.push({ type: 'SHARED_OBSERVATION', observation_id: observation, root_claim_ids: roots.map((root) => root.root_claim_id).sort(), root_count: roots.length });
  }
  if (cycleClaims.length) correlationWarnings.push({ type: 'CITATION_CYCLE', claim_ids: cycleClaims, claim_count: cycleClaims.length });

  const output = {
    engine_version: LIFT_MP_ENGINE_VERSION,
    contract_hash: MP_TOOL_CONTRACT_HASH,
    independent_roots: rootRecords,
    claim_clusters: [...clusters.entries()].map(([ancestry_key, claim_ids]) => ({ ancestry_key, claim_ids: [...claim_ids].sort(), size: claim_ids.length })),
    support_by_answer: supportByAnswer,
    correlation_warnings: correlationWarnings,
    uncertainty: {
      declared_graph_completeness: graphCompleteness,
      missing_provenance_rate: Number(context.missing_provenance_rate ?? Math.max(0, 1 - graphCompleteness)),
      roots_missing_control: rootsMissingControl,
      roots_missing_observation: rootsMissingObservation,
      citation_cycle_claim_count: cycleClaims.length,
      state_dependent: Boolean(context.state_dependent)
    },
    abstention_signals: abstentionSignals,
    attention_flags: correlationWarnings.map((warning) => warning.type)
  };
  return { ...output, analysis_hash: hashObject(output) };
}

export function executeMinorityProphetTool(input) {
  const allowed = ['claims', 'sources', 'provenance_edges', 'context'];
  if (!input || typeof input !== 'object' || allowed.some((field) => !(field in input))) throw new Error('MP tool input is incomplete');
  for (const field of Object.keys(input)) if (!allowed.includes(field)) throw new Error(`MP tool input field is not allowed: ${field}`);
  return analyzeEvidenceV2(input);
}
