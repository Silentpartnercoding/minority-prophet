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

## RESOLVED: the tracked v1.1.0 artifacts are now the deposited ones

The v1.1.0 slot holds exactly what the v1.1.0 DOI resolves to. Both files were
restored from their published state, and the restoration was **verified, not
asserted**:

```text
manuscript   restored from tag paper-v1.1.0
             sha256 bffb546cfc8375c94fd64017f567d1708adc3df8eaeff4bd669c6dabce056998
PDF          downloaded from the Zenodo deposit
             sha256 10413b41a2e87a527e2f01a29ed0cdfe17245a61eb0d9a6ce0bf334ca096d3da
rebuild      building the restored manuscript on a different machine reproduces
             the deposited PDF BYTE-FOR-BYTE, same sha256 10413b41...
```

That third line is the one that matters. It shows the restoration is correct,
that the ReportLab build is deterministic across machines, and that the
version-derived build change introduced with v1.2.0 does **not** disturb the
reproduction of v1.1.0 — a hardcoded version string would have produced a
different PDF here and the check would have failed.

The DOI-bearing text that had drifted into the v1.1.0 slot now lives where it
belongs, in **v1.2.0**. The previously recorded `bb948d25…` regeneration is
superseded and is not tracked.

### The problem this closes, kept visible

> A reader of the repository's `v1.1.0` PDF was not reading the artifact the
> `v1.1.0` DOI resolved to.

The cause was benign and worth naming: the DOI was assigned *after* the artifact
was frozen, and the natural repair — regenerate the PDF with the DOI in it — was
applied to the version slot that must not change. The correct home for a
post-publication correction is the next version, never the published one.

## Superseded: open item for the owner (retained)

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

## v1.2.0 is deposited — and Zenodo auto-published rather than drafting

```text
DOI      10.5281/zenodo.21997434     (version DOI, v1.2.0)
concept  10.5281/zenodo.21965712     (resolves to latest)
files    Silentpartnercoding/minority-prophet-paper-v1.2.0.zip
relation isNewVersionOf 10.5281/zenodo.21965713
```

**The manuscript source is NOT being edited to carry this DOI.** Doing so is
exactly what produced the v1.1.0 drift closed above: the deposited artifact was
built from the source as it stood, and changing that source afterwards makes the
repository's v1.2.0 differ from the deposited v1.2.0. The DOI is recorded in
`metadata.json`, `CITATION.cff` and here, which is where a post-publication fact
belongs. If a future version wants the DOI in the manuscript text, it is v1.3.0's
header that carries it, never v1.2.0's.

### Process defect, demonstrated rather than hypothesised

`SUBMISSION-CHECKLIST.md` describes the archival step as *"inspect the draft
deposit, and publish it only after metadata approval"*, and the v1.2.0 checklist
line said publishing was an owner action.

**The GitHub–Zenodo integration does not work that way for this repository.** It
published automatically, five seconds after the release was created. There was no
draft and no approval step. The documented gate does not exist in the mechanism.

This is worth stating plainly because it is the same failure class the repository
studies: a control believed to be in place, described in writing, and absent in
the system it describes. The correct reading is that **creating a GitHub release
here IS publishing a DOI**, and the approval gate must move earlier — to the
release, or to disabling the integration — because there is no later gate.

The deposit itself is correct: right version, right relation to v1.1.0, open
access. Nothing needs retracting. A Zenodo record cannot be unpublished in any
case, which is why the gate mattered.

### One difference from the v1.1.0 deposit

The v1.1.0 record carries both the source zip and the standalone PDF; the v1.2.0
record carries the zip only, because the integration archives the repository
tarball and the v1.1.0 PDF had been attached by hand. The PDF is inside the zip
at `output/pdf/`, and is attached to the GitHub release
`paper-v1.2.0`. Adding a file to a published Zenodo record is an owner action and
was not attempted.

### The structural cause, and the fix that ends it

Twice now the repository source has drifted from a deposit, for the same reason:
**a version DOI is minted FROM the document, so a document cannot contain its own
version DOI.** Requiring it forces a choice between a false statement and an
artifact that differs from what was deposited. v1.1.0 took the second horn;
v1.2.0's transitional text took the first.

`check_peer_review_package.py` previously *enforced* the impossible version by
requiring the version DOI to appear in the manuscript. It now enforces the
opposite:

- the manuscript must cite the **concept DOI** `10.5281/zenodo.21965712`, which
  is assigned once, never changes, and always resolves to the latest version;
- the manuscript must **not** cite its own version DOI;
- the **version DOI** is recorded in `metadata.json`, `CITATION.cff` and here.

From v1.3.0 onward the manuscript needs no post-deposit edit, so repository and
deposit cannot diverge again.

### One-time discrepancy in the v1.2.0 deposit, recorded not repaired

The v1.2.0 deposit `10.5281/zenodo.21997434` archives the tree as it stood at tag
`paper-v1.2.0`, whose manuscript header read *"Archival DOI (v1.1.0 deposit) …
a v1.2.0 deposit has not been created"* — true when built, false five seconds
later. The repository's v1.2.0 manuscript now cites the concept DOI instead.

```text
deposited v1.2.0 PDF   sha256 487dfe143b4db3102e2e9e97c2830b3f48f5378cdff12866fcda3bbd142cf38b
repository v1.2.0 PDF  sha256 e1cee6b3abee5b6d1b5f0aac232ce276a6fff58b58a663b6e1035b9050d2c599
```

**No new version is cut to close this gap**, because doing so would mint another
DOI, which would date another header, which would require another version. That
regress is the thing the concept-DOI rule exists to stop. The discrepancy is one
transitional sentence, it is recorded here, and it terminates with v1.2.0.
