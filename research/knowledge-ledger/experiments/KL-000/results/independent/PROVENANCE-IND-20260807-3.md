# IND-20260807-3 — provenance and final conformance record

Imported by RUN-20260807-4 on 2026-08-07 by copy. Nothing under
`kl000-independent-spec/` or `kl000-v120-spec/` was modified. Extends
`PROVENANCE.md` (IND-1) and `PROVENANCE-IND-20260807-2.md` (IND-2). This is
the final independent run; the implementer states there is no IND-4.

## What was copied

| File here | Original | SHA-256 (identical) |
|---|---|---|
| `FINDINGS-v120.md` | `impl-rs/FINDINGS-v120.md` | `521e60e21f678927c441f4f47132253469399c986db2e413313d649d74b7d01a` |
| `kl000-independent-result-v120.json` | `impl-rs/results/kl000-independent-result-v120.json` | `8f97a198155fceae03644c5ae53144e51e80b612d2cffe5d277708fb7f7be0dc` |

## The v1.2.0 commission package, digests recorded, not copied

`kl000-v120-spec/`: `PROTOCOL.md` `4c984007…`, `preregistration.json`
`c06590d0…`, `BRIEF.md` `e2209225…`, `MANIFEST.sha256` `70495306…`.
Verified this run: manifest **16/16 OK** with nothing shipped outside it;
the eight screened values absent in bare and comma formats (the LEAK-101
remediation held, confirmed adversarially by the implementer and re-confirmed
here); registered fixture paths resolve. **H3 caveat, adopted:** the
exhaustive conclusion distribution ships in `PROTOCOL.md` and `BRIEF.md` —
legitimate for *this* implementer, who published those figures in
IND-20260807-2 before the package existed, but a live tuning target for any
fresh implementer. Any future commission must withhold it.

## Defect in the imported result artifact (recorded; artifact untouched)

`kl000-independent-result-v120.json` carries ten metadata sections byte-equal
to the v1.1.0 result — `runId: "IND-20260807-2"`, `protocolVersion: "1.1.0"`,
`predecessor`, `runIdNote`, `implementationNote` among them — stale
carry-overs of the updated-in-place workflow, in the decisive artifact.
`repairR52TestSurface.finding` prose is likewise partially copied from the R1
surface. The correct identity (IND-20260807-3, v1.2.0) is in
`FINDINGS-v120.md`. **The load-bearing content is v1.2.0 and internally
consistent**, and was re-verified from this side: both digest verdicts
recomputed against the registered pins, and the R5.2 ablation reproduced
exactly on the reference implementation (38,760 / 0 / C12-only). The
artifact's self-description is not trustworthy for identity; its content is.
This is the implementer's own finding-H1 error pattern, and it is recorded
with the same discipline it prescribes: caught by counting from scratch, not
by reading the header.

## What IND-20260807-3 established

**C11 and C12 reproduce byte-for-byte across implementations.**

```
C11  sha256:84e63c21271a19c3bfbb1d42c5ce61e60288456a48c33829a66ae916bc33eafe   703 bytes, identical
C12  sha256:61000a9b978222ce227601621167d8d66109ba2a0fea13f6431f7830b0aa3b6e   691 bytes, identical
```

Not merely equal hashes: the canonical unsigned forms are byte-identical, and
the implementation's receipt now carries exactly the registered nine members
(`receiptVersion`, its former tenth, removed). **I4 and I6 — the last two
invariants never tested across implementations — are tested now, and the
answer is agreement.** R5.1 is what closed them: the implementer's codec was
already byte-identical to the stated realisation in IND-2; what changed is
that v1.2.0 registered the 279 bytes of `schema`, `reason` and `limits` that
no earlier document stated. The digest result is unaffected by LEAK-101 — a
count gives no path to a hash, and the receipt object was registered *after*
the leaked package — and the implementer had published its own conclusion
figures before receiving any package that carried them.

Alongside: conclusion distribution again exactly 160 / 49,480 / 41,820 /
19,380; zero violations across all thirteen tracked invariant checks; 12/12
controls; four ablated baselines caught; randomized phase again a replication
(F11, permanently, unless a stream is ever registered).

## The mechanistic finding — both owner decisions are enforced by zero invariants

IND-3 ran two ablations, each corrupting one owner decision and nothing else,
through the same checker over the full enumeration; the R5.2 side was
reproduced exactly on the reference implementation this run:

| decision | receipts changed | invariant violations (all 13 checks) | caught by |
|---|---|---|---|
| R1 inverted (ties conclude `supported`) | 22,440 | **0** | C11, C12 |
| R5.2 inverted (margin signed) | 38,760 | **0** | **C12 only** |

**The program's enforcement of its own decisions rests on two pinned inputs,
not on any property that holds across the enumeration.** An evaluator that
gets either decision backwards passes every invariant over 176,120 enumerated
and 1,000,000 randomized worlds; its entire detection surface is the two
fixture worlds. This is IND-2's G4 measured on both decisions. It is why
KL-000's state does not advance past `adversarial-passed`, and it is the
evidence attached to the committed I12 gate.

## The claim, at final strength

Established: **the evaluator, the conclusion function, and the canonical form
agree across two independent implementations in different languages with no
shared code** — the canonical form confirmed for two pinned receipts, not for
all 110,840; the conclusion function confirmed across the full enumeration;
qualified by LEAK-101 (the implementer saw the expected counts in the v1.1.0
package; the digest result is unaffected, the qualification still travels
with the claim); and bounded by the mechanistic finding above — what has been
demonstrated is that both implementations follow the same registered prose,
not that any invariant would notice if one stopped.

Not established, and stated plainly: "verified" in any form. The randomized
phase across implementations. The two undecided/unenforced surfaces (A2;
both owner decisions). Anything outside the declared bounds. Any part of a
knowledge transaction, cross-system result, or First Transmission — the
first-transaction gate is **NOT REACHED**.
