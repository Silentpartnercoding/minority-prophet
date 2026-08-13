import assert from 'node:assert/strict';
import { mkdtemp, readFile, rm } from 'node:fs/promises';
import test from 'node:test';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

import { liftBenchmarkV11 } from './lift-benchmark-v11.js';
import { buildLiveToolPrompt, LIVE_TOOL_CONDITIONS } from './live-tool-prompts.js';
import { startRuntimeServer } from './runtime-http.js';

test('MCP executable responds when invoked through a symlinked path', async () => {
  const directory = await mkdtemp(join(tmpdir(), 'mp-mcp-link-'));
  const target = fileURLToPath(new URL('./mp-mcp-server.js', import.meta.url));
  const linked = join(directory, 'mp-mcp-server.js');
  const { symlink } = await import('node:fs/promises');
  await symlink(target, linked);
  try {
    const request = '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}\n';
    const result = spawnSync(process.execPath, [linked], { input: request, encoding: 'utf8' });
    assert.equal(result.status, 0, result.stderr);
    const response = JSON.parse(result.stdout);
    assert.equal(response.result.tools[0].name, 'analyze_evidence_structure');
  } finally {
    await rm(directory, { recursive: true, force: true });
  }
});

test('runtime requires explicit local opt-in or an authentication token', async () => {
  await assert.rejects(() => startRuntimeServer({ host: '0.0.0.0', port: 0 }), /configure a token/);
});

test('insecure-local flag cannot disable authentication on a non-loopback listener', async () => {
  const server = await startRuntimeServer({
    host: '0.0.0.0', port: 0, token: 'test-token-at-least-24-characters', allowInsecureLocal: true
  });
  try {
    const response = await fetch(`http://127.0.0.1:${server.address().port}/v1/analyze`, {
      method: 'POST', headers: { 'content-type': 'application/json' }, body: '{}'
    });
    assert.equal(response.status, 401);
  } finally {
    await new Promise((resolve) => server.close(resolve));
  }
});

test('HTTP runtime is observable, authenticated, read-only, and redacted', async () => {
  const directory = await mkdtemp(join(tmpdir(), 'mp-runtime-'));
  const telemetryPath = join(directory, 'events.jsonl');
  const token = 'test-token-at-least-24-characters';
  const server = await startRuntimeServer({ host: '127.0.0.1', port: 0, token, telemetryPath });
  const base = `http://127.0.0.1:${server.address().port}`;
  try {
    assert.equal((await fetch(`${base}/healthz`)).status, 200);
    assert.equal((await fetch(`${base}/readyz`)).status, 200);
    assert.equal((await fetch(`${base}/v1/analyze`, { method: 'POST', body: '{}' })).status, 401);
    const world = liftBenchmarkV11().worlds[0];
    const prompt = buildLiveToolPrompt(world, LIVE_TOOL_CONDITIONS.REQUIRED);
    const response = await fetch(`${base}/v1/analyze`, {
      method: 'POST', headers: { authorization: `Bearer ${token}`, 'content-type': 'application/json', 'x-request-id': 'request:test' },
      body: JSON.stringify(prompt.payload.tool_input)
    });
    assert.equal(response.status, 200);
    const receipt = await response.json();
    assert.equal(receipt.request_id, 'request:test');
    assert.equal(receipt.read_only, true);
    assert.equal(receipt.grants_protected_action_authority, false);
    assert.equal('answer' in receipt, false);
    const telemetry = await readFile(telemetryPath, 'utf8');
    assert.match(telemetry, /analysis_completed/);
    assert.doesNotMatch(telemetry, new RegExp(prompt.payload.tool_input.claims[0].text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')));
    assert.match(await (await fetch(`${base}/metrics`)).text(), /mp_engine_analysis_total 1/);
  } finally {
    await new Promise((resolve) => server.close(resolve));
    await rm(directory, { recursive: true, force: true });
  }
});
