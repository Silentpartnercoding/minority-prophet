import type { Metadata } from "next";
import { SiteFooter, SiteNav } from "../components/site-chrome";

export const metadata: Metadata = {
  title: "Developers — Minority Prophet",
  description: "Run the canonical fixture, use the local evidence-structure engine, and understand which integrations are working versus planned.",
};

const repository = "https://github.com/Silentpartnercoding/minority-prophet";

export default function DevelopersPage() {
  return <main>
    <SiteNav />
    <header className="overview-hero developer-hero">
      <div><p className="eyebrow"><span /> DEVELOPERS</p><h1>Start with<br /><em>one inspectable failure.</em></h1><p className="lede">Run the six-agent MP.01 fixture locally, inspect the exact evidence roots, then choose the smallest integration surface your runtime actually needs.</p></div>
      <div className="developer-terminal"><header><i /><i /><i /><span>local / no hosted account</span></header><pre><code><b>$</b> git clone {repository}{"\n"}<b>$</b> cd minority-prophet{"\n"}<b>$</b> python -m experiments.mp01.run_mp01{"\n\n"}<span>votes    A=5  B=1</span>{"\n"}<span>roots    A=1  B=1</span>{"\n"}<strong>ABSTAIN · REQUIRE_INDEPENDENT_SOURCE</strong></code></pre></div>
    </header>

    <section className="developer-paths">
      <div className="page-section-heading"><p className="section-index">01 / CHOOSE THE SURFACE</p><h2>Use only<br /><em>what you need.</em></h2><p>The benchmark, graph library, and runtime are separable. Installation does not authorize an agent or require a particular model provider.</p></div>
      <div className="developer-grid">
        <article><span>PYTHON · WORKING</span><h3>Research and graph primitives</h3><p>Generate worlds, run aggregators, validate declared ancestry, and reproduce deterministic fixtures.</p><pre><code>python -m pip install .{"\n"}python -m benchmark --worlds 500 --seed 7</code></pre><a href={`${repository}#installable-surfaces`}>Python quickstart →</a></article>
        <article><span>NODE / MCP / HTTP · REFERENCE</span><h3>Read-only evidence engine</h3><p>Analyze evidence structure through the versioned local runtime in this repository. It returns no truth label and grants no authority.</p><pre><code>npm --prefix evaluations/multi-model-v1 install{"\n"}MP_ENGINE_ALLOW_INSECURE_LOCAL=1 npm --prefix evaluations/multi-model-v1 exec mp-engine -- doctor</code></pre><a href={`${repository}/blob/main/evaluations/multi-model-v1/RUNTIME-README.md`}>Runtime guide →</a></article>
        <article><span>CONTRACTS · WORKING DRAFTS</span><h3>Vendor-neutral integration</h3><p>Bind exact actions to authority and evidence while keeping request causality, authority provenance, and evidence provenance separate.</p><pre><code>contracts/authority-evidence-v0.1{"\n"}provenance/evidence-lineage.schema.json</code></pre><a href={`${repository}/tree/main/contracts`}>Inspect contracts →</a></article>
      </div>
    </section>

    <section className="maturity-section">
      <div className="page-section-heading"><p className="section-index">02 / INTEGRATION MATURITY</p><h2>Available now.<br /><em>Planned next.</em></h2><p>The public surface should say exactly what a developer can use today.</p></div>
      <div className="maturity-table">
        <div><b>Python evidence graph + benchmark</b><span className="status-working">WORKING</span><p>Local library, deterministic fixtures, tests.</p></div>
        <div><b>Provider-neutral MP engine</b><span className="status-reference">REFERENCE</span><p>Local HTTP, MCP, metrics, redacted telemetry.</p></div>
        <div><b>A/B/C evaluation harness</b><span className="status-working">WORKING</span><p>Development studies, adapters, hashes, verification gates.</p></div>
        <div><b>Automatic framework instrumentation</b><span className="status-planned">PLANNED</span><p>OpenTelemetry, agent frameworks, claim/evidence capture.</p></div>
        <div><b>Packaged Epistemic CI command</b><span className="status-planned">PLANNED</span><p>The research controls exist; one stable installable CLI does not yet.</p></div>
        <div><b>Hosted production intelligence</b><span className="status-planned">NOT PUBLIC</span><p>No production-readiness claim is made by this repository.</p></div>
      </div>
    </section>

    <section className="developer-boundary">
      <p className="section-index">03 / WHAT A PASS MEANS</p><h2>A passing fixture proves<br /><em>the fixture passed.</em></h2><p>It does not prove hidden real-world lineage was recovered, that a source is truthful, or that an action is authorized. Start with declared provenance, preserve unknowns, and make every escalation inspectable.</p><div><a href={`${repository}/blob/main/CONTRIBUTOR-QUICKSTART.md`}>Contributor quickstart →</a><a href={`${repository}/blob/main/SYSTEM-ARCHITECTURE.md`}>System architecture →</a></div>
    </section>
    <SiteFooter />
  </main>;
}
