import { SiteFooter, SiteNav } from "./components/site-chrome";
import { formatPercent, liftModels } from "./lib/lift-study";
import { paperUrl } from "./lib/tournament";

export default function Home() {
  return <main>
    <SiteNav />

    <section className="hero" id="top">
      <div className="hero-copy">
        <p className="eyebrow"><span /> EPISTEMIC INFRASTRUCTURE FOR AI AGENTS</p>
        <h1>An echo is not<br /><em>a witness.</em></h1>
        <p className="lede">When AI agents agree, Minority Prophet tests whether the evidence is independent—or whether the crowd is repeating one recorded source.</p>
        <div className="hero-actions">
          <a className="button primary" href="#demo">See the six-agent demo <span>→</span></a>
          <a className="button secondary" href={paperUrl}>Read the paper <span>→</span></a>
        </div>
      </div>
      <div className="hero-visual lineage-hero" aria-label="Five agents supporting Answer A share one evidence root while one agent supporting Answer B has an independent root">
        <div className="lineage-kicker"><span>MP.01 · SYNTHETIC FIXTURE</span><b>5 : 1</b><small>agent votes before lineage</small></div>
        <div className="lineage-mini">
          <p><b>A1</b><i>ORIGIN</i><span>Source X</span></p>
          <p><b>A2</b><i>DERIVED</i><span>A1</span></p>
          <p><b>A3</b><i>DERIVED</i><span>A1</span></p>
          <p><b>A4</b><i>SUMMARY</i><span>A2</span></p>
          <p><b>A5</b><i>PARAPHRASE</i><span>A3</span></p>
          <p className="minority"><b>B1</b><i>ORIGIN</i><span>Source Y</span></p>
        </div>
        <div className="lineage-collapse"><span>5 votes for A</span><i>→</i><strong>1 recorded root</strong></div>
        <div className="lineage-collapse minority"><span>1 vote for B</span><i>→</i><strong>1 recorded root</strong></div>
      </div>
    </section>

    <section className="canonical-demo" id="demo">
      <div className="canonical-demo-heading">
        <p className="section-index">01 / THE FAILURE</p>
        <div><h2>Five votes.<br /><em>Two evidence roots.</em></h2><p>Everything completed successfully. No tool failed. No agent timed out. Five agents returned Answer A. But their declared ancestry leads back to one source.</p></div>
        <blockquote>Truth is not popularity. Consensus is not independent evidence.</blockquote>
      </div>
      <div className="demo-compare">
        <article className="vote-view">
          <span>WHAT A VOTE COUNT SEES</span>
          <h3>Answer A wins<br />5 to 1.</h3>
          <div className="vote-stack" aria-label="Five votes for Answer A and one vote for Answer B"><i /><i /><i /><i /><i /><i className="minority" /></div>
          <p>Six outputs are treated as six signals.</p>
        </article>
        <article className="root-view">
          <span>WHAT LINEAGE REVEALS</span>
          <h3>The majority<br />disappears.</h3>
          <div className="root-pair"><div><i>A</i><b>1 root</b><small>claim-a1</small></div><em>=</em><div className="minority"><i>B</i><b>1 root</b><small>claim-b1</small></div></div>
          <p>Preserve the minority. Request another independent source.</p>
        </article>
      </div>
      <div className="demo-boundary"><span><b>The point:</b> five agreeing agents can still carry one piece of evidence. Lineage preserves the dissent without pretending either answer is proven.</span><a href="/research/mp01-canonical-demo.json">Inspect the result →</a></div>
    </section>

    <section className="source-family-home" id="source-families">
      <div className="source-family-heading">
        <p className="section-index">01B / SOURCE-FAMILY RECONSTRUCTION</p>
        <div><h2>Six claims.<br /><em>Three actual sources.</em></h2><p>The original human explainer asked whether people could distinguish the number of voices from the number of underlying evidence families.</p></div>
        <a href="/source-family-test.html">Open the 90-second explainer <span>→</span></a>
      </div>
      <div className="source-family-graphic" aria-label="Six agent claims collapse into three source families">
        <div className="source-family-claims">
          <header><span>ORDINARY LOG VIEW</span><strong>6 agent claims</strong></header>
          <article className="weather"><b>A</b><p>weather-17 <small>original</small></p><span>PROCEED</span></article>
          <article className="weather"><b>B</b><p>weather-cache <small>copy of A</small></p><span>PROCEED</span></article>
          <article className="route"><b>C</b><p>route-clearance-9 <small>original</small></p><span>PROCEED</span></article>
          <article className="maintenance"><b>D</b><p>maintenance-alert-4 <small>original</small></p><span>STOP</span></article>
          <article className="maintenance"><b>E</b><p>maintenance-summary <small>summary of D</small></p><span>STOP</span></article>
          <article className="weather"><b>F</b><p>weather-brief <small>summary of B</small></p><span>PROCEED</span></article>
        </div>
        <div className="source-family-collapse"><span>TRACE<br />ANCESTRY</span><b>→</b><small>Nothing deleted.<br />Counting unit changed.</small></div>
        <div className="source-family-roots">
          <header><span>MINORITY PROPHET VIEW</span><strong>3 source families</strong></header>
          <article className="weather"><div><b>Weather source</b><small>1 original → 1 copy → 1 summary</small></div><p><i>A</i><i>B</i><i>F</i></p><span>PROCEED</span></article>
          <article className="route"><div><b>Route-clearance source</b><small>1 independent original</small></div><p><i>C</i></p><span>PROCEED</span></article>
          <article className="maintenance"><div><b>Maintenance source</b><small>1 original → 1 summary</small></div><p><i>D</i><i>E</i></p><span>STOP</span></article>
          <footer><b>4 : 2</b><span>agent vote</span><em>→</em><b>2 : 1</b><span>source-family count</span></footer>
        </div>
      </div>
      <p className="source-family-boundary"><b>What it shows:</b> agreement can shrink when copies are grouped by ancestry. It preserves the minority record; it does not automatically make the minority correct or authorize an action.</p>
    </section>

    <section className="product-loop" id="method">
      <p className="section-index">02 / THE LOOP</p>
      <div className="loop-heading"><h2>Detect. Trace.<br /><em>Challenge. Verify.</em></h2><p>Minority Prophet turns provenance into an inspectable decision process. The assessment can lower confidence, preserve dissent, request evidence, or route the decision onward. It never grants authority.</p></div>
      <div className="loop-grid">
        <article><span>01</span><h3>Detect</h3><p>Find recorded consensus collapse, unsupported claims, circularity, and disappearing dissent.</p></article>
        <article><span>02</span><h3>Trace</h3><p>Reconstruct claims, sources, transformations, agents, and recorded roots.</p></article>
        <article><span>03</span><h3>Challenge</h3><p>Test whether corroboration is independent and whether more evidence is required.</p></article>
        <article><span>04</span><h3>Verify</h3><p>Seek a new root, revise the belief, and preserve the failure as a regression test.</p></article>
      </div>
    </section>

    <section className="experiment-index" id="experiments">
      <div className="experiment-index-heading"><p className="section-index">03 / EVIDENCE</p><h2>See the failure.<br /><em>Measure the difference.</em></h2><p>Controlled studies show what provenance changes, where deterministic checks help, and where the evidence still runs out.</p></div>
      <div className="experiment-preview-grid">
        <article className="experiment-preview lift-preview">
          <p className="panel-label">EPISTEMIC LIFT · CONTROLLED STUDY</p>
          <div className="lift-preview-layout"><div><h3>Baseline → Provenance<br />→ Minority Prophet.</h3><p>Two models faced the same 32 frozen worlds in three controlled conditions. Only the available epistemic information changed.</p></div><div className="lift-preview-chart">
            {liftModels.map((model) => <div key={model.name}><header><b>{model.name}</b><span>C − B <strong>+{formatPercent(model.mpGain)}</strong></span></header><p><i style={{ width: `${model.baseline}%` }} /><span>A {formatPercent(model.baseline)}</span></p><p><i style={{ width: `${model.provenance}%` }} /><span>B {formatPercent(model.provenance)}</span></p><p className="mp"><i style={{ width: `${model.minorityProphet}%` }} /><span>C {formatPercent(model.minorityProphet)}</span></p></div>)}
          </div></div>
          <div className="preview-numbers"><div><strong>192/192</strong><span>completed cells</span></div><div><strong>0</strong><span>failures</span></div><div><strong>Both</strong><span>paired p &lt; 0.05</span></div></div>
          <p className="preview-cost-note">Synthetic, matched worlds. Useful evidence—not a claim about every model or every deployment.</p>
          <a className="preview-link" href="/experiments/epistemic-lift">Inspect the lift <span>→</span></a>
        </article>

        <article className="experiment-preview tournament-preview" id="leaderboard">
          <p className="panel-label">METHOD COMPARISON</p>
          <h3>Same packet.<br />Different methods.</h3>
          <p>AI reasoning, tool-using agents, a conventional vote, and a deterministic evidence rule faced the same eight cases.</p>
          <div className="preview-numbers">
            <div><strong>128/128</strong><span>deterministic result</span></div>
            <div><strong>18.7 ms</strong><span>observed wall time</span></div>
            <div><strong>Per model</strong><span>costs kept separate</span></div>
          </div>
          <div className="preview-cost-list" aria-label="Selected individual run estimates"><span>Deterministic rule <b>$0 model</b></span><span>GPT Terra A <b>≈ $0.89</b></span><span>Claude Opus A <b>≈ $3.25</b></span></div>
          <p className="preview-cost-note">A method comparison, not a model ranking. Eight cases; time and cost stay attached to each run.</p>
          <a className="preview-link" href="/experiments/capability-tournament">Compare the methods <span>→</span></a>
        </article>

        <article className="experiment-preview observatory-preview" id="dashboard">
          <p className="panel-label">EPISTEMIC OBSERVATORY</p>
          <h3>Three witnesses.<br />Ninety-five echoes.</h3>
          <p>Enter a generated world where a copied majority overwhelms the count while three independent instruments retain the constructed truth.</p>
          <div className="mini-world" aria-hidden="true"><span>3 independent</span><i /><i /><i /><b>95 copies → 1 root</b></div>
          <div className="preview-numbers compact"><div><strong>3</strong><span>truth roots</span></div><div><strong>95</strong><span>copied claims</span></div><div><strong>$0</strong><span>model calls in demo</span></div></div>
          <p className="preview-cost-note">A generated teaching world. The ancestry is known so you can see the mechanism clearly.</p>
          <a className="preview-link" href="/experiments/epistemic-observatory">Enter the observatory <span>→</span></a>
        </article>
      </div>
    </section>

    <section className="boundary" id="boundary">
      <p className="section-index">04 / THE TRUST BOUNDARY</p>
      <div className="boundary-heading"><h2>Evidence is not<br /><em>authority.</em></h2><p>Minority Prophet asks whether evidence is independently grounded at the causal boundary relevant to a stated decision. It preserves deeper lineage, exposes when another reasonable cut materially changes settlement, and never turns that assessment into permission.</p></div>
      <div className="boundary-flow" aria-label="Evidence flows through binding, assessment, and enforcement">
        <article><span>01</span><h3>Evidence arrives</h3><p>A trace, score, test result, or replay bundle records what happened.</p></article>
        <article><span>02</span><h3>Context binds</h3><p>The proposition, failure domain, independence cut, threshold, policy, and proposed action are joined.</p></article>
        <article><span>03</span><h3>Prophet assesses</h3><p>Roots are counted at the declared proximal boundary while the full ancestry and minority signal remain visible.</p></article>
        <article><span>04</span><h3>Policy enforces</h3><p>A separate policy proceeds, blocks, or escalates. Assessment never grants authority.</p></article>
      </div>
    </section>

    <section className="principles" id="principles">
      <p className="section-index">05 / FIRST PRINCIPLES</p><h2>Never confuse—</h2>
      <div className="principle-grid">{["Consensus / Truth", "Popularity / Evidence", "Confidence / Correctness", "Reputation / Competence", "Correlation / Independence", "Majority / Reality"].map((item, index) => { const [left, right] = item.split(" / "); return <article key={item}><span>0{index + 1}</span><p><s>{left}</s><b>{right}</b></p></article>; })}</div>
    </section>

    <section className="run" id="run">
      <div><p className="section-index">06 / REPRODUCIBLE FIXTURE</p><h2>Reproduce the<br /><em>result.</em></h2></div>
      <div className="terminal"><div><i /><i /><i /><span>minority-prophet / MP.01</span></div><pre><code><b>$</b> python -m experiments.mp01.run_mp01{"\n\n"}<span>agent votes: A=5, B=1</span>{"\n"}<span>recorded roots: A=1, B=1</span>{"\n"}<strong>ABSTAIN · PRESERVE_MINORITY</strong></code></pre></div>
    </section>
    <SiteFooter />
  </main>;
}
