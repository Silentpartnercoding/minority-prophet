import type { Metadata } from "next";
import { SiteFooter, SiteNav } from "../components/site-chrome";

export const metadata: Metadata = {
  title: "System — Minority Prophet",
  description: "A vendor-neutral control loop connecting identity, evidence lineage, epistemic analysis, policy, and bounded action.",
};

const repository = "https://github.com/Silentpartnercoding/minority-prophet";

const components = [
  {
    status: "IDENTITY + AUTHORITY",
    title: "Border",
    value: "Binds one exact journey before it crosses a protected boundary.",
    detail: "Border intersects the declaration, current authority, destination policy, action, time box, and optional human control. Approved execution boundaries may later emit witness stamps.",
    href: "https://github.com/Silentpartnercoding/minority-prophet-border",
    link: "Inspect Border",
  },
  {
    status: "EVIDENCE",
    title: "Evidence graph",
    value: "Makes repeated support collapse back to its recorded origins.",
    detail: "An append-only claim and evidence DAG validates ancestry, propositions, side consistency, and resolvable root evidence.",
    href: `${repository}/tree/main/provenance`,
    link: "Inspect the graph",
  },
  {
    status: "ANALYSIS",
    title: "Minority Prophet engine",
    value: "Returns evidence structure without returning a truth label or permission.",
    detail: "Call it through HTTP, MCP, or an in-process adapter. The response carries roots, dependence, warnings, and uncertainty—not an answer key.",
    href: `${repository}/blob/main/evaluations/multi-model-v1/RUNTIME-README.md`,
    link: "Read the runtime guide",
  },
  {
    status: "MEMORY",
    title: "Knowledge Ledger",
    value: "Preserves the conclusion, its uncertainty, and how close it is to changing.",
    detail: "Roots, coverage, margin, reversal pressure, shared dependencies, and reasons for abstention travel with the conclusion.",
    href: `${repository}/tree/main/research/knowledge-ledger`,
    link: "Open the research program",
  },
  {
    status: "CONTROL",
    title: "Gate and evidence router",
    value: "Keeps uncertain actions frozen while the system gathers what is missing.",
    detail: "Gate can proceed, block, request bounded evidence, or escalate. Its neutral router may return to the same agent, a human, a program, or an epistemic service before Gate reassesses the complete evidence set.",
    href: "https://github.com/Silentpartnercoding/minority-prophet-gate",
    link: "Inspect Gate",
  },
];

export default function SystemPage() {
  return <main>
    <SiteNav />
    <header className="overview-hero system-hero">
      <div><p className="eyebrow"><span /> THE SYSTEM</p><h1>Know why<br /><em>before you act.</em></h1><p className="lede">Minority Prophet makes recorded evidence lineage inspectable. Border binds the proposed crossing. Gate controls the consequence. The pieces remain separable, and evidence never becomes authority by itself.</p></div>
      <div className="impact-panel">
        <span>VALUE UP FRONT</span>
        <article><b>01</b><p>Bind the actor, authority, action, and destination.</p></article>
        <article><b>02</b><p>Challenge copied evidence without granting permission.</p></article>
        <article><b>03</b><p>Release only the exact consequence the owner allowed.</p></article>
      </div>
    </header>

    <section className="system-flow-section">
      <div className="page-section-heading"><p className="section-index">01 / THE CONTROL LOOP</p><h2>Gate holds the action.<br /><em>Evidence comes back.</em></h2><p>Bring your own identity, policy, and runtime. Minority Prophet reads the evidence structure; Gate keeps the action frozen until a final decision is made.</p></div>
      <div className="control-map" aria-label="Proposed action and verified evidence enter Gate. Gate may request evidence through a neutral router and reassess the returned artifact before a final runtime decision.">
        <div className="control-inputs">
          <article><span>PROPOSED ACTION</span><b>Requesting agent</b><small>Exact action, subject, target, and payload binding</small></article>
          <article className="flow-border"><span>AUTHENTIC CONTEXT</span><b>Border or verifier</b><small>Identity, authority, evidence, policy, and current bindings</small></article>
          <article><span>OWNER POLICY</span><b>Decision rules</b><small>What may proceed, what must stop, and what needs evidence</small></article>
        </div>
        <div className="control-arrow">↓</div>
        <article className="control-gate"><span>THE DECISION POINT</span><b>Gate</b><p>Deterministic policy first. Evidence-sensitive questions enter independent-root assessment.</p><small>PROCEED · BLOCK · REQUEST EVIDENCE · ESCALATE</small></article>
        <div className="evidence-loop">
          <article><span>NOT YET</span><b>Bound evidence request</b><small>The protected action remains frozen. Collection authority is separate.</small></article><i>→</i>
          <article><span>ROUTE BY CAPABILITY</span><b>Neutral router</b><small>Same agent · human · program · epistemic service</small></article><i>→</i>
          <article className="flow-emphasis"><span>ANALYZE, DO NOT AUTHORIZE</span><b>Minority Prophet</b><small>Lineage, roots, dependence, warnings, and uncertainty</small></article><i>↩</i>
          <article><span>RETURN TO GATE</span><b>Verify + reassess</b><small>The complete evidence set is evaluated again under the same frozen action.</small></article>
        </div>
        <div className="control-arrow">↓ FINAL DECISION ONLY</div>
        <div className="gate-outcomes">
          <article><span>PROCEED</span><b>Exact runtime effect</b></article>
          <article><span>BLOCK</span><b>Zero protected effects</b></article>
          <article><span>ESCALATE</span><b>Human authority remains separate</b></article>
          <article><span>RECEIPT</span><b>Record what actually happened</b></article>
        </div>
      </div>
      <p className="architecture-boundary">An MP receipt, a valid signature, a successful transport, or a human handoff cannot skip Gate. Border authenticates and binds; Minority Prophet evaluates evidence structure; Gate decides consequences.</p>
    </section>

    <section className="ledger-insight">
      <div className="page-section-heading"><p className="section-index">02 / THE KNOWLEDGE LEDGER</p><h2>Keep the answer.<br /><em>Keep the doubt.</em></h2><p>Most logs preserve what a system concluded. A Knowledge Ledger receipt also preserves how fragile that conclusion is and why the system may need to abstain.</p></div>
      <div className="ledger-metrics">
        <article><span>ROOT MARGIN</span><b>The distance between opposing recorded root counts.</b><p>The decision is measured in protected evidence origins, not repeated voices.</p></article>
        <article><span>FLIP BUDGET</span><b>Net per-side root gain needed to erase the winning margin.</b><p>This is a root-flow unit—not a count of attacks, incidents, or compromised keys.</p></article>
        <article><span>CONVERSIONS TO REVERSE</span><b>The modeled side-conversion actions required for reversal.</b><p>It stays beside flip budget because one conversion moves the margin by two units.</p></article>
        <article><span>UNCERTAINTY</span><b>The unknowns travel with the conclusion.</b><p>Unsearched locations, unattributed evidence, shared dependencies, side separation, and the abstention reason remain visible.</p></article>
      </div>
      <p className="ledger-boundary">These metrics describe the declared evidence record. They do not count real-world incidents, prove that roots are true or independent, or authorize an action.</p>
    </section>

    <section className="embodiment-section">
      <div className="page-section-heading"><p className="section-index">03 / EMBODIMENT</p><h2>A judgment can reach a body.<br /><em>Not an unlimited one.</em></h2><p>Embodiment is the consequence layer made physical: a bounded prototype tests whether an evidence judgment can cause one pre-authorized action, observe the body, and return a receipt without giving a model general physical control.</p></div>
      <div className="embodiment-flow" aria-label="A human-defined physical sandbox and evidence judgment constrain a named action, which is observed and recorded.">
        <article><span>HUMAN ENVELOPE</span><b>Define the body&apos;s limits</b><p>Exact body identity, calibration, named actions, legal transitions, budgets, workspace state, and emergency-stop status.</p></article><i>→</i>
        <article><span>EPISTEMIC CONDITION</span><b>Require sufficient evidence</b><p>Thin, conflicting, or malformed evidence produces no motion. An evidence judgment still does not widen the human envelope.</p></article><i>→</i>
        <article className="embodiment-body"><span>BOUNDED BODY</span><b>Act only inside the sandbox</b><p>No arbitrary motor commands. No newly invented action. No silent expansion of authority.</p></article><i>→</i>
        <article><span>OBSERVE + RECEIPT</span><b>Check what the body did</b><p>Record intent before action, observe the resulting state, and emit a hash-bound embodiment-health receipt.</p></article>
      </div>
      <div className="embodiment-status"><b>BOUNDED EMBODIMENT</b><p>The research prototype demonstrates the control pattern, not general robot autonomy: evidence may release one named action inside a human-defined envelope, while the body remains observable and externally stoppable.</p></div>
    </section>

    <section className="component-section">
      <div className="page-section-heading"><p className="section-index">04 / COMPOSABLE LAYERS</p><h2>Adopt one layer.<br /><em>Keep your stack.</em></h2><p>Use the evidence graph alone, call the analysis service, place Gate before a protected runtime, or connect your identity system through Border.</p></div>
      <div className="component-grid">{components.map((component) => <article key={component.title}>
        <span>{component.status}</span><h3>{component.title}</h3><strong>{component.value}</strong><p>{component.detail}</p><a href={component.href}>{component.link} <b>→</b></a>
      </article>)}</div>
    </section>

    <section className="boundary-callout">
      <p className="section-index">05 / YOUR TRUST BOUNDARY</p>
      <h2>We inspect evidence.<br /><em>You control authority.</em></h2>
      <p>Minority Prophet does not replace identity, key custody, revocation, network policy, runtime security, or human accountability. It gives those systems a clearer account of what the evidence can support.</p>
      <a href={`${repository}/blob/main/PUBLIC-CLAIMS.md`}>See exactly what is supported →</a>
    </section>
    <SiteFooter />
  </main>;
}
