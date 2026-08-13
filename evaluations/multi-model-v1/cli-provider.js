import { spawn } from 'node:child_process';
import { mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { RESPONSE_SCHEMA } from './prompts.js';

const TOOL_EVENT_TYPES = new Set(['command_execution', 'file_change', 'mcp_tool_call', 'web_search']);

export function runProcess({ command, args, input, cwd, timeoutMs }) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, { cwd, env: process.env, stdio: ['pipe', 'pipe', 'pipe'] });
    let stdout = '';
    let stderr = '';
    const timer = setTimeout(() => {
      child.kill('SIGTERM');
      reject(new Error(`${command} exceeded ${timeoutMs}ms`));
    }, timeoutMs);
    child.stdout.setEncoding('utf8');
    child.stderr.setEncoding('utf8');
    child.stdout.on('data', (chunk) => { stdout += chunk; });
    child.stderr.on('data', (chunk) => { stderr += chunk; });
    child.on('error', (error) => { clearTimeout(timer); reject(error); });
    child.on('close', (code) => {
      clearTimeout(timer);
      if (code !== 0) {
        const diagnostic = stderr.trim() || stdout.trim();
        reject(new Error(`${command} exited ${code}: ${diagnostic.slice(-1200)}`));
      }
      else resolve({ stdout, stderr });
    });
    child.stdin.end(input);
  });
}

function parseJsonLines(value) {
  return value.split(/\r?\n/).filter(Boolean).flatMap((line) => {
    try { return [JSON.parse(line)]; } catch { return []; }
  });
}

export function parseCodexEvents(stdout) {
  const events = parseJsonLines(stdout);
  const started = events.find((event) => event.type === 'thread.started');
  const completed = [...events].reverse().find((event) => event.type === 'turn.completed');
  const toolEvents = events.filter((event) => TOOL_EVENT_TYPES.has(event.item?.type));
  return {
    provider_request_id: started?.thread_id ?? null,
    usage: {
      input_tokens: completed?.usage?.input_tokens ?? null,
      output_tokens: completed?.usage?.output_tokens ?? null,
      cached_tokens: completed?.usage?.cached_input_tokens ?? 0
    },
    tool_event_count: toolEvents.length,
    tool_events: toolEvents.map((event) => event.item)
  };
}

export function parseClaudeEnvelope(stdout, requestedModel = '') {
  const envelope = JSON.parse(stdout);
  const modelEntries = Object.entries(envelope.modelUsage ?? {});
  const requested = requestedModel.toLowerCase();
  const selected = modelEntries.find(([key, value]) => key.toLowerCase().includes(requested) || String(value.canonicalModel ?? '').toLowerCase().includes(requested)) ?? modelEntries.at(-1);
  const modelVersion = selected?.[1]?.canonicalModel ?? selected?.[0] ?? null;
  const serverToolUse = envelope.usage?.server_tool_use ?? {};
  return {
    raw: envelope.structured_output ?? envelope.result ?? '',
    provider_request_id: envelope.session_id ?? null,
    usage: {
      input_tokens: envelope.usage?.input_tokens ?? null,
      output_tokens: envelope.usage?.output_tokens ?? null,
      cached_tokens: envelope.usage?.cache_read_input_tokens ?? 0,
      cache_creation_tokens: envelope.usage?.cache_creation_input_tokens ?? 0
    },
    cost_usd: Number.isFinite(envelope.total_cost_usd) ? envelope.total_cost_usd : null,
    execution_ms: envelope.duration_ms ?? null,
    model_version: modelVersion,
    agent_turns: envelope.num_turns ?? null,
    tool_event_count: (serverToolUse.web_search_requests ?? 0) + (serverToolUse.web_fetch_requests ?? 0)
  };
}

export function userContent(request) {
  return request.messages.map((message) => `${message.role.toUpperCase()}:\n${message.content}`).join('\n\n');
}

export class CodexCliAdapter {
  constructor({ model = 'gpt-5.6-sol', effort = 'medium', timeoutMs = 180_000, rawCapture = false } = {}) {
    this.provider = 'openai-codex-cli';
    this.model = model;
    this.version = model;
    this.effort = effort;
    this.timeoutMs = timeoutMs;
    this.rawCapture = rawCapture;
  }
  async runModel(request) {
    const directory = await mkdtemp(join(tmpdir(), 'mp-codex-'));
    const schemaPath = join(directory, 'response-schema.json');
    const outputPath = join(directory, 'final.json');
    await writeFile(schemaPath, `${JSON.stringify(RESPONSE_SCHEMA)}\n`);
    const started = Date.now();
    try {
      const prompt = `${request.systemPrompt}\n\n${userContent(request)}\n\nClosed-world rule: do not use shell commands, files, network access, web search, MCP, or any other tools. Return only the requested JSON object.`;
      const args = ['exec', '--ephemeral', '--ignore-user-config', '--ignore-rules', '--skip-git-repo-check', '--sandbox', 'read-only', '--cd', directory, '--model', this.model, '-c', `model_reasoning_effort=\"${this.effort}\"`];
      if (!this.rawCapture) args.push('--output-schema', schemaPath);
      args.push('--output-last-message', outputPath, '--json', '-');
      const { stdout } = await runProcess({
        command: 'codex',
        args,
        input: prompt,
        cwd: directory,
        timeoutMs: this.timeoutMs
      });
      const metadata = parseCodexEvents(stdout);
      if (metadata.tool_event_count) throw new Error(`Closed-world violation: Codex emitted ${metadata.tool_event_count} tool event(s)`);
      const finalText = await readFile(outputPath, 'utf8');
      let raw = finalText;
      try { raw = JSON.parse(finalText); } catch {}
      return { ...metadata, raw, cost_usd: null, execution_ms: Date.now() - started, model_version: this.model };
    } finally {
      await rm(directory, { recursive: true, force: true });
    }
  }
}

export class ClaudeCliAdapter {
  constructor({ model = 'sonnet', effort = 'medium', timeoutMs = 180_000, rawCapture = false } = {}) {
    this.provider = 'anthropic-claude-cli';
    this.model = model;
    this.version = model;
    this.effort = effort;
    this.timeoutMs = timeoutMs;
    this.rawCapture = rawCapture;
  }
  async runModel(request) {
    const directory = await mkdtemp(join(tmpdir(), 'mp-claude-'));
    const started = Date.now();
    try {
      const args = ['--print', '--model', this.model, '--effort', this.effort, '--safe-mode', '--tools', '', '--no-session-persistence', '--permission-mode', 'dontAsk', '--output-format', 'json'];
      if (!this.rawCapture) args.push('--json-schema', JSON.stringify(RESPONSE_SCHEMA));
      args.push('--system-prompt', `${request.systemPrompt} Closed-world rule: do not use files, network access, web search, MCP, or any other tools.`);
      const { stdout } = await runProcess({
        command: 'claude',
        args,
        input: userContent(request),
        cwd: directory,
        timeoutMs: this.timeoutMs
      });
      const result = parseClaudeEnvelope(stdout, this.model);
      if (result.tool_event_count) throw new Error(`Closed-world violation: Claude reported ${result.tool_event_count} server tool request(s)`);
      return { ...result, execution_ms: result.execution_ms ?? Date.now() - started, model_version: result.model_version ?? this.model };
    } finally {
      await rm(directory, { recursive: true, force: true });
    }
  }
}
