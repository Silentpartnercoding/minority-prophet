# KL-000 reproduction receipt

## What was done

The confirmatory run was reproduced from a **different repository base**, in a
separate worktree, following only the public instructions in `REPRODUCE.md`.

| | Confirmatory | Reproduction |
|---|---|---|
| Base commit | `887bd2f` (`agent/first-transmission`) | `335b34e` (`github/main`) |
| Interpreter | `/Users/james/Development/.mp-runner-venv/bin/python` | `/opt/homebrew/opt/python@3.14/bin/python3.14` |
| Python | 3.14.6 | 3.14.6 |
| Platform | macOS-26.4.1-arm64 | macOS-26.4.1-arm64 |
| Result | `passed` | `passed` |

## Outcome: exact match

Every field matched except the three declared as permitted to differ (`label`,
`environment`, `elapsedSeconds`). The comparison used the exact script published
in `REPRODUCE.md`, which printed `MATCH`.

```
exhaustive   176,120 worlds    0 violations    65,280 fail-closed
randomized 1,000,000 worlds    0 violations   756,619 fail-closed
conclusions  identical in both phases, to the world
```

Artifact digests:

```
kl000-confirmatory.json      sha256:9dc447ce23057fc8d142035746025b1c064a00c351f7ddf74e66607b8908864b
kl000-reproduction.json      sha256:33f9ef27787d99f52b69ef07704bef0272c59196d9ce9c13fa022f2695113ee9
kl000-effective-sample.json  sha256:1ec6e5a7b07669024b12bbe54f5c6e4add8a0e17f1ba20493d0252cd36e64e37
```

The two result files differ in bytes only in `label`, `environment`, and the two
`elapsedSeconds` values; they are therefore not expected to share a digest, and
the digests above are recorded for identification, not as an equality claim.

## What this establishes

1. **Determinism.** The result carries no hidden dependence on wall-clock, OS
   entropy, hash seed, filesystem ordering, or interpreter installation path.
2. **Base independence.** KL-000 does not depend on either commit that
   distinguishes `agent/first-transmission` from `github/main`. The evaluator
   under test is byte-identical on both
   (`sha256:15dfd500…3a3e21f`), verified directly from both trees.
3. **Instruction sufficiency.** `REPRODUCE.md` alone was enough. Nothing
   undocumented was needed.
4. **Cherry-pick target validity.** The PR branch proposed in `HANDOFF-v1.md`
   targets `github/main`, and KL-000 demonstrably runs and passes there.

## What this does NOT establish, and the claim is bounded accordingly

**This is not an independent reproduction in the sense `RESEARCH-METHOD.md`
requires**, and it must not be reported as one. Three things were held constant
that independence requires varying:

- **Same author.** The evaluator, the world generator, the invariant checker,
  the baselines, and this reproduction were produced in one session by one
  agent. `RESEARCH-METHOD.md`: "The implementation author may not be the sole
  verifier." A shared misconception about what an invariant *means* would
  reproduce perfectly and be invisible here — running the same reasoning twice
  cannot detect it.
- **Same machine and platform.** Both runs executed on the same Apple M4 under
  macOS 26.4.1 / arm64. Platform-dependent behaviour would not show up.
- **Effectively the same interpreter.** "System `python3`" is a *different
  installation* but the *same version*, CPython 3.14.6. Calling this a different
  interpreter would overstate it. A genuine cross-interpreter check needs a
  different major/minor version, or PyPy, or a non-Python implementation.

So this run establishes that the computation is deterministic and portable
across bases. It does **not** establish that the computation is *correct*, in
the specific sense that an independently reasoning implementer would agree with
its conclusions.

## The exact next falsifiable gate

A second evaluator, written from the public schema by an author with **no access
to `knowledge_ledger/transaction.py`**, must reproduce the same conclusion for
all 176,120 exhaustive worlds. Disagreement on any single world rejects the
shared assumption and identifies exactly where the two readings of the schema
diverge.

Until then KL-000's state is `adversarial-passed`, not verified-independent, and
KL-011 — which requires two genuinely independent implementations — remains
blocked on that gate rather than on anything this run produced.
