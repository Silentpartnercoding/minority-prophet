import Link from "next/link";
import { paperUrl } from "../lib/tournament";

export function SiteNav() {
  return <nav className="nav" aria-label="Primary navigation">
    <Link className="wordmark" href="/" aria-label="Minority Prophet home">
      <span className="mark">MP</span>
      <span>MINORITY PROPHET <small>RESEARCH PROGRAM</small></span>
    </Link>
    <div className="navlinks">
      <Link href="/experiments/epistemic-lift">Lift Study</Link>
      <Link href="/experiments/capability-tournament">Tournament</Link>
      <Link href="/experiments/epistemic-observatory">Observatory</Link>
      <a href={paperUrl}>Paper</a>
      <Link className="nav-cta" href="/experiments/epistemic-lift#results">Results ↗</Link>
    </div>
  </nav>;
}

export function SiteFooter() {
  return <footer id="foundations"><div className="mark">MP</div><p>A benchmark for<br />evidence-aware aggregation.</p><span>Public research · lift study v1.1 · 2026</span></footer>;
}
