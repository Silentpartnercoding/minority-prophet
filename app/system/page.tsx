import type { Metadata } from "next";
import { SiteFooter, SiteNav } from "../components/site-chrome";

export const metadata: Metadata = {
  title: "System — Minority Prophet",
  description: "The working, research, and reference components that turn recorded evidence lineage into an inspectable runtime decision.",
};

const repository = "https://github.com/Silentpartnercoding/minority-prophet";

const components = [
  {
    status: "WORKING PUBLIC CORE",
    title: "Evidence graph",
    value: "Makes repeated support collapse back to its recorded origins.",
    detail: "An append-only claim and evidence DAG validates ancestry, propositions, side consistency, and resolvable root evidence.",
    href: `${repository}/tree/main/provenance`,
    link: "Inspect the graph",
  },
  {
    status: "REFERENCE RUNTIME",
    title: "Minority Prophet engine",
    value: "Returns evidence structure without returning a truth label or permission.",
    detail: "A deterministic, provider-neutral, read-only service is available through local HTTP, MCP, or an in-process adapter.",
    href: `${repository}/blob/main/evaluations/multi-model-v1/RUNTIME-README.md`,
    link: "Read the runtime guide",
  },
  {
    status: "SEEDED RESEARCH",
    title: "Knowledge Ledger",
    value: "Preserves what the system came to believe—and the recorded reason why.",
    detail: "The public research program separates evidence coverage from independence and prevents incomplete search from becoming proof of absence.",
    href: `${repository}/tree/main/research/knowledge-ledger`,
    link: "Open the research program",
  },
  {
    status: "REFERENCE CONTROL",
    title: "Gate and evidence router",
    value: "Turns uncertainty into a bounded next step instead of blind approval.",
    detail: "A neutral policy layer can proceed, block, return an agent for evidence, or route to a human or compatible analysis program.",
    href: `${repository}/blob/main/SYSTEM-ARCHITECTURE.md`,
    link: "See the component boundary",
  },
];

export default function SystemPage() {
  return <main>
    <SiteNav />
    <header className="overview-hero system-hero">
      <div><p className="eyebrow"><span /> THE SYSTEM</p><h1>Know why<br /><em>before you act.</em></h1><p className="lede">Minority Prophet makes recorded evidence lineage inspectable. Separate policy components can then preserve dissent, request another source, or stop a consequential action without turning evidence into authority.</p></div>
      <div className="impact-panel">
        <span>VALUE UP FRONT</span>
        <article><b>01</b><p>Collapse repeated claims into recorded evidence roots.</p></article>
        <article><b>02</b><p>Keep independently supported dissent visible.</p></article>
        <article><b>03</b><p>Route uncertainty before it becomes an irreversible action.</p></article>
      </div>
    </header>

    <section className="system-flow-section">
      <div className="page-section-heading"><p className="section-index">01 / THE NERVOUS SYSTEM</p><h2>From an assertion<br /><em>to a controlled decision.</em></h2><p>Each layer has one job. The boundaries are deliberate: identity is not independence, evidence is not authority, and analysis does not execute an action.</p></div>
      <div className="system-flow" aria-label="Evidence moves through capture, ledger, analysis, policy, and enforcement">
        <article><span>CAPTURE</span><b>Claims + evidence</b><small>What was asserted and observed</small></article><i>→</i>
        <article><span>PRESERVE</span><b>Knowledge Ledger</b><small>Who knew what, when, and from whom</small></article><i>→</i>
        <article className="flow-emphasis"><span>ANALYZE</span><b>Minority Prophet</b><small>Roots, dependence, dissent, uncertainty</small></article><i>→</i>
        <article><span>DECIDE</span><b>Gate / policy</b><small>Proceed, return, route, or block</small></article><i>→</i>
        <article><span>ENFORCE</span><b>Protected runtime</b><small>Exact authorized effect only</small></article>
      </div>
    </section>

    <section className="component-section">
      <div className="page-section-heading"><p className="section-index">02 / WHAT EXISTS TODAY</p><h2>Built in layers.<br /><em>Labeled honestly.</em></h2><p>Working code, reference runtime, and active research are shown separately. Passing local tests is not presented as independent validation or production readiness.</p></div>
      <div className="component-grid">{components.map((component) => <article key={component.title}>
        <span>{component.status}</span><h3>{component.title}</h3><strong>{component.value}</strong><p>{component.detail}</p><a href={component.href}>{component.link} <b>→</b></a>
      </article>)}</div>
    </section>

    <section className="boundary-callout">
      <p className="section-index">03 / DEPLOYMENT BOUNDARY</p>
      <h2>Research-grade transparency.<br /><em>Not a production guarantee.</em></h2>
      <p>The repository provides contracts, local adapters, deterministic analysis, and testable reference controls. Production identity, TLS, key custody, revocation, durable audit storage, network policy, and human accountability remain deployment responsibilities.</p>
      <a href={`${repository}/blob/main/PUBLIC-CLAIMS.md`}>Read the supported public claims →</a>
    </section>
    <SiteFooter />
  </main>;
}

