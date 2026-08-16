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

test("agentwex.xyz opens the AWE product at the domain root", async () => {
  const response = await render("/", "https://agentwex.xyz");
  assert.equal(response.status, 200);
  const html = await response.text();
  assert.match(html, /Agent Witness Exchange — The outcome network for AI agents/);
  assert.match(html, /PASSIVE OUTCOME NETWORK FOR AI AGENTS/);
});

test("server-renders the agent knowledge exchange and its authority boundary", async () => {
  const response = await render("/exchange");
  assert.equal(response.status, 200);
  const html = await response.text();
  assert.match(html, /Agent Witness Exchange — The outcome network for AI agents/);
  assert.match(html, /PASSIVE OUTCOME NETWORK FOR AI AGENTS/);
  assert.match(html, /Agent Witness Exchange/);
  assert.match(html, /Install once/);
  assert.match(html, /Every permitted run makes agents smarter/);
  assert.match(html, /captures bounded outcomes in the background/);
  assert.match(html, /verifies which supporting runs are truly independent/);
  assert.match(html, /returns a supported route to the runtime that asked/);
  assert.match(html, /INSTALL ONCE/);
  assert.match(html, /START \+ SET/);
  assert.match(html, /npm install -g https:\/\/agentwex\.xyz\/exchange\/awe-node-0\.1\.0\.tgz/);
  assert.doesNotMatch(html, /npm run awe:install -- --url http:\/\/localhost:3001/);
  assert.doesNotMatch(html, /awe-nav-cta/);
  assert.match(html, /href="https:\/\/agentwex\.xyz\/exchange\/skill\.md"/);
  assert.match(html, /href="https:\/\/agentwex\.xyz\/exchange\/agent\.json"/);
  assert.match(html, /href="https:\/\/agentwex\.xyz\/llms\.txt"/);
  assert.match(html, /02 · BIND AGENT/);
  assert.match(html, /source ~\/\.awe\/otel\.env/);
  assert.match(html, /03 · CONFIRM/);
  assert.match(html, /npm run awe:status/);
  assert.match(html, /That is it/i);
  assert.match(html, /A compatible runtime adapter is still required/);
  assert.match(html, /property="og:title" content="Agent Witness Exchange"/);
  assert.match(html, /LIVE EXCHANGE/);
  assert.match(html, /EXAMPLE EXCHANGE/);
  assert.doesNotMatch(html, /SYNTHETIC FIXTURE/);
  assert.match(html, /Contribute useful outcomes/);
  assert.match(html, /Receive supported routes/);
  assert.match(html, /SUCCESS CONFIRMED/);
  assert.match(html, /A preflight gap or real failure opens the search/);
  assert.match(html, /REQUESTING AGENT/);
  assert.match(html, /FAILED ATTEMPT/);
  assert.match(html, /OAUTH CALLBACK MISMATCH/);
  assert.match(html, /FAILURE ACCEPTED · \+2 CREDITS/);
  assert.match(html, /SEARCH NETWORK →/);
  assert.match(html, /NO ROUTE = 0 SPENT/);
  assert.match(html, /INDEPENDENT SUCCESS/);
  assert.match(html, /COPIED SUCCESS/);
  assert.match(html, /COPY FOLDED INTO R27/);
  assert.match(html, /dependent root collapsed/i);
  assert.match(html, /CANDIDATE ROUTES/);
  assert.match(html, /RANK (?:<!-- -->)?01/);
  assert.match(html, /RANK (?:<!-- -->)?02/);
  assert.match(html, /2<!-- --> independent <!-- -->roots/);
  assert.match(html, /1<!-- --> independent <!-- -->root/);
  assert.match(html, /SELECTED/);
  assert.match(html, /NEEDS 1 MORE ROOT/);
  assert.match(html, /last seen <!-- -->18<!-- -->m ago/i);
  assert.match(html, /valid inside <!-- -->7<!-- -->d window/i);
  assert.match(html, /Distinct routes remain separate/);
  assert.match(html, /RANK ROUTES/);
  assert.match(html, /version alone never wins/);
  assert.match(html, /AWE · ROUTE FOUND · −1 CREDIT/);
  assert.match(html, /BALANCE \+1/);
  assert.match(html, /THE COMPLETE LOOP/);
  assert.match(html, /A failed run returns/);
  assert.match(html, /as a supported route/);
  assert.doesNotMatch(html, /Auto-replays every 15 seconds/);
  assert.doesNotMatch(html, /Illustrative local sequence/);
  assert.doesNotMatch(html, /Replay the exchange/);
  assert.match(html, /migration-audit/);
  assert.match(html, /local evidence insufficient/);
  assert.match(html, /run github-mcp repository-search/);
  assert.match(html, /awe contribute/);
  assert.match(html, /accepted independent failed outcome/);
  assert.match(html, /awe: wrote \.\/awe-route\.json/);
  assert.match(html, /independent roots support route/);
  assert.match(html, /ALLOW · bounded route only/);
  assert.match(html, /awe route apply \.\/awe-route\.json/);
  assert.match(html, /recalculating: github-mcp@/);
  assert.match(html, /applied: \.\/awe-route\.json/);
  assert.match(html, /23 repositories · exit 0/);
  assert.match(html, /fresh working-route confirmation submitted/);
  assert.match(html, /accepted independent confirmation · \+2 credits/);
  assert.match(html, /Set the boundary once/);
  assert.match(html, /Then let the agent work/);
  assert.match(html, /Only the permitted outcome leaves/);
  assert.match(html, /local OpenTelemetry adapter is the thin carrier/);
  assert.match(html, /raw_content=deny/);
  assert.match(html, /609 bytes in this fixture/);
  assert.match(html, /NO MANUAL STEP PER RUN/);
  assert.match(html, /THE TRADE/);
  assert.match(html, /Share an outcome/);
  assert.match(html, /Access the network/);
  assert.match(html, /THE EXCHANGE RULE/);
  assert.match(html, /CONTRIBUTION EARNS ACCESS/);
  assert.match(html, /Join freely/);
  assert.match(html, /Add useful evidence/);
  assert.match(html, /Receive a supported route/);
  const [exchangePageSource, exchangeComponentsSource] = await Promise.all([
    readFile(new URL("../app/exchange/page.tsx", import.meta.url), "utf8"),
    readFile(new URL("../app/exchange/nexus.tsx", import.meta.url), "utf8"),
  ]);
  assert.equal(`${exchangePageSource}${exchangeComponentsSource}`.match(/THE EXCHANGE RULE/g)?.length, 1, "the exchange rule should be implemented once");
  assert.match(html, /COMMUNITY NETWORK/);
  assert.match(html, /PRIVATE NETWORK/);
  assert.match(html, /Payment buys service/);
  assert.match(html, /not epistemic influence/);
  assert.doesNotMatch(html, /Buy credits|Purchase credits|Pay for evidence weight/);
  assert.match(html, /Make sure it is running/);
  assert.match(html, /background node, credit balance, pending contributions, and available routes/);
  assert.match(html, /Share an outcome\.<br\/>Access the network/);
  assert.match(html, /Evidence travels/);
  assert.match(html, /Authority does not/);
  assert.match(html, /proprietary methods/);
  assert.match(html, /route fingerprint only recognizes equivalent bounded outcomes/i);
  assert.match(html, /it does not reveal how the route works/i);
  assert.doesNotMatch(html, new RegExp(["rec", "ipe"].join(""), "i"));
  assert.match(html, /Powered by Minority Prophet/);
  assert.match(html, /It’s like Waze for my agents navigating tools/);
  assert.match(html, /TESTIMONY TEMPLATE · AWAITING VERIFIED ATTRIBUTION/);
  assert.match(html, /Runs continuously after setup/);
  assert.doesNotMatch(html, /Replay background flow/);
  assert.ok(html.indexOf("THE COMPLETE LOOP") < html.indexOf("LIVE EXCHANGE"), "conversion loop should precede the evidence-detail exchange");
  assert.ok(html.indexOf("Share an outcome") < html.indexOf("Set the boundary once"), "trade economics should appear before the privacy boundary");
  assert.ok(html.indexOf("Set the boundary once") < html.indexOf("LIVE EXCHANGE"), "privacy boundary should precede the evidence-detail exchange");
  assert.ok(html.indexOf("Make sure it is running") < html.indexOf("COMMUNITY NETWORK"), "community and private models should close the product journey");
  assert.doesNotMatch(html, /The AWE journey|Your Path|PARTICIPATION PATHS|THE 15-SECOND VERSION/);
  assert.doesNotMatch(html, /PRODUCT FILM|The film|AWE film|FILM UNAVAILABLE/);
  assert.doesNotMatch(html, /MINORITY PROPHET FOR AI AGENTS/);
  assert.doesNotMatch(html, /Minority Prophet — An Echo Is Not a Witness/);
  await Promise.all([
    access(new URL("../public/awe-commercial-v2.mp4", import.meta.url)),
    access(new URL("../public/awe-commercial-v2-poster.jpg", import.meta.url)),
  ]);
});

test("publishes agent-readable AWE discovery and guarded setup instructions", async () => {
  const [llms, skill, manifestSource] = await Promise.all([
    readFile(new URL("../public/llms.txt", import.meta.url), "utf8"),
    readFile(new URL("../public/exchange/skill.md", import.meta.url), "utf8"),
    readFile(new URL("../public/exchange/agent.json", import.meta.url), "utf8"),
  ]);
  const manifest = JSON.parse(manifestSource);

  assert.match(llms, /Agent Witness Exchange \(AWE\)/);
  assert.match(llms, /\/exchange\/skill\.md/);
  assert.match(skill, /npm install -g https:\/\/agentwex\.xyz\/exchange\/awe-node-0\.1\.0\.tgz/);
  assert.match(skill, /AWE routes are evidence\. They never authorize an action/);
  assert.match(skill, /hosted verification network is not yet production-ready/i);
  assert.equal(manifest.format, "awe.machine-discovery.v1");
  assert.equal(manifest.distribution.sourceAvailable, true);
  assert.equal(manifest.distribution.publicNpmPackageReleased, false);
  assert.equal(manifest.distribution.directPackageReleased, true);
  assert.equal(manifest.distribution.directPackageUrl, "https://agentwex.xyz/exchange/awe-node-0.1.0.tgz");
  assert.equal(manifest.distribution.hostedExchangeReleased, false);
  assert.equal(manifest.authorityBoundary.grantsAuthority, false);
  assert.equal(manifest.authorityBoundary.returnedRoutesRequireLocalPolicy, true);
});

test("the AWE quickstart command executes the real local evaluator", async () => {
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
  assert.match(output, /authority granted by AWE: false/);
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
