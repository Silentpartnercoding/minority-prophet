import assert from "node:assert/strict";
import { access, readFile } from "node:fs/promises";
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
  assert.match(html, /GPT Terra A/);
  assert.match(html, /≈ \$0\.89/);
  assert.match(html, /Claude Opus A/);
  assert.match(html, /≈ \$3\.25/);
  assert.match(html, /nothing is combined/);
  assert.match(html, /Conformance result only/);
  assert.match(html, /not 128 independent trials/);
  assert.match(html, /no A→B→C lift is estimated/);
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
    access(new URL("../public/research/capability-tournament-v1-adversarial-review.md", import.meta.url)),
    access(new URL("../public/research/capability-tournament-v1-summary.json", import.meta.url)),
  ]);
});

test("server-renders the complete capability tournament with visible costs", async () => {
  const response = await render("/experiments/capability-tournament");
  assert.equal(response.status, 200);
  const html = await response.text();
  assert.match(html, /Capability Tournament v1 — Minority Prophet/);
  assert.match(html, /bounded conformance comparison/);
  assert.match(html, /not the Baseline → Provenance → Minority Prophet lift experiment/);
  assert.match(html, /OUR PUBLIC COMMITMENT/);
  assert.match(html, /Freeze protocols before execution/);
  assert.match(html, /Repeat before making broader claims/);
  assert.doesNotMatch(html, /CLEAN RUN/);
  assert.match(html, /READ THIS FIRST/);
  assert.match(html, /Eight cases/);
  assert.match(html, /Not 128 independent trials/);
  assert.match(html, /C is code, not an augmented model/);
  assert.match(html, /C minus B is not a Minority Prophet gain estimate/);
  assert.match(html, /complete and truthful by construction/);
  assert.match(html, /OBSERVED TELEMETRY BY LANE/);
  assert.match(html, /No combined score/);
  assert.match(html, /Every run stands alone/);
  assert.match(html, /≈ \$0\.89/);
  assert.match(html, /≈ \$1\.02/);
  assert.match(html, /≈ \$3\.25/);
  assert.match(html, /≈ \$6\.45/);
  assert.match(html, /No costs are added together/);
  assert.match(html, /not invoices/);
  assert.match(html, /WHY THIS JUNCTION MATTERS/);
  assert.match(html, /Agents will talk/);
  assert.match(html, /faster than humans can check/);
  assert.match(html, /OBSERVED ON ONE EIGHT-CASE PACKET/);
  assert.match(html, /Terra A took ≈ (?:<!-- -->)?19,520(?:<!-- -->)?× the elapsed time in this observed packet/);
  assert.match(html, /must not be linearly projected/);
  assert.doesNotMatch(html, /100,000|1,000,000|production capacity forecast/);
  assert.ok(html.indexOf("WHY THIS JUNCTION MATTERS") < html.indexOf("OBSERVED TELEMETRY BY LANE"));
  assert.match(html, /No production scaling claim is made/);
  assert.match(html, /Agent sends/);
  assert.match(html, /Evidence binds/);
  assert.match(html, /Rule checks/);
  assert.match(html, /Decision routes/);
  assert.match(html, /DESCRIPTIVE RESULT TABLE/);
  assert.match(html, /Observed scores, not stable ranks/);
  assert.doesNotMatch(html, /OVERALL LEADERBOARD/);
  assert.match(html, /Claude Opus 5/);
  assert.match(html, /Tools/);
  assert.match(html, /slower than C/);
  assert.match(html, /C did not receive the roots/);
  assert.match(html, /This is not the lift study/);
  assert.match(html, /cannot estimate Baseline → Provenance gain, Minority Prophet gain, H1, H2, or H3/);
  assert.match(html, /capability-tournament-v1-adversarial-review\.md/);
  assert.match(html, /capability-tournament-v1-summary\.json/);
});

test("machine-readable tournament boundary rejects unsupported lift claims", async () => {
  const summaryPath = new URL("../public/research/capability-tournament-v1-summary.json", import.meta.url);
  const summary = JSON.parse(await readFile(summaryPath, "utf8"));
  assert.equal(summary.study_class, "constructed_conformance");
  assert.equal(summary.unit_of_replication.cases, 8);
  assert.equal(summary.unit_of_replication.total_scored_dispositions, 128);
  assert.match(summary.unit_of_replication.independence_warning, /not 128 independent trials/);
  assert.match(summary.condition_boundary.C, /not the same model plus Minority Prophet/);
  assert.deepEqual(
    summary.unsupported_estimands.slice(0, 3),
    ["provenance gain", "Minority Prophet gain", "total epistemic gain"],
  );
  assert.equal(summary.results.length, 14);
});

test("public research artifacts preserve the conformance-only claim boundary", async () => {
  const [results, protocol, extension, adversarialReview] = await Promise.all([
    readFile(new URL("../public/research/capability-tournament-v1-results.md", import.meta.url), "utf8"),
    readFile(new URL("../public/research/capability-tournament-v1-protocol.md", import.meta.url), "utf8"),
    readFile(new URL("../public/research/capability-tournament-v1-claude-extension-results.md", import.meta.url), "utf8"),
    readFile(new URL("../public/research/capability-tournament-v1-adversarial-review.md", import.meta.url), "utf8"),
  ]);
  for (const artifact of [results, protocol, extension]) {
    assert.match(artifact, /constructed[^.\n]{0,80}conformance|conformance study|conformance test/i);
    assert.match(artifact, /not\s+(?:a\s+)?Minority\s+Prophet\s+lift\s+study|does not\s+estimate (?:provenance gain|epistemic lift)/i);
    assert.match(artifact, /not\s+128\s+(?:statistically\s+)?independent\s+trials|not\s+independent\s+trials/i);
  }
  assert.match(adversarialReview, /Wrong conditions for the lift hypothesis/);
  assert.match(adversarialReview, /Pseudoreplication/);
  assert.match(adversarialReview, /Required next study/);
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
