# Operator disclosure — what this package leaked

Written by the operator who assembled the package, not by the implementer.
Recorded here so the independence claim can be stated at the strength it
actually holds.

## The claim I made

I built this package to let KL-000 be reimplemented without sight of the
reference. I verified it by checking that none of the eight tuning targets
appeared anywhere in it:

    110840  243381  65280  756619  634440  189720  26880  26208

That check passed. On the strength of it I described the package as clean.

## What that check did not cover

`preregistration.json` contains an `artifacts` list, and that list names the
reference implementation's source paths:

    research/knowledge-ledger/experiments/KL-000/src/kl000_worlds.py
    research/knowledge-ledger/experiments/KL-000/src/kl000_invariants.py
    research/knowledge-ledger/experiments/KL-000/src/kl000_baselines.py

So the package discloses that the reference is Python, and that it is
decomposed into three modules along worlds / invariants / baselines lines. I
checked for leaked *numbers* and concluded the package was clean, without
checking for leaked *structure*. The two are different, and only one was
tested.

I found this because a contamination detector I wrote fired on this file. The
detector was wrong — it was scanning the spec package rather than the
implementer's output, which is circular. The defect it happened to reveal is
real anyway.

## How much this is likely to matter

Probably little, and the reasons are checkable rather than reassuring:

- Module decomposition is a weak hint next to the semantics of the ten
  invariants, which is where the substance of an independent implementation
  lies.
- The implementer chose Rust, not Python, and a different file layout
  (`sha256.rs`, `json.rs`), including hand-written SHA-256 and canonical JSON
  rather than library calls.
- Its output carried none of the reference's distinctive identifiers at the
  time this was written.

## How the result should be described

Not "independent". Say:

> Independent given a specification package that disclosed the reference
> implementation's language and module decomposition, but not its logic,
> its output field names, or any expected value.

If a future reimplementation needs a stronger claim, the fix is to run it on a
machine that does not hold the reference at all, and to redact the `artifacts`
list — or to record the artifacts as roles rather than paths.

## Provenance of this note

Both facts here are checkable without trusting it: grep `preregistration.json`
for `kl000_`, and grep the implementation for the reference's identifiers.
Do that rather than take this file's word for it.
