import { createServer } from 'node:http';
import { handleAdminRoute } from './admin-routes.js';
import { json } from './http-utils.js';
import { openStore } from './operations.js';
import { handlePublicRoute } from './public-routes.js';
import { handleProvenanceServiceRoute } from './provenance-service.js';

export async function startServer({
  port = 4173,
  statePath,
  adminToken = process.env.MP_ADMIN_TOKEN,
  provenanceToken = process.env.MP_PROVENANCE_TOKEN
} = {}) {
  const store = await openStore(statePath);
  const server = createServer(async (request, response) => {
    try {
      const url = new URL(request.url, `http://${request.headers.host ?? 'localhost'}`);
      if (await handleProvenanceServiceRoute(request, response, url, { provenanceToken })) return;
      if (handlePublicRoute(request, response, url, store)) return;
      if (await handleAdminRoute(request, response, url, { adminToken, statePath })) return;
      json(response, 404, { error: 'not_found' });
    } catch (error) { json(response, 500, { error: 'internal_error', message: error.message }); }
  });
  await new Promise((resolve) => server.listen(port, '127.0.0.1', resolve));
  return server;
}
