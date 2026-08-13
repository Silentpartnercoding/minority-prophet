import type { Metadata } from "next";
import { SiteFooter, SiteNav } from "../../components/site-chrome";
import { formatPercent, liftModels, liftStudy } from "../../lib/lift-study";

export const metadata: Metadata = {
  title: "Epistemic Lift Study v1.1 — Minority Prophet",
  description: "A same-model, same-world A/B/C study measuring provenance gain and Minority Prophet lift under correlated false consensus.",
};

const conditions = [
  { lane: "A", title: "Raw baseline", copy: "The model receives claims and ordinary source labels. It receives no ancestry and no hint about correlated consensus." },
  { lane: "B", title: "+ Provenance", copy: "The same model receives the same world plus complete declared ancestry, timestamps, control domains, and observation origins." },
  { lane: "C", title: "+ Minority Prophet", copy: "The exact B payload gains one deterministic, read-only evidence-structure receipt. It contains no ground truth or recommended answer." },
];

export default function EpistemicLiftPage() {
  return <main>
    <SiteNav />
    <header className="experiment-hero lift-page-hero">
      <div><p className="eyebrow"><span /> EPISTEMIC LIFT v1.1 · DEVELOPMENT STUDY</p><h1>Same model.<br />Same world.<br /><em>Measure the lift.</em></h1><p className="lede">Every model faced the same 32 frozen worlds three ways: claims alone, claims plus provenance, and the identical provenance plus Minority Prophet&apos;s deterministic evidence-structure receipt.</p></div>
      <div className="lift-hero-result"><span>COMPLETE LOCAL REPLICATION</span><strong>{liftStudy.trials}/{liftStudy.trials}</strong><small>model × world × condition cells</small><p>0 failures · 0 parse errors · all integrity checks passed</p></div>
    </header>

    <section className="lift-result-section" id="results">
      <div className="lift-heading"><p className="section-index">01 / PRIMARY RESULT</p><h2>Provenance helped.<br /><em>The MP receipt helped again.</em></h2><p>Both tested configurations exceeded the frozen requirement: at least 15 percentage points of C-over-B lift and an exact paired p-value below 0.05.</p></div>
      <div className="lift-models">
        {liftModels.map((model) => <article className="lift-model" key={model.name}>
          <header><div><span>{model.provider}</span><h3>{model.name}</h3></div><div className="lift-badge">C − B <b>+{formatPercent(model.mpGain)}</b></div></header>
          <div className="lift-bars" aria-label={`${model.name}: baseline ${formatPercent(model.baseline)}, provenance ${formatPercent(model.provenance)}, Minority Prophet ${formatPercent(model.minorityProphet)}`}>
            <div><span>A · BASELINE</span><i><b style={{ width: `${model.baseline}%` }} /></i><strong>{formatPercent(model.baseline)}</strong></div>
            <div><span>B · PROVENANCE</span><i><b style={{ width: `${model.provenance}%` }} /></i><strong>{formatPercent(model.provenance)}</strong></div>
            <div className="mp-bar"><span>C · + MINORITY PROPHET</span><i><b style={{ width: `${model.minorityProphet}%` }} /></i><strong>{formatPercent(model.minorityProphet)}</strong></div>
          </div>
          <footer><span>B − A <b>+{formatPercent(model.provenanceGain)}</b></span><span>C − B <b>+{formatPercent(model.mpGain)}</b></span><span>Exact paired p <b>{model.pairedP}</b></span><span>Transitions <b>{model.improvements} better · {model.regressions} worse</b></span></footer>
        </article>)}
      </div>
      <p className="lift-claim">On this frozen 32-world development candidate, both models showed more than 20 percentage points of paired truth-recovery lift from B to C, with zero regressions.</p>
    </section>

    <section className="lift-design-section">
      <div className="lift-heading"><p className="section-index">02 / CAUSAL DESIGN</p><h2>Only the epistemic<br /><em>information changed.</em></h2><p>The question, world, model version, system prompt, sampling settings, and B/C provenance payload were held fixed. Condition order covered all six A/B/C permutations.</p></div>
      <div className="lift-condition-grid">{conditions.map((condition) => <article className={`lift-condition lift-${condition.lane.toLowerCase()}`} key={condition.lane}><span>CONDITION {condition.lane}</span><h3>{condition.title}</h3><p>{condition.copy}</p></article>)}</div>
      <div className="lift-control-strip"><span>32 worlds</span><i>×</i><span>2 models</span><i>×</i><span>3 conditions</span><i>=</i><strong>192 matched cells</strong></div>
    </section>

    <section className="lift-integrity-section">
      <div><p className="section-index">03 / INTEGRITY</p><h2>Measured,<br /><em>not inferred.</em></h2></div>
      <div className="integrity-grid"><article><strong>192/192</strong><span>responses captured and parsed</span></article><article><strong>64/64</strong><span>model-world A/B/C groups matched</span></article><article><strong>0</strong><span>failed trials or B→C regressions</span></article><article><strong>6</strong><span>condition orders counterbalanced</span></article></div>
      <div className="integrity-copy"><h3>What the tool received</h3><p>Only the exact bytes already visible in B: claims, sources, declared provenance edges, and context. Hidden truth labels were rejected. The receipt reported roots, correlation, current evidence units, and uncertainty—but never a correct answer or permission.</p><h3>What this result does not establish</h3><p>These are synthetic development worlds co-designed with the analysis. The earlier transport run exposed outcomes on the same worlds. This is therefore a complete transport-controlled replication, not an independent confirmation or real-world truth claim.</p></div>
    </section>

    <section className="lift-next-section"><p className="section-index">04 / EVIDENCE BOUNDARY</p><h2>Supported here.<br /><em>Not universal yet.</em></h2><p>The next scientific step is a larger hidden benchmark generated or audited independently of the MP engine, with contamination controls and prospective power. Until then, this result remains a validated DEMO development study—not an official leaderboard entry.</p><div className="lift-links"><a href="/research/epistemic-lift-v1.1-results.md">Full result ↗</a><a href="/research/epistemic-lift-v1.1-protocol.md">Frozen protocol ↗</a><a href="/research/epistemic-lift-v1.1-summary.json">Machine-readable summary ↗</a><a href="/experiments/capability-tournament">Separate conformance study ↗</a></div></section>
    <SiteFooter />
  </main>;
}
