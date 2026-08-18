# Peer-review package

This directory contains the focused, venue-neutral submission candidate extracted from the broader v1.0.7 research synthesis.

- `minority-prophet-peer-review-v1.2.0.md`: canonical manuscript source.
- `minority-prophet-peer-review-v1.1.0.md`: previous version, retained unchanged. Its Zenodo deposit is immutable and is not replaced.
- `LITERATURE-AUDIT.md`: claim-by-claim primary-source audit for retained literature.
- `SUBMISSION-CHECKLIST.md`: remaining maintainer-controlled archival and venue steps.
- `ARCHIVAL-INTEGRITY.md`: hashes and the non-destructive DOI follow-up plan.
- `metadata.json`: machine-readable title, author, abstract, keywords, and status.
- `arxiv/`: upload instructions and copy-ready metadata for the author's arXiv submission.

Build from the repository root:

```text
make paper-setup
make paper-pdf
make paper-check
```

The PDF is written to `output/pdf/minority-prophet-peer-review-v1.2.0.pdf`. The build is deterministic at the content/layout level under the pinned ReportLab dependency; PDF metadata dates are fixed by the script.

The v1.1.0 archival record is https://doi.org/10.5281/zenodo.21965713. The DOI-bearing working-copy PDF is a metadata-only follow-up and must be published as a new archival version rather than replacing that immutable artifact. Because the manuscript is authored in Markdown and rendered directly with ReportLab rather than TeX, the arXiv-ready artifact is the single machine-readable PDF. Do not bundle the companion metadata files into the arXiv upload.

This is a Routine-lane publication artifact. It creates no new experiment, result, or canonical evidence record.
