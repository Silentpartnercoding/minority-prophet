import Link from "next/link";
import { paperUrl } from "../lib/tournament";

export function SiteNav() {
  return <nav className="nav" aria-label="Primary navigation">
    <Link className="wordmark" href="/" aria-label="Minority Prophet home">
      <span className="mark">MP</span>
      <span>MINORITY PROPHET <small>RESEARCH PROGRAM</small></span>
    </Link>
    <div className="navlinks">
      <Link href="/#demo">MP.01 Demo</Link>
      <Link href="/experiments/epistemic-lift">Lift Study</Link>
      <Link href="/#experiments">Experiments</Link>
      <a href={paperUrl}>Paper</a>
      <a className="nav-cta" href="/research/mp01-canonical-demo.json">Run result ↗</a>
    </div>
  </nav>;
}

export function SiteFooter() {
  return <footer id="foundations"><div className="mark">MP</div><p>Why should the system<br />believe its answer?</p><span>Public research · synthetic fixtures labeled · 2026</span></footer>;
}
