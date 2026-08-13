export const esc = (value) => String(value ?? '').replace(/[&<>\"]/g, (character) => ({ '&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;' })[character]);
export const pct = (value) => `${Math.round((value ?? 0) * 100)}%`;
export const bar = (value, signal = false) => `<div class="bar ${signal ? 'signal' : ''}"><i style="width:${Math.max(0, Math.min(100, (value ?? 0) * 100))}%"></i></div>`;
export function layout(title, body, namespace = 'VERIFIED') {
  return `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>${esc(title)} · Minority Prophet</title><link rel="stylesheet" href="/styles.css"></head><body><header><a class="brand" href="/leaderboard">MINORITY PROPHET</a><nav><a href="/leaderboard">Leaderboard</a><a href="/methodology">Methodology</a><a href="/admin">Evaluation console</a></nav></header><main>${body}</main><footer>Truth is not popularity. <span class="tag">${esc(namespace)}</span></footer></body></html>`;
}
