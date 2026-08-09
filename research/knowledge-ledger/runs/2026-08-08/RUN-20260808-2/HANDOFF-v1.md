# Handoff — after RUN-20260808-2

## State

BL-044 answered and closed. Nothing registered, no kernel advanced, nothing
repaired.

## The F11 answer, for whoever picks up BL-016

Registering a draw schedule in prose is **necessary but not sufficient**. It buys
"one coin-flip away", not a stream. Do not adopt it program-wide as it stands.
BL-051 carries the four fixes: define the generator in-document, register draws
as primitives rather than distributions, specify boundary cases and enumeration
orders, publish prefix digests.

The exhaustive-phase miss is the one to internalise: that phase has no PRNG at
all and still failed, because a digest was demanded of a list whose order was
never specified. Any future digest-pinned deterministic phase inherits that bug.

## Read the alert correctly

The chain check is red and the registrations are fine. Verified 4/4 by content
against their pins. Until BL-049 lands, treat the alert as "verify by hand", not
"registrations broken". Details and attribution in FINDING-CHAIN-101.md.

## Owner queue

Gate PR #9 (escalate when the immunity guarantee is void) is open as a draft and
is a published-behaviour change. BL-050 needs an owner call on which internal
vocabulary belongs in a public blocklist, since the blocklist names what it
protects. BL-042 (TRC-101 at registration time) stays urgent before any kernel
registers.
