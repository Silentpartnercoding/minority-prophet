# Peer-review and archival submission checklist

The focused preprint is publicly archived. The record below separates completed publication work from author-account and venue decisions that remain open.

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

## Publication record

- [ ] Add an ORCID and preferred correspondence email if the author wants them in the public record.
- [ ] Choose a venue and apply its template, page limit, and anonymity rules. The current artifact is venue-neutral and author-identified.
- [x] Merge the approved candidate in PR #91.
- [x] Create the immutable `paper-v1.1.0` tag and GitHub release.
- [x] Publish the Zenodo preprint record with the release archive and manuscript PDF.
- [x] Record version DOI `10.5281/zenodo.21965713` in the manuscript source, repository paper metadata, and `CITATION.cff`.
- [x] Prepare the arXiv upload artifact, form metadata, category recommendation, and endorsement instructions in `papers/peer-review/arxiv/`.
- [x] ~~Publish the DOI-bearing PDF as a metadata-only `v1.1.1` archival version~~ — superseded by `v1.2.0`, a content revision adding the CE-14 scope limitation. See `ARCHIVAL-INTEGRITY.md`.
- [x] Create a Zenodo version for `v1.2.0` and record its version DOI `10.5281/zenodo.21997434`. **Published automatically by the GitHub integration on release creation — there was no draft and no approval step.** See the process defect recorded in `ARCHIVAL-INTEGRITY.md`.
- [ ] Decide where the approval gate now lives, given that creating a GitHub release here publishes a DOI immediately: gate the release itself, or disable auto-publication in the Zenodo integration.
- [x] ~~Decide the open item: the tracked `v1.1.0` PDF is not byte-identical to the deposited one.~~ Resolved: both v1.1.0 artifacts restored to the deposited bytes, verified by a byte-identical rebuild.
- [ ] Submit the single PDF to arXiv from the author's own account.
- [ ] Record venue, submission identifier, date, and manuscript status without describing the preprint as peer reviewed.

## Suggested initial distribution sequence

1. [x] Internal/draft-PR review of this focused candidate.
2. [x] Immutable GitHub paper tag and Zenodo DOI.
3. [ ] Author-account arXiv submission, recommended primary category `cs.LO` with `cs.AI` as a possible cross-list, subject to arXiv moderation.
4. [ ] Venue submission. Candidate families include formal methods, distributed/agent systems, information quality, and social-choice venues; select by the reviewer community desired, not by the broadest title.
5. [ ] Later papers can cite the DOI-backed foundational paper and take one open boundary each: root issuance and identity, graded dependence, lineage discovery, markets, evidence-seeking, or dual-ledger architecture.

## Blocking conditions

Do not publish a release if the PDF differs from the reviewed source, repository checks fail, citation metadata disagrees with the title/author/version, or a DOI/status is represented as assigned before the external archive assigns it.
