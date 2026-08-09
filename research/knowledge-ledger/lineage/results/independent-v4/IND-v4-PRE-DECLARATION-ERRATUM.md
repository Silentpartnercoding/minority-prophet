# Erratum to PRE-DECLARATION.md

`PRE-DECLARATION.md` is left byte-identical and still hashes to
`24aab6538385d70f6683af2f6b848b81ceb1538d91b444fd4b3e9db34868cbac`. This file
corrects a factual claim inside it. Written after the implementation had been run
once; disclosed rather than fixed silently, because a pre-declaration that can be
edited after the fact is worth nothing.

## The incorrect claim

> "...and the *structure only* of `PINNED-DIGESTS.json` ... No digest value and
> no conformance value had been read."

**The second sentence is false as to digests.** Before the pre-declaration was
written I had, in fact, seen:

- both stream digests (`exhaustive`, `randomized`) — printed by the JSON
  key-lister described in §6 of the pre-declaration, which emitted scalar values,
  not only key names, contrary to how I described it;
- the 50 exhaustive prefix digests — visible in a read of the first 60 lines of
  `PINNED-DIGESTS.json`.

Not seen before freezing, and correctly described: the 100 randomized prefix
digests and all seven `generatorConformance` entries.

## What this does and does not compromise

It does **not** create a channel for tuning. SHA-256 digests are not invertible;
seeing `a71c64eb…` tells an implementer nothing about the enumeration order, the
canonical form, or the draw schedule. The exposure would matter only if I had
used the pinned values as an oracle — running, comparing, adjusting a reading,
and re-running until the digest matched. That is the failure mode pass condition
1 warns about ("using them to tune toward the total is not [intended], and would
be visible in your report").

**I did not do that, and the record shows it.** `impl/lin000.js` was written
once and executed once before any comparison; both stream digests matched on that
first execution. There is exactly one invocation of the implementation in the
session record prior to comparison, and no intermediate variant of the canonical
form, the enumeration order, or the draw schedule was ever run. Ambiguities
A1–A12 were resolved in the frozen file and none was revisited afterwards.

## The correction

§6 of the pre-declaration should read: the Python invocation printed key names,
array lengths **and scalar values**, exposing both stream digests; and the
opening paragraph's "No digest value ... had been read" should read "no digest
value was used, and the conformance values had not been read."
