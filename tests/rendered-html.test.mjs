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

test("server-renders a failure-first landing page with the canonical fixture and separate studies", async () => {
  const response = await render();
  assert.equal(response.status, 200);
  assert.match(response.headers.get("content-type") ?? "", /^text\/html\b/i);
  const html = await response.text();
  assert.match(html, /<title>Minority Prophet/);
  assert.match(html, /An echo is not/);
  assert.match(html, /a witness/);
  assert.match(html, /When AI agents agree/);
  assert.match(html, /Read the paper/);
  assert.match(html, /Machine-readable result \(JSON\)/);
  assert.match(html, /MP\.01 · SYNTHETIC FIXTURE/);
  assert.match(html, /Five votes/);
  assert.match(html, /Two evidence roots/);
  assert.match(html, /The majority/);
  assert.match(html, /disappears/);
  assert.match(html, /PRESERVE_MINORITY/);
  assert.match(html, /What it does not prove/);
  assert.match(html, /Detect\. Trace/);
  assert.match(html, /Challenge\. Verify/);
  assert.match(html, /PUBLIC EVIDENCE/);
  assert.match(html, /EPISTEMIC OBSERVATORY/);
  assert.match(html, /Evidence is not/);
  assert.match(html, /Assessment never grants authority/);
  assert.match(html, /papers\/00-CURRENT-PAPER\.md/);
  assert.match(html, /CAPABILITY TOURNAMENT V1/);
  assert.match(html, /EPISTEMIC LIFT v1\.1/);
  assert.match(html, /192\/192/);
  assert.match(html, /C − B/);
  assert.match(html, /28\.125%/);
  assert.match(html, /21\.875%/);
  assert.match(html, /Validated DEMO result/);
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
  assert.match(html, /href="\/experiments\/epistemic-lift"/);
  assert.match(html, /href="\/experiments\/epistemic-observatory"/);
  assert.match(html, /href="\/system"/);
  assert.match(html, /href="\/research"/);
  assert.match(html, /href="\/developers"/);
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
    access(new URL("../public/research/epistemic-lift-v1.1-results.md", import.meta.url)),
    access(new URL("../public/research/epistemic-lift-v1.1-protocol.md", import.meta.url)),
    access(new URL("../public/research/epistemic-lift-v1.1-summary.json", import.meta.url)),
    access(new URL("../public/research/mp01-canonical-demo.json", import.meta.url)),
  ]);
});

test("server-renders the system map with explicit component and deployment boundaries", async () => {
  const response = await render("/system");
  assert.equal(response.status, 200);
  const html = await response.text();
  assert.match(html, /System — Minority Prophet/);
  assert.match(html, /Know why/);
  assert.match(html, /before you act/);
  assert.match(html, /VALUE UP FRONT/);
  assert.match(html, /THE NERVOUS SYSTEM/);
  assert.match(html, /Evidence graph/);
  assert.match(html, /Minority Prophet engine/);
  assert.match(html, /Knowledge Ledger/);
  assert.match(html, /Gate and evidence router/);
  assert.match(html, /WORKING PUBLIC CORE/);
  assert.match(html, /REFERENCE RUNTIME/);
  assert.match(html, /SEEDED RESEARCH/);
  assert.match(html, /Production identity/);
  assert.match(html, /PUBLIC-CLAIMS\.md/);
});

test("server-renders the public research map with positive and adverse evidence separated", async () => {
  const response = await render("/research");
  assert.equal(response.status, 200);
  const html = await response.text();
  assert.match(html, /Research — Minority Prophet/);
  assert.match(html, /Claims are earned/);
  assert.match(html, /RESEARCH RULES/);
  assert.match(html, /The Minority Prophet Property/);
  assert.match(html, /CANONICAL/);
  assert.match(html, /DEVELOPMENT DEMO/);
  assert.match(html, /Negative results/);
  assert.match(html, /5,729 eligible resolved weather markets/);
  assert.match(html, /Unified auditor candidate/);
  assert.match(html, /Read the current paper/);
  assert.match(html, /EVIDENCE-ALIGNMENT\.md/);
});

test("server-renders a truthful developer path with local commands and maturity labels", async () => {
  const response = await render("/developers");
  assert.equal(response.status, 200);
  const html = await response.text();
  assert.match(html, /Developers — Minority Prophet/);
  assert.match(html, /one inspectable failure/);
  assert.match(html, /python -m experiments\.mp01\.run_mp01/);
  assert.match(html, /local \/ no hosted account/);
  assert.match(html, /npm --prefix evaluations\/multi-model-v1 install/);
  assert.match(html, /Python evidence graph \+ benchmark/);
  assert.match(html, /Automatic framework instrumentation/);
  assert.match(html, /PLANNED/);
  assert.match(html, /A passing fixture proves/);
  assert.match(html, /does not prove hidden real-world lineage/);
});

test("server-renders the complete same-model epistemic lift study", async () => {
  const response = await render("/experiments/epistemic-lift");
  assert.equal(response.status, 200);
  const html = await response.text();
  assert.match(html, /Epistemic Lift Study v1\.1 — Minority Prophet/);
  assert.match(html, /Same model/);
  assert.match(html, /Same world/);
  assert.match(html, /192\/192/);
  assert.match(html, /GPT-5\.6 Sol/);
  assert.match(html, /Claude Sonnet 5/);
  assert.match(html, /96\.875%/);
  assert.match(html, /90\.625%/);
  assert.match(html, /28\.125%/);
  assert.match(html, /21\.875%/);
  assert.match(html, /0\.003906/);
  assert.match(html, /0\.015625/);
  assert.match(html, /9(?:<!-- -->)? better · (?:<!-- -->)?0(?:<!-- -->)? worse/);
  assert.match(html, /7(?:<!-- -->)? better · (?:<!-- -->)?0(?:<!-- -->)? worse/);
  assert.match(html, /exact B payload/);
  assert.match(html, /Hidden truth labels were rejected/);
  assert.match(html, /validated DEMO development study/);
  assert.match(html, /not an independent confirmation/);
  assert.match(html, /epistemic-lift-v1\.1-results\.md/);
  assert.match(html, /epistemic-lift-v1\.1-protocol\.md/);
  assert.match(html, /epistemic-lift-v1\.1-summary\.json/);
});

test("machine-readable lift summary preserves results and development boundary", async () => {
  const summary = JSON.parse(await readFile(new URL("../public/research/epistemic-lift-v1.1-summary.json", import.meta.url), "utf8"));
  assert.equal(summary.status, "COMPLETED");
  assert.equal(summary.verification, "PASSED");
  assert.equal(summary.official_leaderboard_eligible, false);
  assert.equal(summary.design.completed_cells, 192);
  assert.equal(summary.design.failed_cells, 0);
  assert.equal(summary.results.length, 2);
  assert.equal(summary.results[0].minority_prophet_gain_C_minus_B, 0.28125);
  assert.equal(summary.results[1].minority_prophet_gain_C_minus_B, 0.21875);
  assert.ok(summary.results.every((result) => result.B_to_C_regressions === 0));
  assert.ok(summary.claim_boundary.includes("not an official leaderboard result"));
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
