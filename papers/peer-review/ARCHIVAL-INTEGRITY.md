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

## v1.2.0 supersedes the planned metadata-only v1.1.1

`v1.1.1` was planned as a metadata-only correction carrying the assigned DOI. It
was **not published**, and is superseded by **v1.2.0**, which carries the same
DOI correction *and* adds one limitation to Section 7 (the aggregator answers a
symmetric question and does not decide universal or existential claims — CE-14).

The version number changed because the content changed. A release that alters
what a paper claims about its own scope must not be labelled metadata-only, and
publishing a content revision under a number reserved for a metadata fix is the
same class of error as restating a theorem away from its proof.

No result, proof, validation number, or claim of v1.1.0 is retracted. Section 4
is unaffected: its theorems concern the symmetric aggregator and are correct
about it.

```text
SHA-256  487dfe143b4db3102e2e9e97c2830b3f48f5378cdff12866fcda3bbd142cf38b
File     minority-prophet-peer-review-v1.2.0.pdf
DOI      not yet assigned; no v1.2.0 deposit exists
```

## Open item for the owner: the tracked v1.1.0 PDF is not the deposited one

The repository's tracked `output/pdf/minority-prophet-peer-review-v1.1.0.pdf`
hashes to `bb948d25…` — the DOI-bearing regeneration. The **Zenodo deposit**
behind `10.5281/zenodo.21965713` is `10413b41…`, which says the DOI was not yet
assigned. Both facts are recorded above and neither is new, but the consequence
is worth stating plainly:

> Someone reading the repository's `v1.1.0` PDF is not reading the artifact the
> `v1.1.0` DOI resolves to.

This was left as-is rather than repaired, because both available repairs are
owner decisions with archival consequences: restoring the deposited bytes as the
tracked file, or removing the tracked v1.1.0 PDF now that v1.2.0 exists.
Overwriting or retagging the deposit is not among them.
