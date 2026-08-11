import type { Metadata } from "next";
import { SiteFooter, SiteNav } from "../../components/site-chrome";
import { formatTime, formatTokens, laneDetails, laneLabel, type Lane, tournamentRows } from "../../lib/tournament";

export const metadata: Metadata = {
  title: "Capability Tournament v1 — Minority Prophet",
  description: "A same-input comparison of AI reasoning, tool-using AI, conventional voting, and deterministic distinct-root aggregation.",
};

const maxTournamentTime = Math.max(...tournamentRows.map((row) => row.timeMs));
const costOrder = ["Minority Prophet", "GPT-5.6 Terra", "Claude Opus 5", "GPT-5.6 Sol", "Cluster vote", "Claude Sonnet 5", "GPT-5.6 Luna", "Claude Haiku 4.5"];
const costGroups = costOrder.map((name) => ({ name, rows: tournamentRows.filter((row) => row.name === name).sort((a, b) => a.lane.localeCompare(b.lane)) }));
const bestAiLane = tournamentRows.find((row) => row.name === "GPT-5.6 Terra" && row.lane === "A")!;
const canonicalLane = tournamentRows.find((row) => row.name === "Minority Prophet")!;
const scaleTimeRatio = Math.round(bestAiLane.timeMs / canonicalLane.timeMs).toLocaleString("en-US");
const scaleRows = [1_000, 100_000, 1_000_000].map((dispositions) => {
  const canonicalSeconds = canonicalLane.timeMs / 128 * dispositions / 1000;
  const aiSeconds = bestAiLane.timeMs / 128 * dispositions / 1000;
  const aiCost = bestAiLane.cost! / 128 * dispositions;
  const aiDuration = aiSeconds < 3600 ? `${(aiSeconds / 60).toFixed(1)} min` : `${(aiSeconds / 86_400).toFixed(1)} days`;
  return {
    dispositions: dispositions.toLocaleString("en-US"),
    canonical: `${canonicalSeconds < 1 ? canonicalSeconds.toFixed(3) : canonicalSeconds.toFixed(1)} seconds · $0 model API`,
    ai: `${Math.round(aiSeconds).toLocaleString("en-US")} seconds (${aiDuration}) · ≈ $${aiCost < 10 ? aiCost.toFixed(2) : Math.round(aiCost).toLocaleString("en-US")}`,
    difference: `≈ ${scaleTimeRatio}× elapsed time`,
  };
});
const speedMultiple = (timeMs: number) => {
  if (timeMs === 18.7) return "C reference";
  if (timeMs < 18.7) return `${(18.7 / timeMs).toFixed(1)}× faster than C`;
  return `${Math.round(timeMs / 18.7).toLocaleString("en-US")}× slower than C`;
};

export default function CapabilityTournamentPage() {
  return <main>
    <SiteNav />
    <header className="experiment-hero tournament-page-hero">
      <div><p className="eyebrow"><span /> CAPABILITY TOURNAMENT</p><h1>Same packet.<br /><em>Different methods.</em></h1><p className="lede">The Capability Tournament is an ongoing public comparison of how general models, tool-using agents, conventional algorithms, and deterministic evidence rules handle the same frozen challenge. It matters because fast agent networks need to know which decisions require probabilistic judgment and which should become transparent, repeatable code.</p></div>
      <div className="tournament-promise"><span>OUR PUBLIC COMMITMENT</span><h2>Keep the comparison inspectable.</h2><ul><li>Freeze protocols before execution.</li><li>Give every lane the same public packet.</li><li>Preserve failures, raw scores, costs, and boundaries.</li><li>Add new models as labeled extensions.</li><li>Repeat before making broader claims.</li></ul></div>
    </header>

    <section className="cost-section" aria-labelledby="cost-heading">
      <div className="cost-heading"><p className="section-index">01 / COST BY MODEL AND LANE</p><h2 id="cost-heading">No combined score.<br /><em>Every run stands alone.</em></h2><p>Each amount below belongs to one contestant lane running the full eight-case packet. Cost, accuracy, and time stay attached to that exact run.</p></div>
      <div className="cost-model-grid">
        {costGroups.map((group) => <article className={group.name === "Minority Prophet" ? "canonical-cost-model" : ""} key={group.name}>
          <header><h3>{group.name}</h3><span>{group.rows[0]?.provider}</span></header>
          {group.rows.map((row) => <div className="cost-lane-row" key={`${row.name}-${row.lane}`}>
            <span className={`lane-badge lane-${row.lane.toLowerCase()}`}>{laneLabel(row.lane)}</span>
            <p><b>{row.correct}/128</b>{row.rawCorrect !== undefined && row.rawCorrect !== row.correct ? <small>{row.rawCorrect}/128 raw</small> : <small>protocol score</small>}</p>
            <p><b>{formatTime(row.timeMs)}</b><small>wall time</small></p>
            <p className="individual-cost"><b>{row.cost === 0 ? "$0 model" : row.cost ? `≈ $${row.cost.toFixed(2)}` : "—"}</b><small>{row.cost === 0 ? "model cost" : "run estimate"}</small></p>
          </div>)}
        </article>)}
      </div>
      <p className="cost-boundary">No costs are added together. GPT figures are API list-price proxies; Claude figures are CLI-reported provider estimates. They are not invoices or controlled API-cost measurements. Haiku B excludes cost telemetry for one timed-out attempt that returned no completed usage record.</p>
    </section>

    <section className="leaderboard-section tournament-detail" id="results">
      <div className="section-heading tournament-heading"><div><p className="section-index">02 / THE TEST</p><h2>One input.<br /><em>Different capabilities.</em></h2></div></div>
      <div className="lane-grid" aria-label="Tournament lane definitions">{laneDetails.map((item) => <article key={item.lane} className={`lane-card lane-${item.lane.toLowerCase()}`}><span>LANE {item.lane}</span><h3>{item.title}</h3><p>{item.copy}</p></article>)}</div>

      <div className="result-block">
        <div className="result-title"><div><p className="panel-label">OVERALL LEADERBOARD</p><h3>Accuracy first</h3></div><p>One clean replicate · GPT/Codex initial grid · preregistered Claude extension</p></div>
        <div className="leaderboard-table-wrap"><table className="leaderboard-table"><thead><tr><th>Rank</th><th>Contestant</th><th>Lane</th><th>Protocol score</th><th>Raw answers</th><th>Exact cases</th><th>Invalid trials</th><th>Wall time</th><th>Tools</th><th>Input / output tokens</th><th>Cost estimate</th></tr></thead>
          <tbody>{[...tournamentRows].sort((a, b) => b.correct - a.correct || a.timeMs - b.timeMs).map((row, index) => <tr key={`${row.name}-${row.lane}`}><td>{String(index + 1).padStart(2, "0")}</td><td><b>{row.name}</b><small>{row.provider}</small></td><td><span className={`lane-badge lane-${row.lane.toLowerCase()}`}>{laneLabel(row.lane)}</span></td><td><strong>{row.correct}/128</strong></td><td>{row.rawCorrect ?? row.correct}/128</td><td>{row.exact}/8{row.rawExact !== undefined && row.rawExact !== row.exact ? ` (${row.rawExact} raw)` : ""}</td><td>{row.invalidTrials}/8</td><td>{formatTime(row.timeMs)}</td><td>{row.toolCalls}</td><td>{formatTokens(row.inputTokens)} / {formatTokens(row.outputTokens)}</td><td>{row.cost === 0 ? "$0 model cost" : row.cost ? `$${row.cost.toFixed(3)}` : "—"}</td></tr>)}</tbody>
        </table></div>
        <p className="speed-note table-boundary">Lane B means tools were available, not necessarily used. “Protocol score” counts failed or workspace-boundary-violating trials as incorrect; “Raw answers” preserves answer accuracy before that penalty.</p>
      </div>

      <div className="result-block speed-block"><div className="result-title"><div><p className="panel-label">SPEED COMPARISON</p><h3>How long each run took</h3></div><p>Wall time · shorter is faster · logarithmic bars</p></div><div className="speed-chart">
        {[...tournamentRows].sort((a, b) => a.timeMs - b.timeMs).map((row) => { const width = Math.max(2, Math.log10(row.timeMs + 1) / Math.log10(maxTournamentTime + 1) * 100); return <div className="speed-row" key={`speed-${row.name}-${row.lane}`}><div><b>{row.name}</b><span className={`lane-badge lane-${row.lane.toLowerCase()}`}>{laneLabel(row.lane)}</span></div><div className="speed-track"><i style={{ width: `${width}%` }} /></div><strong>{formatTime(row.timeMs)}</strong><small>{speedMultiple(row.timeMs)}</small></div>; })}
        <p className="speed-note">Descriptive subscription-CLI wall time, including provider and harness overhead. This is not a controlled API-serving latency benchmark.</p>
      </div></div>

      <div className="lane-breakouts">{(["A", "B", "C"] as Lane[]).map((lane) => <section key={lane}><div><span className={`lane-badge lane-${lane.toLowerCase()}`}>Lane {lane}</span><h3>{lane === "A" ? "Reasoning only" : lane === "B" ? "Tools available" : "Deterministic root vote"}</h3></div>{tournamentRows.filter((row) => row.lane === lane).sort((a, b) => b.correct - a.correct).map((row) => <article key={`${lane}-${row.name}`}><p><b>{row.name}</b><small>{row.provider}</small></p><strong>{row.correct}/128</strong><span>{formatTime(row.timeMs)} · {row.toolCalls} tools{row.invalidTrials ? ` · ${row.invalidTrials} invalid` : ""}</span></article>)}</section>)}</div>

      <div className="tournament-boundary"><div><h3>C did not receive the roots.</h3><p>Every lane received the same raw records and immediate parent links. C followed those links to derive origins itself. No lane received the hidden answer key, a root map, a root count, or precomputed root IDs.</p></div><div><h3>What this result does not prove.</h3><p>It tests conformance to a constructed distinct-origin rule under complete, truthful lineage. It does not prove that real-world roots are honest, independent, current, authorized, or ultimately true.</p></div><div className="tournament-links"><a href="/research/capability-tournament-v1-results.md">Read the full result ↗</a><a href="/research/capability-tournament-v1-protocol.md">Read the frozen protocol ↗</a></div></div>
    </section>

    <section className="scale-section" aria-labelledby="scale-heading">
      <div className="scale-story">
        <p className="section-index">03 / WHY THIS JUNCTION MATTERS</p>
        <h2 id="scale-heading">Agents will talk<br /><em>faster than humans can check.</em></h2>
        <p>In an agent-to-agent system, claims, receipts, delegated tasks, and proposed actions can cross service boundaries continuously. Re-asking a general model to rediscover a known lineage rule at every handoff adds cost, latency, and a fresh chance to change the rule.</p>
        <p>A deterministic verifier gives that fast-moving network a small, transparent checkpoint and sends only unresolved cases onward for judgment.</p>
      </div>
      <div className="network-flow" aria-label="An agent claim passes through evidence binding and deterministic assessment before separate policy or human review">
        <article><span>01</span><b>Agent sends</b><small>claim + lineage</small></article><i>→</i><article><span>02</span><b>Evidence binds</b><small>records + context</small></article><i>→</i><article className="flow-highlight"><span>03</span><b>Rule checks</b><small>origins + exact ties</small></article><i>→</i><article><span>04</span><b>Decision routes</b><small>policy or human</small></article>
      </div>
      <div className="scale-comparison">
        <div className="scale-measured"><span>MEASURED ON THE SAME 128 DISPOSITIONS</span><article><b>Canonical C</b><strong>128/128</strong><small>18.7 ms · $0 model calls</small></article><article><b>Best AI lane · Terra A</b><strong>116/128</strong><small>365.0 s · ≈ $0.89 proxy</small></article></div>
        <div className="scale-illustration"><span>SIMPLE LINEAR ILLUSTRATION · SAME SCALE, BOTH METHODS</span><div className="scale-matrix-wrap"><table className="scale-matrix"><thead><tr><th>Decisions</th><th>Canonical C</th><th>Terra A</th><th>Elapsed difference</th></tr></thead><tbody>{scaleRows.map((row) => <tr key={row.dispositions}><td>{row.dispositions}</td><td>{row.canonical}</td><td>{row.ai}</td><td>{row.difference}</td></tr>)}</tbody></table></div></div>
        <p>This illustration scales the observed per-packet rates linearly to make the operational consequence legible. It is not a production capacity, latency, or billing forecast: concurrency, batching, hardware, network overhead, provider behavior, and prices will change deployment results.</p>
      </div>
      <div className="scale-takeaway"><span>THE VALUE</span><p>Use expensive probabilistic intelligence where judgment is needed. Use deterministic code where the invariant is already known. At scale, that separation keeps the agent network fast without turning uncertainty into permission.</p></div>
    </section>
    <SiteFooter />
  </main>;
}
