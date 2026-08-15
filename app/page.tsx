import { SiteFooter, SiteNav } from "./components/site-chrome";
import { formatPercent, liftModels } from "./lib/lift-study";

export default function Home() {
  return <main>
    <SiteNav />

    <section className="hero" id="top">
      <div className="hero-copy">
        <p className="eyebrow"><span /> EPISTEMIC INFRASTRUCTURE FOR AI AGENTS</p>
        <h1>When agents agree,<br /><em>check the evidence.</em></h1>
        <p className="lede">Minority Prophet tests whether AI-agent agreement rests on independent evidence or on recorded shared sources, derivations, circularity, and collapsed dissent.</p>
        <div className="hero-actions">
          <a className="button primary" href="#demo">See the six-agent demo <span>→</span></a>
          <a className="button secondary" href="/research/mp01-canonical-demo.json">Inspect the result <span>→</span></a>
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
      <div className="demo-boundary"><b>What this proves:</b> recorded copies do not become new evidence roots. <b>What it does not prove:</b> that Answer B is true or that hidden copying can always be inferred.</div>
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
      <div className="experiment-index-heading"><p className="section-index">03 / PUBLIC EVIDENCE</p><h2>See the claim.<br /><em>Measure the lift.</em></h2><p>Three distinct experiments: a same-model causal lift study, a bounded method-conformance tournament, and an interactive synthetic world. Their claims and units stay separate.</p></div>
      <div className="experiment-preview-grid">
        <article className="experiment-preview lift-preview">
          <p className="panel-label">EPISTEMIC LIFT v1.1 · COMPLETE DEVELOPMENT STUDY</p>
          <div className="lift-preview-layout"><div><h3>Baseline → Provenance<br />→ Minority Prophet.</h3><p>Two models faced the same 32 frozen worlds in three controlled conditions. Only the available epistemic information changed.</p></div><div className="lift-preview-chart">
            {liftModels.map((model) => <div key={model.name}><header><b>{model.name}</b><span>C − B <strong>+{formatPercent(model.mpGain)}</strong></span></header><p><i style={{ width: `${model.baseline}%` }} /><span>A {formatPercent(model.baseline)}</span></p><p><i style={{ width: `${model.provenance}%` }} /><span>B {formatPercent(model.provenance)}</span></p><p className="mp"><i style={{ width: `${model.minorityProphet}%` }} /><span>C {formatPercent(model.minorityProphet)}</span></p></div>)}
          </div></div>
          <div className="preview-numbers"><div><strong>192/192</strong><span>completed cells</span></div><div><strong>0</strong><span>failures</span></div><div><strong>Both</strong><span>paired p &lt; 0.05</span></div></div>
          <p className="preview-cost-note">Validated DEMO result on synthetic development worlds—not yet an independent hidden evaluation or official leaderboard entry.</p>
          <a className="preview-link" href="/experiments/epistemic-lift">Open the complete lift result <span>→</span></a>
        </article>

        <article className="experiment-preview tournament-preview" id="leaderboard">
          <p className="panel-label">CAPABILITY TOURNAMENT V1</p>
          <h3>Same packet.<br />Different methods.</h3>
          <p>AI reasoning, tool-using AI, a conventional vote, and the canonical deterministic method faced the same eight cases and 128 within-case dispositions.</p>
          <div className="preview-numbers">
            <div><strong>128/128</strong><span>canonical result</span></div>
            <div><strong>18.7 ms</strong><span>canonical wall time</span></div>
            <div><strong>Per model</strong><span>costs kept separate</span></div>
          </div>
          <div className="preview-cost-list" aria-label="Selected individual run estimates"><span>Canonical C <b>$0 model</b></span><span>GPT Terra A <b>≈ $0.89</b></span><span>Claude Opus A <b>≈ $3.25</b></span></div>
          <p className="preview-cost-note">Conformance result only: C is deterministic code, not the same model plus Minority Prophet. The 128 dispositions are not 128 independent trials, no A→B→C lift is estimated, and nothing is combined.</p>
          <a className="preview-link" href="/experiments/capability-tournament">Open the conformance result <span>→</span></a>
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
      <p className="section-index">04 / THE ARCHITECTURAL BOUNDARY</p>
      <div className="boundary-heading"><h2>Evidence is not<br /><em>authority.</em></h2><p>Minority Prophet asks whether the evidence supporting a claim is independently grounded or merely repeated. It never turns that assessment into permission.</p></div>
      <div className="boundary-flow" aria-label="Evidence flows through binding, assessment, and enforcement">
        <article><span>01</span><h3>Evidence arrives</h3><p>A trace, score, test result, or replay bundle records what happened.</p></article>
        <article><span>02</span><h3>Context binds</h3><p>Identity, delegated authority, policy, evidence, and the proposed action are joined.</p></article>
        <article><span>03</span><h3>Prophet assesses</h3><p>Independent roots are distinguished from copies and manufactured agreement.</p></article>
        <article><span>04</span><h3>Policy enforces</h3><p>A separate policy proceeds, blocks, or escalates. Assessment never grants authority.</p></article>
      </div>
    </section>

    <section className="principles" id="principles">
      <p className="section-index">05 / NON-NEGOTIABLE PRINCIPLES</p><h2>Never confuse—</h2>
      <div className="principle-grid">{["Consensus / Truth", "Popularity / Evidence", "Confidence / Correctness", "Reputation / Competence", "Correlation / Independence", "Majority / Reality"].map((item, index) => { const [left, right] = item.split(" / "); return <article key={item}><span>0{index + 1}</span><p><s>{left}</s><b>{right}</b></p></article>; })}</div>
    </section>

    <section className="run" id="run">
      <div><p className="section-index">06 / REPRODUCIBLE FIXTURE</p><h2>Run the<br /><em>failure.</em></h2></div>
      <div className="terminal"><div><i /><i /><i /><span>minority-prophet / MP.01</span></div><pre><code><b>$</b> python -m experiments.mp01.run_mp01{"\n\n"}<span>agent votes: A=5, B=1</span>{"\n"}<span>recorded roots: A=1, B=1</span>{"\n"}<strong>ABSTAIN · PRESERVE_MINORITY</strong></code></pre></div>
    </section>
    <SiteFooter />
  </main>;
}
