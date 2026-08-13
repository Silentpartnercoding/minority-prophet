import { setTimeout as delay } from 'node:timers/promises';

export async function fetchWithRetry(url, options, { retries = 3, baseDelayMs = 400 } = {}) {
  let lastError;
  for (let attempt = 0; attempt <= retries; attempt += 1) {
    try {
      const result = await fetch(url, options);
      if (result.ok) return result;
      lastError = new Error(`Provider HTTP ${result.status}: ${await result.text()}`);
      if (result.status < 429 && result.status < 500) throw lastError;
    } catch (error) { lastError = error; }
    if (attempt < retries) await delay(baseDelayMs * 2 ** attempt);
  }
  throw lastError;
}

export class OpenAICompatibleAdapter {
  constructor({ provider, model, baseUrl, apiKey, headers = {} }) { this.provider = provider; this.model = model; this.version = model; this.baseUrl = baseUrl.replace(/\/$/, ''); this.apiKey = apiKey; this.headers = headers; }
  async runModel(request) {
    const started = Date.now();
    const result = await fetchWithRetry(`${this.baseUrl}/chat/completions`, { method: 'POST', headers: { 'content-type': 'application/json', authorization: `Bearer ${this.apiKey}`, ...this.headers }, body: JSON.stringify({ model: this.model, messages: [{ role: 'system', content: request.systemPrompt }, ...request.messages], temperature: request.temperature, top_p: request.topP, seed: request.seed, max_tokens: request.maxTokens, response_format: { type: 'json_object' } }) });
    const body = await result.json();
    return { raw: body.choices?.[0]?.message?.content ?? '', provider_request_id: result.headers.get('x-request-id') ?? body.id ?? null, usage: { input_tokens: body.usage?.prompt_tokens ?? null, output_tokens: body.usage?.completion_tokens ?? null, cached_tokens: body.usage?.prompt_tokens_details?.cached_tokens ?? 0 }, cost_usd: null, execution_ms: Date.now() - started, model_version: body.model ?? this.model };
  }
}
