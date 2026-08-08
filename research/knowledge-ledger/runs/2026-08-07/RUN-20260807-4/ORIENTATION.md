# ORIENTATION — RUN-20260807-4 (final run of the program)

Opened 2026-08-07T22:19:15Z on branch `agent/knowledge-ledger-run-20260807-1`,
HEAD `ecb2b45` (RUN-20260807-3's close plus the R5.2 ratification). Worktree
clean at start except this run directory. Environment unchanged from run-3
(lock copied, pip freeze identical).

## 1. What this run is

Close out KL-000. Import IND-20260807-3 (passed — both digests reproduce),
record the mechanistic finding (both owner decisions are enforced by zero
invariants), attach both ablations to the committed I12 gate, record A1/A2 as
permanent limits without deciding A2, produce the final KL-000 record,
rebuild the PR branch without pushing, confirm the eleven seeded kernels, and
close with the full packet. First-transaction gate NOT REACHED.

## 2. Verification of IND-20260807-3's claims — all pass, with one defect found in the artifact

| # | Claim | Verified how | Result |
|---|---|---|---|
| 1 | C11 digest and 703-byte canonical form reproduce; C12 digest and 691-byte form reproduce | read from `pinnedDigestAnalysis`; both `digestMatches: true`, `firstDifferingByteOffset: -1`, `canonicalUnsignedFormMatches: true`; member list now exactly the registered nine, `receiptVersion` gone | confirmed |
| 2 | Conclusion distribution 160 / 49,480 / 41,820 / 19,380; 0 violations over 13 tracked checks (11 hard invariants with I2/I5 split a/b); 12/12 controls | read from result | confirmed |
| 3 | R5.2-inverted ablation: 38,760 receipts change, 0 invariant violations, caught by C12 alone | **re-run on the reference side** over the full enumeration through `check_world` | **38,760 / 0 / C12-only — exact** (`logs/r52-ablation-verification.txt`) |
| 4 | R1-inverted ablation: 22,440 / 0 / C11+C12 | reference-side equivalent verified in RUN-20260807-3 (22,440 / 0 / C11-only against the 11-fixture v1.1.0 set; C12 now also catches it, consistent) | confirmed |
| 5 | Both pinned fixtures internally consistent (pinned string hashes to pinned digest; string is a fixed point of the stated realisation) | recomputed | confirmed, 703 and 691 bytes |
| 6 | H1: three registered sites say "all nine non-`contentDigest` members"; the correct count is eight | grep: `PROTOCOL-v1.2.0.md:87`, `preregistration-v1.2.0.json` lines 17 and 76 | **confirmed — this run's own miscount**, handled as protocol Amendment 2 (document-only; the machine-readable `memberList` and `digestScope` are correct, which is why no digest was affected — proven by the reproduction itself) |
| 7 | H3 packaging: manifest 16/16; the eight screened values absent in both formats; the exhaustive conclusion distribution ships in PROTOCOL.md and BRIEF.md | re-ran all three checks against `kl000-v120-spec/` | confirmed on all three |
| 8 | Eleven kernels still seeded with exact next gates, none silently advanced | scripted audit of all eleven STATUS.json files | confirmed (`logs/kernel-audit.txt`) |

## 3. Defect found in the imported artifact (recorded, artifact untouched)

`kl000-independent-result-v120.json` carries **ten metadata sections
byte-equal to the v1.1.0 result** — including `runId: "IND-20260807-2"`,
`protocolVersion: "1.1.0"`, `predecessor`, `runIdNote`, and an
`implementationNote` that still says "across both versions". The substantive
content is unambiguously v1.2.0 (12 controls, `pinnedDigestAnalysis` with
both matches, `repairR52TestSurface`, 14 attacks), and `FINDINGS-v120.md`
carries the correct identity (IND-20260807-3, v1.2.0, "there is no IND-4").
The `repairR52TestSurface.finding` prose is also partially copied from the R1
surface (it discusses R1 where its own numbers discuss R5.2).

This is the implementer's own H1 pattern — updated-in-place artifacts carry
stale fields — occurring in the decisive artifact of the program. It does not
void the result: the load-bearing content is internally consistent, the
digest verdicts were re-verified here against the registered pins, and the
ablation numbers were reproduced on the reference side. It is recorded as a
constraint (the result's self-description cannot be trusted for identity;
the FINDINGS document and the content can) and left unmodified, per the
standing rule.

## 4. Scope refusals

- A2 is **not decided.** Recorded as an owner decision the program did not
  reach, with both readings and consequences (19,152 worlds).
- The implementer's §3 margin-naming argument (`margin` collides C01 and
  C12) is recorded for the owner with its own recommendation (do not reverse
  R5.2; consider a v1.3.0 rename) — not acted on.
- No promotion, no push, no registry edit. The PR branch is rebuilt locally
  only.
