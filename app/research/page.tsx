import type { Metadata } from "next";
import { SiteFooter, SiteNav } from "../components/site-chrome";
import { paperUrl } from "../lib/tournament";

export const metadata: Metadata = {
  title: "Research — Minority Prophet",
  description: "The established results, negative findings, open boundaries, and reproducibility records behind Minority Prophet.",
};

const repository = "https://github.com/Silentpartnercoding/minority-prophet";

const records = [
  { tag: "FORMAL", title: "The Minority Prophet Property", copy: "Compiler-ratified proofs state when recorded copies cannot change a root-based verdict—and exactly which assumptions are required.", href: `${repository}/tree/main/formal`, link: "Formal model" },
  { tag: "CANONICAL", title: "Evidence-aligned records", copy: "Frozen manifests preserve successful, rejected, incomplete, and adverse results instead of rewriting the research history.", href: `${repository}/blob/main/CANONICAL-RECORDS.md`, link: "Canonical registry" },
  { tag: "DEVELOPMENT DEMO", title: "Epistemic lift v1.1", copy: "Two model configurations faced the same 32 synthetic worlds under claims-only, provenance, and provenance-plus-MP conditions.", href: "/experiments/epistemic-lift", link: "Measured lift" },
  { tag: "CONFORMANCE", title: "Capability tournament", copy: "A bounded comparison keeps deterministic code, model reasoning, tool use, cost, and elapsed time separate.", href: "/experiments/capability-tournament", link: "Conformance result" },
  { tag: "RESEARCH PROGRAM", title: "Knowledge Ledger", copy: "Versioned protocols test provenance, evidence coverage, independence, interoperability, and the danger of absence claims.", href: `${repository}/tree/main/research/knowledge-ledger`, link: "Ledger research" },
  { tag: "BOUNDARY", title: "Lineage inference series", copy: "The closed LIR series records where lineage reconstruction worked, where identity missingness fragmented it, and what it does not establish.", href: `${repository}/tree/main/experiments/lir1`, link: "Lineage series" },
];

export default function ResearchPage() {
  return <main>
    <SiteNav />
    <header className="overview-hero research-hero">
      <div><p className="eyebrow"><span /> PUBLIC RESEARCH</p><h1>Claims are earned,<br /><em>not announced.</em></h1><p className="lede">Minority Prophet preserves positive, negative, incomplete, and rejected results. Every public claim should lead back to a frozen record, a stated boundary, and a reproducible artifact.</p></div>
      <div className="impact-panel research-principles">
        <span>RESEARCH RULES</span>
        <article><b>✓</b><p>Freeze the question before reading the answer.</p></article>
        <article><b>✓</b><p>Publish adverse evidence beside successful results.</p></article>
        <article><b>✓</b><p>Keep synthetic, replay, and real-world evidence distinct.</p></article>
      </div>
    </header>

    <section className="research-records">
      <div className="page-section-heading"><p className="section-index">01 / THE EVIDENCE BASE</p><h2>One program.<br /><em>Different claim classes.</em></h2><p>No combined vanity score. Each artifact answers a bounded question and retains its own unit of analysis.</p></div>
      <div className="research-grid">{records.map((record) => <article key={record.title}><span>{record.tag}</span><h3>{record.title}</h3><p>{record.copy}</p><a href={record.href}>{record.link} <b>→</b></a></article>)}</div>
    </section>

    <section className="negative-evidence">
      <div><p className="section-index">02 / WHAT DID NOT WIN</p><h2>Negative results<br /><em>are part of the product.</em></h2></div>
      <div className="negative-list">
        <article><b>Resolved markets</b><p>Dependence adjustment did not beat market price across 5,729 eligible resolved weather markets.</p></article>
        <article><b>Lineage without identity</b><p>Text and time alone did not recover recorded PHEME reply roots; substantial identity missingness reduced recall sharply.</p></article>
        <article><b>Unified auditor candidate</b><p>A frozen comparison rejected a more complex dependence auditor rather than promoting it past simpler comparators.</p></article>
      </div>
    </section>

    <section className="reading-paths">
      <p className="section-index">03 / READING PATHS</p><h2>Start with the question<br /><em>you need answered.</em></h2>
      <div>
        <a href={paperUrl}><span>THE SCIENTIFIC CLAIM</span><b>Read the current paper</b><i>→</i></a>
        <a href={`${repository}/blob/main/PUBLIC-CLAIMS.md`}><span>THE SHORTEST BOUNDARY</span><b>Read public claims</b><i>→</i></a>
        <a href={`${repository}/blob/main/EVIDENCE-ALIGNMENT.md`}><span>CLAIM → RECORD</span><b>Inspect evidence alignment</b><i>→</i></a>
        <a href={`${repository}/blob/main/research/knowledge-ledger/RESEARCH-METHOD.md`}><span>HOW WORK GRADUATES</span><b>Read the research method</b><i>→</i></a>
      </div>
    </section>
    <SiteFooter />
  </main>;
}

