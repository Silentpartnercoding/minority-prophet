"use client";

import { useState } from "react";

const claims = [
  { actor: "A", reviewer: "Reviewer A", source: "weather-17", stance: "PROCEED", family: "weather", lineage: "Original record · weather family" },
  { actor: "B", reviewer: "Reviewer B", source: "weather-cache", stance: "PROCEED", family: "weather", lineage: "Copy of weather-17 · same family" },
  { actor: "C", reviewer: "Reviewer C", source: "route-clearance-9", stance: "PROCEED", family: "route", lineage: "Independent original · route family" },
  { actor: "D", reviewer: "Reviewer D", source: "maintenance-alert-4", stance: "STOP", family: "maintenance", lineage: "Original record · maintenance family" },
  { actor: "E", reviewer: "Reviewer E", source: "maintenance-summary", stance: "STOP", family: "maintenance", lineage: "Summary of maintenance-alert-4 · same family" },
  { actor: "F", reviewer: "Reviewer F", source: "weather-brief", stance: "PROCEED", family: "weather", lineage: "Summary of weather-cache · same family" },
];

export function SourceFamilyExplainer() {
  const [revealed, setRevealed] = useState(false);
  return <section className={`source-family-demo ${revealed ? "revealed" : ""}`}>
    <div className="source-family-demo-heading"><p className="section-index">02 / INTERACTIVE RECONSTRUCTION</p><h2>Who said what?</h2><p>The ordinary view counts claims and actors. Reveal the lineage to group copied and summarized evidence.</p></div>
    <div className="source-log-panel">
      <header><span>ORDINARY LOG VIEW</span><div><b>4</b><small>PROCEED</small><b>2</b><small>STOP</small><b>6</b><small>ACTORS</small></div></header>
      <div className="source-log-feed">{claims.map((claim) => <article className={claim.family} key={claim.actor}><b>{claim.actor}</b><div><strong>{claim.reviewer}</strong><code>{claim.source}</code><small>{claim.lineage}</small></div><span>{claim.stance}</span></article>)}</div>
      <button type="button" disabled={revealed} onClick={() => setRevealed(true)}>{revealed ? "Source ancestry revealed" : "Reveal source ancestry"}<span>→</span></button>
    </div>

    <div className="source-reconstruction" aria-live="polite" aria-hidden={!revealed}>
      <div className="source-reconstruction-note"><b>Nothing was deleted or rerun.</b><span>All six claim events and all six actors remain. Only the counting unit changed.</span></div>
      <div className="source-reconstruction-counts"><article><strong>6</strong><span>claim events</span></article><article><strong>6</strong><span>unique actors</span></article><article><strong>3</strong><span>source families</span></article></div>
      <div className="source-family-graphic">
        <div className="source-family-claims">
          <header><span>AGENT COUNT</span><strong>6 voices</strong></header>
          {claims.map((claim) => <article className={claim.family} key={claim.actor}><b>{claim.actor}</b><p>{claim.source}<small>{claim.lineage}</small></p><span>{claim.stance}</span></article>)}
        </div>
        <div className="source-family-collapse"><span>TRACE<br />ANCESTRY</span><b>→</b><small>Counting unit<br />changed</small></div>
        <div className="source-family-roots">
          <header><span>EVIDENCE COUNT</span><strong>3 families</strong></header>
          <article className="weather"><div><b>Weather source</b><small>1 original → 1 copy → 1 summary</small></div><p><i>A</i><i>B</i><i>F</i></p><span>PROCEED</span></article>
          <article className="route"><div><b>Route-clearance source</b><small>1 independent original</small></div><p><i>C</i></p><span>PROCEED</span></article>
          <article className="maintenance"><div><b>Maintenance source</b><small>1 original → 1 summary</small></div><p><i>D</i><i>E</i></p><span>STOP</span></article>
          <footer><b>4 : 2</b><span>agent vote</span><em>→</em><b>2 : 1</b><span>source-family count</span></footer>
        </div>
      </div>
      <p className="source-family-boundary"><b>What Minority Prophet added:</b> the four PROCEED claims resolve to two supporting roots; the two STOP claims resolve to one contradictory root.</p>
    </div>
  </section>;
}
