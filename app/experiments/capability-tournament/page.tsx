import type { Metadata } from "next";
import { SiteFooter, SiteNav } from "../../components/site-chrome";
import { formatTime, formatTokens, laneDetails, laneLabel, type Lane, recordedCosts, tournamentRows } from "../../lib/tournament";

export const metadata: Metadata = {
  title: "Capability Tournament v1 — Minority Prophet",
  description: "A same-input comparison of AI reasoning, tool-using AI, conventional voting, and deterministic distinct-root aggregation.",
};

const maxTournamentTime = Math.max(...tournamentRows.map((row) => row.timeMs));
const speedMultiple = (timeMs: number) => {
  if (timeMs === 18.7) return "C reference";
  if (timeMs < 18.7) return `${(18.7 / timeMs).toFixed(1)}× faster than C`;
  return `${Math.round(timeMs / 18.7).toLocaleString("en-US")}× slower than C`;
};

export default function CapabilityTournamentPage() {
  return <main>
    <SiteNav />
    <header className="experiment-hero tournament-page-hero">
      <div><p className="eyebrow"><span /> CAPABILITY TOURNAMENT V1</p><h1>Same packet.<br /><em>Three lanes.</em></h1><p className="lede">A frozen, same-input comparison of unaided AI reasoning, tool-using AI, conventional voting, and deterministic distinct-root aggregation.</p></div>
      <div className="experiment-hero-result"><span>CLEAN RUN</span><strong>128 / 128</strong><small>canonical dispositions · 8 cases</small><p>18.7 ms · $0 model cost</p></div>
    </header>

    <section className="cost-section" aria-labelledby="cost-heading">
      <div><p className="section-index">01 / COST VISIBILITY</p><h2 id="cost-heading">What the recorded runs<br /><em>approximately cost.</em></h2></div>
      <div className="cost-grid">
        <article><span>OPENAI / CODEX</span><strong>{`≈ $${recordedCosts.openAI.toFixed(2)}`}</strong><p>List-price proxy from recorded input and output tokens.</p></article>
        <article><span>ANTHROPIC / CLAUDE CODE</span><strong>{`≈ $${recordedCosts.claude.toFixed(2)}`}</strong><p>CLI-reported provider estimate for completed telemetry.</p></article>
        <article className="cost-total"><span>COMBINED RECORDED ESTIMATE</span><strong>{`≈ $${recordedCosts.combined.toFixed(2)}`}</strong><p>Comparison estimate, not an invoice or subscription bill.</p></article>
        <article className="cost-canonical"><span>CANONICAL LANE C</span><strong>$0 model cost</strong><p>Deterministic code; compute and hosting are not claimed to be free.</p></article>
      </div>
      <p className="cost-boundary">Approximate only. GPT figures are list-price proxies; Claude figures are CLI provider estimates. The total excludes an unreturned timed-out attempt and does not represent actual account billing.</p>
    </section>

    <section className="leaderboard-section tournament-detail" id="results">
      <div className="section-heading tournament-heading"><div><p className="section-index">02 / THE TEST</p><h2>One input.<br /><em>Different capabilities.</em></h2></div><div className="verified-stamp"><i /> CLEAN RUN · 8 CASES · 128 DECISIONS</div></div>
      <div className="lane-grid" aria-label="Tournament lane definitions">{laneDetails.map((item) => <article key={item.lane} className={`lane-card lane-${item.lane.toLowerCase()}`}><span>LANE {item.lane}</span><h3>{item.title}</h3><p>{item.copy}</p></article>)}</div>
      <div className="headline-result"><div><span>CANONICAL C</span><strong>128 / 128</strong><small>correct dispositions</small></div><p>Minority Prophet completed the frozen task in <b>18.7 milliseconds</b> with zero model tokens. The most accurate GPT reasoning lane took <b>365.0 seconds</b>: about <b>19,519× longer</b>.</p></div>

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
    <SiteFooter />
  </main>;
}
