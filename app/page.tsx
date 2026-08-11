"use client";

import { useMemo, useState } from "react";

type ClaimKind = "independent" | "copied" | "contradiction";
type Lane = "A" | "B" | "C" | "STANDARD";

type TournamentRow = {
  name: string;
  provider: string;
  lane: Lane;
  correct: number;
  rawCorrect?: number;
  exact: number;
  rawExact?: number;
  invalidTrials: number;
  timeMs: number;
  inputTokens?: number;
  outputTokens?: number;
  toolCalls: number;
  cost?: number;
};

const paperUrl = "https://github.com/Silentpartnercoding/minority-prophet/blob/main/papers/00-CURRENT-PAPER.md";

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

const tournamentRows: TournamentRow[] = [
  { name: "Minority Prophet", provider: "Canonical v1", lane: "C", correct: 128, exact: 8, invalidTrials: 0, timeMs: 18.7, inputTokens: 0, outputTokens: 0, toolCalls: 0, cost: 0 },
  { name: "Claude Opus 5", provider: "Anthropic / Claude Code", lane: "A", correct: 106, exact: 6, invalidTrials: 0, timeMs: 478_018, inputTokens: 326_569, outputTokens: 41_681, toolCalls: 0, cost: 3.2534465 },
  { name: "Claude Opus 5", provider: "Anthropic / Claude Code", lane: "B", correct: 0, rawCorrect: 96, exact: 0, rawExact: 6, invalidTrials: 8, timeMs: 364_977, inputTokens: 1_489_495, outputTokens: 19_965, toolCalls: 35, cost: 4.315915 },
  { name: "Claude Sonnet 5", provider: "Anthropic / Claude Code", lane: "A", correct: 23, exact: 0, invalidTrials: 0, timeMs: 809_652, inputTokens: 639_869, outputTokens: 82_258, toolCalls: 0, cost: 3.4657121 },
  { name: "Claude Sonnet 5", provider: "Anthropic / Claude Code", lane: "B", correct: 32, rawCorrect: 74, exact: 2, rawExact: 4, invalidTrials: 5, timeMs: 1_609_078, inputTokens: 2_431_595, outputTokens: 199_228, toolCalls: 27, cost: 6.4535862 },
  { name: "Claude Haiku 4.5", provider: "Anthropic / Claude Code", lane: "A", correct: 0, exact: 0, invalidTrials: 0, timeMs: 1_058_605, inputTokens: 218_476, outputTokens: 98_985, toolCalls: 0, cost: 1.146448 },
  { name: "Claude Haiku 4.5", provider: "Anthropic / Claude Code", lane: "B", correct: 0, rawCorrect: 10, exact: 0, rawExact: 0, invalidTrials: 8, timeMs: 2_154_859, inputTokens: 3_145_023, outputTokens: 145_142, toolCalls: 59, cost: 1.9173406 },
  { name: "GPT-5.6 Terra", provider: "OpenAI / Codex", lane: "A", correct: 116, exact: 5, invalidTrials: 0, timeMs: 365_015, inputTokens: 300_475, outputTokens: 16_746, toolCalls: 0, cost: 0.8900575 },
  { name: "GPT-5.6 Sol", provider: "OpenAI / Codex", lane: "A", correct: 102, exact: 5, invalidTrials: 0, timeMs: 512_249, inputTokens: 300_694, outputTokens: 25_952, toolCalls: 0, cost: 2.237102 },
  { name: "Cluster vote", provider: "Conventional baseline", lane: "STANDARD", correct: 96, exact: 6, invalidTrials: 0, timeMs: 9.5, inputTokens: 0, outputTokens: 0, toolCalls: 0, cost: 0 },
  { name: "GPT-5.6 Sol", provider: "OpenAI / Codex", lane: "B", correct: 69, exact: 4, invalidTrials: 0, timeMs: 351_070, inputTokens: 1_101_609, outputTokens: 12_559, toolCalls: 19, cost: 2.418447 },
  { name: "GPT-5.6 Terra", provider: "OpenAI / Codex", lane: "B", correct: 68, exact: 4, invalidTrials: 0, timeMs: 245_782, inputTokens: 1_097_326, outputTokens: 9_151, toolCalls: 18, cost: 1.021252 },
  { name: "GPT-5.6 Luna", provider: "OpenAI / Codex", lane: "B", correct: 35, exact: 2, invalidTrials: 0, timeMs: 496_317, inputTokens: 1_933_985, outputTokens: 20_412, toolCalls: 41, cost: 0.8089608 },
  { name: "GPT-5.6 Luna", provider: "OpenAI / Codex", lane: "A", correct: 16, exact: 1, invalidTrials: 0, timeMs: 296_033, inputTokens: 289_024, outputTokens: 13_697, toolCalls: 0, cost: 0.371206 },
];

const laneDetails = [
  { lane: "A", title: "AI reasons alone", copy: "The model receives the complete raw packet inline. Shell, files, web, retrieval, and every other tool are disabled." },
  { lane: "B", title: "The same AI may use tools", copy: "The same model receives the identical packet. It may choose shell, scripts, packages, or web tools. It is not told to use Minority Prophet." },
  { lane: "C", title: "Canonical Minority Prophet", copy: "The same raw packet enters deterministic code. It derives origins by following parent links, counts distinct roots, and abstains on exact ties." },
];
const maxTournamentTime = Math.max(...tournamentRows.map((row) => row.timeMs));

const formatTime = (timeMs: number) => {
  if (timeMs < 1000) return `${timeMs.toFixed(1)} ms`;
  if (timeMs < 60_000) return `${(timeMs / 1000).toFixed(1)} s`;
  return `${(timeMs / 60_000).toFixed(1)} min`;
};
const formatTokens = (value = 0) => value === 0 ? "0" : value.toLocaleString("en-US");
const speedMultiple = (timeMs: number) => {
  if (timeMs === 18.7) return "C reference";
  if (timeMs < 18.7) return `${(18.7 / timeMs).toFixed(1)}× faster than C`;
  return `${Math.round(timeMs / 18.7).toLocaleString("en-US")}× slower than C`;
};
const laneLabel = (lane: Lane) => lane === "STANDARD" ? "Standard" : `Lane ${lane}`;

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
          <a href="#leaderboard">Leaderboard</a>
          <a href="#dashboard">Dashboard</a>
          <a href="#boundary">Boundary</a>
          <a href="#principles">Principles</a>
          <a className="nav-cta" href="#run">Run v0.1 ↗</a>
        </div>
      </nav>

      <section className="hero" id="top">
        <div className="hero-copy">
          <p className="eyebrow"><span /> CAPABILITY TOURNAMENT / CLEAN V1 RUN</p>
          <h1>Truth is not<br /><em>popularity.</em></h1>
          <p className="lede">A frozen, same-input tournament testing whether AI reasoning, tool-using AI, conventional methods, or distinct-root aggregation best recover the constructed evidence answer.</p>
          <div className="hero-actions">
            <a className="button primary" href="#leaderboard">See the results <span>↓</span></a>
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

      <section className="leaderboard-section" id="leaderboard">
        <div className="section-heading tournament-heading">
          <div><p className="section-index">02 / CAPABILITY TOURNAMENT V1</p><h2>The same packet.<br /><em>Three lanes.</em></h2></div>
          <div className="verified-stamp"><i /> CLEAN RUN · 8 CASES · 128 DECISIONS</div>
        </div>

        <div className="lane-grid" aria-label="Tournament lane definitions">
          {laneDetails.map((item) => <article key={item.lane} className={`lane-card lane-${item.lane.toLowerCase()}`}>
            <span>LANE {item.lane}</span><h3>{item.title}</h3><p>{item.copy}</p>
          </article>)}
        </div>

        <div className="headline-result">
          <div><span>CANONICAL C</span><strong>128 / 128</strong><small>correct dispositions</small></div>
          <p>Minority Prophet completed the frozen task in <b>18.7 milliseconds</b> with zero model tokens. The most accurate GPT reasoning lane took <b>365.0 seconds</b>: about <b>19,519× longer</b>.</p>
        </div>

        <div className="result-block">
          <div className="result-title"><div><p className="panel-label">OVERALL LEADERBOARD</p><h3>Accuracy first</h3></div><p>One clean replicate · GPT/Codex initial grid · preregistered Claude extension</p></div>
          <div className="leaderboard-table-wrap">
            <table className="leaderboard-table">
              <thead><tr><th>Rank</th><th>Contestant</th><th>Lane</th><th>Protocol score</th><th>Raw answers</th><th>Exact cases</th><th>Invalid trials</th><th>Wall time</th><th>Tools called</th><th>Input / output tokens</th><th>Cost estimate</th></tr></thead>
              <tbody>{[...tournamentRows].sort((a, b) => b.correct - a.correct || a.timeMs - b.timeMs).map((row, index) => <tr key={`${row.name}-${row.lane}`}>
                <td>{String(index + 1).padStart(2, "0")}</td>
                <td><b>{row.name}</b><small>{row.provider}</small></td>
                <td><span className={`lane-badge lane-${row.lane.toLowerCase()}`}>{laneLabel(row.lane)}</span></td>
                <td><strong>{row.correct}/128</strong></td><td>{row.rawCorrect ?? row.correct}/128</td><td>{row.exact}/8{row.rawExact !== undefined && row.rawExact !== row.exact ? ` (${row.rawExact} raw)` : ""}</td><td>{row.invalidTrials}/8</td><td>{formatTime(row.timeMs)}</td><td>{row.toolCalls}</td><td>{formatTokens(row.inputTokens)} / {formatTokens(row.outputTokens)}</td>
                <td>{row.cost === 0 ? "$0 model cost" : row.cost ? `$${row.cost.toFixed(3)}` : "—"}</td>
              </tr>)}</tbody>
            </table>
          </div>
          <p className="speed-note">Lane B means tools were available, not necessarily used. “Protocol score” counts failed or workspace-boundary-violating trials as incorrect, as preregistered; “Raw answers” preserves answer accuracy before that penalty. GPT costs are list-price proxies; Claude costs are CLI-reported provider estimates. Neither is an actual subscription bill.</p>
        </div>

        <div className="result-block speed-block">
          <div className="result-title"><div><p className="panel-label">SPEED COMPARISON</p><h3>How long each run took</h3></div><p>Wall time · shorter is faster · bars use a log scale</p></div>
          <div className="speed-chart">
            {[...tournamentRows].sort((a, b) => a.timeMs - b.timeMs).map((row) => {
              const width = Math.max(2, Math.log10(row.timeMs + 1) / Math.log10(maxTournamentTime + 1) * 100);
              return <div className="speed-row" key={`speed-${row.name}-${row.lane}`}>
                <div><b>{row.name}</b><span className={`lane-badge lane-${row.lane.toLowerCase()}`}>{laneLabel(row.lane)}</span></div>
                <div className="speed-track"><i style={{ width: `${width}%` }} /></div>
                <strong>{formatTime(row.timeMs)}</strong><small>{speedMultiple(row.timeMs)}</small>
              </div>;
            })}
            <p className="speed-note">Descriptive subscription-CLI wall time, including provider and harness overhead. It is not a controlled API-serving latency benchmark.</p>
          </div>
        </div>

        <div className="lane-breakouts">
          {(["A", "B", "C"] as Lane[]).map((lane) => <section key={lane}>
            <div><span className={`lane-badge lane-${lane.toLowerCase()}`}>Lane {lane}</span><h3>{lane === "A" ? "Reasoning only" : lane === "B" ? "Tools available" : "Deterministic root vote"}</h3></div>
            {tournamentRows.filter((row) => row.lane === lane).sort((a, b) => b.correct - a.correct).map((row) => <article key={`${lane}-${row.name}`}>
              <p><b>{row.name}</b><small>{row.provider}</small></p><strong>{row.correct}/128</strong><span>{formatTime(row.timeMs)} · {row.toolCalls} tools{row.invalidTrials ? ` · ${row.invalidTrials} invalid` : ""}</span>
            </article>)}
          </section>)}
        </div>

        <div className="tournament-boundary">
          <div><h3>C did not receive the roots.</h3><p>Every lane received the same raw records and immediate parent links. C followed those links to derive origins itself. No lane received the hidden answer key, a root map, a root count, or precomputed root IDs.</p></div>
          <div><h3>What this result does not prove.</h3><p>It tests conformance to a constructed distinct-origin rule under complete, truthful lineage. It does not prove that real-world roots are honest, independent, current, authorized, or ultimately true.</p></div>
          <div className="tournament-links"><a href="/research/capability-tournament-v1-results.md">Read the full result ↗</a><a href="/research/capability-tournament-v1-protocol.md">Read the frozen protocol ↗</a></div>
        </div>
      </section>

      <section className="dashboard-section" id="dashboard">
        <div className="section-heading">
          <div><p className="section-index">03 / EPISTEMIC OBSERVATORY</p><h2>World <em>MP-00001</em></h2></div>
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
        <p className="demo-disclaimer">Interactive synthetic demonstration · Tournament results above come from the separate frozen Capability Tournament v1.</p>
      </section>

      <section className="boundary" id="boundary">
        <p className="section-index">04 / THE ARCHITECTURAL BOUNDARY</p>
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
        <p className="section-index">05 / NON-NEGOTIABLE PRINCIPLES</p>
        <h2>Never confuse—</h2>
        <div className="principle-grid">
          {["Consensus / Truth", "Popularity / Evidence", "Confidence / Correctness", "Reputation / Competence", "Correlation / Independence", "Majority / Reality"].map((item, index) => {
            const [left, right] = item.split(" / ");
            return <article key={item}><span>0{index + 1}</span><p><s>{left}</s><b>{right}</b></p></article>;
          })}
        </div>
      </section>

      <section className="run" id="run">
        <div><p className="section-index">06 / REPRODUCIBLE V0.1</p><h2>Run the<br /><em>baselines.</em></h2></div>
        <div className="terminal"><div><i /><i /><i /><span>minority-prophet / v0.1</span></div><pre><code><b>$</b> python -m benchmark --worlds 500 --seed 7{"\n\n"}<span>Generating synthetic worlds...</span>{"\n"}<span>Evaluating reproducible baselines...</span>{"\n"}<strong>Report ready.</strong></code></pre></div>
      </section>

      <footer id="foundations"><div className="mark">MP</div><p>A benchmark for<br />evidence-aware aggregation.</p><span>Public research · v0.1 · 2026</span></footer>
    </main>
  );
}
