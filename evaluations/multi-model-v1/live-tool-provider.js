import { mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseClaudeEnvelope, parseCodexEvents, runProcess, userContent } from './cli-provider.js';

const PROJECT_ROOT = dirname(fileURLToPath(import.meta.url));
const SERVER_PATH = join(PROJECT_ROOT, 'mp-mcp-server.js');
const ALLOWED_MCP_TOOL = 'analyze_evidence_structure';

async function readTelemetry(path) {
  try {
    const value = await readFile(path, 'utf8');
    return value.split(/\r?\n/).filter(Boolean).map((line) => JSON.parse(line));
  } catch (error) {
    if (error.code === 'ENOENT') return [];
    throw error;
  }
}

function validateTelemetry(events, request) {
  const calls = events.filter((event) => event.event === 'tool_call');
  const successful = calls.filter((event) => event.success === true);
  if (request.requireToolCall && successful.length !== 1) {
    const eventSummary = events.map((event) => `${event.event}:${event.success ?? 'n/a'}${event.error ? `:${event.error}` : ''}`).join(', ') || 'none';
    throw new Error(`Expected exactly one successful Minority Prophet call; observed ${successful.length}; MCP events: ${eventSummary}`);
  }
  if (successful.length > 1) throw new Error(`Minority Prophet was called more than once (${successful.length})`);
  if (successful.length === 1 && successful[0].input_hash !== request.expectedToolInputHash) {
    throw new Error(`Minority Prophet input hash mismatch: ${successful[0].input_hash}`);
  }
  return {
    mcp_initialize_count: events.filter((event) => event.event === 'initialize').length,
    mcp_tools_list_count: events.filter((event) => event.event === 'tools_list').length,
    mp_tool_call_count: calls.length,
    mp_tool_success_count: successful.length,
    mp_tool_execution_ms: successful.reduce((sum, event) => sum + event.execution_ms, 0),
    mp_tool_input_hash: successful[0]?.input_hash ?? null,
    mp_tool_output_hash: successful[0]?.output_hash ?? null,
    mcp_events: events
  };
}

function quotedToml(value) {
  return JSON.stringify(value);
}

export class CodexLiveMcpAdapter {
  constructor({ model = 'gpt-5.6-sol', effort = 'medium', timeoutMs = 240_000 } = {}) {
    this.provider = 'openai-codex-cli-live-mcp';
    this.model = model;
    this.version = model;
    this.effort = effort;
    this.timeoutMs = timeoutMs;
  }
  async runModel(request) {
    const directory = await mkdtemp(join(tmpdir(), 'mp-codex-live-'));
    const outputPath = join(directory, 'final.json');
    const telemetryPath = join(directory, 'mcp-telemetry.jsonl');
    const started = Date.now();
    try {
      const prompt = `${request.systemPrompt}\n\n${userContent(request)}\n\nOnly the provisioned Minority Prophet MCP tool is permitted. Do not use shell commands, files, network access, web search, or any other tool. Return only the requested final JSON object after any permitted tool call.`;
      const args = [
        'exec', '--ignore-user-config', '--ignore-rules', '--skip-git-repo-check', '--sandbox', 'read-only', '--cd', directory,
        '--model', this.model, '-c', `model_reasoning_effort=${quotedToml(this.effort)}`,
        '-c', `mcp_servers.minority_prophet.command=${quotedToml(process.execPath)}`,
        '-c', `mcp_servers.minority_prophet.args=[${quotedToml(SERVER_PATH)}]`,
        '-c', `mcp_servers.minority_prophet.env={MP_MCP_TELEMETRY_PATH=${quotedToml(telemetryPath)}}`,
        '--output-last-message', outputPath, '--json', '-'
      ];
      const { stdout } = await runProcess({ command: 'codex', args, input: prompt, cwd: directory, timeoutMs: this.timeoutMs });
      const elapsed = Date.now() - started;
      const metadata = parseCodexEvents(stdout);
      const disallowed = metadata.tool_events.filter((event) => event.type !== 'mcp_tool_call' || event.server !== 'minority_prophet' || event.tool !== ALLOWED_MCP_TOOL);
      if (disallowed.length) throw new Error(`Codex emitted ${disallowed.length} disallowed tool event(s)`);
      const toolTelemetry = validateTelemetry(await readTelemetry(telemetryPath), request);
      const finalText = await readFile(outputPath, 'utf8');
      let raw = finalText;
      try { raw = JSON.parse(finalText); } catch {}
      return { ...metadata, ...toolTelemetry, raw, cost_usd: null, execution_ms: elapsed, model_version: this.model };
    } finally {
      await rm(directory, { recursive: true, force: true });
    }
  }
}

export class ClaudeLiveMcpAdapter {
  constructor({ model = 'sonnet', effort = 'medium', timeoutMs = 240_000 } = {}) {
    this.provider = 'anthropic-claude-cli-live-mcp';
    this.model = model;
    this.version = model;
    this.effort = effort;
    this.timeoutMs = timeoutMs;
  }
  async runModel(request) {
    const directory = await mkdtemp(join(tmpdir(), 'mp-claude-live-'));
    const telemetryPath = join(directory, 'mcp-telemetry.jsonl');
    const mcpPath = join(directory, 'mcp.json');
    await writeFile(mcpPath, `${JSON.stringify({ mcpServers: { minority_prophet: { type: 'stdio', command: process.execPath, args: [SERVER_PATH], env: { MP_MCP_TELEMETRY_PATH: telemetryPath } } } })}\n`);
    const started = Date.now();
    try {
      const args = [
        '--print', '--model', this.model, '--effort', this.effort,
        '--tools', '', '--allowedTools', 'mcp__minority_prophet__analyze_evidence_structure',
        '--mcp-config', mcpPath, '--strict-mcp-config', '--setting-sources', '', '--disable-slash-commands',
        '--no-session-persistence', '--permission-mode', 'dontAsk', '--output-format', 'json',
        '--system-prompt', `${request.systemPrompt} Only the provisioned Minority Prophet MCP tool is permitted. Do not use files, shell, network, web search, or any other tool.`
      ];
      const { stdout } = await runProcess({ command: 'claude', args, input: userContent(request), cwd: directory, timeoutMs: this.timeoutMs });
      const elapsed = Date.now() - started;
      const result = parseClaudeEnvelope(stdout, this.model);
      if (result.tool_event_count) throw new Error(`Claude reported ${result.tool_event_count} disallowed server-tool request(s)`);
      const toolTelemetry = validateTelemetry(await readTelemetry(telemetryPath), request);
      return { ...result, ...toolTelemetry, execution_ms: elapsed, provider_execution_ms: result.execution_ms, model_version: result.model_version ?? this.model };
    } finally {
      await rm(directory, { recursive: true, force: true });
    }
  }
}
