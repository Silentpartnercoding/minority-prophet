import { MP_ENGINE_VERSION } from './src/domain/constants.js';
import { hashObject } from './src/lib/hash.js';

function rootsFor(claimId, parents, memo = new Map(), path = new Set()) {
  if (memo.has(claimId)) return memo.get(claimId);
  if (path.has(claimId)) return new Set();
  const directParents = parents.get(claimId) ?? [];
  const roots = directParents.length === 0 ? new Set([claimId]) : new Set(directParents.flatMap((parent) => [...rootsFor(parent, parents, memo, new Set(path).add(claimId))]));
  memo.set(claimId, roots);
  return roots;
}

export function analyzeEvidence({ claims, sources, provenance_edges, context = {} }) {
  const parents = new Map(claims.map((claim) => [claim.claim_id, []]));
  for (const edge of provenance_edges) parents.get(edge.child_claim_id)?.push(edge.parent_claim_id);
  const rootIds = claims.filter((claim) => (parents.get(claim.claim_id) ?? []).length === 0).map((claim) => claim.claim_id).sort();
  const rootClaim = new Map(claims.map((claim) => [claim.claim_id, claim]));
  const clusters = new Map();
  const dependencyScores = {};
  const memo = new Map();
  for (const claim of claims) {
    const roots = [...rootsFor(claim.claim_id, parents, memo)].sort();
    const key = roots.join('+') || `cycle:${claim.claim_id}`;
    if (!clusters.has(key)) clusters.set(key, []);
    clusters.get(key).push(claim.claim_id);
    dependencyScores[claim.claim_id] = Number((1 - 1 / Math.max(1, 1 + (parents.get(claim.claim_id)?.length ?? 0))).toFixed(4));
  }
  const independenceScores = {};
  for (const claimIds of clusters.values()) for (const claimId of claimIds) independenceScores[claimId] = Number((1 / claimIds.length).toFixed(4));
  const answerRoots = {};
  for (const rootId of rootIds) { const answer = rootClaim.get(rootId)?.asserted_answer ?? 'unknown'; answerRoots[answer] ??= []; answerRoots[answer].push(rootId); }
  const claimClusters = [...clusters.entries()].map(([ancestry_key, claim_ids]) => ({ ancestry_key, claim_ids, size: claim_ids.length }));
  const output = {
    engine_version: MP_ENGINE_VERSION,
    independent_roots: rootIds,
    claim_clusters: claimClusters,
    dependency_scores: dependencyScores,
    independence_scores: independenceScores,
    correlation_warnings: claimClusters.filter((cluster) => cluster.size >= 4).map((cluster) => ({ type: 'CORRELATED_CLAIM_CLUSTER', claim_ids: cluster.claim_ids, message: `${cluster.size} claims share the same root ancestry and should not be counted as independent confirmations.` })),
    evidence_summary: { claim_count: claims.length, source_count: sources.length, independent_root_count: rootIds.length, roots_by_asserted_answer: answerRoots },
    uncertainty: { missing_provenance_rate: context.missing_provenance_rate ?? 0, circularity_detected: claimClusters.some((cluster) => cluster.ancestry_key.startsWith('cycle:')), confidence_label: provenance_edges.length ? 'graph-derived' : 'limited' },
    recommended_attention: Object.entries(answerRoots).sort((a, b) => b[1].length - a[1].length).map(([asserted_answer, root_claim_ids]) => ({ asserted_answer, root_claim_ids, independent_root_count: root_claim_ids.length }))
  };
  return { ...output, analysis_hash: hashObject(output) };
}
