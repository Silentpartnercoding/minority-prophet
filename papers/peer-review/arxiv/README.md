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

## Endorsement is REQUIRED here, not conditional — policy changed 21 Jan 2026

Checked against `blog.arxiv.org/2026/01/21/attention-authors-updated-endorsement-policy`
and `info.arxiv.org/help/endorsement.html`.

> "As of January 21, 2026, arXiv will no longer accept institutional email
> addresses ... as the sole qualifier of endorsement for new authors."

There are exactly two paths for a new submitter to a category:

1. **institutional email AND previous authorship on an existing arXiv paper in
   the same endorsement domain** — both, not either;
2. **personal endorsement** from an established arXiv author in that domain.

**Path 1 is closed for this submission.** It would be the author's first arXiv
paper, so there is no prior paper in the `cs` domain to claim ownership of. An
institutional address — including an alumni address — does not change this,
because the address was never the whole requirement.

**Therefore path 2 is the route: personal endorsement.** Plan for it rather than
discovering it at the form. arXiv also states that staff cannot waive the
requirement or supply an endorsement.

An institutional email is still worth associating with the account: arXiv
recommends it and says it expedites the process. It is not sufficient on its own.

**Affiliation honesty.** Registering with an institutional address is an identity
and contact matter. It is not a claim of current affiliation, and the manuscript
must not assert one that does not hold. This paper lists an author name and a
repository, with no institutional affiliation, which is the correct state and
should stay that way unless the affiliation is real.

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
3. **Expect arXiv to request endorsement** (see the policy note above). Use the request link it emails to the author. One positive endorsement is required for the relevant endorsement domain.
   To find eligible endorsers, open the abstract page of a related arXiv paper and use its **"Which authors of this paper are endorsers?"** link; the contact address appears under *Submission history*. Note that this paper's own reference list contains no arXiv-hosted work, so search the `cs.LO` listings for adjacent formal-methods papers rather than the bibliography.
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
