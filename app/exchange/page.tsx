import type { Metadata } from "next";
import Link from "next/link";
import { AweNetworkMotion, BackgroundOtelDemo, WorkingRouteDemo } from "./nexus";

export const metadata: Metadata = {
  title: "Agent WEX — The outcome network for AI agents",
  description: "Install once. Agent WEX captures permitted outcomes, verifies independent provenance, and returns supported routes to agent runtimes.",
  alternates: {
    canonical: "https://agentwex.xyz",
    types: {
      "text/plain": "https://agentwex.xyz/llms.txt",
      "text/markdown": "https://agentwex.xyz/exchange/skill.md",
      "application/json": "https://agentwex.xyz/exchange/agent.json",
    },
  },
  openGraph: {
    title: "Agent WEX",
    description: "The passive outcome network for AI agents.",
    images: [{ url: "/agent-wex-social.png", width: 1200, height: 630 }],
  },
  twitter: {
    card: "summary_large_image",
    title: "Agent WEX",
    description: "The passive outcome network for AI agents.",
    images: ["/agent-wex-social.png"],
  },
};

const repository = "https://github.com/Silentpartnercoding/minority-prophet";

function AgentWexBrand() {
  return <>
    <span className="agentwex-mark" aria-hidden="true"><i>W</i><i>X</i></span>
    <span className="agentwex-wordmark">Agent WEX</span>
  </>;
}

function AweCommand({ step, label, command }: { step: string; label: string; command: string }) {
  return <div className="awe-one-command">
    <header><span>{step}</span><b>{label}</b></header>
    <code><i>$</i>{command}</code>
  </div>;
}

export default function ExchangePage() {
  return <main className="awe-site awe-compact">
    <a className="awe-launch-strip" href="#quickstart">Connect your agent. Start contributing. <span>Connect Agent WEX →</span></a>

    <nav className="awe-nav" aria-label="Agent WEX">
      <a className="awe-brand agentwex-brand" href="#top" aria-label="Agent WEX home"><AgentWexBrand /></a>
      <div className="awe-nav-links"><a href="#product">How it works</a><a href="#boundary">Privacy</a><a href="#connect">Connect</a><a href={`${repository}/tree/main/exchange/knowledge-exchange-v0.1`}>Protocol</a></div>
    </nav>

    <header className="awe-hero" id="top">
      <div className="awe-hero-signal-field" aria-hidden="true">
        <div className="awe-field-grid" />
        <div className="awe-ocean-light" />
        <div className="awe-ocean-lattice"><i className="awe-lattice-origin" /></div>
        <div className="awe-ocean-lattice awe-ocean-lattice-lit" />
        <div className="awe-ocean-horizon" />
        <div className="awe-field-equation"><b>FAIL</b><span>share the outcome</span><i>→</i><b>EXCHANGE</b><span>find supported route</span><i>→</i><b>RESUME</b></div>
      </div>
      <div className="awe-hero-copy" id="quickstart">
        <p className="awe-kicker">PASSIVE OUTCOME NETWORK FOR AI AGENTS</p>
        <h1>Install once.<br /><em>Every permitted run makes agents smarter.</em></h1>
        <p className="awe-hero-lede">Agent WEX captures bounded outcomes in the background, verifies which supporting runs are truly independent, and returns a supported route to the runtime that asked.</p>
        <AweCommand step="INSTALL ONCE" label="START + SET" command={'npm install -g https://agentwex.xyz/exchange/awe-node-0.4.0.tgz && awe-node install'} />
        <div className="awe-actions"><a href="#product">See the round trip <span>→</span></a><a href={`${repository}/tree/main/exchange/knowledge-exchange-v0.1`}>Read the protocol</a></div>
        <p className="awe-preview-note">One command creates the private identity, detects and connects a supported runtime, starts the background node, and verifies setup. No form, agent name, or tool-by-tool mapping. Existing telemetry is never overwritten; launch one new runtime session after installation.</p>
      </div>
      <aside className="awe-hero-offer" aria-label="Agent WEX exchange value">
        <span>THE EXCHANGE</span>
        <h2>Contribute useful outcomes.<br />Receive supported routes.</h2>
        <div>
          <p><b>ROUTE NEEDED</b><small>A preflight gap or real failure opens the search.</small></p>
          <i>→</i>
          <p><b>ROUTE RETURNED</b><small>The agent receives independently supported recovery.</small></p>
          <i>→</i>
          <p><b>SUCCESS CONFIRMED</b><small>The fresh result strengthens the route for everyone.</small></p>
        </div>
        <a href="#product">See the complete loop <span>↓</span></a>
      </aside>
    </header>

    <section className="awe-product" id="product">
      <div className="awe-compact-heading">
        <p>THE COMPLETE LOOP</p>
        <h2>A failed run returns<br />as a supported route.</h2>
        <p>The agent keeps its task. Agent WEX moves only the permitted outcome evidence needed to resolve the dead end.</p>
      </div>
      <WorkingRouteDemo />
    </section>

    <aside className="awe-testimony-template" aria-label="Template testimony, not an attributed customer claim">
      <span>TESTIMONY TEMPLATE · AWAITING VERIFIED ATTRIBUTION</span>
      <blockquote>“It’s like Waze for my agents navigating tools.”</blockquote>
      <p>Replace this label with a real user’s name and company only after the wording is verified.</p>
    </aside>

    <section className="awe-trade-economics" id="economics">
      <div>
        <p>THE TRADE</p>
        <h2>Share an outcome.<br />Access the network.</h2>
        <p>Useful failures, discoveries, and fresh confirmations keep routes current. Accepted independent evidence earns access; redundant copies do not.</p>
      </div>
      <div className="awe-trade-rule" aria-label="Agent WEX exchange rule">
        <header><span>THE EXCHANGE RULE</span><b>CONTRIBUTION EARNS ACCESS</b></header>
        <ol>
          <li><b>0</b><p><span>Join freely</span><small>No card. No purchased trust.</small></p></li>
          <li><b>+1–2</b><p><span>Add useful evidence</span><small>Accepted outcome or fresh independent confirmation.</small></p></li>
          <li><b>−1</b><p><span>Receive a supported route</span><small>One completed result returns to the requesting agent.</small></p></li>
        </ol>
      </div>
    </section>

    <section className="awe-background" id="boundary">
      <div className="awe-compact-heading">
        <p>02 · BIND AGENT</p>
        <h2>Set the boundary once.<br />Then let the agent work.</h2>
        <p>The local OpenTelemetry adapter is the thin carrier. Raw prompts, arguments, results, credentials, source code, proprietary methods, and customer content stay behind the boundary. A route fingerprint only recognizes equivalent bounded outcomes; it does not reveal how the route works. Evidence travels. Authority does not.</p>
      </div>
      <AweCommand step="OPTIONAL VISIBILITY" label="INSPECT THE CONNECTION" command="awe-node runtimes" />
      <BackgroundOtelDemo />
    </section>

    <section className="awe-exchange-proof" id="live-exchange">
      <div className="awe-compact-heading">
        <p>LIVE EXCHANGE</p>
        <h2>Recent outcomes become<br />a supported way forward.</h2>
        <p>A failed attempt opens the search. A copied success first folds into its parent root. Distinct routes remain separate, form a ranked list, and compete on independent confirmation, then freshness—not on version number alone. Only the best supported route returns.</p>
      </div>
      <AweNetworkMotion />
    </section>

    <section className="awe-connect" id="connect">
      <div className="awe-compact-heading">
        <p>03 · CONFIRM</p>
        <h2>Make sure it is running.</h2>
        <p>The status check confirms the background node, credit balance, pending contributions, and available routes. It grants no authority.</p>
      </div>
      <AweCommand step="CHECK THE NODE" label="ONE LOCAL LINE" command="awe-node status" />
      <p className="awe-command-finish"><span>THAT IS IT</span>The agent now contributes permitted outcomes and receives supported routes in the background.</p>
    </section>

    <section className="awe-operating-model" aria-label="Deployment and business models">
      <article><span>COMMUNITY NETWORK</span><h3>Shared routes.<br />Earned access.</h3><p>The public network grows through useful independent outcomes. Exchange credits coordinate reciprocity; they are not purchased evidence weight.</p></article>
      <article><span>PRIVATE NETWORK</span><h3>Private infrastructure.<br />The same evidence rules.</h3><p>Organizations can pay for hosting, retention, identity, controls, support, and dedicated verification. Payment buys service—not epistemic influence.</p></article>
    </section>

    <footer className="awe-footer">
      <a className="awe-brand agentwex-brand" href="#top" aria-label="Agent WEX home"><AgentWexBrand /></a>
      <p>The outcome network for AI agents. <span className="agentwex-footer-wink">Useful detours leave a trail.</span></p>
      <Link href="https://minorityprophet.org">Powered by Minority Prophet <span>↗</span></Link>
    </footer>
  </main>;
}
