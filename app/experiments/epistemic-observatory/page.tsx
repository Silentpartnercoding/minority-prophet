import type { Metadata } from "next";
import { SiteFooter, SiteNav } from "../../components/site-chrome";
import { Observatory } from "./observatory";

export const metadata: Metadata = {
  title: "Epistemic Observatory — Minority Prophet",
  description: "An interactive synthetic world showing why copied claims are not independent evidence.",
};

export default function EpistemicObservatoryPage() {
  return <main>
    <SiteNav />
    <header className="experiment-hero observatory-page-hero">
      <div><p className="eyebrow"><span /> INTERACTIVE SYNTHETIC DEMONSTRATION</p><h1>Three witnesses.<br /><em>Ninety-five echoes.</em></h1><p className="lede">Explore a generated world where three independent instruments report the constructed truth while ninety-five copied claims repeat one false origin.</p></div>
      <div className="experiment-hero-result"><span>WORLD MP-00001</span><strong>03 : 95</strong><small>independent truth / copied falsehood</small><p>Generated world · seed 7</p></div>
    </header>
    <section className="observatory-intro"><p className="section-index">01 / HOW TO READ IT</p><div><h2>Follow the lineage.<br /><em>Count the origins.</em></h2><p>Filter the claims, select a row, and inspect where it came from. The majority looks large only until its copies collapse back to the same source.</p></div><div className="demo-boundary-card"><span>BOUNDARY</span><p>The ancestry is built into this generated world. It demonstrates the mechanism; it does not validate real sources.</p></div></section>
    <section className="dashboard-section observatory-detail"><div className="section-heading"><div><p className="section-index">02 / EPISTEMIC OBSERVATORY</p><h2>World <em>MP-00001</em></h2></div><div className="live"><i /> SYNTHETIC WORLD · SEED 7</div></div><Observatory /><p className="demo-disclaimer">Interactive generated world. No model is called by this page.</p></section>
    <section className="observatory-takeaway"><p className="section-index">03 / THE TAKEAWAY</p><h2>Ninety-five votes<br />can still be <em>one claim.</em></h2><p>Lineage changes the unit being counted. Instead of rewarding repetition, the demonstration counts distinguishable evidence origins and preserves uncertainty when provenance is incomplete.</p><a className="preview-link" href="/experiments/epistemic-lift">See the measured lift study <span>→</span></a></section>
    <SiteFooter />
  </main>;
}
