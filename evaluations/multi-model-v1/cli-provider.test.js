import test from 'node:test';
import assert from 'node:assert/strict';
import { parseClaudeEnvelope, parseCodexEvents } from './cli-provider.js';

test('Codex CLI telemetry parser detects tool use', () => {
  const parsed = parseCodexEvents([
    JSON.stringify({ type:'thread.started',thread_id:'thread_1' }),
    JSON.stringify({ type:'item.completed',item:{ type:'command_execution' } }),
    JSON.stringify({ type:'turn.completed',usage:{ input_tokens:10,cached_input_tokens:3,output_tokens:4 } })
  ].join('\n'));
  assert.equal(parsed.provider_request_id, 'thread_1');
  assert.equal(parsed.usage.cached_tokens, 3);
  assert.equal(parsed.tool_event_count, 1);
});

test('Claude CLI envelope preserves structured output and telemetry', () => {
  const parsed = parseClaudeEnvelope(JSON.stringify({
    structured_output:{answer:'North'},session_id:'session_1',duration_ms:12,total_cost_usd:0,
    usage:{input_tokens:9,output_tokens:3,cache_read_input_tokens:2,server_tool_use:{web_search_requests:0,web_fetch_requests:0}},
    modelUsage:{'claude-haiku-helper':{canonicalModel:'claude-haiku-helper'},'claude-sonnet-x':{canonicalModel:'claude-sonnet-x'}},num_turns:1
  }), 'sonnet');
  assert.deepEqual(parsed.raw, {answer:'North'});
  assert.equal(parsed.model_version, 'claude-sonnet-x');
  assert.equal(parsed.agent_turns, 1);
  assert.equal(parsed.tool_event_count, 0);
});
