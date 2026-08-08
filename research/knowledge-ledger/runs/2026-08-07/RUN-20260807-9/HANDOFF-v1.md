# HANDOFF v1 — RUN-20260807-9

The provenance break is closed: verified first, corrected by amendment with
registered text preserved, and enforced forward by TRC-101. No behaviour,
number, or digest moved; no state changed.

## Where the work is

Base eacc2f6 (RUN-8 close). Commits: 7c7fce9 (open, both facts verified,
break found wider than briefed), 394d9b7 (amendment-log corrections:
v1.1.0 A1, v1.2.0 A3, v1.3.0 A1, FINAL-RECORD, STATUS), 54194e7 (TRC-101 +
map + 55-check enforcement), then this packet. Tree clean; 172 repo + 88
KL-000 tests green with pipefail; four chains verify; nothing pushed.

## The plain counts (machine-checked)

Paper claims in KL-000's scope: 14. Fully tested 6, partially 4, untested 4
(abstention threshold, Lemma 1, Theorem 1, R1 root integrity). KL-000
rules: 19. Paper-derived 6, partial 6, specification-local-with-reason 7.
One receipt-contradicts-paper finding: flip_budget (RCP-101 -> BL-040).

## Yours

1. BL-042: apply TRC-101 at registration time BEFORE the eleven kernels
   register (cheap; prevents BRK-101 recurring at the worst moment).
2. The digest-moving bundle's composition: BL-040 flip_budget + BL-026
   margin rename (now a deviation-from-paper question) + BL-037/BL-041
   lineage-bearing schema.
3. A2 (paper evidence recorded; still yours). 4. PPR-101 (paper's |margin|
   bars). 5. Delivery of RUN-6..9 to main; promotion, untouched as always.

## For any resumer

The map (KL-000/TRACEABILITY-v1.3.0.json) is now the first place to look
before calling any KL-000 rule a free choice -- M30: "owner decision" is a
provenance claim and gets audited like one. The registered documents'
original characterisations stand with their corrections beside them, as
every correction in this program has been made.
