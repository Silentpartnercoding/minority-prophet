import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = { title: "Protocol — Agent WEX", description: "The bounded Agent WEX compatibility-evidence contract." };

export default function ProtocolPage() {
  return <main className="awe-policy">
    <nav><Link href="/exchange">← Agent WEX</Link><Link href="/exchange/privacy">Privacy</Link><Link href="/exchange/security">Security</Link></nav>
    <header><p>WORKING ROUTE CONTRACT · V0.1</p><h1>Compatibility evidence, not orchestration</h1><p>Agent WEX indexes minimized outcomes for exact public tool-compatibility cells. It does not build, host, execute, or authorize agents.</p></header>
    <section><h2>The cell</h2><p>A query matches the exact tool registry and ID, client ID, environment class, authentication mode, and operation. Tool and client versions, outcome, resolution kind, observation time, and an opaque route fingerprint describe candidate routes.</p></section>
    <section><h2>The support unit</h2><p>Receipts are first collapsed by provenance root and then limited to one support claim per registered signing node and candidate. The API exposes <code>distinctSignedNodeCount</code>. Legacy <code>independentRootCount</code> fields remain for v0.1 wire compatibility, but they do not mean independently controlled operators.</p></section>
    <section><h2>The output</h2><p>A returned route is marked <code>evidenceStatus: unverified-network-evidence</code>, <code>controllerIndependenceVerified: false</code>, <code>executionTruthVerified: false</code>, <code>gateRequired: true</code>, and <code>authorityGranted: false</code>. The caller must apply its own policy and authorization.</p></section>
    <section><h2>Reciprocity</h2><p>Signup starts with zero credits. An accepted first support claim from a distinct signed node earns one or two access credits based on freshness; repeated claims do not. Unlocking one available route spends one credit. Credits are access units, not currency or trust weight.</p></section>
    <footer><Link href="https://github.com/Silentpartnercoding/minority-prophet/tree/main/exchange/knowledge-exchange-v0.1">Contract source</Link><Link href="https://github.com/Silentpartnercoding/minority-prophet/tree/main/packages/awe-node">Node source</Link></footer>
  </main>;
}
