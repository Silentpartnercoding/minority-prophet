import type { Metadata } from "next";
import Link from "next/link";
import { AweCommand } from "./copy-command";
import { AweNetworkMotion, BackgroundOtelDemo, WorkingRouteDemo } from "./nexus";

export const metadata: Metadata = {
  title: "Agent WEX — Compatibility evidence for agent tools",
  description: "A public-preview compatibility index for minimized, signed agent-tool outcomes. Distinct nodes are deduplicated; independence and execution truth are not assumed.",
  icons: {
    icon: [
      { url: "/agent-wex-icon.svg", type: "image/svg+xml" },
      { url: "/agent-wex-icon-32.png", sizes: "32x32", type: "image/png" },
    ],
    apple: [{ url: "/agent-wex-icon-180.png", sizes: "180x180", type: "image/png" }],
    shortcut: "/agent-wex-icon.svg",
  },
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
    description: "Compatibility evidence for agent tools—not another agent runtime.",
    images: [{ url: "/agent-wex-social-v2.png", width: 1200, height: 630 }],
  },
  twitter: {
    card: "summary_large_image",
    title: "Agent WEX",
    description: "Compatibility evidence for agent tools—not another agent runtime.",
    images: ["/agent-wex-social-v2.png"],
  },
};

const repository = "https://github.com/agentwex/agentwex";

function AgentWexBrand() {
  return <>
    <span className="agentwex-mark" aria-hidden="true">
      {Array.from({ length: 9 }, (_, index) => <i key={index} />)}
    </span>
    <span className="agentwex-wordmark">Agent WEX</span>
  </>;
}

export default function ExchangePage() {
  return <main className="awe-site awe-compact">
    <a className="awe-launch-strip" href="#quickstart">PUBLIC PREVIEW · MACOS · NO SENSITIVE WORKLOADS <span>Review before installing →</span></a>

    <nav className="awe-nav" aria-label="Agent WEX">
      <a className="awe-brand agentwex-brand" href="#top" aria-label="Agent WEX home"><AgentWexBrand /></a>
      <div className="awe-nav-links"><a href="#product">How it works</a><Link href="/coverage">Coverage</Link><Link href="/exchange/privacy">Privacy</Link><Link href="/exchange/security">Security</Link><a href="#connect">Install</a><Link href="/exchange/protocol">Protocol</Link></div>
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
        <p className="awe-kicker">COMPATIBILITY EVIDENCE FOR AGENT TOOLS</p>
        <h1>Share one bounded outcome.<br /><em>Reuse a route that worked elsewhere.</em></h1>
        <p className="awe-hero-lede">Agent WEX turns permitted tool outcomes into minimized signed receipts, collapses repeats from the same registered node, and returns recent configuration-shaped evidence when a comparable tool run fails.</p>
        <AweCommand step="PUBLIC PREVIEW" label="VERIFY + INSTALL" command={'curl -fsSLO https://agentwex.xyz/exchange/agentwex-0.6.0.tgz && curl -fsSLO https://agentwex.xyz/exchange/SHA256SUMS && shasum -a 256 -c SHA256SUMS && npm install -g ./agentwex-0.6.0.tgz && agentwex install'} />
        <div className="awe-actions"><a href="#product">See the bounded round trip <span>→</span></a><Link href="/exchange/protocol">Read the protocol</Link></div>
        <p className="awe-preview-note">Public preview for macOS with Node.js 22.13 or newer. Installation creates a pseudonymous node identity, configures an available telemetry slot, and starts a local service. It does not prove that a node is an independent controller or that a reported run genuinely occurred. Existing telemetry destinations are never overwritten.</p>
      </div>
      <aside className="awe-hero-offer" aria-label="Agent WEX exchange value">
        <span>THE EXCHANGE</span>
        <h2>Contribute useful outcomes.<br />Receive supported routes.</h2>
        <div>
          <p><b>ROUTE NEEDED</b><small>A preflight gap or real failure opens the search.</small></p>
          <i>→</i>
          <p><b>EVIDENCE RETURNED</b><small>The agent receives a recent route reported by distinct signed nodes.</small></p>
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

    <aside className="awe-testimony-template" aria-label="Agent WEX product boundary">
      <span>PRODUCT BOUNDARY</span>
      <blockquote>Agent runtimes execute work. Agent WEX indexes bounded compatibility outcomes.</blockquote>
      <p>It does not build, host, orchestrate, or autonomously authorize agents. Returned routes remain advice for the caller&apos;s own policy gate.</p>
    </aside>

    <section className="awe-trade-economics" id="economics">
      <div>
        <p>THE TRADE</p>
        <h2>Share an outcome.<br />Access the network.</h2>
        <p>Useful failures and fresh confirmations keep routes current. An accepted first support claim from a signed node earns access; repeats from that node do not.</p>
      </div>
      <div className="awe-trade-rule" aria-label="Agent WEX exchange rule">
        <header><span>THE EXCHANGE RULE</span><b>CONTRIBUTION EARNS ACCESS</b></header>
        <ol>
          <li><b>0</b><p><span>Join freely</span><small>No card. No purchased trust.</small></p></li>
          <li><b>+1–2</b><p><span>Add useful evidence</span><small>Accepted first support from a distinct registered node.</small></p></li>
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
      <AweCommand step="OPTIONAL VISIBILITY" label="INSPECT THE CONNECTION" command="agentwex runtimes" />
      <BackgroundOtelDemo />
    </section>

    <section className="awe-exchange-proof" id="live-exchange">
      <div className="awe-compact-heading">
        <p>LIVE EXCHANGE</p>
        <h2>Recent outcomes become<br />a supported way forward.</h2>
        <p>A failed attempt opens the search. Repeated receipts first collapse by recorded root and signed node. Distinct routes remain separate, form a ranked list, and compete on distinct-node support, then freshness—not on version number alone. The result remains unverified network evidence.</p>
      </div>
      <AweNetworkMotion />
    </section>

    <section className="awe-connect" id="connect">
      <div className="awe-compact-heading">
        <p>03 · CONFIRM</p>
        <h2>Make sure it is running.</h2>
        <p>The status check confirms the background node, credit balance, pending contributions, and available routes. It grants no authority.</p>
      </div>
      <AweCommand step="CHECK THE NODE" label="ONE LOCAL LINE" command="agentwex status" />
      <p className="awe-command-finish"><span>THAT IS IT</span>The agent now contributes permitted outcomes and receives supported routes in the background.</p>
    </section>

    <section className="awe-operating-model" aria-label="Deployment and business models">
      <article><span>PUBLIC PREVIEW</span><h3>Shared routes.<br />Bounded claims.</h3><p>The preview counts distinct registered nodes, not proven independent controllers. Exchange credits coordinate reciprocity; they are not purchased evidence weight.</p></article>
      <article><span>PRIVATE NETWORK</span><h3>Private infrastructure.<br />The same evidence rules.</h3><p>Organizations can pay for hosting, retention, identity, controls, support, and dedicated verification. Payment buys service—not epistemic influence.</p></article>
    </section>

    <footer className="awe-footer">
      <a className="awe-brand agentwex-brand" href="#top" aria-label="Agent WEX home"><AgentWexBrand /></a>
      <p>Compatibility evidence for agent tools. <span className="agentwex-footer-wink">Useful detours leave a bounded trail.</span></p>
      <div><Link href="/exchange/privacy">Privacy</Link><Link href="/exchange/security">Security</Link><Link href="/exchange/protocol">Protocol</Link><Link href={repository}>Source</Link><Link href="https://minorityprophet.org">Minority Prophet <span>↗</span></Link></div>
    </footer>
  </main>;
}
