# CHAIN-101 — the registration chain check tests a proxy, and main carries duplicate history

Recorded by RUN-20260808-2. Two findings, one of which is mine.

## What fired

After PR #28 landed, the run monitor reported:

    !! KL-000 REGISTRATION CHAIN BROKEN: v1.0.0: c9773479 != 9525993b;
       -v1.1.0: 1a8256f5 != aa38c54d; -v1.2.0: 7e9e55fb != ced7c398;
       -v1.3.0: 08f8703a != bde70198

All four at once, each against a *different* commit. That pattern reads as a
history rewrite.

## The registrations are intact

Checked rather than assumed:

| preregistration | pinned commit on main | content at HEAD == content at pin |
|---|---|---|
| `preregistration.json` | yes | **yes** |
| `preregistration-v1.1.0.json` | yes | **yes** |
| `preregistration-v1.2.0.json` | yes | **yes** |
| `preregistration-v1.3.0.json` | yes | **yes** |

Every commit the `PROTOCOL-COMMIT` sidecars pin exists, is an ancestor of main,
and holds a blob byte-identical to the file at HEAD. The registration evidence
verifies. Nothing was lost and nothing was rewritten.

## Finding 1 — main contains two copies of its own registration history

Two commits share a message, a date, and a byte-identical
`preregistration.json` blob (`9bf8531d`), under different SHAs and different
trees:

    c977347  "Preregister KL-000 dual-ledger conformance, protocol v1.0.0"   <- pinned by the sidecar
    9525993  "Preregister KL-000 dual-ledger conformance, protocol v1.0.0"   <- what git resolves as last-touching

`9525993` was on public main **before** PR #24. `c977347` arrived **with** it.
The RUN-20260807-1 worktree branch carried its own copies of the registration
commits, 78 commits ahead of `github/main`, and PR #24 merged that line rather
than rebasing onto it. Both lines are now ancestors of main.

**Attribution: this was introduced by RUN-20260808-1's delivery of the research
work, not by any Codex pull request.** The monitor fired immediately after PR
#28 and the first reading of the alert blamed it; the ancestry says otherwise.
The chain has been red since PR #24 merged, and was not noticed because the
chain was verified on the run branch after that merge and never against
`github/main` — the same "measured the thing in front of me rather than the
thing that shipped" defect as the LAN-mirror misreading recorded in
RUN-20260808-1.

## Finding 2 — the check itself is wrong in both directions

The chain check asks: *does the file's last-touching commit equal the pinned
SHA?* That is a proxy for the property anyone actually needs, which is *have the
registered bytes changed since registration?*

The proxy assumes a linear history with exactly one commit per registered file.
It therefore:

- **reports red on an intact repository** whenever history is merged from a line
  that duplicates a registration commit — the present case;
- **would report green on a genuine tampering** that preserved commit identity
  while altering content, since it never compares bytes at all.

The substantive check is the one in the table above: the pinned commit is an
ancestor of the published branch, and the blob at HEAD equals the blob at the
pin. That survives merges, duplicated history and rebases, and it is what a
reader must verify to trust a preregistration.

## Disposition

Recorded, not repaired. Changing the check is a monitoring change and touches
nothing frozen, but it should be made deliberately rather than folded into a
logging run: **BL-049**. Until then the chain alert should be read as "verify
the substantive property by hand", not as "the registrations are broken" —
they are not.

The duplicate history is left in place. Removing it would mean rewriting
published history, which is a far worse remedy than an untidy graph, and the
sidecars still resolve to correct content.
