import test from 'node:test';
import assert from 'node:assert/strict';
import { parseClaudeStream } from './capability-tournament-claude.js';

test('parses structured Claude result and audits tool requests', () => {
  const stdout = [
    JSON.stringify({ type: 'assistant', message: { content: [{ type: 'tool_use', name: 'Bash', input: { command: 'python solve.py' } }] } }),
    JSON.stringify({ type: 'assistant', message: { content: [{ type: 'tool_use', name: 'StructuredOutput', input: { answers: Array(16).fill('A') } }] } }),
    JSON.stringify({
      type: 'result', is_error: false, structured_output: { answers: Array(16).fill('A'), method_summary: 'computed', tools_used: ['Bash'] },
      usage: { input_tokens: 10, output_tokens: 5, cache_read_input_tokens: 2, cache_creation_input_tokens: 3 },
      modelUsage: { 'claude-sonnet-x': { canonicalModel: 'claude-sonnet-x' } }, total_cost_usd: 0.01, duration_ms: 42, session_id: 'session'
    })
  ].join('\n');
  const result = parseClaudeStream(stdout, 'sonnet');
  assert.equal(result.answers.length, 16);
  assert.equal(result.tool_events.length, 1);
  assert.equal(result.tool_events[0].type, 'Bash');
  assert.equal(result.model_version, 'claude-sonnet-x');
  assert.equal(result.provider_cost_estimate_usd, 0.01);
});
