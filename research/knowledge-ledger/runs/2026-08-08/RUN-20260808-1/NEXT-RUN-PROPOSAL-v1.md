# NEXT-RUN-PROPOSAL v1 — after RUN-20260808-1

No committed gate. Two candidates, and they do not compete for the same slot.

**Out of house: BL-044 is packaged and can go now.** It needs an implementer, not
a run. The sharpest question in the program — does registering a draw schedule
actually buy cross-implementation randomized reproducibility — is now testable by
digest rather than by counters, which is what makes it worth asking after
publication burned the counter-based version.

**In house: BL-046.** The XRP-101 harness generalises to `immunity_applicable`,
the T5 floor and `unbound_root_weight`. Cheap, and the base rate is discouraging:
of three quantities compared, one had diverged badly enough to mispublish a
security claim. `immunity_applicable` is the sharpest, because T1's precondition
depends on it and a disagreement there is a disagreement about when the immunity
theorem applies at all.

Before any kernel registers: **BL-042** (TRC-101 at registration time).

Owner queue otherwise unchanged: BL-045 (paper v1.0.4 adoption; PPR-101), A2
(BL-043), the digest-moving bundle (BL-026/BL-037), registration scheduling
(BL-039).
