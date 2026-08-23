import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { access, readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import test from "node:test";

async function render(path = "/", origin = "http://localhost") {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}`);
  const { default: worker } = await import(workerUrl.href);
  return worker.fetch(
    new Request(`${origin}${path}`, { headers: { accept: "text/html" } }),
    { ASSETS: { fetch: async () => new Response("Not found", { status: 404 }) } },
    { waitUntil() {}, passThroughOnException() {} },
  );
}

test("agentwex.xyz opens the Agent WEX product at the domain root", async () => {
  const response = await render("/", "https://agentwex.xyz");
  assert.equal(response.status, 200);
  const html = await response.text();
  assert.match(html, /Agent WEX — Shared reliability for agent tools/);
  assert.match(html, /SHARED RELIABILITY FOR AGENT TOOLS/);
});

test("server-renders the agent knowledge exchange and its authority boundary", async () => {
  const response = await render("/exchange");
  assert.equal(response.status, 200);
  const html = await response.text();
  assert.match(html, /Agent WEX — Shared reliability for agent tools/);
  assert.match(html, /PUBLIC PREVIEW · MACOS · NO SENSITIVE WORKLOADS/);
  assert.match(html, /Check before the call/);
  assert.match(html, /Turn failures into the next answer/);
  assert.match(html, /Aggregate preflight is free/);
  assert.match(html, /Fewer failed calls/);
  assert.match(html, /Vendor intelligence/);
  assert.match(html, /unrestricted cross-provider optimization/);
  assert.match(html, /agentwex-0\.6\.0\.tgz/);
  assert.match(html, /SHA256SUMS/);
  assert.match(html, /does not prove that a node is an independent controller/);
  assert.match(html, /It does not build, host, orchestrate, or autonomously authorize agents/);
  assert.match(html, /Duplicate retries neither manufacture consensus nor mint more credits/);
  assert.match(html, /href="\/exchange\/privacy"/);
  assert.match(html, /href="\/exchange\/security"/);
  assert.match(html, /href="\/exchange\/protocol"/);
  assert.match(html, /agent-wex-social-v3\.png/);
  assert.doesNotMatch(html, /awe contribute|awe ask|awe route apply/);
  assert.doesNotMatch(html, /truly independent|independently verified runs/i);
});

test("publishes agent-readable Agent WEX discovery and guarded setup instructions", async () => {
  const [llms, skill, manifestSource] = await Promise.all([
    readFile(new URL("../public/llms.txt", import.meta.url), "utf8"),
    readFile(new URL("../public/exchange/skill.md", import.meta.url), "utf8"),
    readFile(new URL("../public/exchange/agent.json", import.meta.url), "utf8"),
  ]);
  const manifest = JSON.parse(manifestSource);

  assert.match(llms, /Agent WEX/);
  assert.match(llms, /Aggregate preflight is free/);
  assert.match(llms, /failed call into credits/);
  assert.match(llms, /\/exchange\/skill\.md/);
  assert.match(skill, /agentwex-0\.6\.0\.tgz/);
  assert.match(skill, /shasum -a 256 -c SHA256SUMS/);
  assert.match(skill, /agentwex install/);
  assert.match(skill, /agentwex preflight/);
  assert.match(skill, /agentwex contributions --limit 25/);
  assert.match(skill, /self-reported estimates/);
  assert.doesNotMatch(skill, /--name|My agent|AWE_NODE_NAME/);
  assert.match(skill, /Agent WEX routes are evidence\. They never authorize an action/);
  assert.match(skill, /preview verifies receipt signatures/i);
  assert.equal(manifest.format, "awe.machine-discovery.v1");
  assert.equal(manifest.distribution.sourceAvailable, true);
  assert.equal(manifest.distribution.publicNpmPackageReleased, false);
  assert.equal(manifest.distribution.directPackageReleased, true);
  assert.equal(manifest.distribution.directPackageUrl, "https://agentwex.xyz/exchange/agentwex-0.6.0.tgz");
  assert.match(manifest.distribution.directPackageSha256, /^[a-f0-9]{64}$/);
  assert.equal(manifest.distribution.directPackageSha256, "44e886163a6693966f8df65dad4088d544227cc3d73cb116b21a31e66a653bd9");
  assert.ok(manifest.capabilities.includes("free_aggregate_preflight"));
  assert.ok(manifest.capabilities.includes("regression_and_outage_alerts"));
  assert.equal(manifest.economics.duplicateRetriesEarnCredits, false);
  assert.equal(manifest.preflight.aggregateAssessmentCostCredits, 0);
  assert.equal(manifest.preflight.unrestrictedCrossToolProviderAuthRuntimeRoutingClaimed, false);
  assert.equal(manifest.impactMeasurement.verifiedSavingsClaimed, false);
  assert.equal(manifest.runtimeAdapters.bernstein.optional, true);
  assert.equal(manifest.runtimeAdapters.bernstein.transport, "localhost_lifecycle_plugin");
  assert.equal(manifest.distribution.hostedExchangeReleased, true);
  assert.equal(manifest.distribution.hostedExchangeStage, "public-preview");
  assert.equal(manifest.authorityBoundary.controllerIndependenceVerified, false);
  assert.equal(manifest.authorityBoundary.executionTruthVerified, false);
  assert.equal(manifest.runtimeAdapters.claudeCode.automaticConnection, true);
  assert.equal(manifest.runtimeAdapters.claudeCode.preciseMappingOptional, true);
  assert.equal(manifest.runtimeAdapters.codex.status, "alpha");
  assert.equal(manifest.runtimeAdapters.codex.discardsArgumentsAndOutputLocally, true);
  assert.equal(manifest.runtimeAdapters.geminiCli.status, "alpha");
  assert.equal(manifest.modelCompatibility.directModelAdapterClaimed, false);
  assert.equal(manifest.authorityBoundary.grantsAuthority, false);
  assert.equal(manifest.authorityBoundary.returnedRoutesRequireLocalPolicy, true);
});

test("the Agent WEX quickstart command executes the real local evaluator", async () => {
  const packageJson = JSON.parse(await readFile(new URL("../package.json", import.meta.url), "utf8"));
  assert.equal(packageJson.scripts["awe:demo"], "node exchange/knowledge-exchange-v0.1/demo.mjs");

  const output = execFileSync(
    process.execPath,
    [fileURLToPath(new URL("../exchange/knowledge-exchange-v0.1/demo.mjs", import.meta.url))],
    { encoding: "utf8" },
  );
  assert.match(output, /capture  3 minimized route outcomes/);
  assert.match(output, /verify   2 independent success roots; 1 dependent root collapsed/);
  assert.match(output, /return   tool 3\.2\.0 \+ client 1\.8\.0/);
  assert.match(output, /authority granted by Agent WEX: false/);
});

test("server-renders the public coverage boundary without demo evidence", async () => {
  const response = await render("/coverage", "https://agentwex.xyz");
  assert.equal(response.status, 200);
  const html = await response.text();
  assert.match(html, /See where the network/);
  assert.match(html, /Distinct signed nodes/);
  assert.match(html, /No demonstration rows/);
  assert.doesNotMatch(html, /five independent|verified independent operators/i);
});

test("server-renders a failure-first landing page with the core fixture and separate studies", async () => {
  const response = await render();
  assert.equal(response.status, 200);
  assert.match(response.headers.get("content-type") ?? "", /^text\/html\b/i);
  const html = await response.text();
  assert.match(html, /<title>Minority Prophet/);
  assert.match(html, /An echo is not/);
  assert.match(html, /a witness/);
  assert.match(html, /When AI agents agree/);
  assert.match(html, /Read the paper/);
  assert.match(html, /Inspect the result/);
  assert.match(html, /MP\.01 · SYNTHETIC FIXTURE/);
  assert.match(html, /Five votes/);
  assert.match(html, /Two evidence roots/);
  assert.match(html, /The majority/);
  assert.match(html, /disappears/);
  assert.match(html, /Preserve the minority/);
  assert.match(html, /without pretending either answer is proven/);
  assert.match(html, /Detect\. Trace/);
  assert.match(html, /Challenge\. Verify/);
  assert.match(html, /03 \/ EVIDENCE/);
  assert.match(html, /EPISTEMIC OBSERVATORY/);
  assert.match(html, /Evidence is not/);
  assert.match(html, /Assessment never grants authority/);
  assert.match(html, /causal boundary relevant to a stated decision/);
  assert.match(html, /failure domain, independence cut, threshold/);
  assert.match(html, /declared proximal boundary/);
  assert.match(html, /papers\/00-CURRENT-PAPER\.md/);
  assert.match(html, /METHOD COMPARISON/);
  assert.match(html, /EPISTEMIC LIFT · CONTROLLED STUDY/);
  assert.match(html, /192\/192/);
  assert.match(html, /C − B/);
  assert.match(html, /28\.125%/);
  assert.match(html, /21\.875%/);
  assert.match(html, /Synthetic, matched worlds/);
  assert.match(html, /GPT Terra A/);
  assert.match(html, /≈ \$0\.89/);
  assert.match(html, /Claude Opus A/);
  assert.match(html, /≈ \$3\.25/);
  assert.match(html, /A method comparison, not a model ranking/);
  assert.match(html, /Eight cases/);
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
  assert.match(html, /THE CONTROL LOOP/);
  assert.match(html, /Gate holds the action/);
  assert.match(html, /Border or verifier/);
  assert.match(html, /REQUEST EVIDENCE/);
  assert.match(html, /Neutral router/);
  assert.match(html, /RETURN TO GATE/);
  assert.match(html, /FINAL DECISION ONLY/);
  assert.match(html, /Evidence graph/);
  assert.match(html, /Minority Prophet engine/);
  assert.match(html, /Knowledge Ledger/);
  assert.match(html, /Gate and evidence router/);
  assert.match(html, /IDENTITY \+ AUTHORITY/);
  assert.match(html, /ANALYSIS/);
  assert.match(html, /MEMORY/);
  assert.match(html, /Keep the answer/);
  assert.match(html, /Keep the doubt/);
  assert.match(html, /FLIP BUDGET/);
  assert.match(html, /CONVERSIONS TO REVERSE/);
  assert.match(html, /Net per-side root gain/);
  assert.match(html, /Unsearched locations/);
  assert.match(html, /not a count of attacks/);
  assert.match(html, /EMBODIMENT/);
  assert.match(html, /A judgment can reach a body/);
  assert.match(html, /HUMAN ENVELOPE/);
  assert.match(html, /BOUNDED EMBODIMENT/);
  assert.match(html, /not general robot autonomy/);
  assert.match(html, /does not replace identity/);
  assert.match(html, /PUBLIC-CLAIMS\.md/);
});

test("server-renders the public research map with positive and adverse evidence separated", async () => {
  const response = await render("/research");
  assert.equal(response.status, 200);
  const html = await response.text();
  assert.match(html, /Research — Minority Prophet/);
  assert.match(html, /Claims are earned/);
  assert.match(html, /THE METHOD/);
  assert.match(html, /The Minority Prophet Property/);
  assert.match(html, /Evidence-aligned history/);
  assert.match(html, /CONTROLLED STUDY/);
  assert.match(html, /What failed/);
  assert.match(html, /5,729 eligible weather markets/);
  assert.match(html, /Complexity without gain/);
  assert.match(html, /Read the scientific claim/);
  assert.match(html, /EVIDENCE-ALIGNMENT\.md/);
});

test("server-renders a vendor-neutral developer integration path", async () => {
  const response = await render("/developers");
  assert.equal(response.status, 200);
  const html = await response.text();
  assert.match(html, /Developers — Minority Prophet/);
  assert.match(html, /one inspectable failure/);
  assert.match(html, /python -m experiments\.mp01\.run_mp01/);
  assert.match(html, /LOCAL QUICKSTART/);
  assert.match(html, /npm --prefix evaluations\/multi-model-v1 install/);
  assert.match(html, /Count evidence roots/);
  assert.match(html, /Identity providers/);
  assert.match(html, /Observability systems/);
  assert.match(html, /Analysis informs/);
  assert.match(html, /never authenticates an actor/);
});

test("publishes a source-family explainer without testing the viewer", async () => {
  const html = await readFile(new URL("../public/source-family-test.html", import.meta.url), "utf8");
  assert.match(html, /DEMO · NOT A TEST/);
  assert.match(html, /You are not being graded/);
  assert.match(html, /Nothing was deleted or rerun/);
  assert.match(html, /claim events/);
  assert.match(html, /unique actors/);
  assert.match(html, /source families/);
  assert.match(html, /2 supporting roots/);
  assert.match(html, /1 contradictory root/);
  assert.doesNotMatch(html, /<select|Submit sealed response/);
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
  assert.match(html, /The same claims, sources, provenance/);
  assert.match(html, /never the answer key/);
  assert.match(html, /Strong here/);
  assert.match(html, /not independent confirmation/);
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
  assert.match(html, /Method Comparison — Minority Prophet/);
  assert.match(html, /METHOD COMPARISON/);
  assert.match(html, /THE METHOD/);
  assert.match(html, /Freeze the protocol first/);
  assert.match(html, /Repeat before generalizing/);
  assert.doesNotMatch(html, /CLEAN RUN/);
  assert.match(html, /READ THIS FIRST/);
  assert.match(html, /Eight cases/);
  assert.match(html, /Not 128 trials/);
  assert.match(html, /Code and models are different lanes/);
  assert.match(html, /does not measure MP lift/);
  assert.match(html, /The ancestry is known/);
  assert.match(html, /OBSERVED TELEMETRY BY LANE/);
  assert.match(html, /No combined score/);
  assert.match(html, /Every run stands alone/);
  assert.match(html, /≈ \$0\.89/);
  assert.match(html, /≈ \$1\.02/);
  assert.match(html, /≈ \$3\.25/);
  assert.match(html, /≈ \$6\.45/);
  assert.match(html, /Costs are per run, never combined/);
  assert.match(html, /WHY THIS JUNCTION MATTERS/);
  assert.match(html, /Agents will talk/);
  assert.match(html, /faster than humans can check/);
  assert.match(html, /OBSERVED ON ONE EIGHT-CASE PACKET/);
  assert.match(html, /Terra A took ≈ (?:<!-- -->)?19,520(?:<!-- -->)?× the elapsed time in this observed packet/);
  assert.match(html, /must not be linearly projected/);
  assert.doesNotMatch(html, /100,000|1,000,000|production capacity forecast/);
  assert.ok(html.indexOf("WHY THIS JUNCTION MATTERS") < html.indexOf("OBSERVED TELEMETRY BY LANE"));
  assert.match(html, /packet shape can all change the comparison/);
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
  assert.match(html, /Every lane traced its own roots/);
  assert.match(html, /This measures method conformance/);
  assert.match(html, /does not prove real-world roots/);
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
  assert.match(html, /Generated world · seed 7/);
  assert.match(html, /ancestry is built into this generated world/);
  assert.match(html, /No model is called by this page/);
});
