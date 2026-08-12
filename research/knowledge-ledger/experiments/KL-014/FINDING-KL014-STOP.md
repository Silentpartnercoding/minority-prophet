# KL-014 — stopped as not executable, before producing any number

The registered endpoint is lead-follow timing: count distinct wallets acting on a
token in the 60 seconds after a subject wallet's first position, against a
baseline of random 60-second windows in the same token.

**It cannot be measured from this data source, and the baseline is what proved it.**

## What the baseline showed

Built first, deliberately, because every earlier failure today came from building
the interesting side before the contrast.

Sampling each token's most recent 1,000 signatures reaches back between **2.5 and
33 hours**, depending on how active the token still is. Median distinct wallets in
an arbitrary 60-second window: **0** — most of these tokens are dead now.

Subject events are **354 to 9,085 hours old**. Every one of 12 sampled events lies
outside the baseline's reach.

    12/12 events outside baseline reach
    oldest event: 9,085 hours (~1 year)
    furthest baseline reach: 33 hours

## Why that is fatal rather than inconvenient

Comparing "wallets active after a subject's buy, during the token's rise" against
"wallets active in an arbitrary minute now, when the token is dead" measures
**era, not influence**. It would have produced a large, significant, entirely
spurious effect — subject windows busy, baseline windows empty.

Reaching the correct era means paging back hundreds of thousands of signatures per
token. At the sustained rate that is hours per token across fourteen tokens, and
it buys a comparison on wallets selected by a post-hoc custodian filter.

## What was NOT done

No follower count was computed. No subject event was measured. The stop happened
before any number existed, which is the only reason it is a stop rather than a
retraction.

## What would make it executable

Subjects drawn from **recently graduated** tokens, where the event and the
baseline occupy the same reachable window. That is a different population —
recent winners rather than all-time winners — and it needs its own registration,
because the subject set would no longer be the eleven wallets this registration
inherited.

## The pattern this closes

Five errors today shared one shape: a comparison whose control could not expose
the confound.

  - v0.1 population: 2 of 1,570 tokens ever tradeable
  - exchange result: controls that never reach an exchange
  - root-collapse: a control arm left unprofiled
  - combined statistic: two filters in one number, significance belonging to the other
  - **this one: a baseline that cannot reach the events**

The first four produced numbers before the flaw was found. This one did not,
because the contrast was built first. That is the only procedural change that has
worked, and it is the finding worth keeping.
