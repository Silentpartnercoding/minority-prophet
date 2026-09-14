# KL-019 — registered, never executed

Filed 2026-09-14 when this line was rescued from a stale branch. It is recorded as an
open registration rather than as finished work, because that is what it is.

**Why it was registered.** KL-018's endpoint passed at p = 0.00000 and its own control
refuted it. Subjects are top holders, so they buy during the launch burst, while the
baseline sampled random windows across a token's whole life. The comparison measured
*when* subjects buy rather than *whether anyone follows them*.

This registration is the repair. Each event is compared to the sixty seconds
immediately preceding it, in the same token, seconds apart, so burst level, token age,
liquidity, hype and lifecycle are identical on both sides by construction. It also
freezes in advance the three things that moved KL-018's result most: a tie rule, a
minimum of 150 non-tied events with an instruction to stop rather than report another
borderline number, and a replication requirement for anything landing between one and
five percent.

**Why it was never run.** The branch it lived on stopped the day it was registered.

**Feasibility, measured 2026-09-14 rather than assumed.**

- The design is immune to market regime, because it is self-matched. A different market
  moves both sides of every comparison together.
- The population is abundant. Seventy graduated tokens returned, every one inside the
  six-hour recency gate, median age 1.4 hours.
- DexScreener answers, so the tradeability gate is checkable.
- The registered source path, `frontend-api.pump.fun`, returns HTTP 530 and is dead.
  `frontend-api-v3.pump.fun` answers with the same shape and carries
  `created_timestamp` and `usd_market_cap`. **That is a deviation from the frozen spec
  and must be recorded in the collection commit if this runs, not swapped silently.**

**What blocks it, precisely.** One environment variable. The collectors read `SOL_RPC`
and pace themselves at eight requests a second, which is a paid endpoint's budget. No
Solana mainnet endpoint is configured on this machine: the one in the neighbouring
trading project points at devnet, and the Helius key beside it is empty. The sibling
experiment KL-012 records the shape that worked, an Alchemy Solana mainnet URL with the
key in the path.

It also ships no collector of its own. KL-018 shipped one and this did not, so running
it means writing the collector to this frozen spec.

**The recency gate means it can only be run forward.** Only tokens under six hours old
qualify, so there is no archive to replay. Whenever it runs, it runs on that day's
market, and the result describes that day.
