# DRI-8 v1 — post-result note, 2026-09-16

**The verdict is unchanged.** This note adds a measurement taken after the run,
while building DRI-9, which explains the size of the effect this record reports.
`result.json`, the manifest and the frozen protocol are untouched, and the
README's hash still matches what the manifest attests.

## What was measured

On DRI-8's own development world, merging the true hidden group and asking the
rule what it would now decide:

| Family | Decisions | Settlements changed | Stamps changed | Looks changed |
|---|---:|---:|---:|---:|
| shared upstream pair | 720 | 0 | 38 | 144 |
| shared upstream trio | 720 | 0 | 0 | 276 |

Knowing the hidden dependence never changed a settlement. In the pair family it
moved 38 stamps; in the trio family it moved nothing at all.

## Why

An arm that learns a merge records it as an identity at a `learned` cut, and the
rule settles across six cuts together. The other five still carry the record's
own separate machine, controller and origin identities for those sources, so a
learned merge is one view among six and is outvoted by the five that describe the
disguise. The arm could discover the dependence and then not act on it.

On DRI-9's development world, where the same comparison was run both ways,
adding a learned cut changed 0 of 960 decisions in each family, while
**overriding** the merged sources' identities at every cut changed 316 and 368 —
and every one of those moved toward the true grouping. Those figures come from
DRI-9's unfrozen world, not this one, and are cited as the diagnosis rather than
as a result of this experiment.

## What this means for this record

- **The verdict stands.** Supported, 49 of 49, with the criterion's weakness
  already stated in the README.
- **The interpretation narrows.** This experiment measured how much its arms
  could act on what probing found, not how much probing can find. The reported
  0.3–3.5% is the arm's grip, not the instrument's reach.
- **The successor must fix the arm first.** Believing two sources are one means
  their separate recorded identities stop counting as evidence of independence.
  DRI-9 is being rebuilt on that basis, and DRI-8's probe arm will be re-run
  against it.
