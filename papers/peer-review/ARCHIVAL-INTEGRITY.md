# Archival integrity record

## Published v1.1.0

The repository tag, GitHub release asset, and Zenodo PDF are byte-identical:

```text
SHA-256  10413b41a2e87a527e2f01a29ed0cdfe17245a61eb0d9a6ce0bf334ca096d3da
File     minority-prophet-peer-review-v1.1.0.pdf
DOI      10.5281/zenodo.21965713
```

That immutable PDF was generated immediately before the DOI was assigned and therefore says that the DOI was not yet assigned. The DOI nevertheless resolves to that exact published artifact.

## DOI-bearing metadata follow-up

The repository working copy now records the assigned DOI in the manuscript, `metadata.json`, and `CITATION.cff`. Its regenerated PDF is a metadata-only correction with SHA-256:

```text
bb948d2591ed12f53f2305234cf266ab81f0d2235e57152217605e795719b33a
```

Do not replace or retag `paper-v1.1.0`. The correct archival completion is to publish this corrected PDF as `paper-v1.1.1` and create a new Zenodo version. Zenodo will assign that version its own DOI while retaining concept DOI `10.5281/zenodo.21965712` across the version family. Until that occurs, cite `10.5281/zenodo.21965713` for the exact v1.1.0 deposit.
