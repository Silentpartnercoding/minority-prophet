# Peer-review and archival submission checklist

The candidate is reviewable now. The maintainer-controlled actions below convert it from a review branch into an immutable public preprint record.

## Completed in this package

- [x] One central thesis: copy-invariant aggregation over declared rooted claim graphs.
- [x] Claims reconciled with the compiled Lean statements and `formal/CLAIM-SCOPE.md`.
- [x] Broad truth-recovery, comparator-superiority, market, and LLM claims removed from this candidate.
- [x] Complete bibliography for every external literature claim retained.
- [x] Literature audit against primary or official sources.
- [x] Standard data/code, ethics, funding, competing-interest, author-contribution, and AI-assistance statements.
- [x] Reproducible PDF source, build command, content checks, and rendered PDF.
- [x] Repository citation metadata and Zenodo-ready deposit metadata.
- [x] Existing adverse, null, and historical records preserved unchanged.

## Maintainer actions after peer-review PR approval

- [ ] Add an ORCID and preferred correspondence email if the author wants them in the public record.
- [ ] Choose a venue and apply its template, page limit, and anonymity rules. The current artifact is venue-neutral and author-identified.
- [ ] Merge the approved candidate.
- [ ] Create an immutable tag such as `paper-v1.1.0` from the approved commit.
- [ ] Connect the GitHub repository to Zenodo, create the release, inspect the draft deposit, and publish it only after metadata approval.
- [ ] Insert the assigned DOI into the paper, `.zenodo.json`, and `CITATION.cff` in a metadata-only follow-up release if the archive does not support DOI reservation before upload.
- [ ] Submit the archival PDF (and source package if requested) to arXiv or the selected preprint server from the author's own account.
- [ ] Record venue, submission identifier, date, and manuscript status without describing the preprint as peer reviewed.

## Suggested initial distribution sequence

1. Internal/draft-PR review of this focused candidate.
2. Immutable GitHub paper tag and Zenodo DOI.
3. arXiv submission in a suitable computer-science category selected by the author and moderator.
4. Venue submission. Candidate families include formal methods, distributed/agent systems, information quality, and social-choice venues; select by the reviewer community desired, not by the broadest title.
5. Later papers can cite the DOI-backed foundational paper and take one open boundary each: root issuance and identity, graded dependence, lineage discovery, markets, evidence-seeking, or dual-ledger architecture.

## Blocking conditions

Do not publish a release if the PDF differs from the reviewed source, repository checks fail, citation metadata disagrees with the title/author/version, or a DOI/status is represented as assigned before the external archive assigns it.

