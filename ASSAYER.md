# ASSAYER.md — the position, and what it forbids us

This document states what Minority Prophet is *for*, in one metaphor, and then
spends most of its length on the constraints that metaphor imposes **on us**.
A doctrine that only binds others is advertising.

---

## 1. The position

Intelligence is being built at enormous scale. Agency — intelligence acting in
the world — is being built at comparable scale. Between them sits a function
almost nobody is funded to perform: deciding whether a claim is *grounded*.

That middle seat is not the oracle's, and not the referee's. It is the
**assayer's**.

An assayer does not find the ore, does not own the mine, and takes no share in
the find. They apply a fixed, published test to a sample and report what the
test showed. Their report is worth something precisely because of everything
they are *not*: not the prospector, not the buyer, not a partner in the outcome.

The fire does not care whose gold it is. That indifference is the product.

---

## 2. Why a verifier must be of different substance

The tempting metaphor is the Trinity — a third person completing two that
already exist. It is the wrong shape, and the reason is worth stating exactly.

The doctrine is *homoousios*: one substance. The Spirit **proceeds from** the
Father and the Son. Whatever else that is, it is not independence.

A verifier that proceeds from the thing it verifies inherits that thing's
errors — including, especially, the errors it cannot see in itself. This is not
a claim about honesty. A scrupulously sincere self-evaluation still fails,
because sincerity does not create the outside view that the evaluation requires.
Shared substance means shared blind spots, and shared blind spots are invisible
from the inside by construction.

So: **take the third position, refuse the third nature.**

This is the same structure as the bootstrap problem. You cannot lift yourself by
your own straps. What works is not more effort applied from inside — it is
growth into something you were not, until the straps burst. Every real advance
in verification has this shape. It is never "reason harder about yourself." It
is always "admit something you are not."

---

## 3. What the assay actually tests

Four properties, in the order they fail:

| Property | The question | Failure mode |
|---|---|---|
| **Provenance** | Where did this come from? | An unattributed claim counted as evidence |
| **Independence** | Do two supports share a source? | Correlated repetition read as corroboration |
| **Invariance** | Does presentation change the answer? | The same facts, restyled, scoring differently |
| **Falsifiability** | Could this have come out otherwise? | A test that cannot fail, passing |

Independence is the hard one, and it is hard for a reason that determines the
honest form of every report we issue.

---

## 4. The trout in the milk — what an assay can and cannot say

> "Some circumstantial evidence is very strong, as when you find a trout in the
> milk."
> — Thoreau, *Journal*, 11 November 1850

The milkman's crime is not proved by anything found in the milk. It is proved by
finding something that has **no business being there**. Absence of water cannot
be demonstrated. Presence of a trout can.

The same asymmetry governs us:

- **Independence cannot be proved.** No finite examination of two sources
  establishes that they share no ancestry. The ancestry may simply be
  unrecorded, and unrecorded ancestry is exactly where the population of
  interest lives.
- **Dependence can be detected.** A shared idiosyncratic error — the same wrong
  digit, the same distinctive phrasing, the same inherited mistake — is a trout.
  It has no business being in two independent sources.

Therefore the only report we are ever entitled to issue is:

> **No dependence trace was found by test T over sample S.**

Never "these sources are independent." The first sentence is an assay result.
The second is a claim about the world that no assay can support. Any artifact,
paper, dashboard or API of ours that states the second is a defect, and should
be reported as one.

The consolation is that this is not a weakness peculiar to us. It is the
condition of all empirical verification, and the disciplines that thrive under
it — metallurgy, epidemiology, audit — thrive by being precise about it rather
than by pretending otherwise.

---

## 5. What this forbids us

These are binding. Each is stated so that a violation is observable by someone
outside the project.

**A1 — No assaying what we depend on.**
We do not certify a system whose output our own conclusion relies on. If a
component is inside our reasoning, it is not a sample; it is an instrument, and
instruments get calibrated, not graded.

**A2 — Agreement inside one control domain is not validation.**
Any number of agents directed by the same operator, on the same instructions,
constitute one control domain. Their concurrence is internal replication. It may
be evidence of consistency; it is never evidence of correctness. A result is
independently validated only when reproduced by a party who could have reached a
different answer and had no reason to prefer ours.

**A3 — The test is published before the sample.**
A test chosen after seeing the data can be made to pass. The fixed public test,
pinned by digest and dated ahead of the run, is the entire difference between an
assay and an opinion.

**A4 — The test must be able to fail, and must have failed.**
A gate that has never rejected anything is not known to be a gate. We keep and
publish the negative results — the rejections, the withdrawn claims, the
premises an outsider corrected. A verification record with no failures in it is
itself a finding, and not a good one.

**A5 — No positive claims of absence.**
Per §4. Report what the test found, name the test, name the sample, state the
coverage. Silence in the instrument is reported as silence in the instrument.

**A6 — Our own instruments are auditable, including by the people we assay.**
An assayer who will not show you the furnace is asking for trust, which is the
commodity we exist to make unnecessary.

**A7 — We do not take a position in the outcome.**
Not in the sample, not in the sample's owner, not in the answer. The moment the
report's content is worth something to us, the report is worth nothing to anyone
else.

---

## 6. How you would know we had broken it

The doctrine is falsifiable, and here is how to falsify it:

1. Find a published result of ours that has never been reproduced outside our
   control domain, presented as validated. → **A2 violated.**
2. Find a test whose definition changed after the sample was drawn, without the
   change and its date being recorded. → **A3 violated.**
3. Find a gate in production that has rejected nothing since introduction, and
   is described as enforcing anything. → **A4 violated.**
4. Find the word "independent" applied to sources in any output of ours,
   unqualified by the test that was run and the coverage it had. → **A5
   violated.**
5. Find a certification issued to a system that appears in our own dependency
   graph. → **A1 violated.**

Each of these is checkable by a stranger with the public artifacts and no access
to us. That is the point. A doctrine whose violations only we can detect is
another bootstrap.

---

## 7. Why this is worth doing

The current evaluation ecosystem has a structural problem that is nobody's
fault: the parties with the capability to evaluate frontier systems are, almost
without exception, the parties that built them. Benchmarks are self-reported.
Evals are run by the party holding the incentive. This is the bootstrap problem
operating at the scale of an industry, and it will not resolve from the inside,
because from the inside there is no lever.

The seat is empty. It is not filled by being cleverer than the labs, or by
building a better model. It is filled by being **of different substance** — by
running a test that was fixed in advance, that can fail, that has failed, and
whose failures are published by someone with nothing to gain from the result.

That is not a grand claim. It is a narrow, boring, and entirely achievable one.
Assaying has always been a small trade. It is load-bearing anyway.
