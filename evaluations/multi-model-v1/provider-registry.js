import { DeterministicAdapter } from './providers.js';
import { OpenAICompatibleAdapter, fetchWithRetry } from './http-provider.js';

export class AnthropicAdapter {
  constructor({ model, apiKey, baseUrl = 'https://api.anthropic.com/v1' }) { this.provider = 'anthropic'; this.model = model; this.version = model; this.baseUrl = baseUrl.replace(/\/$/, ''); this.apiKey = apiKey; }
  async runModel(request) {
    const started = Date.now();
    const result = await fetchWithRetry(`${this.baseUrl}/messages`, { method: 'POST', headers: { 'content-type': 'application/json', 'x-api-key': this.apiKey, 'anthropic-version': '2023-06-01' }, body: JSON.stringify({ model: this.model, system: request.systemPrompt, messages: request.messages, temperature: request.temperature, top_p: request.topP, max_tokens: request.maxTokens }) });
    const body = await result.json();
    return { raw: body.content?.filter((item) => item.type === 'text').map((item) => item.text).join('\n') ?? '', provider_request_id: result.headers.get('request-id') ?? body.id ?? null, usage: { input_tokens: body.usage?.input_tokens ?? null, output_tokens: body.usage?.output_tokens ?? null, cached_tokens: body.usage?.cache_read_input_tokens ?? 0 }, cost_usd: null, execution_ms: Date.now() - started, model_version: body.model ?? this.model };
  }
}

export class GoogleAdapter {
  constructor({ model, apiKey, baseUrl = 'https://generativelanguage.googleapis.com/v1beta' }) { this.provider = 'google'; this.model = model; this.version = model; this.apiKey = apiKey; this.baseUrl = baseUrl.replace(/\/$/, ''); }
  async runModel(request) {
    const result = await fetchWithRetry(`${this.baseUrl}/models/${this.model}:generateContent?key=${encodeURIComponent(this.apiKey)}`, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ systemInstruction: { parts: [{ text: request.systemPrompt }] }, contents: request.messages.map((message) => ({ role: message.role === 'assistant' ? 'model' : 'user', parts: [{ text: message.content }] })), generationConfig: { temperature: request.temperature, topP: request.topP, maxOutputTokens: request.maxTokens, responseMimeType: 'application/json' } }) });
    const body = await result.json();
    return { raw: body.candidates?.[0]?.content?.parts?.map((part) => part.text ?? '').join('') ?? '', provider_request_id: result.headers.get('x-request-id'), usage: { input_tokens: body.usageMetadata?.promptTokenCount ?? null, output_tokens: body.usageMetadata?.candidatesTokenCount ?? null, cached_tokens: body.usageMetadata?.cachedContentTokenCount ?? 0 }, cost_usd: null, model_version: body.modelVersion ?? this.model };
  }
}

export function createAdapter(config, env = process.env) {
  if (config.provider === 'deterministic') return new DeterministicAdapter(config.model);
  if (config.provider === 'anthropic') return new AnthropicAdapter({ model: config.model, apiKey: env.ANTHROPIC_API_KEY, baseUrl: config.base_url });
  if (config.provider === 'google') return new GoogleAdapter({ model: config.model, apiKey: env.GOOGLE_API_KEY, baseUrl: config.base_url });
  const defaults = { openai: ['https://api.openai.com/v1','OPENAI_API_KEY'], deepseek: ['https://api.deepseek.com/v1','DEEPSEEK_API_KEY'], openrouter: ['https://openrouter.ai/api/v1','OPENROUTER_API_KEY'], local: ['http://127.0.0.1:11434/v1','LOCAL_API_KEY'] };
  const selected = defaults[config.provider];
  if (!selected) throw new Error(`Unsupported provider: ${config.provider}`);
  return new OpenAICompatibleAdapter({ provider: config.provider, model: config.model, baseUrl: config.base_url ?? selected[0], apiKey: env[selected[1]] ?? '' });
}
