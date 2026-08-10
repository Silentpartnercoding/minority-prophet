# Border — no counterexample within the declared search

`minority-prophet-border` @ `41c1c070473f`. Attacks run out-of-tree against the
public API. Every suite below established a **verified baseline first**, because a
rejection that happens for a schema reason proves nothing about a security rule.

## DSSE / admission binding — 9 of 9 hold

    BASELINE valid envelope verifies                   (control)
    action digest substituted             -> rejected
    decision point flipped                -> rejected
    expiry extended                       -> rejected
    policy digest swapped                 -> rejected
    subject name swapped                  -> rejected
    signatures stripped                   -> rejected
    unknown key id                        -> rejected
    envelope signed with a foreign key    -> rejected

The first attempt at this suite ran without a valid baseline: the envelope failed
with "unknown admission statement type", so all three tamper tests were rejected
for the wrong reason and would have been recorded as passes. Repeated with a real
admission statement.

## Subject-link normalization — 8 of 8 hold

    1 provider vs minimum_providers=2     -> escalate
    same provider twice != two providers  -> escalate
    two distinct providers                -> accept      (control)
    different pairwise subjects           -> block
    revoked evidence                      -> SubjectLinkError
    expired evidence                      -> SubjectLinkError
    wrong audience                        -> block
    invalid signature                     -> SubjectLinkError

Worth recording: on the accepting control, `establishes_provider_independence` is
**False**. Two distinct providers satisfy a count requirement and Border still
declines to call that independence, which is exactly what its documentation says
and the opposite of the failure mode this programme names as central.

## Not tested

Delegated-authority scope, canonical serialization edge cases beyond the
substitutions above, the OpenID gateway paths, witness-write failure, and replay
across a durable store. Absence of a result, not a clean result.
