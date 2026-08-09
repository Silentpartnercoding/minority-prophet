# LIR-1 mistakes and blocked sources

Entries are append-only. Each entry must state the source, timestamp, failure,
consequence, fallback, and whether the fallback changes the registered claim.

## 2026-08-08 — interrupted PHEME transfer was not resumable through the redirect

The first PHEME download was interrupted twice by the execution transport. A
blind `curl --continue-at -` through Figshare's redirected downloader produced
a 53,254,530-byte concatenated file whose MD5
`f509a567ef585b715f94dc8d3ffc92ca` did not match Figshare's supplied MD5
`11530d4c0c7127fc78bbc1e46f2498f8`. The invalid file was moved to macOS Trash,
not used as input. A fresh uninterrupted download matched the supplied MD5,
parsed successfully, and has SHA-256
`079f6ffdbc0b367399262f101774372e5d19dd8278c33d6c97a84461a9bc58dd`.
This changes no registered claim. Future acquisition code must verify a range
response before appending redirected downloads.

## 2026-08-08 — PHEME uses two representations for leaf nodes

The first normalization attempt expected every `structure.json` child value to
be an object. PHEME represents leaves as either `{}` or `[]`, so the parser
stopped before writing output. The parser now accepts only an empty list as the
alternate leaf representation and still rejects non-empty or malformed lists.
No partial normalized file or scientific result was produced, and no
registered claim changed.

## 2026-08-08 — some PHEME conversation structures are forests

The next normalization attempt assumed each thread's `structure.json` had one
top-level platform root. At least one file also contains a disconnected
reaction as a second top-level component, consistent with a missing parent in
the captured conversation. The parser now preserves each top-level component
as its own recorded root while keeping the directory's source tweet as the
case identifier. It does not invent an edge between disconnected components.
No partial output or scientific result was produced, and no registered claim
changed.

## 2026-08-08 — archive metadata files inflated the first inventory count

The first completed inventory glob counted nine `.DS_Store` files as candidate
thread paths, reporting 2,411 available rumor threads and nine invalid paths.
The normalized claims were unaffected because those paths were skipped. The
inventory selector now admits directories only; the superseded inventory was
regenerated before commit. This changes no registered claim.

## 2026-08-08 — first R2 inventory admitted an incomplete thread

The first unscored R2 inventory reported one missing tweet file. The R2
preregistration requires complete cases, so that in-memory selection was not
accepted or committed. The selector now excludes the entire affected thread
and records the exclusion count before filling the cap from the next eligible
case. No R2 inference outcome had been run and no registered claim changed.
