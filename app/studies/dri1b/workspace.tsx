"use client";

import { ChangeEvent, useMemo, useState } from "react";

const labels = ["agent", "machine", "controller", "evidence_origin", "upstream_component", "joint_or_insufficient"] as const;
const cuts = labels.slice(0, 5);
const bases = ["attested", "declared", "inferred", "unknown"] as const;
const dispositions = ["settled_true", "settled_false", "unsettled"] as const;
type Label = typeof labels[number];
type Cut = typeof cuts[number];
type Basis = typeof bases[number];
type Disposition = typeof dispositions[number];
type Tab = "author" | "adjudicator" | "reviewer";

type Observation = {
  observation_id: string;
  value: boolean;
  statement: string;
  roots: Record<Cut, string>;
  basis: Record<Cut, Basis>;
};

type PublicPacket = {
  case_id: string;
  proposition: string;
  proposed_action: string;
  consequence: "low" | "high";
  reversibility: "reversible" | "irreversible";
  deadline_class: "none" | "seconds" | "minutes" | "hours" | "days";
  minimum_winning_roots: 2 | 3;
  observations: Observation[];
};

type WithheldPacket = {
  author_id: string;
  target_label: Label;
  material_failure: string;
  causal_rationale: string;
  cut_dispositions: Record<Cut, { value: Disposition; rationale: string }>;
  nearest_rejected_alternative: string;
  minority_class: "material_reversal" | "false_rescue_trap" | "no_headcount_minority";
};

const emptyRoots = () => Object.fromEntries(cuts.map((cut) => [cut, ""])) as Record<Cut, string>;
const emptyBases = () => Object.fromEntries(cuts.map((cut) => [cut, "unknown"])) as Record<Cut, Basis>;
const observation = (index: number): Observation => ({ observation_id: `obs-${String(index).padStart(2, "0")}`, value: true, statement: "", roots: emptyRoots(), basis: emptyBases() });
const emptyDispositions = () => Object.fromEntries(cuts.map((cut) => [cut, { value: "unsettled", rationale: "" }])) as WithheldPacket["cut_dispositions"];

const initialPublic: PublicPacket = {
  case_id: "", proposition: "", proposed_action: "", consequence: "low", reversibility: "reversible", deadline_class: "none", minimum_winning_roots: 2, observations: [observation(1), observation(2), observation(3)],
};
const initialWithheld: WithheldPacket = {
  author_id: "", target_label: "agent", material_failure: "", causal_rationale: "", cut_dispositions: emptyDispositions(), nearest_rejected_alternative: "", minority_class: "material_reversal",
};

function prettyLabel(label: string) {
  return label.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function safeFileName(value: string) {
  return value.toLowerCase().replace(/[^a-z0-9._-]+/g, "-").replace(/^-+|-+$/g, "") || "draft-case";
}

function downloadJson(filename: string, value: unknown) {
  const blob = new Blob([`${JSON.stringify(value, null, 2)}\n`], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

async function readJsonFile(event: ChangeEvent<HTMLInputElement>) {
  const file = event.target.files?.[0];
  if (!file) return null;
  return JSON.parse(await file.text()) as Record<string, unknown>;
}

function fieldError(value: string, min: number, label: string) {
  return value.trim().length < min ? `${label} needs at least ${min} characters.` : "";
}

function validateAuthor(publicPacket: PublicPacket, withheld: WithheldPacket) {
  const errors = [
    !/^[a-z0-9][a-z0-9._-]{7,127}$/.test(publicPacket.case_id) ? "Case ID must be 8+ lowercase letters, numbers, dots, dashes, or underscores." : "",
    fieldError(publicPacket.proposition, 20, "Proposition"), fieldError(publicPacket.proposed_action, 10, "Proposed action"),
    publicPacket.consequence === "low" && (publicPacket.reversibility !== "reversible" || publicPacket.minimum_winning_roots !== 2) ? "Low-consequence cases must be reversible and require 2 winning roots under the frozen protocol." : "",
    publicPacket.consequence === "high" && (publicPacket.reversibility !== "irreversible" || publicPacket.minimum_winning_roots !== 3) ? "High-consequence cases must be irreversible and require 3 winning roots under the frozen protocol." : "",
    !/^author-[a-z0-9-]{4,64}$/.test(withheld.author_id) ? "Author ID must look like author-abcd." : "",
    fieldError(withheld.material_failure, 20, "Material failure"), fieldError(withheld.causal_rationale, 50, "Causal rationale"), fieldError(withheld.nearest_rejected_alternative, 20, "Rejected alternative"),
  ];
  publicPacket.observations.forEach((item, index) => {
    if (!/^[a-z0-9][a-z0-9._-]{3,127}$/.test(item.observation_id)) errors.push(`Observation ${index + 1} needs a valid ID.`);
    if (item.statement.trim().length < 5) errors.push(`Observation ${index + 1} needs a statement.`);
    cuts.forEach((cut) => { if (!item.roots[cut].trim()) errors.push(`Observation ${index + 1} needs a ${prettyLabel(cut)} root.`); });
  });
  cuts.forEach((cut) => { if (withheld.cut_dispositions[cut].rationale.trim().length < 10) errors.push(`${prettyLabel(cut)} disposition needs a rationale.`); });
  return errors.filter(Boolean);
}

export function Dri1bWorkspace() {
  const [tab, setTab] = useState<Tab>("author");
  const [publicPacket, setPublicPacket] = useState<PublicPacket>(initialPublic);
  const [withheld, setWithheld] = useState<WithheldPacket>(initialWithheld);
  const [authorErrors, setAuthorErrors] = useState<string[]>([]);
  const [adjudicationCase, setAdjudicationCase] = useState<Record<string, unknown> | null>(null);
  const [adjudicatorId, setAdjudicatorId] = useState("");
  const [adjudicationDecision, setAdjudicationDecision] = useState<"accepted" | "rejected">("accepted");
  const [adjudicationRationale, setAdjudicationRationale] = useState("");
  const [adjudicationError, setAdjudicationError] = useState("");
  const [adjudicationChecks, setAdjudicationChecks] = useState([false, false, false, false]);
  const [reviewPacket, setReviewPacket] = useState<PublicPacket | null>(null);
  const [reviewError, setReviewError] = useState("");
  const [reviewerId, setReviewerId] = useState("");
  const [selectedLabel, setSelectedLabel] = useState<Label>("agent");
  const [confidence, setConfidence] = useState(50);
  const [failureCitation, setFailureCitation] = useState("");
  const [rejectedReason, setRejectedReason] = useState("");
  const [reviewErrors, setReviewErrors] = useState<string[]>([]);

  const bundle = useMemo(() => ({ schema: "minority-prophet.dri1b-case.v1", public: publicPacket, withheld }), [publicPacket, withheld]);

  function setPublic<K extends keyof PublicPacket>(key: K, value: PublicPacket[K]) {
    setPublicPacket((current) => ({ ...current, [key]: value }));
  }

  function updateObservation(index: number, updater: (current: Observation) => Observation) {
    setPublicPacket((current) => ({ ...current, observations: current.observations.map((item, itemIndex) => itemIndex === index ? updater(item) : item) }));
  }

  function exportAuthor(kind: "full" | "public" | "withheld") {
    const errors = validateAuthor(publicPacket, withheld);
    setAuthorErrors(errors);
    if (errors.length) return;
    const id = safeFileName(publicPacket.case_id);
    if (kind === "full") downloadJson(`${id}.author-bundle.json`, bundle);
    if (kind === "public") downloadJson(`${id}.public.json`, { schema: bundle.schema, public: publicPacket });
    if (kind === "withheld") downloadJson(`${id}.withheld.json`, { schema: bundle.schema, case_id: publicPacket.case_id, withheld });
  }

  async function loadAdjudication(event: ChangeEvent<HTMLInputElement>) {
    try {
      const parsed = await readJsonFile(event);
      if (!parsed || parsed.schema !== "minority-prophet.dri1b-case.v1" || !parsed.public || !parsed.withheld) throw new Error("This must be a complete DRI-1B author bundle containing public and withheld sections.");
      setAdjudicationCase(parsed); setAdjudicationError("");
    } catch (error) { setAdjudicationCase(null); setAdjudicationError(error instanceof Error ? error.message : "Could not read that file."); }
  }

  function exportAdjudication() {
    if (!adjudicationCase) return setAdjudicationError("Load a complete author bundle first.");
    if (!/^adjudicator-[a-z0-9-]{4,64}$/.test(adjudicatorId)) return setAdjudicationError("Adjudicator ID must look like adjudicator-abcd.");
    if (adjudicationRationale.trim().length < 20) return setAdjudicationError("Give a rationale of at least 20 characters.");
    if (!adjudicationChecks.every(Boolean)) return setAdjudicationError("Complete every eligibility check before downloading the adjudication.");
    const publicSection = adjudicationCase.public as { case_id?: string };
    downloadJson(`${safeFileName(publicSection.case_id ?? "case")}.${adjudicatorId}.adjudication.json`, {
      format: "minority-prophet.dri1b-adjudication-draft", case_id: publicSection.case_id, adjudicator_id: adjudicatorId, decision: adjudicationDecision, rationale: adjudicationRationale.trim(), eligibility_checks_complete: true, authority_effect: "none",
    });
    setAdjudicationError("");
  }

  async function loadReview(event: ChangeEvent<HTMLInputElement>) {
    try {
      const parsed = await readJsonFile(event);
      if (!parsed) return;
      const serialized = JSON.stringify(parsed).toLowerCase();
      if ("withheld" in parsed || "target_label" in parsed || serialized.includes("causal_rationale")) throw new Error("Blinding failure: this file appears to contain withheld answer-key material. Stop and contact the coordinator.");
      if (parsed.schema !== "minority-prophet.dri1b-case.v1" || !parsed.public) throw new Error("Load a DRI-1B public packet, not an author bundle or response.");
      setReviewPacket(parsed.public as PublicPacket); setReviewError(""); setReviewErrors([]);
    } catch (error) { setReviewPacket(null); setReviewError(error instanceof Error ? error.message : "Could not read that file."); }
  }

  function exportReview() {
    const errors = [
      !reviewPacket ? "Load a public packet first." : "",
      !/^reviewer-[a-z0-9-]{4,64}$/.test(reviewerId) ? "Reviewer ID must look like reviewer-abcd." : "",
      fieldError(failureCitation, 10, "Material failure citation"), fieldError(rejectedReason, 10, "Rejected alternative reason"),
    ].filter(Boolean);
    setReviewErrors(errors);
    if (errors.length || !reviewPacket) return;
    downloadJson(`${safeFileName(reviewPacket.case_id)}.${reviewerId}.response.json`, {
      schema: "minority-prophet.dri1b-selector-response.v1", case_id: reviewPacket.case_id, reviewer_id: reviewerId, selected_label: selectedLabel, confidence, material_failure_citation: failureCitation.trim(), rejected_alternative_reason: rejectedReason.trim(), authority_effect: "none",
    });
  }

  return <section className="dri-workspace">
    <div className="dri-workspace-head"><div><p className="section-index">02 / PARTICIPANT WORKSPACE</p><h2>Choose your<br /><em>assigned role.</em></h2></div><aside><b>LOCAL-ONLY</b><p>No study data is uploaded or stored by Minority Prophet.</p></aside></div>
    <div className="dri-notice"><b>Development setup only.</b><span>Do not use confirmatory cases until the coordinator provides a sealed packet and explicit execution authorization.</span></div>
    <div className="dri-tabs" role="tablist" aria-label="Study role">
      {(["author", "adjudicator", "reviewer"] as Tab[]).map((role, index) => <button key={role} role="tab" aria-selected={tab === role} className={tab === role ? "active" : ""} onClick={() => setTab(role)}><span>0{index + 1}</span><b>{role === "reviewer" ? "Blinded reviewer" : prettyLabel(role)}</b></button>)}
    </div>

    {tab === "author" && <div className="dri-panel">
      <header><div><span>ROLE 01</span><h3>Case author</h3></div><p>Create one sanitized decision case at five lineage cuts. The public packet must contain the facts but not reveal the answer.</p></header>
      <div className="dri-form-section"><h4>A · Decision context</h4><div className="dri-form-grid">
        <label>Case ID<input value={publicPacket.case_id} onChange={(event) => setPublic("case_id", event.target.value)} placeholder="case-0001" /><small>Opaque; do not encode the answer.</small></label>
        <label>Author ID<input value={withheld.author_id} onChange={(event) => setWithheld((current) => ({ ...current, author_id: event.target.value }))} placeholder="author-abcd" /></label>
        <label className="wide">Proposition<textarea value={publicPacket.proposition} onChange={(event) => setPublic("proposition", event.target.value)} placeholder="State exactly what the evidence is meant to establish." /></label>
        <label className="wide">Proposed action<textarea value={publicPacket.proposed_action} onChange={(event) => setPublic("proposed_action", event.target.value)} placeholder="State the bounded action under consideration—never a live command." /></label>
        <label>Consequence<select value={publicPacket.consequence} onChange={(event) => setPublic("consequence", event.target.value as PublicPacket["consequence"])}><option value="low">Low</option><option value="high">High</option></select></label>
        <label>Reversibility<select value={publicPacket.reversibility} onChange={(event) => setPublic("reversibility", event.target.value as PublicPacket["reversibility"])}><option value="reversible">Reversible</option><option value="irreversible">Irreversible</option></select></label>
        <label>Deadline<select value={publicPacket.deadline_class} onChange={(event) => setPublic("deadline_class", event.target.value as PublicPacket["deadline_class"])}>{["none", "seconds", "minutes", "hours", "days"].map((value) => <option key={value}>{value}</option>)}</select></label>
        <label>Winning roots<select value={publicPacket.minimum_winning_roots} onChange={(event) => setPublic("minimum_winning_roots", Number(event.target.value) as 2 | 3)}><option value="2">2 · low/reversible</option><option value="3">3 · high/irreversible</option></select></label>
      </div></div>

      <div className="dri-form-section"><div className="dri-form-title"><h4>B · Observations and lineage</h4><button onClick={() => setPublicPacket((current) => ({ ...current, observations: [...current.observations, observation(current.observations.length + 1)] }))}>+ Add observation</button></div>
        <div className="dri-observations">{publicPacket.observations.map((item, index) => <article key={index}><div className="dri-observation-head"><b>OBS {String(index + 1).padStart(2, "0")}</b>{publicPacket.observations.length > 3 && <button onClick={() => setPublicPacket((current) => ({ ...current, observations: current.observations.filter((_, itemIndex) => itemIndex !== index) }))}>Remove</button>}</div><div className="dri-form-grid">
          <label>Observation ID<input value={item.observation_id} onChange={(event) => updateObservation(index, (current) => ({ ...current, observation_id: event.target.value }))} /></label>
          <label>Supports proposition?<select value={item.value ? "true" : "false"} onChange={(event) => updateObservation(index, (current) => ({ ...current, value: event.target.value === "true" }))}><option value="true">True / supports</option><option value="false">False / contradicts</option></select></label>
          <label className="wide">Statement<textarea value={item.statement} onChange={(event) => updateObservation(index, (current) => ({ ...current, statement: event.target.value }))} placeholder="What was observed—not what you infer from it." /></label>
        </div><div className="dri-root-table"><div><b>Cut</b><b>Root ID</b><b>Basis</b></div>{cuts.map((cut) => <div key={cut}><span>{prettyLabel(cut)}</span><input aria-label={`${prettyLabel(cut)} root for observation ${index + 1}`} value={item.roots[cut]} onChange={(event) => updateObservation(index, (current) => ({ ...current, roots: { ...current.roots, [cut]: event.target.value } }))} placeholder={`${cut}-root`} /><select aria-label={`${prettyLabel(cut)} basis for observation ${index + 1}`} value={item.basis[cut]} onChange={(event) => updateObservation(index, (current) => ({ ...current, basis: { ...current.basis, [cut]: event.target.value as Basis } }))}>{bases.map((basis) => <option key={basis}>{basis}</option>)}</select></div>)}</div></article>)}</div>
      </div>

      <div className="dri-form-section dri-withheld"><h4>C · Withheld answer key</h4><p>Never send this section to a blinded reviewer.</p><div className="dri-form-grid">
        <label>Target label<select value={withheld.target_label} onChange={(event) => setWithheld((current) => ({ ...current, target_label: event.target.value as Label }))}>{labels.map((label) => <option key={label} value={label}>{prettyLabel(label)}</option>)}</select></label>
        <label>Minority class<select value={withheld.minority_class} onChange={(event) => setWithheld((current) => ({ ...current, minority_class: event.target.value as WithheldPacket["minority_class"] }))}><option value="material_reversal">Material reversal</option><option value="false_rescue_trap">False rescue trap</option><option value="no_headcount_minority">No headcount minority</option></select></label>
        <label className="wide">Material shared failure<textarea value={withheld.material_failure} onChange={(event) => setWithheld((current) => ({ ...current, material_failure: event.target.value }))} /></label>
        <label className="wide">Causal rationale<textarea value={withheld.causal_rationale} onChange={(event) => setWithheld((current) => ({ ...current, causal_rationale: event.target.value }))} placeholder="Why is this the nearest sufficient causal boundary for this decision?" /></label>
        <label className="wide">Nearest rejected alternative<textarea value={withheld.nearest_rejected_alternative} onChange={(event) => setWithheld((current) => ({ ...current, nearest_rejected_alternative: event.target.value }))} placeholder="Explain why the nearest finer or coarser cut is not sufficient." /></label>
      </div><div className="dri-dispositions">{cuts.map((cut) => <article key={cut}><b>{prettyLabel(cut)}</b><select value={withheld.cut_dispositions[cut].value} onChange={(event) => setWithheld((current) => ({ ...current, cut_dispositions: { ...current.cut_dispositions, [cut]: { ...current.cut_dispositions[cut], value: event.target.value as Disposition } } }))}>{dispositions.map((value) => <option key={value}>{prettyLabel(value)}</option>)}</select><textarea value={withheld.cut_dispositions[cut].rationale} onChange={(event) => setWithheld((current) => ({ ...current, cut_dispositions: { ...current.cut_dispositions, [cut]: { ...current.cut_dispositions[cut], rationale: event.target.value } } }))} placeholder="Resulting roots, conflicts, and remaining shared failure." /></article>)}</div></div>
      {authorErrors.length > 0 && <ErrorList errors={authorErrors} />}
      <div className="dri-actions"><button className="primary" onClick={() => exportAuthor("full")}>Validate + download author bundle <span>↓</span></button><button onClick={() => exportAuthor("public")}>Download public packet <span>↓</span></button><button onClick={() => exportAuthor("withheld")}>Download sealed key <span>↓</span></button></div>
    </div>}

    {tab === "adjudicator" && <div className="dri-panel">
      <header><div><span>ROLE 02</span><h3>Adjudicator</h3></div><p>Inspect the complete author bundle. Two adjudicators must independently accept both the target and its causal rationale.</p></header>
      <Upload label="Load complete author bundle" hint="Required: .author-bundle.json with public and withheld sections." onChange={loadAdjudication} />
      {adjudicationCase && <div className="dri-packet-review"><span>BUNDLE LOADED</span><h4>{String((adjudicationCase.public as { case_id?: string }).case_id ?? "Unnamed case")}</h4><dl><div><dt>Target</dt><dd>{prettyLabel(String((adjudicationCase.withheld as { target_label?: string }).target_label ?? ""))}</dd></div><div><dt>Proposition</dt><dd>{String((adjudicationCase.public as { proposition?: string }).proposition ?? "")}</dd></div><div><dt>Material failure</dt><dd>{String((adjudicationCase.withheld as { material_failure?: string }).material_failure ?? "")}</dd></div><div><dt>Causal rationale</dt><dd>{String((adjudicationCase.withheld as { causal_rationale?: string }).causal_rationale ?? "")}</dd></div></dl></div>}
      <div className="dri-checklist"><b>Eligibility check</b>{["Public packet does not leak the target or stratum.", "All five cuts are complete and materially different where required.", "Target follows from the graph and decision context—not the desired vote outcome.", "No private data, live command, or authority decision appears."].map((copy, index) => <label key={copy}><input type="checkbox" checked={adjudicationChecks[index]} onChange={(event) => setAdjudicationChecks((current) => current.map((value, itemIndex) => itemIndex === index ? event.target.checked : value))} /> {copy}</label>)}</div>
      <div className="dri-form-grid"><label>Adjudicator ID<input value={adjudicatorId} onChange={(event) => setAdjudicatorId(event.target.value)} placeholder="adjudicator-abcd" /></label><label>Decision<select value={adjudicationDecision} onChange={(event) => setAdjudicationDecision(event.target.value as "accepted" | "rejected")}><option value="accepted">Accept</option><option value="rejected">Reject</option></select></label><label className="wide">Rationale<textarea value={adjudicationRationale} onChange={(event) => setAdjudicationRationale(event.target.value)} placeholder="Explain why the target is or is not entailed by the packet." /></label></div>
      {adjudicationError && <ErrorList errors={[adjudicationError]} />}
      <div className="dri-actions"><button className="primary" onClick={exportAdjudication}>Download adjudication <span>↓</span></button></div>
    </div>}

    {tab === "reviewer" && <div className="dri-panel">
      <header><div><span>ROLE 03</span><h3>Blinded reviewer</h3></div><p>Select the nearest available cut where the evidence is independent enough for the stated decision. Do not reward or suppress an observation because it is a minority.</p></header>
      <div className="dri-review-rule"><b>Before you begin</b><p>Do not search for the case, contact another reviewer, or use an AI assistant. This tool rejects obvious answer-key fields but cannot prove that blinding was preserved.</p></div>
      <Upload label="Load public case packet" hint="Only a .public.json file. An author bundle will trigger a blinding warning." onChange={loadReview} />
      {reviewError && <ErrorList errors={[reviewError]} />}
      {reviewPacket && <PublicCase packet={reviewPacket} />}
      <div className="dri-form-grid"><label>Reviewer ID<input value={reviewerId} onChange={(event) => setReviewerId(event.target.value)} placeholder="reviewer-abcd" /></label><label>Nearest sufficient cut<select value={selectedLabel} onChange={(event) => setSelectedLabel(event.target.value as Label)}>{labels.map((label) => <option key={label} value={label}>{prettyLabel(label)}</option>)}</select></label><label className="wide dri-confidence">Confidence <b>{confidence}%</b><input type="range" min="0" max="100" step="1" value={confidence} onChange={(event) => setConfidence(Number(event.target.value))} /></label><label className="wide">Material failure visible in the packet<textarea value={failureCitation} onChange={(event) => setFailureCitation(event.target.value)} placeholder="Cite the dependency or missing lineage that materially affects this decision." /></label><label className="wide">Why the nearest alternative is insufficient<textarea value={rejectedReason} onChange={(event) => setRejectedReason(event.target.value)} /></label></div>
      {reviewErrors.length > 0 && <ErrorList errors={reviewErrors} />}
      <div className="dri-actions"><button className="primary" onClick={exportReview}>Validate + download blinded response <span>↓</span></button></div>
    </div>}
  </section>;
}

function Upload({ label, hint, onChange }: { label: string; hint: string; onChange: (event: ChangeEvent<HTMLInputElement>) => void }) {
  return <label className="dri-upload"><span>JSON FILE</span><b>{label}</b><small>{hint}</small><input type="file" accept="application/json,.json" onChange={onChange} /></label>;
}

function ErrorList({ errors }: { errors: string[] }) {
  return <div className="dri-errors" role="alert"><b>Fix before downloading</b><ul>{errors.map((error, index) => <li key={`${error}-${index}`}>{error}</li>)}</ul></div>;
}

function PublicCase({ packet }: { packet: PublicPacket }) {
  return <div className="dri-public-case"><header><span>PUBLIC PACKET · {packet.case_id}</span><h4>{packet.proposition}</h4><p><b>Proposed action:</b> {packet.proposed_action}</p><small>{prettyLabel(packet.consequence)} consequence · {prettyLabel(packet.reversibility)} · {packet.minimum_winning_roots} winning roots · deadline {packet.deadline_class}</small></header><div className="dri-review-observations">{packet.observations.map((item) => <article key={item.observation_id}><div><b>{item.observation_id}</b><span className={item.value ? "supports" : "contradicts"}>{item.value ? "SUPPORTS" : "CONTRADICTS"}</span></div><p>{item.statement}</p><dl>{cuts.map((cut) => <div key={cut}><dt>{prettyLabel(cut)}</dt><dd>{item.roots[cut]} <small>{item.basis[cut]}</small></dd></div>)}</dl></article>)}</div></div>;
}
