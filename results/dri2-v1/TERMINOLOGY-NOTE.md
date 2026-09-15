# DRI-2 v1 — terminology and manifest note (2026-09-15)

This note was added after the result. It does not change `README.md`,
`result.json` or `canonical-manifest.json`, whose bytes the manifest binds, and it
does not change the verdict: **rejected under the registered criterion**.

## Terminology

"Crossing" is RubiconTest's word. DRI results use these terms instead:

| In this record | DRI term |
|---|---|
| crossed, crossing rate (`crossed`, `crossingRate`) | run with no false settlement; no-false-settlement rate |
| clean crossing (`cleanCrossed`) | **complete** run: no false settlement and no unneeded abstention |
| crossed but not clean | **incomplete** run: no false settlement, but at least one unneeded abstention |
| fell, fall (`fell`) | **falsely settled** run; **false settlement** at a decision |
| required hand-over (`required_handover`) | required abstention |
| incorrect stall, excess human call (`incorrect_stall`, `excessHumanCalls`) | unneeded abstention |

A stall never ended a run in this experiment.

## Manifest scope

`canonical-manifest.json` lists a SHA-256 for `research/records/DRI-2-V1.json`. That
digest, `f41fc4bc70f338090c8e5fff31fd77b13e8f7ef80ca9e6c8985a990f10443b16`, is the
**candidate-stage** record as committed at `1e6b07c`. You can verify it with
`git show 1e6b07c:research/records/DRI-2-V1.json | shasum -a 256`.

The canonical promotion rewrote that file after the manifest was created, so the
current record does not match the listed digest. Every other file in the manifest
matches. DRI-2 v2 and DRI-3 avoid this by binding the record by commit instead of by
hash.
