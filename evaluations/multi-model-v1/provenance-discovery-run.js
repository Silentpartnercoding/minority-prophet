#!/usr/bin/env node
import { execFileSync } from 'node:child_process';
import { mkdir, readFile, rename, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { ClaudeCliAdapter, CodexCliAdapter } from './cli-provider.js';
import { discoveryJobs, provenanceDiscoveryBenchmark } from './provenance-discovery-benchmark.js';
import { normalizedLlmInference, scoreProvenance } from './provenance-discovery-scoring.js';
import { publicDiscoveryWorld } from './provenance-discovery-worlds.js';
import { decideFromInferredRoots, inferProvenance, inferProvenanceExp008Comparator } from './provenance-inference.js';
import { hashObject } from './src/lib/hash.js';

const PROJECT_ROOT = fileURLToPath(new URL('.', import.meta.url));
const FROZEN_MANIFEST = 'sha256:570f1ee0dd78b0cb109af3c4e8533a7ae4a54aa976c1df319706c679725317b1';
const FROZEN_PROTOCOL_COMMIT = '51240e818e46aa137afb2bb81d03f655e2a6b094';
const benchmark = provenanceDiscoveryBenchmark();
if (benchmark.manifest.manifest_hash !== FROZEN_MANIFEST) throw new Error(`Discovery manifest not frozen: ${benchmark.manifest.manifest_hash}`);
const commit = execFileSync('git', ['rev-parse', 'HEAD'], { cwd: PROJECT_ROOT, encoding: 'utf8' }).trim();
if (execFileSync('git', ['status', '--porcelain', '--untracked-files=no'], { cwd: PROJECT_ROOT, encoding: 'utf8' }).trim()) throw new Error('Commit the protocol before execution');
const statePath = process.env.MP_DISCOVERY_STATE ?? join(PROJECT_ROOT, 'data/runtime/provenance-discovery-v1.json');
const outputDir = process.env.MP_DISCOVERY_OUTPUT ?? join(PROJECT_ROOT, 'public/generated/provenance-discovery-v1');
const schema = {
  type: 'object', additionalProperties: false,
  required: ['root_groups', 'answer', 'abstain', 'confidence', 'summary'],
  properties: {
    root_groups: { type: 'array', items: { type: 'object', required: ['document_ids'], properties: { document_ids: { type: 'array', items: { type: 'string' } }, explanation: { type: 'string' } } } },
    answer: { type: 'string' }, abstain: { type: 'boolean' }, confidence: { type: 'number' }, summary: { type: 'string' }
  }
};
const systemPrompt = 'Infer which reports share the same underlying origin using only observable report text, URLs, publishers, and timestamps. Do not assume that similar conclusions share an origin. Return only concise JSON matching response_schema. Do not expose private chain-of-thought.';
const shouldAbstain = (world) => ['generic_boilerplate', 'opaque_paraphrase'].includes(world.family);

function parse(raw) {
  try {
    if (raw && typeof raw === 'object') return raw;
    const start = raw.indexOf('{'); const end = raw.lastIndexOf('}');
    return JSON.parse(raw.slice(start, end + 1));
  } catch { return null; }
}
async function loadState() { try { return JSON.parse(await readFile(statePath, 'utf8')); } catch (error) { if (error.code === 'ENOENT') return { manifest: benchmark.manifest, protocol_commit: FROZEN_PROTOCOL_COMMIT, trials: [] }; throw error; } }
async function save(state) { await mkdir(join(PROJECT_ROOT, 'data/runtime'), { recursive: true }); const next = `${statePath}.next`; await writeFile(next, `${JSON.stringify(state, null, 2)}\n`, { mode: 0o600 }); await rename(next, statePath); }

const state = await loadState();
if (state.protocol_commit !== FROZEN_PROTOCOL_COMMIT) throw new Error('Checkpoint protocol commit does not match the frozen protocol');
if (state.manifest?.manifest_hash !== FROZEN_MANIFEST) throw new Error('Checkpoint manifest does not match the frozen protocol');
const adapters = [new CodexCliAdapter({ rawCapture: true, timeoutMs: 240_000 }), new ClaudeCliAdapter({ rawCapture: true, timeoutMs: 240_000 })];
const jobs = discoveryJobs(adapters, benchmark.worlds);
let cursor = 0;
async function worker() {
  while (cursor < jobs.length) {
    const { adapter, world, key } = jobs[cursor++];
    if (state.trials.some((trial) => trial.key === key)) continue;
    const packet = publicDiscoveryWorld(world);
    const started = Date.now();
    try {
      const result = await adapter.runModel({ systemPrompt, messages: [{ role: 'user', content: JSON.stringify({ instruction: 'Partition every document into groups that share one underlying origin, then answer the question by counting independently originating observations. A group may contain one document.', evidence_packet: packet, response_schema: schema }) }], temperature: 0, topP: 1, seed: world.seed, maxTokens: 1200 });
      const response = parse(result.raw);
      const inferred = response ? normalizedLlmInference(world, response) : Object.fromEntries(world.documents.map((document) => [document.document_id, document.document_id]));
      const provenance = scoreProvenance(world, inferred);
      state.trials.push({ key, provider: adapter.provider, model: adapter.model, model_version: result.model_version, world_id: world.world_id, family: world.family, world_hash: world.world_hash, status: response ? 'COMPLETED' : 'PARSE_FAILURE', response, raw_response: result.raw, inferred_root_by_document: inferred, provenance, downstream_correct: Boolean(response && !response.abstain && response.answer.trim().toLowerCase() === world.hidden.ground_truth.toLowerCase()), abstention_correct: Boolean(response && Boolean(response.abstain) === shouldAbstain(world)), execution_ms: result.execution_ms ?? Date.now() - started, usage: result.usage, cost_usd: result.cost_usd, provider_request_id: result.provider_request_id, raw_hash: hashObject(result.raw) });
    } catch (error) {
      state.trials.push({ key, provider: adapter.provider, model: adapter.model, world_id: world.world_id, family: world.family, world_hash: world.world_hash, status: 'FAILED', error: error.message, provenance: { pairwise_precision: 0, pairwise_recall: 0, pairwise_f1: 0 }, downstream_correct: false, abstention_correct: false, execution_ms: Date.now() - started });
    }
    await save(state);
  }
}
await Promise.all(Array.from({ length: 4 }, () => worker()));

const mpTrials = benchmark.worlds.map((world) => {
  const packet = publicDiscoveryWorld(world); const started = performance.now();
  const inference = inferProvenance(packet); const decision = decideFromInferredRoots(packet, inference); const executionMs = performance.now() - started;
  return { model: 'minority-prophet-provenance-candidate', world_id: world.world_id, family: world.family, world_hash: world.world_hash, status: 'COMPLETED', inferred_root_by_document: inference.inferred_root_by_document, provenance: scoreProvenance(world, inference.inferred_root_by_document), downstream_correct: !decision.abstain && decision.answer.toLowerCase() === world.hidden.ground_truth.toLowerCase(), abstention_correct: decision.abstain === shouldAbstain(world), execution_ms: executionMs, decision };
});
state.mp_trials = mpTrials;
state.comparator_trials = benchmark.worlds.map((world) => {
  const packet = publicDiscoveryWorld(world); const started = performance.now();
  const inference = inferProvenanceExp008Comparator(packet); const decision = decideFromInferredRoots(packet, inference); const executionMs = performance.now() - started;
  return { model: 'exp008-inference-comparator', world_id: world.world_id, family: world.family, world_hash: world.world_hash, status: 'COMPLETED', inferred_root_by_document: inference.inferred_root_by_document, provenance: scoreProvenance(world, inference.inferred_root_by_document), downstream_correct: !decision.abstain && decision.answer.toLowerCase() === world.hidden.ground_truth.toLowerCase(), abstention_correct: decision.abstain === shouldAbstain(world), execution_ms: executionMs, decision };
});
state.completed_at = new Date().toISOString();
await save(state);

function summarize(model, trials) {
  const rows = trials.filter((trial) => trial.model === model); const mean = (field) => rows.reduce((sum, row) => sum + field(row), 0) / rows.length;
  return { model, trials: rows.length, completed: rows.filter((row) => row.status === 'COMPLETED').length, pairwise_precision: mean((row) => row.provenance.pairwise_precision), pairwise_recall: mean((row) => row.provenance.pairwise_recall), pairwise_f1: mean((row) => row.provenance.pairwise_f1), downstream_truth_recovery: mean((row) => Number(row.downstream_correct)), abstention_accuracy: mean((row) => Number(row.abstention_correct)), safe_task_success: mean((row) => Number(row.downstream_correct || (row.abstention_correct && ['generic_boilerplate', 'opaque_paraphrase'].includes(row.family)))), mean_execution_ms: mean((row) => row.execution_ms), input_tokens: rows.reduce((sum, row) => sum + (row.usage?.input_tokens ?? 0), 0), output_tokens: rows.reduce((sum, row) => sum + (row.usage?.output_tokens ?? 0), 0), cached_tokens: rows.reduce((sum, row) => sum + (row.usage?.cached_tokens ?? 0), 0), provider_reported_cost_usd: rows.reduce((sum, row) => sum + (row.cost_usd ?? 0), 0), by_family: Object.fromEntries(benchmark.manifest.families.map((family) => { const subset = rows.filter((row) => row.family === family); return [family, { f1: subset.reduce((sum, row) => sum + row.provenance.pairwise_f1, 0) / subset.length, truth_recovery: subset.filter((row) => row.downstream_correct).length / subset.length, abstention_accuracy: subset.filter((row) => row.abstention_correct).length / subset.length }]; })) };
}
const all = [...state.trials, ...state.mp_trials, ...state.comparator_trials];
const models = [...new Set(all.map((trial) => trial.model))];
const expectedModelTrials = benchmark.worlds.length * adapters.length;
const reportBase = { schema: 'mp-provenance-discovery-report.v1', status: state.trials.length === expectedModelTrials ? 'COMPLETED' : 'INCOMPLETE', namespace: 'DEMO', protocol_commit: state.protocol_commit, runner_commit: commit, manifest: benchmark.manifest, claim_boundary: 'Synthetic development corpus with observable citation, syndication, and distinctive-detail clues; not real-world or independent validation.', models: models.map((model) => summarize(model, all)), limitations: ['benchmark and candidate inference were designed by the same control domain', 'four worlds per family', 'synthetic text', 'generic boilerplate and opaque paraphrase have deliberately insufficient observable lineage evidence', 'model tools and external retrieval disabled'] };
const report = { ...reportBase, report_hash: hashObject(reportBase) };
await mkdir(outputDir, { recursive: true });
await writeFile(join(outputDir, 'result.json'), `${JSON.stringify(report, null, 2)}\n`);
console.log(JSON.stringify({ status: report.status, report_hash: report.report_hash, models: report.models }, null, 2));
