import { json } from './http-utils.js';
import { publishLocalDemo, runLocalDemo } from './operations.js';

export async function handleAdminRoute(request, response, url, { adminToken, statePath }) {
  if (request.method !== 'POST' || !url.pathname.startsWith('/api/admin/')) return false;
  if (!adminToken || request.headers.authorization !== `Bearer ${adminToken}`) { json(response, 401, { error: 'unauthorized' }); return true; }
  if (url.pathname === '/api/admin/start-demo') { const result = await runLocalDemo({ statePath }); json(response, 201, { run: result.run, verification: result.verification }); return true; }
  if (url.pathname === '/api/admin/publish-demo') { json(response, 201, await publishLocalDemo({ statePath })); return true; }
  json(response, 404, { error: 'unknown_admin_operation' }); return true;
}
