import { leaderboardData, modelDetail, rankLeaderboard } from './leaderboard.js';
import { adminPage, methodologyPage, runPage } from './info-pages.js';
import { modelPage } from './model-page.js';
import { CSS } from './styles.js';
import { leaderboardPage } from './web-render.js';
import { html, json, namespaceFor, send } from './http-utils.js';

export function handlePublicRoute(request, response, url, store) {
  const namespace = namespaceFor(url);
  if (url.pathname === '/styles.css') { send(response, 200, 'text/css', CSS); return true; }
  if (url.pathname === '/' || url.pathname.startsWith('/leaderboard')) {
    const view = url.pathname.endsWith('/baseline') ? 'baseline' : url.pathname.endsWith('/provenance') ? 'provenance' : url.pathname.endsWith('/lift') ? 'lift' : 'minority-prophet';
    html(response, 200, leaderboardPage(rankLeaderboard(leaderboardData(store, namespace), view), namespace)); return true;
  }
  if (url.pathname === '/methodology') { html(response, 200, methodologyPage()); return true; }
  if (url.pathname === '/admin') { html(response, 200, adminPage(store.all('benchmark_runs'))); return true; }
  if (url.pathname.startsWith('/models/')) {
    const modelSlug = decodeURIComponent(url.pathname.slice('/models/'.length));
    const model = store.find('models', (item) => item.slug === modelSlug);
    html(response, model ? 200 : 404, modelPage(model ? modelDetail(store, model.provider, model.name, namespace) : null, namespace)); return true;
  }
  if (url.pathname.startsWith('/runs/')) {
    const id = decodeURIComponent(url.pathname.slice('/runs/'.length));
    const run = store.find('benchmark_runs', (item) => item.id === id);
    html(response, run ? 200 : 404, runPage(run, store.find('verification_records', (item) => item.run_id === id))); return true;
  }
  if (url.pathname === '/api/leaderboard') { json(response, 200, rankLeaderboard(leaderboardData(store, 'VERIFIED'))); return true; }
  if (url.pathname === '/api/demo/leaderboard') { json(response, 200, rankLeaderboard(leaderboardData(store, 'DEMO'))); return true; }
  if (url.pathname === '/api/models') { json(response, 200, leaderboardData(store, 'VERIFIED').map(({ provider,model,model_version,benchmark_version,last_evaluated }) => ({ provider,model,model_version,benchmark_version,last_evaluated }))); return true; }
  if (url.pathname.startsWith('/api/runs/')) { const item = store.find('benchmark_runs', (run) => run.id === decodeURIComponent(url.pathname.slice('/api/runs/'.length))); json(response, item ? 200 : 404, item ?? { error: 'not_found' }); return true; }
  if (url.pathname.startsWith('/api/benchmark/')) { const item = store.find('benchmark_versions', (entry) => entry.id === decodeURIComponent(url.pathname.slice('/api/benchmark/'.length))); json(response, item ? 200 : 404, item ?? { error: 'not_found' }); return true; }
  return false;
}
