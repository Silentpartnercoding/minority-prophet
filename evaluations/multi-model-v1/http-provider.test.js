import assert from 'node:assert/strict';
import test from 'node:test';
import { OpenAICompatibleAdapter } from './http-provider.js';

test('OpenAI-compatible adapter merges request controls and records provider cost', async () => {
  const originalFetch = globalThis.fetch;
  let requestBody;
  globalThis.fetch = async (_url, options) => {
    requestBody = JSON.parse(options.body);
    return new Response(JSON.stringify({
      id: 'generation-test',
      model: 'vendor/model-version',
      choices: [{ message: { content: '{"answer":"North"}' } }],
      usage: { prompt_tokens: 10, completion_tokens: 4, cost: 0.00125 }
    }), { status: 200, headers: { 'x-request-id': 'request-test' } });
  };

  try {
    const adapter = new OpenAICompatibleAdapter({
      provider: 'openrouter',
      model: 'vendor/model',
      baseUrl: 'https://example.test/v1',
      apiKey: 'test-key',
      requestBody: { reasoning: { enabled: false, exclude: true } }
    });
    const result = await adapter.runModel({
      systemPrompt: 'Return JSON.', messages: [], temperature: 0, topP: 1, seed: 7, maxTokens: 500
    });
    assert.deepEqual(requestBody.reasoning, { enabled: false, exclude: true });
    assert.equal(result.cost_usd, 0.00125);
    assert.equal(result.provider_request_id, 'request-test');
  } finally {
    globalThis.fetch = originalFetch;
  }
});
