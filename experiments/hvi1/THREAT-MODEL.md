# HVI-1 control-domain threat model

The adversary controls evidence production and may create unlimited account
names, signing keys, services, verifier labels, or corporate labels. It may
copy the same claim and evidence bytes into every representation. It wins if
representation multiplication increases accepted independent evidence without
new supported separation.

The adversary may also self-verify, omit controller provenance, or supply
conflicting controller assertions. The evaluator must preserve those states as
ineligible or uncertain rather than interpreting signatures as independence.

The experiment assumes controller assertions marked `supported` are correct.
Compromise of their issuer, undisclosed beneficial ownership, collusion between
nominally separate controllers, and the truth of the underlying claim are out
of scope. Those are upstream evidence problems, not discoveries made by this
evaluator.

The verifier must be unable to manufacture independence merely by issuing the
receipt it later evaluates. A third-party label is not a trust guarantee.
Independence comes from supported separation, transparent rules, explicit
uncertainty, and inability to mint the evidence being verified.
