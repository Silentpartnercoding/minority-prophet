import test from 'node:test';
import assert from 'node:assert/strict';
import { CAPABILITY_RESPONSE_SCHEMA, listPriceProxy, parseEvents } from './capability-tournament.js';

test('capability response requires one disposition per frozen proposition', () => {
  assert.equal(CAPABILITY_RESPONSE_SCHEMA.properties.answers.minItems, 16);
  assert.equal(CAPABILITY_RESPONSE_SCHEMA.properties.answers.maxItems, 16);
  assert.deepEqual(CAPABILITY_RESPONSE_SCHEMA.properties.answers.items.enum, ['A', 'B', 'ABSTAIN']);
});

test('tool telemetry counts one completed lifecycle record per call', () => {
  const item = { id: 'call-1', type: 'command_execution', command: 'python analyze.py' };
  const stdout = [
    JSON.stringify({ type: 'item.started', item }),
    JSON.stringify({ type: 'item.completed', item }),
    JSON.stringify({ type: 'turn.completed', usage: { input_tokens: 10, output_tokens: 2 } })
  ].join('\n');
  const parsed = parseEvents(stdout);
  assert.equal(parsed.tool_events.length, 1);
  assert.equal(parsed.tool_events[0].command, 'python analyze.py');
});

test('price proxy applies cached-token and long-context rates per trial', () => {
  assert.equal(listPriceProxy('gpt-5.6-sol', {
    input_tokens: 100_000,
    cached_input_tokens: 80_000,
    cache_write_input_tokens: 0,
    output_tokens: 10_000
  }), 0.44);
  assert.equal(listPriceProxy('gpt-5.6-luna', {
    input_tokens: 300_000,
    cached_input_tokens: 200_000,
    cache_write_input_tokens: 0,
    output_tokens: 10_000
  }), 0.33);
});
