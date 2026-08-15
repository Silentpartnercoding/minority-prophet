import Link from "next/link";
import { paperUrl } from "../lib/tournament";

export function SiteNav() {
  return <nav className="nav" aria-label="Primary navigation">
    <Link className="wordmark" href="/" aria-label="Minority Prophet home">
      <span className="mark">MP</span>
      <span>MINORITY PROPHET <small>RESEARCH PROGRAM</small></span>
    </Link>
    <div className="navlinks">
      <Link href="/system">System</Link>
      <Link href="/research">Research</Link>
      <Link href="/developers">Developers</Link>
      <a href={paperUrl}>Paper</a>
      <Link className="nav-cta" href="/#demo">Run MP.01 ↗</Link>
    </div>
  </nav>;
}

export function SiteFooter() {
  return <footer id="foundations"><div className="mark">MP</div><p>Why should the system<br />believe its answer?</p><div className="footer-links"><Link href="/system">System</Link><Link href="/research">Research</Link><Link href="/developers">Developers</Link><a href={paperUrl}>Paper</a></div><span>Public research · synthetic fixtures labeled · 2026</span></footer>;
}
