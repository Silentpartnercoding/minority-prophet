#!/usr/bin/env node
import { appendFileSync, realpathSync } from 'node:fs';
import { performance } from 'node:perf_hooks';
import { fileURLToPath } from 'node:url';
import { executeMinorityProphetTool, MP_TOOL_CONTRACT_HASH, MP_TOOL_DEFINITION } from './mp-tool-v2.js';
import { hashObject } from './src/lib/hash.js';

const telemetryPath = process.env.MP_MCP_TELEMETRY_PATH ?? '';

function record(event) {
  if (!telemetryPath) return;
  appendFileSync(telemetryPath, `${JSON.stringify({ timestamp: new Date().toISOString(), ...event })}\n`, { encoding: 'utf8', mode: 0o600 });
}

function result(id, value) {
  return { jsonrpc: '2.0', id, result: value };
}

function error(id, code, message) {
  return { jsonrpc: '2.0', id, error: { code, message } };
}

export function handleMcpRequest(request) {
  const id = request?.id;
  if (request?.method === 'initialize') {
    record({ event: 'initialize' });
    return result(id, {
      protocolVersion: request.params?.protocolVersion ?? '2025-06-18',
      capabilities: { tools: {} },
      serverInfo: { name: 'minority-prophet', version: 'epistemic-lift-live-tool-v1' }
    });
  }
  if (request?.method === 'tools/list') {
    record({ event: 'tools_list' });
    return result(id, { tools: [{
      name: MP_TOOL_DEFINITION.name,
      description: MP_TOOL_DEFINITION.description,
      inputSchema: MP_TOOL_DEFINITION.input_schema,
      annotations: { readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: false }
    }] });
  }
  if (request?.method === 'tools/call') {
    const name = request.params?.name;
    if (name !== MP_TOOL_DEFINITION.name) return error(id, -32602, `Unknown tool: ${name}`);
    const input = request.params?.arguments;
    const started = performance.now();
    try {
      const output = executeMinorityProphetTool(input);
      const executionMs = performance.now() - started;
      const receipt = {
        tool_name: MP_TOOL_DEFINITION.name,
        tool_version: output.engine_version,
        read_only: true,
        input_hash: hashObject(input),
        contract_hash: MP_TOOL_CONTRACT_HASH,
        output
      };
      record({
        event: 'tool_call',
        success: true,
        input_hash: receipt.input_hash,
        output_hash: hashObject(output),
        execution_ms: executionMs
      });
      return result(id, {
        content: [{ type: 'text', text: JSON.stringify(receipt) }],
        structuredContent: receipt,
        isError: false
      });
    } catch (toolError) {
      const executionMs = performance.now() - started;
      record({ event: 'tool_call', success: false, execution_ms: executionMs, error: toolError.message });
      return result(id, {
        content: [{ type: 'text', text: `Minority Prophet input rejected: ${toolError.message}` }],
        isError: true
      });
    }
  }
  if (id === undefined || id === null) return null;
  return error(id, -32601, `Method not found: ${request?.method ?? ''}`);
}

function send(message) {
  if (!message) return;
  process.stdout.write(`${JSON.stringify(message)}\n`);
}

export function startMcpStdio() {
  let pending = '';
  process.stdin.setEncoding('utf8');
  process.stdin.on('data', (chunk) => {
    pending += chunk;
    const lines = pending.split(/\r?\n/);
    pending = lines.pop() ?? '';
    for (const line of lines) {
      if (!line.trim()) continue;
      try { send(handleMcpRequest(JSON.parse(line))); }
      catch (requestError) { send(error(null, -32700, requestError.message)); }
    }
  });
}

function invokedDirectly() {
  if (!process.argv[1]) return false;
  try { return realpathSync(fileURLToPath(import.meta.url)) === realpathSync(process.argv[1]); }
  catch { return false; }
}

if (invokedDirectly()) startMcpStdio();
