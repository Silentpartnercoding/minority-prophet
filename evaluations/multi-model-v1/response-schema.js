export const RESPONSE_SCHEMA = Object.freeze({
  type: 'object',
  required: ['answer', 'confidence', 'abstain', 'reasoning_summary', 'evidence_used', 'independence_assessment'],
  properties: {
    answer: { type: 'string' },
    confidence: { type: 'number', minimum: 0, maximum: 1 },
    abstain: { type: 'boolean' },
    reasoning_summary: { type: 'string' },
    evidence_used: { type: 'array', items: { type: 'string' } },
    independence_assessment: { type: 'string' }
  },
  additionalProperties: false
});
