import assert from "node:assert/strict";
import { access } from "node:fs/promises";
import test from "node:test";

async function render(path = "/") {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}`);
  const { default: worker } = await import(workerUrl.href);
  return worker.fetch(
    new Request(`http://localhost${path}`, { headers: { accept: "text/html" } }),
    { ASSETS: { fetch: async () => new Response("Not found", { status: 404 }) } },
    { waitUntil() {}, passThroughOnException() {} },
  );
}

test("server-renders a concise landing page with both experiment previews", async () => {
  const response = await render();
  assert.equal(response.status, 200);
  assert.match(response.headers.get("content-type") ?? "", /^text\/html\b/i);
  const html = await response.text();
  assert.match(html, /<title>Minority Prophet/);
  assert.match(html, /Truth is not/);
  assert.match(html, /THE CENTRAL QUESTION/);
  assert.match(html, /LIVE EXPERIMENTS/);
  assert.match(html, /EPISTEMIC OBSERVATORY/);
  assert.match(html, /DEMONSTRATION WORLD/);
  assert.match(html, /Evidence is not/);
  assert.match(html, /Assessment never grants authority/);
  assert.match(html, /Read the paper/);
  assert.match(html, /papers\/00-CURRENT-PAPER\.md/);
  assert.match(html, /CAPABILITY TOURNAMENT V1/);
  assert.match(html, /≈ \$28\.30/);
  assert.match(html, /not an invoice/);
  assert.match(html, /model calls in demo/);
  assert.match(html, /href="\/experiments\/capability-tournament"/);
  assert.match(html, /href="\/experiments\/epistemic-observatory"/);
  assert.doesNotMatch(html, /OVERALL LEADERBOARD/);
  assert.doesNotMatch(html, /Claude extension pending/);
  assert.doesNotMatch(html, /Starter Project|react-loading-skeleton/i);

  await Promise.all([
    access(new URL("../public/research/capability-tournament-v1-results.md", import.meta.url)),
    access(new URL("../public/research/capability-tournament-v1-protocol.md", import.meta.url)),
    access(new URL("../public/research/capability-tournament-v1-claude-extension.md", import.meta.url)),
    access(new URL("../public/research/capability-tournament-v1-claude-extension-v1.1-amendment.md", import.meta.url)),
    access(new URL("../public/research/capability-tournament-v1-claude-extension-results.md", import.meta.url)),
    access(new URL("../public/research/capability-tournament-v1-claude-extension-summary.json", import.meta.url)),
  ]);
});

test("server-renders the complete capability tournament with visible costs", async () => {
  const response = await render("/experiments/capability-tournament");
  assert.equal(response.status, 200);
  const html = await response.text();
  assert.match(html, /Capability Tournament v1 — Minority Prophet/);
  assert.match(html, /COST VISIBILITY/);
  assert.match(html, /≈ \$7\.75/);
  assert.match(html, /≈ \$20\.55/);
  assert.match(html, /≈ \$28\.30/);
  assert.match(html, /not an invoice or subscription bill/);
  assert.match(html, /OVERALL LEADERBOARD/);
  assert.match(html, /Claude Opus 5/);
  assert.match(html, /Tools/);
  assert.match(html, /19,519× longer/);
  assert.match(html, /C did not receive the roots/);
});

test("server-renders the synthetic observatory on its own page", async () => {
  const response = await render("/experiments/epistemic-observatory");
  assert.equal(response.status, 200);
  const html = await response.text();
  assert.match(html, /Epistemic Observatory — Minority Prophet/);
  assert.match(html, /Three witnesses/);
  assert.match(html, /Ninety-five echoes/);
  assert.match(html, /LINEAGE INSPECTOR/);
  assert.match(html, /\$0 model calls in this browser demo/);
  assert.match(html, /synthetic teaching instrument/);
  assert.match(html, /No LLM or paid model is called by this page/);
});
