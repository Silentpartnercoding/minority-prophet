export function send(response, status, type, body) { response.writeHead(status, { 'content-type': `${type}; charset=utf-8`, 'cache-control': 'no-store', 'x-content-type-options': 'nosniff' }); response.end(body); }
export const json = (response, status, value) => send(response, status, 'application/json', JSON.stringify(value, null, 2));
export const html = (response, status, value) => send(response, status, 'text/html', value);
export const namespaceFor = (url) => url.searchParams.get('namespace') === 'DEMO' ? 'DEMO' : 'VERIFIED';
