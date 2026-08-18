# arXiv submission kit

This directory prepares the author-controlled arXiv submission without pretending that it has already occurred.

## Upload artifact

Upload exactly one file:

`output/pdf/minority-prophet-peer-review-v1.2.0.pdf`

The manuscript is authored in Markdown and rendered directly by ReportLab; it is not generated from TeX. arXiv permits a single machine-readable PDF in this case. Do not upload this directory or combine the PDF with these metadata files.

Before upload, run:

```text
make paper-check
pdffonts output/pdf/minority-prophet-peer-review-v1.2.0.pdf
```

Confirm that the title, author, abstract, page count, DOI, and rendered pages match the repository record.

## Suggested classification

- Primary: `cs.LO` (Logic in Computer Science), because the focused contribution is a formally verified aggregation property and sensitivity result.
- Possible cross-list: `cs.AI` (Artificial Intelligence), because the application is evidence aggregation and uncertainty in AI systems.
- Do not add `cs.MA` merely because the broader project discusses agents; this focused paper does not evaluate a multiagent system.

The author chooses the category in the arXiv form, and moderators may reclassify it.

## What endorsement actually requires

Checked against `info.arxiv.org/help/endorsement.html` rather than assumed.

- Endorsement is per **endorsement domain**, not per paper. For this submission
  the domain is the one containing `cs.LO`.
- The author sends an endorser a **six-character alphanumeric code** that arXiv
  issues; the endorser enters it on arXiv's endorsement form.
- An eligible endorser must have submitted a paper in that domain **between
  three months and five years ago**, and must themselves hold a positive
  endorsement for it.
- Endorsement **is not peer review**. The endorser checks that the paper is
  appropriate for the subject area, not that it is correct.
- One positive endorsement is sufficient.

**Unverified and worth planning around:** arXiv auto-endorses submitters whose
registered email is at a recognised academic institution. A personal-domain
address is therefore likely to trigger the endorsement requirement rather than
bypass it. Confirm at registration; do not assume an account alone is enough.

## Author-controlled steps

1. Register or sign in at arXiv and start a new submission.
2. Select the category before seeking endorsement; endorsement is category-dependent.
3. If arXiv requests endorsement, use the request link it emails to the author. One positive endorsement is required for the relevant endorsement domain.
4. Upload the PDF alone and review arXiv's processed preview.
5. Paste the fields from `metadata.json` into the submission form.
6. Select a distribution license after checking any intended venue's preprint policy.
7. Agree to arXiv's submittal agreement and submit from the author's own account.
8. After announcement, add the public arXiv identifier to the manuscript metadata and submission checklist; do not describe moderation as peer review.

## Endorsement request template

Subject: arXiv endorsement request for a formally verified evidence-aggregation preprint

Hello [Name],

I am preparing an arXiv submission titled "The Minority Prophet Property: Copy-Invariant Evidence Aggregation in Rooted Claim Graphs." It presents Lean-checked copy-invariance and root-margin results for aggregation over declared provenance graphs, with explicit limits around truth, independence, and root qualification.

arXiv has asked me for endorsement in [category/domain]. If the paper is appropriate for that area and you are eligible and comfortable endorsing the submission, the arXiv request link is [link]. The manuscript and archival record are available at https://doi.org/10.5281/zenodo.21965712.

Thank you for considering it,
James Siyuan He
