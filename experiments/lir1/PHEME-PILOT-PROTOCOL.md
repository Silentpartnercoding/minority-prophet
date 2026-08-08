# LIR-1 PHEME pilot protocol

**Status:** frozen after source acquisition and structural inventory, before
development threshold evaluation or confirmatory outcome execution.

## Frozen source and eligible data

- Figshare article `6392078`, file `11767817`;
- supplied MD5 `11530d4c0c7127fc78bbc1e46f2498f8` (verified);
- acquired SHA-256
  `079f6ffdbc0b367399262f101774372e5d19dd8278c33d6c97a84461a9bc58dd`;
- rumor directories only; non-rumors are excluded because this pilot needs the
  released true/false rumor annotation;
- complete thread directories sorted by path and admitted without exceeding
  the 5,000-claim cap;
- deterministic case split from the LIR-1 preregistration.

The frozen inventory contains 317 cases, 5,000 claim instances, 4,664 recorded
direct edges, and no missing tweet files. Raw and normalized tweet text remains
local because the release states that Twitter retains content rights.

## Label scope

`structure.json` supplies an `explicit_edge` label. Disconnected top-level
components remain separate recorded roots. The target is recovery of the
released reply-tree relation and its connected root family. It is not causal
evidence-independence recovery. Released rumor truth is recorded at case level,
but replies lack a frozen stance label; therefore this pilot will not compute
majority or truth-aggregation accuracy from reply counts.

## Development threshold

On development cases only, evaluate parent-score thresholds
`0.40, 0.45, ..., 0.85` at 40% nested edge hiding. Select the threshold with
maximum exact-parent F1; ties select the higher threshold. Freeze the selected
threshold and its development receipt in a commit before evaluating any
confirmatory outcome.

## Confirmatory endpoints

At every registered hidden fraction, report exact-parent precision/recall/F1,
root-pair precision/recall/F1, and root-count absolute error. The PHEME
secondary criterion from `PREREGISTRATION.md` is exact-parent F1 above 0.50 at
40% edge hiding. Confidence intervals resample cases, not tweets.

All fractions and all outcomes remain visible. A weak, adverse, or collapsed
result is retained. No threshold may be changed after the development commit.
