import { SiteFooter, SiteNav } from "./components/site-chrome";
import { paperUrl } from "./lib/tournament";

export default function Home() {
  return <main>
    <SiteNav />

    <section className="hero" id="top">
      <div className="hero-copy">
        <p className="eyebrow"><span /> EVIDENCE-AWARE AGGREGATION</p>
        <h1>Truth is not<br /><em>popularity.</em></h1>
        <p className="lede">Minority Prophet tests whether systems can distinguish independent evidence from copied consensus—without confusing an evidence assessment with permission.</p>
        <div className="hero-actions">
          <a className="button primary" href="#experiments">Explore the evidence <span>↓</span></a>
          <a className="button secondary" href={paperUrl}>Read the paper <span>→</span></a>
        </div>
      </div>
      <div className="hero-visual" aria-label="Three independent true observations opposed by ninety-five copied false claims">
        <div className="ratio-label"><span>DEMONSTRATION WORLD</span><b>03 : 95</b><small>independent truth / copied falsehood</small></div>
        <div className="signal-field">{Array.from({ length: 98 }).map((_, index) => <i key={index} className={index < 3 ? "truth-signal" : "copy-signal"} />)}</div>
        <div className="truth-note">3 independent evidence roots <span>→</span> ground truth</div>
        <div className="false-note">95 claims <span>→</span> one social root</div>
      </div>
    </section>

    <section className="question" id="benchmark">
      <p className="section-index">01 / THE CENTRAL QUESTION</p>
      <div><h2>Which belief is best<br /><em>supported?</em></h2><p>A hundred voices can still be one copied story. The research asks whether complete ancestry and distinct evidence origins can recover the constructed answer when ordinary vote counts fail.</p></div>
      <blockquote>“Can evidence-aware aggregation recover truth when vote counts fail?”</blockquote>
    </section>

    <section className="experiment-index" id="experiments">
      <div className="experiment-index-heading"><p className="section-index">02 / LIVE EXPERIMENTS</p><h2>See the claim.<br /><em>Inspect the evidence.</em></h2><p>Two separate experiences: one measured tournament and one interactive synthetic world. Each keeps its evidence boundary visible.</p></div>
      <div className="experiment-preview-grid">
        <article className="experiment-preview tournament-preview" id="leaderboard">
          <p className="panel-label">CAPABILITY TOURNAMENT V1</p>
          <h3>Same packet.<br />Different methods.</h3>
          <p>AI reasoning, tool-using AI, a conventional vote, and the canonical deterministic method faced the same 128 decisions.</p>
          <div className="preview-numbers">
            <div><strong>128/128</strong><span>canonical result</span></div>
            <div><strong>18.7 ms</strong><span>canonical wall time</span></div>
            <div><strong>Per model</strong><span>costs kept separate</span></div>
          </div>
          <div className="preview-cost-list" aria-label="Selected individual run estimates"><span>Canonical C <b>$0 model</b></span><span>GPT Terra A <b>≈ $0.89</b></span><span>Claude Opus A <b>≈ $3.25</b></span></div>
          <p className="preview-cost-note">Each figure belongs to that individual model and lane across all eight cases. The full page shows every run separately; nothing is combined.</p>
          <a className="preview-link" href="/experiments/capability-tournament">Open the full leaderboard <span>→</span></a>
        </article>

        <article className="experiment-preview observatory-preview" id="dashboard">
          <p className="panel-label">EPISTEMIC OBSERVATORY</p>
          <h3>Three witnesses.<br />Ninety-five echoes.</h3>
          <p>Enter a generated world where a copied majority overwhelms the count while three independent instruments retain the constructed truth.</p>
          <div className="mini-world" aria-hidden="true"><span>3 independent</span><i /><i /><i /><b>95 copies → 1 root</b></div>
          <div className="preview-numbers compact"><div><strong>3</strong><span>truth roots</span></div><div><strong>95</strong><span>copied claims</span></div><div><strong>$0</strong><span>model calls in demo</span></div></div>
          <p className="preview-cost-note">This is an interactive synthetic demonstration, not the tournament result and not a real-world truth claim.</p>
          <a className="preview-link" href="/experiments/epistemic-observatory">Enter the observatory <span>→</span></a>
        </article>
      </div>
    </section>

    <section className="boundary" id="boundary">
      <p className="section-index">03 / THE ARCHITECTURAL BOUNDARY</p>
      <div className="boundary-heading"><h2>Evidence is not<br /><em>authority.</em></h2><p>Minority Prophet asks whether the evidence supporting a claim is independently grounded or merely repeated. It never turns that assessment into permission.</p></div>
      <div className="boundary-flow" aria-label="Evidence flows through binding, assessment, and enforcement">
        <article><span>01</span><h3>Evidence arrives</h3><p>A trace, score, test result, or replay bundle records what happened.</p></article>
        <article><span>02</span><h3>Context binds</h3><p>Identity, delegated authority, policy, evidence, and the proposed action are joined.</p></article>
        <article><span>03</span><h3>Prophet assesses</h3><p>Independent roots are distinguished from copies and manufactured agreement.</p></article>
        <article><span>04</span><h3>Policy enforces</h3><p>A separate policy proceeds, blocks, or escalates. Assessment never grants authority.</p></article>
      </div>
    </section>

    <section className="principles" id="principles">
      <p className="section-index">04 / NON-NEGOTIABLE PRINCIPLES</p><h2>Never confuse—</h2>
      <div className="principle-grid">{["Consensus / Truth", "Popularity / Evidence", "Confidence / Correctness", "Reputation / Competence", "Correlation / Independence", "Majority / Reality"].map((item, index) => { const [left, right] = item.split(" / "); return <article key={item}><span>0{index + 1}</span><p><s>{left}</s><b>{right}</b></p></article>; })}</div>
    </section>

    <section className="run" id="run">
      <div><p className="section-index">05 / REPRODUCIBLE V0.1</p><h2>Run the<br /><em>baselines.</em></h2></div>
      <div className="terminal"><div><i /><i /><i /><span>minority-prophet / v0.1</span></div><pre><code><b>$</b> python -m benchmark --worlds 500 --seed 7{"\n\n"}<span>Generating synthetic worlds...</span>{"\n"}<span>Evaluating reproducible baselines...</span>{"\n"}<strong>Report ready.</strong></code></pre></div>
    </section>
    <SiteFooter />
  </main>;
}
