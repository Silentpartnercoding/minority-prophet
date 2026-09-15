# DRI-2 v1 — post-result note (2026-09-15)

This note was added after the verdict. It changes nothing in `README.md`,
`result.json` or `canonical-manifest.json`, whose bytes the manifest binds, and it
does not change the verdict: **rejected under the registered criterion**.

## The speed checks were misplaced

The six "faster than" checks in the success criterion came from a different
benchmark's rule. In that benchmark, time ranks contestants once all of them have
crossed. The owner has clarified that speed is not a criterion for DRI-2. The
checks were carried into DRI-2 by the implementing agent's proposal, which the
owner approved before the freeze. The mistake is recorded here, and the registered
verdict is left as it is.

## The registered checks with speed set aside

This is descriptive, not a verdict.

| Registered checks | Count | Passed |
|---|---:|---:|
| Speed ("faster than") | 6 | 1 |
| Everything else | 44 | 44 |

The other 44 checks are:

- crossing more often than headcount and every fixed cut;
- no comparison arm crossing more often than the method;
- non-inferiority in the genuinely independent family;
- reproducibility.

## What the clock measured

Speed was compared only on worlds both arms crossed. Determined-or-escalate crossed
every world the method crossed.

A required hand-over costs 1 ms. A probe costs 1,000 ms, and a wrong-time escalation
2,000 ms. The method probes whenever the cuts disagree, including before hand-overs
that looking cannot resolve. An arm that asks at once pays almost nothing there.

So the speed comparison mostly reflects the frozen price list, not navigation
skill. The method was faster where junctions resolvable by looking outnumbered
hand-overs (single domain, against determined-or-escalate), and slower where
hand-overs dominated.

Illustration, computed from the frozen generator after the verdict. Each world
has three decisions; times are in virtual ms.

| World | Decision | Needs | Method | Determined-or-escalate |
|---|---|---|---|---|
| `separate_control_shared_origin\|one_handover\|0000` | 1 | hand-over | look, then ask: 1,001 | ask: 1 |
| | 2 | settle | settle: 1 | settle: 1 |
| | 3 | settle | settle: 1 | settle: 1 |
| | **Total** | | **1,003** | **3** |
| `single_domain\|one_handover\|0000` | 1 | gather | look, then settle: 1,001 | ask too early: 2,001 |
| | 2 | hand-over | look, then ask: 1,001 | ask: 1 |
| | 3 | gather | look, then settle: 1,001 | ask too early: 2,001 |
| | **Total** | | **3,003** | **4,003** |

An officially supported verdict on the intended question would need a new,
separately registered version on fresh worlds. Its write-up would have to disclose
that this result was already known.
