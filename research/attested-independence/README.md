# Attested independence

**A new series, opened 2026-09-16.** It is not a continuation of
[decision-relative independence](../decision-relative-independence/README.md),
which closed on the finding that no rule reading the record can separate
independent evidence from dependence the record does not carry. Naming this
work as a twelfth DRI experiment would imply it inherits that question. It does
not.

## The question

The old question was *can we detect it?* — answered no, and proved.

This one is: **can a witness be made to declare and back how far it actually
went, and what does it cost to stop counting the ones that do not?**

That is a question about records and incentives rather than about instruments.
Nothing in it needs a detector, and no result here can be rescued by building a
better one.

## Why it is worth asking

The policy in [`canon/ATTESTED-INDEPENDENCE.md`](../../canon/ATTESTED-INDEPENDENCE.md)
refuses to convert the record's silence into independence. That is sound in the
direction that matters and obviously not free. Its price is the only open
question about it, and unlike everything in the closed series, the price is
directly measurable.

## Experiments

- **AID-1 — what attestation costs. Run, and rejected**, 61 of 111 checks.
  [`AID-1-DESIGN-DRAFT.md`](AID-1-DESIGN-DRAFT.md) is the specification;
  [`experiments/aid1run/PREREGISTRATION.md`](../../experiments/aid1run/PREREGISTRATION.md)
  is the world, written by someone other than the policy's author; the result is
  [`results/aid1-v1/`](../../results/aid1-v1/README.md).

  The price is real and unevenly distributed. At full adoption the policy
  prevents 177 of 350 silent false settlements in DR3's hidden-source case — the
  case nothing in the closed series could touch — at **zero** cost in correct
  settlements. One error class up, prevention decays to **zero** as adoption
  rises, because attestation raises admissible depth and hands back the
  independence the policy was withholding. Where witnesses genuinely cannot
  attest, it loses every settlement at every adoption rate and prevents nothing.
  And it **suppresses**: 720 of 720 minority decisions settled against a true
  contrary claim at full adoption, while every other arm abstains and the claim
  lives. The `ScopeViolation` guard did not hold and cannot, because the use is
  caller-declared.

  Two defects in the policy were disclosed in the protocol before the run and
  left in place deliberately, so this measured the policy as shipped. Repairing
  them is a registered successor, not an edit to this record.
- **AID-2 — does the range do what the number could not. Run, and rejected**,
  74 of 120 checks.
  [`AID-2-DESIGN-DRAFT.md`](AID-2-DESIGN-DRAFT.md) froze the criteria before the
  world existed;
  [`experiments/aid2run/PREREGISTRATION.md`](../../experiments/aid2run/PREREGISTRATION.md)
  is the world, written by someone other than the policy's author; the result is
  [`results/aid2-v1/`](../../results/aid2-v1/README.md).

  **The range does fix what it was built to fix.** In AID-1's suppression
  construction the bounds arm preserves the true contrary claim **360 of 360**
  at every adoption rate, where the point estimate deletes all 360. A range
  serves two decisions that one number could not.

  **And it is inert on a case nobody anticipated.** Where only the minority's
  *recorded kinship* is a decoy, bounds and point are identical at every rate —
  360, 306, 204, 48, **0** — while the plain ladder holds 360 throughout. The
  upper bound runs the ladder at *admissible* depth, so a witness the policy
  discounts is discounted at both ends and a recorded ancestry token collapses
  the pair at both ends at once.

  **And it is blind to a backed witness with a shared origin.** Against three
  device-attested copies of one fabricator it prevents **0 of 360**, while
  closing three free-declaration strains essentially completely. A device
  attestation earns depth; it says nothing about shared origin. That is the A5
  defect still present, gated behind a depth check rather than removed.

  Three defects in the instrument were disclosed before the confirmatory salt
  was touched and left in place. Two are implementation errors rather than
  properties of the bounds idea, so **this does not close the bounds question** —
  a successor that fixes the upper bound and reads all four corners of the count
  box is a different instrument and must be separately registered.

- **AID-1-OBS — who states depth today.** An observational census of corpora and
  exchange formats, in
  [`experiments/aid1/OBSERVATIONAL-REPORT.md`](../../experiments/aid1/OBSERVATIONAL-REPORT.md).
  **Nobody states depth, and when the census ran, in no published format could
  they.** Of 52 claim objects, none states a witness depth, a backing, or an
  identity; of the five formats then in use for evidence crossing a boundary,
  none had a slot for one, each closing its origin object to additions. So the
  first obstacle was not that witnesses would refuse to say how far they went —
  it is that we had never given them anywhere to say it.

  **That obstacle is now removed** (2026-09-16, owner-approved):
  [`contracts/authority-evidence-v0.2`](../../contracts/authority-evidence-v0.2/README.md)
  adds the four axes as optional fields, and the census returns 1 of 6 formats.
  The instance count is still 0 of 52 — a field is not a statement, and no
  producer has been asked to fill it. Observational, not preregistered in the strict sense;
  read its disclosure section before citing any figure, and note it is refuted
  by exhibiting one instance that states a depth.

## Boundaries, stated up front

- Every synthetic rate in this series will be synthetic. Real attestation
  adoption is a fact about other people's systems, not about our generator.
- Same control domain unless an outside party states otherwise on the record.
- Evidence assessment never grants authority to act. Nothing here changes that.
