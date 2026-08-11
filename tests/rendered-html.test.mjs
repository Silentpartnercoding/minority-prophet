import assert from "node:assert/strict";
import { access } from "node:fs/promises";
import test from "node:test";

async function render() {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}`);
  const { default: worker } = await import(workerUrl.href);
  return worker.fetch(
    new Request("http://localhost/", { headers: { accept: "text/html" } }),
    { ASSETS: { fetch: async () => new Response("Not found", { status: 404 }) } },
    { waitUntil() {}, passThroughOnException() {} },
  );
}

test("server-renders the Minority Prophet research interface", async () => {
  const response = await render();
  assert.equal(response.status, 200);
  assert.match(response.headers.get("content-type") ?? "", /^text\/html\b/i);
  const html = await response.text();
  assert.match(html, /<title>Minority Prophet/);
  assert.match(html, /Truth is not/);
  assert.match(html, /THE CENTRAL BENCHMARK/);
  assert.match(html, /EPISTEMIC OBSERVATORY/);
  assert.match(html, /DEMONSTRATION WORLD/);
  assert.match(html, /Evidence is not/);
  assert.match(html, /Evidence assessment never grants authority/);
  assert.match(html, /Read the paper/);
  assert.match(html, /papers\/00-CURRENT-PAPER\.md/);
  assert.match(html, /CAPABILITY TOURNAMENT \/ CLEAN V1 RUN/);
  assert.match(html, /OVERALL LEADERBOARD/);
  assert.match(html, /C did not receive the roots/);
  assert.match(html, /Claude Opus 5/);
  assert.match(html, /Tools called/);
  assert.match(html, /tools were available, not necessarily used/);
  assert.match(html, /19,519× longer/);
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
