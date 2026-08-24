import type { Metadata } from "next";
import { SiteFooter, SiteNav } from "../components/site-chrome";
import { SourceFamilyExplainer } from "./source-family-explainer";

export const metadata: Metadata = {
  title: "Source-Family Explainer — Minority Prophet",
  description: "A 90-second interactive explanation of why six agent claims can contain only three source families.",
};

export default function SourceFamilyTestPage() {
  return <main className="source-family-page">
    <SiteNav />
    <header className="overview-hero source-family-page-hero">
      <div>
        <p className="eyebrow"><span /> SOURCE INDEPENDENCE · 90-SECOND EXPLAINER</p>
        <h1>Six claims.<br /><em>Three actual sources.</em></h1>
        <p className="lede">Ordinary logs count what agents said. Minority Prophet preserves every claim, then reconstructs where the evidence actually came from.</p>
      </div>
      <div className="impact-panel source-family-impact">
        <span>THE COUNTING UNITS</span>
        <article><b>06</b><p>Claim events</p></article>
        <article><b>06</b><p>Unique actors</p></article>
        <article><b>03</b><p>Source families</p></article>
      </div>
    </header>

    <section className="source-family-page-intro">
      <p className="section-index">01 / WHAT TO DO</p>
      <div><h2>Read the log.<br /><em>Then reveal its ancestry.</em></h2><p>The six responses do not change. Only the unit being counted changes—from agent outputs to recorded evidence origins.</p></div>
      <aside><b>DEMO · NOT A TEST</b><p>You are not being graded. There are no questions, no account, and nothing is submitted.</p></aside>
    </section>

    <SourceFamilyExplainer />

    <section className="boundary source-family-page-boundary">
      <p className="section-index">03 / THE BOUNDARY</p>
      <div className="boundary-heading"><h2>Reconstruction is not<br /><em>authorization.</em></h2><p>The graph can show that four agreeing agents represent only two supporting roots. It cannot prove the minority correct, determine policy, or grant permission to act.</p></div>
      <div className="boundary-flow">
        <article><span>01</span><h3>Preserve</h3><p>Keep all six claims and all six actors visible.</p></article>
        <article><span>02</span><h3>Trace</h3><p>Follow copies and summaries back to their recorded origins.</p></article>
        <article><span>03</span><h3>Recount</h3><p>Count distinguishable source families instead of repetitions.</p></article>
        <article><span>04</span><h3>Escalate</h3><p>Let separate policy decide whether more evidence is required.</p></article>
      </div>
    </section>
    <SiteFooter />
  </main>;
}
