"use client";

import { useMemo, useState } from "react";

type ClaimKind = "independent" | "copied" | "contradiction";
const claims: { id: string; agent: string; belief: string; confidence: number; kind: ClaimKind; source: string }[] = [
  { id: "C-003", agent: "Observer 03", belief: "TRUE", confidence: 98, kind: "independent", source: "Instrument C" },
  { id: "C-002", agent: "Observer 02", belief: "TRUE", confidence: 96, kind: "independent", source: "Instrument B" },
  { id: "C-001", agent: "Observer 01", belief: "TRUE", confidence: 97, kind: "independent", source: "Instrument A" },
  { id: "C-098", agent: "Repeater 95", belief: "FALSE", confidence: 91, kind: "copied", source: "C-041 → C-007" },
  { id: "C-097", agent: "Repeater 94", belief: "FALSE", confidence: 88, kind: "copied", source: "C-018 → C-007" },
  { id: "C-096", agent: "Repeater 93", belief: "FALSE", confidence: 93, kind: "copied", source: "C-007" },
  { id: "C-007", agent: "Origin 01", belief: "FALSE", confidence: 72, kind: "contradiction", source: "No evidence attached" },
];
const metrics = [["Truth accuracy", "0.00", "baseline"], ["Minority recovery", "0.00", "baseline"], ["Independent roots", "3", "world"], ["Copied claims", "95", "world"]];

export function Observatory() {
  const [filter, setFilter] = useState<"all" | ClaimKind>("all");
  const [selected, setSelected] = useState("C-003");
  const visibleClaims = useMemo(() => claims.filter((claim) => filter === "all" || claim.kind === filter), [filter]);
  const active = claims.find((claim) => claim.id === selected) ?? claims[0];
  return <>
    <div className="metric-grid">{metrics.map(([label, value, meta], index) => <article key={label}><span>0{index + 1}</span><p>{label}</p><strong>{value}</strong><small>{meta}</small></article>)}</div>
    <div className="observatory">
      <aside><p className="panel-label">VIEW CLAIMS</p>{(["all", "independent", "copied", "contradiction"] as const).map((kind) => <button key={kind} onClick={() => setFilter(kind)} className={filter === kind ? "active" : ""}><i className={kind} /> {kind === "all" ? "All beliefs" : kind} <span>{kind === "all" ? 98 : kind === "independent" ? 3 : kind === "copied" ? 94 : 1}</span></button>)}<div className="pending"><b>7</b><span>Pending<br />investigations</span></div></aside>
      <div className="claim-table"><div className="table-head"><span>Claim</span><span>Agent</span><span>Belief</span><span>Confidence</span><span>Lineage</span></div>{visibleClaims.map((claim) => <button className={`table-row ${selected === claim.id ? "selected" : ""}`} key={claim.id} onClick={() => setSelected(claim.id)}><span>{claim.id}</span><span>{claim.agent}</span><span className={claim.belief === "TRUE" ? "value-true" : "value-false"}>{claim.belief}</span><span><i className="confidence" style={{ "--value": `${claim.confidence}%` } as React.CSSProperties} />{claim.confidence}%</span><span>{claim.source}</span></button>)}</div>
      <aside className="inspector"><p className="panel-label">LINEAGE INSPECTOR</p><div className={`node large ${active.kind}`}><b>{active.id}</b><span>{active.belief} · synthetic</span></div><div className="line" /><div className="node"><b>{active.source}</b><span>{active.kind === "independent" ? "Evidence root" : "Claim ancestry"}</span></div><dl><div><dt>Observer</dt><dd>{active.agent}</dd></div><div><dt>Confidence</dt><dd>{active.confidence}%</dd></div><div><dt>Independence</dt><dd>{active.kind === "independent" ? "Known to generator" : "Not established"}</dd></div></dl></aside>
    </div>
  </>;
}
