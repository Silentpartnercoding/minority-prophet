import type { Metadata } from "next";
import { SiteFooter, SiteNav } from "../components/site-chrome";

export const metadata: Metadata = {
  title: "Developers — Minority Prophet",
  description: "Add evidence lineage, epistemic analysis, and bounded intervention to a multi-agent system without replacing its identity or runtime stack.",
};

const repository = "https://github.com/Silentpartnercoding/minority-prophet";

export default function DevelopersPage() {
  return <main>
    <SiteNav />
    <header className="overview-hero developer-hero">
      <div><p className="eyebrow"><span /> DEVELOPERS</p><h1>Start with<br /><em>one inspectable failure.</em></h1><p className="lede">Run MP.01. Watch five voices collapse to one source. Then connect only the layer your system needs.</p></div>
      <div className="developer-terminal"><header><i /><i /><i /><span>LOCAL QUICKSTART</span></header><pre><code><b>$</b> git clone {repository}{"\n"}<b>$</b> cd minority-prophet{"\n"}<b>$</b> python -m experiments.mp01.run_mp01{"\n\n"}<span>votes    A=5  B=1</span>{"\n"}<span>roots    A=1  B=1</span>{"\n"}<strong>ABSTAIN · REQUIRE_INDEPENDENT_SOURCE</strong></code></pre></div>
    </header>

    <section className="developer-paths">
      <div className="page-section-heading"><p className="section-index">01 / CHOOSE THE SURFACE</p><h2>Use only<br /><em>what you need.</em></h2><p>The benchmark, graph library, and analysis service are separable. None requires a particular model, identity provider, or agent framework.</p></div>
      <div className="developer-grid">
        <article><span>PYTHON</span><h3>Count evidence roots</h3><p>Generate worlds, validate declared ancestry, and reproduce deterministic fixtures.</p><pre><code>python -m pip install .{"\n"}python -m benchmark --worlds 500 --seed 7</code></pre><a href={`${repository}#installable-surfaces`}>Python quickstart →</a></article>
        <article><span>MCP / HTTP</span><h3>Call the evidence engine</h3><p>Receive roots, dependence, warnings, and uncertainty—never a truth label or permission.</p><pre><code>npm --prefix evaluations/multi-model-v1 install{"\n"}MP_ENGINE_ALLOW_INSECURE_LOCAL=1 npm --prefix evaluations/multi-model-v1 exec mp-engine -- doctor</code></pre><a href={`${repository}/blob/main/evaluations/multi-model-v1/RUNTIME-README.md`}>Runtime guide →</a></article>
        <article><span>SCHEMAS</span><h3>Carry authority and provenance</h3><p>Keep who requested, who may act, and why the system believes something as separate facts.</p><pre><code>contracts/authority-evidence-v0.1{"\n"}provenance/evidence-lineage.schema.json</code></pre><a href={`${repository}/tree/main/contracts`}>Inspect the contracts →</a></article>
      </div>
    </section>

    <section className="maturity-section">
      <div className="page-section-heading"><p className="section-index">02 / WHERE IT CONNECTS</p><h2>Keep your models.<br /><em>Keep your stack.</em></h2><p>Minority Prophet adds evidence semantics between systems that already know how to identify, observe, decide, and act.</p></div>
      <div className="maturity-table">
        <div><b>Agent frameworks</b><span className="status-working">EMIT</span><p>Claims, evidence links, transformations, and delegation events.</p></div>
        <div><b>Identity providers</b><span className="status-reference">BIND</span><p>Actor, principal, scope, credential, and revocation state.</p></div>
        <div><b>Observability systems</b><span className="status-reference">SUPPLY</span><p>Execution traces become inputs to a knowledge record—not truth by themselves.</p></div>
        <div><b>Minority Prophet</b><span className="status-working">ANALYZE</span><p>Roots, dependence, dissent, uncertainty, and missing evidence.</p></div>
        <div><b>Policy engines</b><span className="status-reference">DECIDE</span><p>Consume the assessment while retaining all authority.</p></div>
        <div><b>Protected runtimes</b><span className="status-reference">ENFORCE</span><p>Execute only the final action bound by identity and policy.</p></div>
      </div>
    </section>

    <section className="developer-boundary">
      <p className="section-index">03 / THE CONTRACT</p><h2>Analysis informs.<br /><em>Policy decides.</em></h2><p>An MP receipt describes evidence structure. It never authenticates an actor, grants permission, or executes a tool.</p><div><a href={`${repository}/blob/main/CONTRIBUTOR-QUICKSTART.md`}>Integration quickstart →</a><a href={`${repository}/tree/main/contracts`}>Inspect the contracts →</a></div>
    </section>
    <SiteFooter />
  </main>;
}
