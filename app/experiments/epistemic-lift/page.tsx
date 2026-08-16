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
      <div><p className="eyebrow"><span /> EPISTEMIC LIFT · CONTROLLED SYNTHETIC STUDY</p><h1>Same model.<br />Same world.<br /><em>Measure the lift.</em></h1><p className="lede">Two models faced the same 32 worlds three ways: claims alone, provenance, and provenance plus a Minority Prophet evidence receipt.</p></div>
      <div className="lift-hero-result"><span>192 MATCHED CELLS</span><strong>{liftStudy.trials}/{liftStudy.trials}</strong><small>model × world × condition</small><p>0 failures · 0 parse errors · integrity checks passed</p></div>
    </header>

    <section className="lift-result-section" id="results">
      <div className="lift-heading"><p className="section-index">01 / PRIMARY RESULT</p><h2>Provenance helped.<br /><em>The MP receipt helped again.</em></h2><p>Both tested models cleared the pre-set threshold for C-over-B lift and paired significance.</p></div>
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
      <p className="lift-claim">Across these 32 frozen worlds, both models gained more than 20 percentage points from B to C, with no B-to-C regressions.</p>
    </section>

    <section className="lift-design-section">
      <div className="lift-heading"><p className="section-index">02 / CAUSAL DESIGN</p><h2>Only the epistemic<br /><em>information changed.</em></h2><p>The question, world, model version, system prompt, sampling settings, and B/C provenance payload were held fixed. Condition order covered all six A/B/C permutations.</p></div>
      <div className="lift-condition-grid">{conditions.map((condition) => <article className={`lift-condition lift-${condition.lane.toLowerCase()}`} key={condition.lane}><span>CONDITION {condition.lane}</span><h3>{condition.title}</h3><p>{condition.copy}</p></article>)}</div>
      <div className="lift-control-strip"><span>32 worlds</span><i>×</i><span>2 models</span><i>×</i><span>3 conditions</span><i>=</i><strong>192 matched cells</strong></div>
    </section>

    <section className="lift-integrity-section">
      <div><p className="section-index">03 / INTEGRITY</p><h2>Measured,<br /><em>not inferred.</em></h2></div>
      <div className="integrity-grid"><article><strong>192/192</strong><span>responses captured and parsed</span></article><article><strong>64/64</strong><span>model-world A/B/C groups matched</span></article><article><strong>0</strong><span>failed trials or B→C regressions</span></article><article><strong>6</strong><span>condition orders counterbalanced</span></article></div>
      <div className="integrity-copy"><h3>What the tool received</h3><p>The same claims, sources, provenance, and context already visible in B. It returned roots, dependence, and uncertainty—never the answer key or permission to act.</p><h3>Where the evidence ends</h3><p>These are synthetic worlds designed with the method. They show controlled lift here, not independent confirmation or real-world truth recovery.</p></div>
    </section>

    <section className="lift-next-section"><p className="section-index">04 / EVIDENCE BOUNDARY</p><h2>Strong here.<br /><em>Unproven elsewhere.</em></h2><p>A hidden, independently audited benchmark is the next test. Until then, these numbers belong to this study alone.</p><div className="lift-links"><a href="/research/epistemic-lift-v1.1-results.md">Full result ↗</a><a href="/research/epistemic-lift-v1.1-protocol.md">Frozen protocol ↗</a><a href="/research/epistemic-lift-v1.1-summary.json">Machine-readable summary ↗</a><a href="/experiments/capability-tournament">Separate method study ↗</a></div></section>
    <SiteFooter />
  </main>;
}
