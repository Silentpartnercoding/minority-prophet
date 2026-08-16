import type { Metadata } from "next";
import { SiteFooter, SiteNav } from "../components/site-chrome";
import { paperUrl } from "../lib/tournament";

export const metadata: Metadata = {
  title: "Research — Minority Prophet",
  description: "Reproducible studies of evidence lineage, synthetic consensus, minority recovery, and epistemic lift.",
};

const repository = "https://github.com/Silentpartnercoding/minority-prophet";

const records = [
  { tag: "FORMAL MODEL", title: "The Minority Prophet Property", copy: "Machine-checked proofs state when repetition cannot change a root-based verdict—and the assumptions that make the result hold.", href: `${repository}/tree/main/formal`, link: "Read the formal model" },
  { tag: "RECORDS", title: "Evidence-aligned history", copy: "Frozen records keep successes, failures, and unfinished findings visible together.", href: `${repository}/blob/main/CANONICAL-RECORDS.md`, link: "Inspect the record" },
  { tag: "CONTROLLED STUDY", title: "Epistemic lift", copy: "The same models faced the same 32 worlds with claims alone, provenance, and provenance plus Minority Prophet.", href: "/experiments/epistemic-lift", link: "See the measured lift" },
  { tag: "METHOD TEST", title: "Capability comparison", copy: "Model reasoning, tool use, voting, and a deterministic evidence rule meet the same bounded packet.", href: "/experiments/capability-tournament", link: "Compare the methods" },
  { tag: "KNOWLEDGE LEDGER", title: "Keep the doubt", copy: "Receipts carry evidence roots, coverage, uncertainty, flip budget, and the conditions that would reverse a conclusion.", href: `${repository}/tree/main/research/knowledge-ledger`, link: "Explore the ledger" },
  { tag: "LINEAGE", title: "Where inference breaks", copy: "The lineage series shows what can be reconstructed—and what disappears when identity and provenance are missing.", href: `${repository}/tree/main/experiments/lir1`, link: "Read the lineage series" },
];

export default function ResearchPage() {
  return <main>
    <SiteNav />
    <header className="overview-hero research-hero">
      <div><p className="eyebrow"><span /> RESEARCH</p><h1>Claims are earned,<br /><em>not announced.</em></h1><p className="lede">Every claim links to its evidence, its limits, and a reproducible record.</p></div>
      <div className="impact-panel research-principles">
        <span>THE METHOD</span>
        <article><b>01</b><p>Ask before measuring.</p></article>
        <article><b>02</b><p>Publish what failed.</p></article>
        <article><b>03</b><p>Name what the evidence cannot establish.</p></article>
      </div>
    </header>

    <section className="research-records">
      <div className="page-section-heading"><p className="section-index">01 / THE EVIDENCE BASE</p><h2>One question<br /><em>at a time.</em></h2><p>Each artifact answers a bounded question. Failures remain visible; unlike measurements never become one score.</p></div>
      <div className="research-grid">{records.map((record) => <article key={record.title}><span>{record.tag}</span><h3>{record.title}</h3><p>{record.copy}</p><a href={record.href}>{record.link} <b>→</b></a></article>)}</div>
    </section>

    <section className="negative-evidence">
      <div><p className="section-index">02 / NEGATIVE EVIDENCE</p><h2>What failed<br /><em>stays visible.</em></h2></div>
      <div className="negative-list">
        <article><b>Resolved markets</b><p>Dependence adjustment did not beat market price across 5,729 eligible weather markets.</p></article>
        <article><b>Lineage without identity</b><p>Text and time alone did not recover reply roots when identity was missing.</p></article>
        <article><b>Complexity without gain</b><p>A more complex dependence auditor lost to simpler comparators and was rejected.</p></article>
      </div>
    </section>

    <section className="reading-paths">
      <p className="section-index">03 / READING PATHS</p><h2>Start with the question<br /><em>you need answered.</em></h2>
      <div>
        <a href={paperUrl}><span>PAPER</span><b>Read the scientific claim</b><i>→</i></a>
        <a href={`${repository}/blob/main/PUBLIC-CLAIMS.md`}><span>CLAIMS</span><b>See what is supported</b><i>→</i></a>
        <a href={`${repository}/blob/main/EVIDENCE-ALIGNMENT.md`}><span>EVIDENCE MAP</span><b>Trace claim to record</b><i>→</i></a>
        <a href={`${repository}/blob/main/research/knowledge-ledger/RESEARCH-METHOD.md`}><span>METHOD</span><b>See how findings graduate</b><i>→</i></a>
      </div>
    </section>
    <SiteFooter />
  </main>;
}
