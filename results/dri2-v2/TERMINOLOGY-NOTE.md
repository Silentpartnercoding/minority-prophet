# DRI-2 v2 — terminology note (2026-09-15)

This note was added after the result. It does not change `README.md`,
`result.json` or `canonical-manifest.json`, and it does not change the verdict:
**supported**.

"Crossing" is RubiconTest's word. DRI results use these terms instead:

| In this record | DRI term |
|---|---|
| crossed, crossing rate (`crossed`, `crossingRate`) | run with no false settlement; no-false-settlement rate |
| clean crossing (`cleanCrossed`) | **complete** run: no false settlement and no unneeded abstention |
| crossed but not clean | **incomplete** run: no false settlement, but at least one unneeded abstention |
| fell (`fell`) | **falsely settled** run; **false settlement** at a decision |
| required abstention (`required_handover`) | required abstention |
| unneeded abstention (`incorrect_stall`, `excessHumanCalls`) | unneeded abstention |

Run outcomes from the frozen output, out of 3,156 runs per family (complete /
incomplete / falsely settled):

| Family | Method under test | Determined-or-escalate |
|---|---|---|
| single domain | 3,156 / 0 / 0 | 1,328 / 1,828 / 0 |
| joint domain | 3,111 / 41 / 4 | 1,519 / 1,633 / 4 |
| separate control, shared origin | 3,156 / 0 / 0 | 2,723 / 433 / 0 |
