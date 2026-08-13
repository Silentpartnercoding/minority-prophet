#!/usr/bin/env node
import { ClaudeCliAdapter, CodexCliAdapter } from './cli-provider.js';

const request = {
  condition: 'COMPATIBILITY_PROBE',
  systemPrompt: 'Return a JSON object matching the supplied schema.',
  messages: [{ role: 'user', content: JSON.stringify({ instruction: 'Return answer OK, confidence 1, abstain false, a brief summary, empty evidence_used, and a brief independence_assessment.' }) }],
  tools: [],
  temperature: 0,
  topP: 1,
  seed: 1,
  maxTokens: 100
};

const adapters = [
  ...['gpt-5.6-sol', 'gpt-5.6-terra', 'gpt-5.6-luna'].map((model) => new CodexCliAdapter({ model, effort: 'medium' })),
  ...['opus', 'sonnet', 'haiku'].map((model) => new ClaudeCliAdapter({ model, effort: 'medium' }))
];

const results = [];
for (const adapter of adapters) {
  const started = Date.now();
  try {
    const result = await adapter.runModel(request);
    results.push({ provider: adapter.provider, requested_model: adapter.model, resolved_model: result.model_version, callable: true, tool_events: result.tool_event_count, execution_ms: result.execution_ms ?? Date.now() - started });
  } catch (error) {
    results.push({ provider: adapter.provider, requested_model: adapter.model, callable: false, error: error.message, execution_ms: Date.now() - started });
  }
}
console.log(JSON.stringify(results, null, 2));
