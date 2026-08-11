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
const speedMultiple = (timeMs: number) => {
  if (timeMs === 18.7) return "C reference";
  if (timeMs < 18.7) return `${(18.7 / timeMs).toFixed(1)}× faster than C`;
  return `${Math.round(timeMs / 18.7).toLocaleString("en-US")}× slower than C`;
};

export default function CapabilityTournamentPage() {
  return <main>
    <SiteNav />
    <header className="experiment-hero tournament-page-hero">
      <div><p className="eyebrow"><span /> CAPABILITY TOURNAMENT · CONFORMANCE STUDY</p><h1>Same packet.<br /><em>Different methods.</em></h1><p className="lede">This is a bounded conformance comparison: general models, tool-using agents, conventional algorithms, and a deterministic evidence rule handle the same frozen complete-lineage packet. It is not the Baseline → Provenance → Minority Prophet lift experiment.</p></div>
      <div className="tournament-promise"><span>OUR PUBLIC COMMITMENT</span><h2>Keep the comparison inspectable.</h2><ul><li>Freeze protocols before execution.</li><li>Give every lane the same public packet.</li><li>Preserve failures, raw scores, costs, and boundaries.</li><li>Add new models as labeled extensions.</li><li>Repeat before making broader claims.</li></ul></div>
    </header>

    <section className="study-warning" aria-labelledby="study-warning-heading">
      <p className="section-index">READ THIS FIRST</p>
      <div><h2 id="study-warning-heading">Eight cases.<br /><em>Not 128 independent trials.</em></h2><p>The packet contains eight generated cases with 16 related dispositions inside each case. The 128 decisions are useful for inspecting rule execution, but they do not supply 128 statistically independent replications.</p></div>
      <div className="study-warning-points"><article><b>C is code, not an augmented model.</b><p>Condition C runs the canonical deterministic root vote. It is not the same model receiving Minority Prophet output, so C minus B is not a Minority Prophet gain estimate.</p></article><article><b>The lineage is complete and truthful by construction.</b><p>The result checks whether methods recover a declared distinct-origin rule. It does not test hidden copying, forged roots, missing provenance, source honesty, or external truth.</p></article></div>
    </section>

    <section className="scale-section scale-section-summary" aria-labelledby="scale-heading">
      <div className="scale-story">
        <p className="section-index">01 / WHY THIS JUNCTION MATTERS</p>
        <h2 id="scale-heading">Agents will talk<br /><em>faster than humans can check.</em></h2>
        <p>In an agent-to-agent system, claims, receipts, delegated tasks, and proposed actions can cross service boundaries continuously. This exercise asks whether a known lineage rule is better implemented as transparent code than re-inferred from scratch inside each bounded packet.</p>
        <p>A deterministic verifier gives that fast-moving network a small, transparent checkpoint and sends only unresolved cases onward for judgment.</p>
      </div>
      <div className="network-flow" aria-label="An agent claim passes through evidence binding and deterministic assessment before separate policy or human review">
        <article><span>01</span><b>Agent sends</b><small>claim + lineage</small></article><i>→</i><article><span>02</span><b>Evidence binds</b><small>records + context</small></article><i>→</i><article className="flow-highlight"><span>03</span><b>Rule checks</b><small>origins + exact ties</small></article><i>→</i><article><span>04</span><b>Decision routes</b><small>policy or human</small></article>
      </div>
      <div className="scale-comparison">
        <div className="scale-measured"><span>OBSERVED ON ONE EIGHT-CASE PACKET</span><article><b>Canonical C</b><strong>128/128</strong><small>18.7 ms · $0 model calls</small></article><article><b>Best AI lane · Terra A</b><strong>116/128</strong><small>365.0 s · ≈ $0.89 proxy</small></article></div>
        <div className="scale-illustration"><div className="scale-illustration-heading"><span>DESCRIPTIVE TELEMETRY · NOT A CAPACITY FORECAST</span><strong>Terra A took ≈ {scaleTimeRatio}× the elapsed time in this observed packet.</strong></div><p className="scale-caveat">The methods ran through different execution paths: local deterministic code versus subscription-backed model CLI calls. The ratio describes this run only. It must not be linearly projected to production throughput, latency, or cost.</p></div>
        <p>No production scaling claim is made. Concurrency, batching, hardware, network overhead, provider behavior, prices, and packet shape can all change the comparison.</p>
      </div>
      <div className="scale-takeaway"><span>THE VALUE</span><p>Use expensive probabilistic intelligence where judgment is needed. Use deterministic code where the invariant is already known. At scale, that separation keeps the agent network fast without turning uncertainty into permission.</p></div>
    </section>

    <section className="cost-section" aria-labelledby="cost-heading">
      <div className="cost-heading"><p className="section-index">02 / OBSERVED TELEMETRY BY LANE</p><h2 id="cost-heading">No combined score.<br /><em>Every run stands alone.</em></h2><p>Each amount below belongs to one contestant lane running the full eight-case packet. Cost, accuracy, and time stay attached to that exact run; they do not establish stable provider rankings.</p></div>
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
      <div className="section-heading tournament-heading"><div><p className="section-index">03 / THE TEST</p><h2>One input.<br /><em>Different capabilities.</em></h2></div></div>
      <div className="lane-grid" aria-label="Tournament lane definitions">{laneDetails.map((item) => <article key={item.lane} className={`lane-card lane-${item.lane.toLowerCase()}`}><span>LANE {item.lane}</span><h3>{item.title}</h3><p>{item.copy}</p></article>)}</div>

      <div className="result-block">
        <div className="result-title"><div><p className="panel-label">DESCRIPTIVE RESULT TABLE</p><h3>Observed scores, not stable ranks</h3></div><p>One clean replicate · eight cases · correlated within-case dispositions</p></div>
        <div className="leaderboard-table-wrap"><table className="leaderboard-table"><thead><tr><th>Contestant</th><th>Lane</th><th>Protocol score</th><th>Raw answers</th><th>Exact cases</th><th>Invalid trials</th><th>Wall time</th><th>Tools</th><th>Input / output tokens</th><th>Cost estimate</th></tr></thead>
          <tbody>{[...tournamentRows].sort((a, b) => b.correct - a.correct || a.timeMs - b.timeMs).map((row) => <tr key={`${row.name}-${row.lane}`}><td><b>{row.name}</b><small>{row.provider}</small></td><td><span className={`lane-badge lane-${row.lane.toLowerCase()}`}>{laneLabel(row.lane)}</span></td><td><strong>{row.correct}/128</strong></td><td>{row.rawCorrect ?? row.correct}/128</td><td>{row.exact}/8{row.rawExact !== undefined && row.rawExact !== row.exact ? ` (${row.rawExact} raw)` : ""}</td><td>{row.invalidTrials}/8</td><td>{formatTime(row.timeMs)}</td><td>{row.toolCalls}</td><td>{formatTokens(row.inputTokens)} / {formatTokens(row.outputTokens)}</td><td>{row.cost === 0 ? "$0 model cost" : row.cost ? `$${row.cost.toFixed(3)}` : "—"}</td></tr>)}</tbody>
        </table></div>
        <p className="speed-note table-boundary">Lane B means tools were available, not necessarily used. “Protocol score” counts failed or workspace-boundary-violating trials as incorrect; “Raw answers” preserves answer accuracy before that penalty. With one replicate per model and lane, differences are descriptive and have no confidence intervals or paired significance test.</p>
      </div>

      <div className="result-block speed-block"><div className="result-title"><div><p className="panel-label">SPEED COMPARISON</p><h3>How long each run took</h3></div><p>Wall time · shorter is faster · logarithmic bars</p></div><div className="speed-chart">
        {[...tournamentRows].sort((a, b) => a.timeMs - b.timeMs).map((row) => { const width = Math.max(2, Math.log10(row.timeMs + 1) / Math.log10(maxTournamentTime + 1) * 100); return <div className="speed-row" key={`speed-${row.name}-${row.lane}`}><div><b>{row.name}</b><span className={`lane-badge lane-${row.lane.toLowerCase()}`}>{laneLabel(row.lane)}</span></div><div className="speed-track"><i style={{ width: `${width}%` }} /></div><strong>{formatTime(row.timeMs)}</strong><small>{speedMultiple(row.timeMs)}</small></div>; })}
        <p className="speed-note">Descriptive subscription-CLI wall time, including provider and harness overhead. This is not a controlled API-serving latency benchmark.</p>
      </div></div>

      <div className="lane-breakouts">{(["A", "B", "C"] as Lane[]).map((lane) => <section key={lane}><div><span className={`lane-badge lane-${lane.toLowerCase()}`}>Lane {lane}</span><h3>{lane === "A" ? "Reasoning only" : lane === "B" ? "Tools available" : "Deterministic root vote"}</h3></div>{tournamentRows.filter((row) => row.lane === lane).sort((a, b) => b.correct - a.correct).map((row) => <article key={`${lane}-${row.name}`}><p><b>{row.name}</b><small>{row.provider}</small></p><strong>{row.correct}/128</strong><span>{formatTime(row.timeMs)} · {row.toolCalls} tools{row.invalidTrials ? ` · ${row.invalidTrials} invalid` : ""}</span></article>)}</section>)}</div>

      <div className="tournament-boundary"><div><h3>C did not receive the roots.</h3><p>Every lane received the same raw records and immediate parent links. C followed those links to derive origins itself. No lane received the hidden answer key, a root map, a root count, or precomputed root IDs.</p></div><div><h3>This is not the lift study.</h3><p>Tournament A and B both received complete lineage, while C is deterministic code rather than the same model plus Minority Prophet analysis. These lanes cannot estimate Baseline → Provenance gain, Minority Prophet gain, H1, H2, or H3.</p></div><div><h3>What this result does not prove.</h3><p>It tests conformance to a constructed distinct-origin rule under complete, truthful lineage. It does not prove that real-world roots are honest, independent, current, authorized, or ultimately true.</p></div><div><h3>What comes next.</h3><p>A separate causal study must run the same model and immutable world under claims only, claims plus provenance, and the identical provenance plus non-answer-leaking Minority Prophet analysis, with repeated seeds and paired uncertainty estimates.</p></div><div className="tournament-links"><a href="/research/capability-tournament-v1-results.md">Read the full result ↗</a><a href="/research/capability-tournament-v1-protocol.md">Read the frozen protocol ↗</a><a href="/research/capability-tournament-v1-adversarial-review.md">Read the adversarial review ↗</a><a href="/research/capability-tournament-v1-summary.json">Machine-readable boundary ↗</a></div></div>
    </section>

    <SiteFooter />
  </main>;
}
