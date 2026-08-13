import { METHODOLOGY } from './artifacts.js';
import { esc, layout } from './web-base.js';

export function methodologyPage() {
  const body = `<section class="hero"><div class="eyebrow">Methodology</div><h1>Measure the lift.</h1></section><div class="grid"><div class="card"><h2>Baseline</h2><p>The model receives the claims.</p></div><div class="card"><h2>Provenance</h2><p>The model receives claims plus where they came from.</p></div><div class="card"><h2>Minority Prophet</h2><p>The model receives claims, provenance, and evidence-independence analysis.</p></div></div><p>The difference between Baseline and Provenance measures the value of provenance visibility. The difference between Provenance and Minority Prophet measures Minority Prophet's value-add. This distinction is fundamental.</p><h2>MP Score</h2><p>${esc(METHODOLOGY.mp_score.formula)}. Component scores are always visible.</p><pre>${esc(JSON.stringify(METHODOLOGY,null,2))}</pre>`;
  return layout('Methodology', body);
}

export function adminPage(runs) {
  const rows = runs.map((run) => `<tr><td><a href="/runs/${esc(run.id)}">${esc(run.id)}</a></td><td>${esc(run.status)}</td><td>${run.completed_trials}/${run.expected_trials}</td><td>$${Number(run.cost_telemetry?.provider_reported_cost_usd ?? run.cost_telemetry?.api_cost_usd ?? 0).toFixed(4)} reported estimate</td><td>${esc(run.namespace)}</td></tr>`).join('');
  return layout('Evaluation console', `<section class="hero"><div class="eyebrow">Local operator view</div><h1>Evaluation console</h1><p class="subhead">Run state, trial progress, cost telemetry, verification, and publication status. Scores are immutable.</p></section><table><tr><th>Run</th><th>Status</th><th>Progress</th><th>Cost</th><th>Namespace</th></tr>${rows}</table><p class="muted">Start, pause, resume, verify, invalidate, and publish operations use authenticated local admin API/CLI commands. Individual scores cannot be edited.</p>`);
}

export function runPage(run, verification) {
  if (!run) return layout('Run not found','<h1>Run not found.</h1>');
  return layout(`Run ${run.id}`, `<section class="hero"><div class="eyebrow">${esc(run.namespace)} · ${esc(run.status)}</div><h1>Run record</h1></section><pre>${esc(JSON.stringify({ ...run, verification },null,2))}</pre>`, run.namespace);
}
