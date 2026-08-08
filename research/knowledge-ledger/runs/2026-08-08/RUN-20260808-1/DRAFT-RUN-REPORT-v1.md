# RUN-20260808-1 — draft run report

Short run, three recording tasks and one commission, all owner-directed.

## (a) XRP-101 recorded — `research/knowledge-ledger/FINDING-XRP-101.md`

The cross-repository alignment check the owner asked for had run outside the run
system and existed only as merged pull requests. Now recorded with evidence
regenerated at write time (`logs/xrp101-evidence.txt`): 77 configurations, all
three implementations agreeing 77/77 on all three compared quantities after the
repair, and the pre-repair divergence stated in the terms that matter — Gate
published a reversal price of 4 forgeries where 2 compromises suffice, and both
products asserted abstention-at-flip_budget unconditionally when parity makes it
unreachable at odd margins.

The rule it establishes: a quantity named by the paper and implemented in more
than one repository is verified by no single repository's suite.

## (b) Placement pointers added — `CONFORMANCE-PROFILE-v1.md`

The profile named neither Gate nor Border, though P1–P5 now ship in both. A
table now records which rules live where, at which commit, cut from which
version of this file — and states that the extracts are copies that do not
update themselves, with XRP-101 cited as what that costs.

## (c) BL-046 opened

The XRP-101 audit compared three of six shared quantities. `immunity_applicable`,
the T5 floor and `unbound_root_weight` are unmeasured across implementations.
Ranked 1 alongside BL-044.

## Commission — BL-044, and the blocker found while packaging it

The LIN-000 commission package is built and screened
(`$HOME/Development/lin000-spec`, three files plus MANIFEST.sha256).

**Twelve of LIN-000's fourteen outcome counters were already public** — published
hours earlier by this program's own delivery of RUN-6..10, inside RUN-10's draft
run report. Two more were public before that. The registered pass condition was
counter equality, which is now unfalsifiable-by-tuning for anyone with web
access.

Found by screening the withheld set against every file on `github/main` in both
bare and comma-separated form, not against the package alone. Recorded as M27.

**Repair, applied in the brief rather than in the registration:** the pass
condition becomes reproduction of two pinned world-stream digests. Knowing a
count gives no path to a SHA-256 over the stream that produced it — the C11
argument, reused. `lineage/REGISTRATION.md` was not edited; adding a pass
condition to a committed registration would be the defect this program was built
to refuse, so the addendum lives in the commission.

This also sharpens the experiment. BL-044 exists to test whether registering a
draw schedule buys cross-implementation randomized reproducibility (the F11
repair). A stream digest tests exactly that and nothing else.

## Not done

Kernel states unchanged. No registration created or edited. A2, BL-045/PPR-101
and BL-042 remain owner-queued.
