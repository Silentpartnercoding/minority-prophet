import type { Metadata } from "next";
import { SiteFooter, SiteNav } from "../../components/site-chrome";

export const metadata: Metadata = {
  title: "Decision Trace — Minority Prophet",
  description:
    "Watch the composed stack decide not to act, and verify afterwards that it did not. Four stages, one hash-chained record, nothing executed.",
};

export default function DecisionTracePage() {
  return <main>
    <SiteNav />

    <header className="experiment-hero">
      <div>
        <p className="eyebrow"><span /> RUNNABLE LOCAL COMPOSITION</p>
        <h1>Watch it decide<br /><em>not to act.</em></h1>
        <p className="lede">Three separable components, one hash-chained decision timeline. The interesting case is not the refusal. It is the record proving nothing ran.</p>
      </div>
      <div className="experiment-hero-result">
        <span>LOCAL DEMO RESULT</span>
        <strong>0</strong>
        <small>effects executed · ledger verified</small>
        <p>$0 model calls · runs on your machine</p>
      </div>
    </header>

    <section className="observatory-intro">
      <p className="section-index">01 / WHAT IS COMPOSED</p>
      <div>
        <h2>Three components that<br /><em>cannot become each other.</em></h2>
        <p><strong>Border</strong> verifies identity and authority bindings for one exact action. <strong>Minority Prophet</strong> analyses evidence structure and returns no authority at all. <strong>Gate</strong> interprets authenticated evidence and controls the runtime consequence.</p>
        <p>The separation is the design. Minority Prophet can report that evidence is weak without being able to stop anything. Gate can stop something without being able to judge evidence. Neither can quietly absorb the other.</p>
      </div>
      <div className="demo-boundary-card">
        <span>BOUNDARY</span>
        <p>A local development composition. The HMAC, SQLite ledger, loopback service and container profile are fixtures. Nothing here is production-ready and nothing connects a real effectful runtime.</p>
      </div>
    </section>

    <section className="cost-section">
      <div className="cost-heading">
        <p className="section-index">02 / THE SHADOW OBSERVER</p>
        <div>
          <h2>It records what it<br /><em>would</em> have done.</h2>
        </div>
        <p>Run this one first. The refusal is easy to believe. A recorded <em>proceed</em> from something structurally unable to act is the part worth inspecting.</p>
      </div>
      <div className="result-block">
        <p className="result-title">make shadow-demo</p>
        <p>Records a fixed hypothetical proceed decision as <strong>would_execute</strong> while executing nothing. The shadow observer has no target transport, no effect credential, no handler and no execution method.</p>
        <p>It cannot act even when the decision says proceed, which is precisely the case that makes the record worth having. It is preparation for private shadow staging, not a production-readiness claim.</p>
      </div>
    </section>

    <section className="dashboard-section">
      <div className="section-heading">
        <div>
          <p className="section-index">03 / THE BLOCKING PATH</p>
          <h2>Four stages, <em>one record</em></h2>
        </div>
        <div className="verified-stamp"><i /> LEDGER VERIFIED LOCALLY</div>
      </div>
      <div className="network-flow">
        <article><span>01</span><b>Border</b><small>Authority bound to one exact action</small></article>
        <i>→</i>
        <article><span>02</span><b>Minority Prophet</b><small>Evidence structure · no authority</small></article>
        <i>→</i>
        <article className="flow-highlight"><span>03</span><b>Gate</b><small>Block · nothing executed</small></article>
        <i>→</i>
        <article><span>04</span><b>Ledger</b><small>Hash-chained · independently verified</small></article>
      </div>
      <div className="result-block">
        <p className="result-title">Expected local result</p>
        <p><code>gate: block</code> · <code>effects_executed: 0</code> · <code>ledger_verified: true</code></p>
        <p>The trace across all four stages is served locally. <strong>make verify</strong> checks the ledger rather than trusting the program&apos;s own account of what happened.</p>
      </div>
    </section>

    <section className="boundary">
      <div className="boundary-heading">
        <p className="section-index">04 / HOW TO RUN IT</p>
        <h2>Five commands.<br /><em>No account, no key, no cost.</em></h2>
      </div>
      <div className="boundary-flow">
        <article><span>01</span><b>make bootstrap</b><small>Fetches the engine at an exact reviewed commit, packs it, records its SHA-256</small></article>
        <article><span>02</span><b>make up</b><small>Starts the local composition</small></article>
        <article><span>03</span><b>make doctor</b><small>Confirms the installation record and boundaries</small></article>
        <article><span>04</span><b>make shadow-demo</b><small>Records a proceed decision while executing nothing</small></article>
        <article><span>05</span><b>make demo</b><small>Runs the blocking path and verifies the ledger</small></article>
      </div>
      <p className="demo-disclaimer">Bootstrap never installs from a moving branch. The installation record states the source repository, exact commit, source-tree status and release eligibility, so a claim about what ran names exactly what ran.</p>
    </section>

    <section className="observatory-takeaway">
      <p className="section-index">05 / THE TAKEAWAY</p>
      <h2>Assessment is not<br /><em>authorisation.</em></h2>
      <p>This composition demonstrates a boundary rather than a result. Minority Prophet judges evidence and is given no power to act on that judgement. Gate holds the power and is given no ability to judge. The ledger makes both claims checkable afterwards by someone who was not there.</p>
      <p>It establishes nothing on its own. The method, the machine-checked core, the benchmarks and the published negative results, including an external validation that returned zero coverage on real corpora, are in the research record.</p>
      <a className="preview-link" href="/experiments/epistemic-observatory">See where the evidence comes from <span>→</span></a>
    </section>

    <SiteFooter />
  </main>;
}
