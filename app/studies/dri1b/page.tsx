import type { Metadata } from "next";
import { SiteFooter, SiteNav } from "../../components/site-chrome";
import { Dri1bWorkspace } from "./workspace";

export const metadata: Metadata = {
  title: "DRI-1B Human Study Workspace — Minority Prophet",
  description: "Local-only authoring, adjudication, and blinded-review tools for the preregistered DRI-1B proximal-root identifiability study.",
};

export default function Dri1bStudyPage() {
  return <main className="dri-study">
    <SiteNav />
    <header className="dri-hero">
      <div>
        <p className="eyebrow"><span /> HUMAN IDENTIFIABILITY STUDY · DRI-1B</p>
        <h1>Where does shared<br /><em>failure really end?</em></h1>
        <p className="lede">Help test whether people can identify the nearest evidence boundary that is independent enough for a particular decision.</p>
      </div>
      <aside className="dri-status">
        <span>PROTOCOL STATUS</span>
        <strong>SETUP</strong>
        <p>Frozen protocol only</p>
        <small>No confirmatory collection authorized</small>
        <a href="https://github.com/Silentpartnercoding/minority-prophet/blob/63c55438788cfa3ddb0caa16d864b32d050da62a/experiments/dri1b/PREREGISTRATION.md">Read immutable protocol →</a>
      </aside>
    </header>

    <section className="dri-explainer">
      <p className="section-index">01 / THE QUESTION</p>
      <div><h2>Not every root must be<br /><em>the ultimate root.</em></h2><p>If two reports share a machine, controller, source, or upstream component, which shared dependency actually matters to this decision? DRI-1B tests whether blinded humans can draw that line consistently—without automatically rescuing every minority view.</p></div>
      <div className="dri-boundary"><span>WHAT A PASS WOULD MEAN</span><p>The target is understandable and reproducible enough to justify testing an automated selector later. It would not prove the evidence true or authorize an action.</p></div>
    </section>

    <Dri1bWorkspace />

    <section className="dri-send">
      <p className="section-index">03 / COORDINATOR HANDOFF</p>
      <h2>Send a role,<br /><em>not an answer.</em></h2>
      <div>
        <article><b>Author</b><p>Send this page and assign an opaque author ID. Receive the full bundle through your agreed private channel.</p></article>
        <article><b>Adjudicator</b><p>Send only the full author bundle. Two adjudicators work independently; disagreement rejects the case.</p></article>
        <article><b>Reviewer</b><p>Send only the public packet after the holdout is sealed and execution is authorized. Never send the withheld key.</p></article>
      </div>
      <p className="dri-send-note">This browser does not upload responses. Downloaded files remain on the participant’s device until the study coordinator collects them.</p>
    </section>
    <SiteFooter />
  </main>;
}
