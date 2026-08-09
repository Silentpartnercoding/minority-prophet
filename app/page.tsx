"use client";

import { useMemo, useState } from "react";

type ClaimKind = "independent" | "copied" | "contradiction";

const paperUrl = "https://github.com/Silentpartnercoding/minority-prophet/blob/main/papers/minority-prophet-v1.0.7.md";

const claims: { id: string; agent: string; belief: string; confidence: number; kind: ClaimKind; source: string }[] = [
  { id: "C-003", agent: "Observer 03", belief: "TRUE", confidence: 98, kind: "independent", source: "Instrument C" },
  { id: "C-002", agent: "Observer 02", belief: "TRUE", confidence: 96, kind: "independent", source: "Instrument B" },
  { id: "C-001", agent: "Observer 01", belief: "TRUE", confidence: 97, kind: "independent", source: "Instrument A" },
  { id: "C-098", agent: "Repeater 95", belief: "FALSE", confidence: 91, kind: "copied", source: "C-041 → C-007" },
  { id: "C-097", agent: "Repeater 94", belief: "FALSE", confidence: 88, kind: "copied", source: "C-018 → C-007" },
  { id: "C-096", agent: "Repeater 93", belief: "FALSE", confidence: 93, kind: "copied", source: "C-007" },
  { id: "C-007", agent: "Origin 01", belief: "FALSE", confidence: 72, kind: "contradiction", source: "No evidence attached" },
];

const metrics = [
  ["Truth accuracy", "0.00", "baseline"],
  ["Minority recovery", "0.00", "baseline"],
  ["Independent roots", "3", "world"],
  ["Copied claims", "95", "world"],
];

export default function Home() {
  const [filter, setFilter] = useState<"all" | ClaimKind>("all");
  const [selected, setSelected] = useState("C-003");
  const visibleClaims = useMemo(
    () => claims.filter((claim) => filter === "all" || claim.kind === filter),
    [filter],
  );
  const active = claims.find((claim) => claim.id === selected) ?? claims[0];

  return (
    <main>
      <nav className="nav" aria-label="Primary navigation">
        <a className="wordmark" href="#top" aria-label="Minority Prophet home">
          <span className="mark">MP</span>
          <span>MINORITY PROPHET <small>RESEARCH PROGRAM</small></span>
        </a>
        <div className="navlinks">
          <a href={paperUrl}>Paper</a>
          <a href="#benchmark">Benchmark</a>
          <a href="#dashboard">Dashboard</a>
          <a href="#boundary">Boundary</a>
          <a href="#principles">Principles</a>
          <a className="nav-cta" href="#run">Run v0.1 ↗</a>
        </div>
      </nav>

      <section className="hero" id="top">
        <div className="hero-copy">
          <p className="eyebrow"><span /> EVIDENCE AGGREGATION BENCHMARK / V0.1</p>
          <h1>Truth is not<br /><em>popularity.</em></h1>
          <p className="lede">A focused benchmark testing whether aggregation methods can recover independently grounded truth under overwhelming copying pressure.</p>
          <div className="hero-actions">
            <a className="button primary" href="#dashboard">Explore the test <span>↓</span></a>
            <a className="button secondary" href={paperUrl}>Read the paper <span>→</span></a>
          </div>
        </div>
        <div className="hero-visual" aria-label="Three independent true observations opposed by ninety-five copied false claims">
          <div className="ratio-label"><span>DEMONSTRATION WORLD</span><b>03 : 95</b><small>independent truth / copied falsehood</small></div>
          <div className="signal-field">
            {Array.from({ length: 98 }).map((_, index) => (
              <i key={index} className={index < 3 ? "truth-signal" : "copy-signal"} />
            ))}
          </div>
          <div className="truth-note">3 independent evidence roots <span>→</span> ground truth</div>
          <div className="false-note">95 claims <span>→</span> one social root</div>
        </div>
      </section>

      <section className="question" id="benchmark">
        <p className="section-index">01 / THE CENTRAL BENCHMARK</p>
        <div>
          <h2>Which belief is best<br /><em>supported?</em></h2>
          <p>The Minority Prophet Test presents conflicting beliefs, complete ancestry, and hidden ground truth. It measures whether an aggregation method can distinguish independent observation from repeated assertion.</p>
        </div>
        <blockquote>“Can evidence-aware aggregation recover truth when vote counts fail?”</blockquote>
      </section>

      <section className="dashboard-section" id="dashboard">
        <div className="section-heading">
          <div><p className="section-index">02 / EPISTEMIC OBSERVATORY</p><h2>World <em>MP-00001</em></h2></div>
          <div className="live"><i /> SYNTHETIC WORLD · SEED 7</div>
        </div>

        <div className="metric-grid">
          {metrics.map(([label, value, meta], index) => <article key={label}>
            <span>0{index + 1}</span><p>{label}</p><strong>{value}</strong><small>{meta}</small>
          </article>)}
        </div>

        <div className="observatory">
          <aside>
            <p className="panel-label">VIEW CLAIMS</p>
            {(["all", "independent", "copied", "contradiction"] as const).map((kind) => (
              <button key={kind} onClick={() => setFilter(kind)} className={filter === kind ? "active" : ""}>
                <i className={kind} /> {kind === "all" ? "All beliefs" : kind} <span>{kind === "all" ? 98 : kind === "independent" ? 3 : kind === "copied" ? 94 : 1}</span>
              </button>
            ))}
            <div className="pending"><b>7</b><span>Pending<br />investigations</span></div>
          </aside>

          <div className="claim-table">
            <div className="table-head"><span>Claim</span><span>Agent</span><span>Belief</span><span>Confidence</span><span>Lineage</span></div>
            {visibleClaims.map((claim) => (
              <button className={`table-row ${selected === claim.id ? "selected" : ""}`} key={claim.id} onClick={() => setSelected(claim.id)}>
                <span>{claim.id}</span><span>{claim.agent}</span><span className={claim.belief === "TRUE" ? "value-true" : "value-false"}>{claim.belief}</span><span><i className="confidence" style={{ "--value": `${claim.confidence}%` } as React.CSSProperties} />{claim.confidence}%</span><span>{claim.source}</span>
              </button>
            ))}
          </div>

          <aside className="inspector">
            <p className="panel-label">LINEAGE INSPECTOR</p>
            <div className={`node large ${active.kind}`}><b>{active.id}</b><span>{active.belief} · synthetic</span></div>
            <div className="line" />
            <div className="node"><b>{active.source}</b><span>{active.kind === "independent" ? "Evidence root" : "Claim ancestry"}</span></div>
            <dl><div><dt>Observer</dt><dd>{active.agent}</dd></div><div><dt>Confidence</dt><dd>{active.confidence}%</dd></div><div><dt>Independence</dt><dd>{active.kind === "independent" ? "Known to generator" : "Not established"}</dd></div></dl>
          </aside>
        </div>
        <p className="demo-disclaimer">Demonstration data · No empirical leaderboard score is claimed until the first frozen evaluation run.</p>
      </section>

      <section className="boundary" id="boundary">
        <p className="section-index">03 / THE ARCHITECTURAL BOUNDARY</p>
        <div className="boundary-heading">
          <h2>Evidence is not<br /><em>authority.</em></h2>
          <p>Decision-quality systems can produce useful behavioral scores and replay bundles. Minority Prophet does not turn those records into permission. It asks whether the evidence supporting a present claim is independently grounded or merely repeated.</p>
        </div>
        <div className="boundary-flow" aria-label="Decision quality evidence flows through Border, Minority Prophet, and Gate">
          <article><span>01</span><h3>Behavioral evidence</h3><p>A decision trace, score, test result, or replay bundle records what happened.</p></article>
          <article><span>02</span><h3>Border binds</h3><p>Identity, delegated authority, policy, evidence, and the exact proposed action are bound together.</p></article>
          <article><span>03</span><h3>Prophet assesses</h3><p>Independent roots are distinguished from copies, correlated validators, and manufactured agreement.</p></article>
          <article><span>04</span><h3>Gate enforces</h3><p>A separate policy proceeds, blocks, or escalates. Evidence assessment never grants authority.</p></article>
        </div>
      </section>

      <section className="principles" id="principles">
        <p className="section-index">04 / NON-NEGOTIABLE PRINCIPLES</p>
        <h2>Never confuse—</h2>
        <div className="principle-grid">
          {["Consensus / Truth", "Popularity / Evidence", "Confidence / Correctness", "Reputation / Competence", "Correlation / Independence", "Majority / Reality"].map((item, index) => {
            const [left, right] = item.split(" / ");
            return <article key={item}><span>0{index + 1}</span><p><s>{left}</s><b>{right}</b></p></article>;
          })}
        </div>
      </section>

      <section className="run" id="run">
        <div><p className="section-index">05 / REPRODUCIBLE V0.1</p><h2>Run the<br /><em>baselines.</em></h2></div>
        <div className="terminal"><div><i /><i /><i /><span>minority-prophet / v0.1</span></div><pre><code><b>$</b> python -m benchmark --worlds 500 --seed 7{"\n\n"}<span>Generating synthetic worlds...</span>{"\n"}<span>Evaluating reproducible baselines...</span>{"\n"}<strong>Report ready.</strong></code></pre></div>
      </section>

      <footer id="foundations"><div className="mark">MP</div><p>A benchmark for<br />evidence-aware aggregation.</p><span>Public research · v0.1 · 2026</span></footer>
    </main>
  );
}
