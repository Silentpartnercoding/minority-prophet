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

- **AID-1 — what attestation costs.**
  [`AID-1-DESIGN-DRAFT.md`](AID-1-DESIGN-DRAFT.md) is the specification: the
  policy under test, the arms, the traps the world must contain, and criteria
  fixed before any world exists. Specification only; the world is to be written
  by someone other than the author of the policy, which is the one discipline
  that worked in the closed series.
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
