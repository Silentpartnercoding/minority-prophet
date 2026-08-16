# Peer-review package

This directory contains the focused, venue-neutral submission candidate extracted from the broader v1.0.7 research synthesis.

- `minority-prophet-peer-review-v1.1.0.md`: canonical manuscript source.
- `LITERATURE-AUDIT.md`: claim-by-claim primary-source audit for retained literature.
- `SUBMISSION-CHECKLIST.md`: remaining maintainer-controlled archival and venue steps.
- `metadata.json`: machine-readable title, author, abstract, keywords, and status.

Build from the repository root:

```text
make paper-setup
make paper-pdf
make paper-check
```

The PDF is written to `output/pdf/minority-prophet-peer-review-v1.1.0.pdf`. The build is deterministic at the content/layout level under the pinned ReportLab dependency; PDF metadata dates are fixed by the script.

This is a Routine-lane publication artifact. It creates no new experiment, result, or canonical evidence record.

