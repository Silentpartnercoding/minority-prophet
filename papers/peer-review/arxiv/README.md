# arXiv submission record

A record of what is to be submitted, in what form, and why it has not been —
not a tutorial for using arXiv. Registration steps, endorsement mechanics, and
request wording are one person's task list; they went stale twice in a day while
living here, which is the argument against keeping them.

**Status: not submitted.**

## Artifact

One file: `output/pdf/minority-prophet-peer-review-v1.2.0.pdf`

Nothing in this directory is uploaded with it. The manuscript is authored in
Markdown and rendered by ReportLab, not generated from TeX, and arXiv's
documented PDF-only route covers that case. Expect PDF-only submissions to draw
more moderator attention than TeX ones.

Title, abstract, and author metadata come from
[`../metadata.json`](../metadata.json), which is the single source. A second
copy formerly lived here and was enforced against the first by CI — duplication
policed by a test rather than removed.

## Classification

- Primary `cs.LO`, because the focused contribution is a formally verified
  aggregation property and sensitivity result.
- Cross-list `cs.AI`, because the application is evidence aggregation under
  uncertainty.
- **Not** `cs.MA`: the broader project discusses agents, this paper evaluates no
  multiagent system.

Moderators may reclassify.

## Why it is not submitted

Endorsement. arXiv's [21 January 2026 policy
update](https://blog.arxiv.org/2026/01/21/attention-authors-updated-endorsement-policy)
stopped accepting an institutional email address as the sole qualifier for new
authors. Two paths remain: institutional email **and** prior authorship on an
existing arXiv paper in the same endorsement domain, or personal endorsement
from an established author in that domain.

The first path is closed here — this would be the author's first arXiv paper, so
there is no prior `cs` paper to claim. An institutional address does not change
that, because the address was never the whole requirement. Personal endorsement
is therefore required, and `cs` is a single endorsement domain, so an endorser
with papers in any `cs` subject class is eligible.

## On affiliation

The manuscript asserts no institutional affiliation, and should not acquire one
at submission unless it is real. Registering an institutional email address is
an identity and contact matter, not a claim of current affiliation.

## After announcement

Record the arXiv identifier and date in `../ARCHIVAL-INTEGRITY.md` alongside the
Zenodo DOIs — that is provenance and belongs with the other deposit facts. Do
not describe arXiv moderation as peer review.
