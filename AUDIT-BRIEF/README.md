# If you want to attack this

`SECURITY.md` invites adversarial testing. This directory exists so that
invitation is usable, and it is deliberately **not** a method.

## Attack it however you like

There is no prescribed sequence here, and that is on purpose. A staged brief
tells a reviewer where to look; they look there; and the maintainers learn about
the places they had already thought of. `CLAIMS.md` section C4 records the
programme's own conclusion on this: every mistake made building it was caught by
tooling, and **no design error ever was**. A method written by the maintainers
would encode the same blind spot.

What you bring that the maintainers cannot is a different frame. Please use it.

## Three things that will save you time

**1. `CLAIMS.md`, in this repository.** Six numbered claims, each with the
evidence behind it and an explicit "breaks if" condition; a section on what is
deliberately *not* claimed; and a list of known weaknesses published so nobody
spends a day rediscovering them. That is a target without being a method — it
tells you what is asserted, not how to attack it.

**2. `CONTEXT-FOR-YOUR-TOOLING.md`.** If you are working with an AI assistant,
paste this first. The original version of this invitation was refused by one —
correctly, because it opened with attack objectives and never said whose
repositories these were or that permission existed. That file supplies the
missing context and nothing else.

**3. What has already been found.** An internal review on 2026-08-10 found three
defects, all since fixed:

- a meta-validation tool reporting success on a verifier that never read the
  verdict it was verifying
- a field documented as establishing evidence identity that no code path used
  for it
- **a runtime controller that performed an effect before recording it, so a retry
  after a lost response performed it again** — three retries, three transfers

The third is the only one with a runtime consequence, and it was in a **seam
between two components** rather than inside either. Every component-level finding
was documentation or reporting. Make of that what you will; the maintainers'
reading is that the seams are underexplored, but that is their model and you are
not obliged to share it.

Full record: `research/knowledge-ledger/runs/2026-08-10/RUN-20260810-1/`.

## What the maintainers want back

Whatever you found, including nothing. "No counterexample within the search I ran"
is a real result and is more useful than silence.

If you are unrelated to the maintainers, **say so in your report.** Every review
of this work so far has been run by an agent directed by the maintainer, which
under the project's own rules is one control domain and therefore internal
replication rather than independent validation. Unrelated provenance is the single
thing this project cannot manufacture for itself. It is the most valuable part of
anything you send.

## The only hard boundary

`SECURITY.md`. Your own copy, no running systems, no secrets or personal data,
private disclosure before publication. Testing rights are not distribution rights.
