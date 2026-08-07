# KL-001 first check, corrected registration (FC1.1)

Registered before execution by RUN-20260807-6, after FC1's E4 **failed as
registered**. FC1's registration, script, and result are preserved
unmodified; this document supersedes only expectation E4 and adds E5.

## The drafting error FC1.1 corrects

FC1's E4 demanded that the repository world W1 and its KL-000-vocabulary
twin W4 produce receipts "identical in every structural field (`conclusion`,
all of `search`, all of `evidence`)". But `evidence.supportingRoots` and
`evidence.opposingRoots` are, by the registered receipt object (v1.2.0
R5.1), sorted echoes of the *declared rootId strings* — `scanner-A`/
`scanner-B` in W1, `r1`/`r2` in W4. They can never be identical under
renaming, and their difference is the receipt doing exactly what the
specification requires. The expectation conflated structure with the names
structure is expressed in. The error class is the program's own M15/H1
family: an expectation written by reading a concept ("structural") instead
of enumerating the fields it quantifies over.

## Corrected expectations (worlds W1–W4 unchanged, from FC1)

- **E4′ — name-free structural identity.** W1's and W4's receipts are
  identical in every field that carries no declared identifier:
  `conclusion`, `reason`, all four members of `search`, and the five
  name-free members of `evidence` (`records`, `distinctRoots`,
  `repeatedRecordsCollapsed`, `margin`, `conversionsToReverse`).
- **E5′ — the divergence is exactly the names.** The members on which the
  two receipts differ are exactly: `claim.proposition`, `transactionId`'s
  echo aside (equal here by construction), `evidence.supportingRoots`,
  `evidence.opposingRoots`, and consequently `contentDigest`. Nothing else.

E1–E3 stand as registered in FC1 and already passed; they are not re-judged.

## Verdict rule, restated

**(a)** holds if E4′ and E5′ both pass: the evaluator sees structure only,
the repository costume is a renaming, FC1's check is I2 restated, and
KL-001's named first gate was already paid by KL-000 — with FC1's E4
failure standing in the record as a mis-registration, not as evidence
against (a). **(b)** holds if E4′ or E5′ fails: a name-free field diverged
under renaming, which would be genuinely new behaviour and the finding.

## Invalidation

As FC1: evaluator hash mismatch; W4 out of KL-000 bounds; judging from
anything but the emitted receipts.
