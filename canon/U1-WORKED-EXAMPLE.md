# U1, worked: a case where the paperwork says two and the content says one

Companion to `U1-PROXIMATE-ROOTS.md`. That document argues that shared ancestry is
cause-in-fact rather than dependence, that the count is a maximum independent set, and
that a shared idiosyncratic marker overrides any provenance record claiming
re-derivation. The argument is abstract. This is a specimen you can grow yourself in
under a minute, on your own machine, with no data and no library.

The specimen is a version-control system. It keeps meticulous provenance records, and
there is an ordinary, blameless operation that makes those records say two independent
sources where the truth is one source copied.

**Grow it.** Nine commands. Any git will do.

```bash
git init -b main . && git commit --allow-empty -m root

git switch -c feature
printf 'def add(a, b):\n    # NOTE: bulid order matters here\n    return a + b\n' > lib.py
git add -A && git commit -m "add lib"

# The squash: content is copied onto main, parentage is not.
git switch main && git merge --squash feature && git commit -m "Build the library"

# Both lines then move on independently.
git switch feature && printf 'def sub(a, b):\n    return a - b\n' >> lib.py
git add -A && git commit -m "extend on the branch"
git switch main    && printf 'def mul(a, b):\n    return a * b\n' >> lib.py
git add -A && git commit -m "extend on main"
```

**Read the paperwork.**

```bash
git merge-base main feature                                 # the shared ancestor
git ls-tree -r --name-only $(git merge-base main feature)    # prints nothing
git merge --no-commit --no-ff feature                        # what git concludes
git merge --abort                                            # leave the tree clean
```

The listing prints nothing, and that silence is the finding: the shared ancestor
contains **zero files**. Git therefore reports:

```
CONFLICT (add/add): Merge conflict in lib.py
```

`add/add` is git saying the two sides created this file independently. On the record,
these are strangers who happen to have written the same file.

**Read the content.**

```bash
git show main:lib.py    | grep -c bulid      # 1
git show feature:lib.py | grep -c bulid      # 1
```

The misspelling `bulid` is on both sides. Nobody typed that twice. It is a trout in the
milk: an idiosyncratic error with no innocent explanation, and it survives the operation
that destroyed the record.

**What the two verdicts are actually answering.**

Git is not wrong. It is answering a narrower question honestly: *do I have a recorded
common version of this file to merge against?* No, so it declines to guess and asks a
human. That is correct behaviour and it is why `add/add` exists.

The trap is that the answer looks like an independence claim and is not one. A reader
who takes the record at face value counts two sources. A reader who reads the substance
counts one. The record was not forged; it was **discarded by a routine operation**, which
is the more common case and the harder one to notice.

**What our rule returns.**

```python
from canon.root_identity import Witness, proximately_dependent, effective_witnesses

a = Witness("main",   ancestry=frozenset(), markers=frozenset({"typo:bulid"}))
b = Witness("branch", ancestry=frozenset(), markers=frozenset({"typo:bulid"}))

proximately_dependent(a, b)     # True
effective_witnesses([a, b])     # 1
```

Recorded ancestry is empty, exactly as git reports it. The shared marker is decisive
anyway, which is the whole point of `shares_markers` outranking `shares_ancestry`. And
supplying a provenance record that explicitly asserts an intervening re-derivation does
not move it:

```python
effective_witnesses([a, b],
    lambda x, y: proximately_dependent(x, y, rederived=lambda *_: True))   # still 1
```

The content outranks the paperwork because the paperwork is what an adversary controls.
Here there was no adversary at all, only a squash, and the rule holds for the same
reason.

This case is already pinned in the suite as
`tests/test_root_identity.py::test_marker_detects_dependence_with_no_recorded_ancestry`.

**Now break it, because the limit matters more than the demonstration.**

Fix the typo on one side before merging and the marker is gone. The record is still
empty, nothing now links the two, and the count becomes 2. It is wrong, and no counting
rule can rescue it.

That is `U1`'s stated residual, reachable in this toy in one command. Detection can only
ever report that no trace was found, never that none exists. What absorbs the residual is
requiring a margin above the count rather than trusting the count, which is `R3`, and the
deliberately uncomfortable test asserting that laundered copies are over-counted is
`test_ATTACK_laundered_provenance_inflates_the_count`.

**Why this specimen is worth keeping.**

- It needs no dataset, no credentials and no domain knowledge.
- The ground truth is not in dispute. You performed the copy yourself.
- The failure is produced by a tool nobody suspects, doing its job correctly.
- Both halves are visible in one place: the rule getting it right, and the rule's limit
  getting it wrong, one edit apart.

The general shape, stated without git: **when a provenance record and the content
disagree about independence, the content is the side that is expensive to fake.** Records
are cheap to lose and cheap to forge. An idiosyncratic error has to be re-derived to be
shared honestly, and re-derivation is exactly the thing being claimed.
