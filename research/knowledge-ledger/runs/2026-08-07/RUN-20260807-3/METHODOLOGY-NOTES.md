# Methodology notes — RUN-20260807-3

Continuing M1–M6 (RUN-20260807-1) and M7–M12 (RUN-20260807-2), all in force.

## M13 — A digest pin is a function of a codec and an object; pinning one pins neither

C11 under v1.1.0 pinned a hash while registering only the codec: 39.7% of the
hashed bytes were values no document stated (SPEC-108). A conforming
implementation could not compute the pin, and a matching implementation would
have proven only that it guessed the reference's schema. When registering any
digest, enumerate what is hashed — member list, member values or their
derivation rules, and the codec — and let the fixture carry the full
pre-image (the canonical string), so a mismatch localises to a byte instead
of terminating at a hash inequality.

## M14 — Registrations and commission packages are different artifacts with contradictory requirements

The registration must contain the prediction table (falsifiability); the
package must not (blindness). v1.1.0 shipped one file in both roles and
leaked every screened value (LEAK-101), defeating a redaction correctly
applied to the file beside it. A package is *derived* from a registration by
deletion, carries its own manifest of digests, and is screened per shipped
file — in every number format the documents use. A screen that passes on the
wrong scope is worse than none; this is the third instance of that shape in
the program's record (PROV-004's transcription, the v1.0.0 artifacts list,
now this).

## M15 — When a check contradicts a documented claim, suspect the check's scope before the claim

Twice this run a verification contradicted the record and the *verifier* was
wrong both times: a leak grep ran comma-less against the wrong directory
(finding nothing where the leak existed), and the first G4 ablation inverted
all presence conclusions instead of implementing the specific contested
reading (finding too much). Both were caught because the claims under test
were stated precisely enough to disagree with. The discipline: reproduce the
claim's own scope exactly — same file, same format, same ablation — before
concluding anything about the claim; and preserve the wrong first attempt
with its correction, since a verifier error class that produced one silent
false negative will produce another.

## M16 — A self-caught registration typo is amended in the protocol log, never by editing the preregistration

v1.2.0's prose said "ten members" over a nine-entry list, caught minutes
after the registration commit. The protocol document was corrected as a
logged pre-execution amendment (the v1.0.0 Amendment-1 precedent); the
preregistration — whose machine-readable `memberList` was always correct —
was not touched, preserving the sidecar chain, and its prose error stays on
record. The rule: the immutability of the registered file outranks its
cosmetic correctness, because the chain is checkable and the typo is
documented, whereas an edited registration is unverifiable however right.

## M17 — Conformance claims name their object

"Two implementations agree" is four different claims here, with four
different strengths: the evaluator's partitioning (established,
IND-20260807-1), the conclusion function (established, IND-20260807-2,
qualified by LEAK-101), the receipt bytes (untested until IND-20260807-3),
and the randomized phase (a replication forever under F11). Every agreement
statement in this run's record names which object it is about. The
alternative — "the implementations agree" unqualified — would have been true
and misleading at every stage of this program so far.
