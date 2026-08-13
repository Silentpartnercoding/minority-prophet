import { validateParsedResponse } from './src/domain/validation.js';
function candidateJson(raw) {
  const text = typeof raw === 'string' ? raw : JSON.stringify(raw);
  const start = text.indexOf('{');
  const end = text.lastIndexOf('}');
  return start >= 0 && end > start ? text.slice(start, end + 1) : text;
}
export function parseModelResponse(raw) {
  try {
    const parsed = typeof raw === 'object' && raw !== null ? raw : JSON.parse(candidateJson(raw));
    validateParsedResponse(parsed);
    return { parse_success: true, parsed, parse_error: null };
  } catch (error) {
    return { parse_success: false, parsed: null, parse_error: error.message };
  }
}
