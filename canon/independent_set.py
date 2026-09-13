"""Exact maximum-independent-set counting, with a budget instead of a fallback.

Greedy was offered earlier as a cheap approximation on the grounds that it only
ever under-counts, and under-counting is conservative. That reasoning is wrong
and this module exists to retire it.

**Greedy is order-dependent, and order is usually attacker-influenced.** Take a
hub `X` cited by three otherwise-unrelated witnesses `A`, `B`, `C`. Present `X`
first and greedy keeps `X`, then rejects all three: count 1. Present `A, B, C`
first and greedy keeps all three: count 3. Identical evidence, and whoever
controls the ordering picks the answer.

That is not conservatism. It is a censorship primitive: an adversary who cannot
inflate a count can still *deflate* one, making genuinely independent evidence
look derivative and suppressing a true claim. "Conservative" is the wrong word
for a number an attacker can choose.

It also destroys falsifiability. If the count is a fuzzy under-approximation,
a refusal no longer distinguishes "the evidence really was dependent" from "the
algorithm took a bad path", and an assay whose negative results are
uninterpretable is not an assay.

So: exact, or refuse. Never approximate silently. ``CountingBudgetExceeded`` is
a `DENY` with a stated reason, consistent with `Unknown ≠ Allow`.

Exactness is affordable in practice. The dependence graph shatters into
connected components -- witnesses from unrelated lineages share no edges -- and
each component is solved separately and summed. Real corpora produce many small
components rather than one large one.
"""

from __future__ import annotations

from typing import Callable, Hashable, Sequence, TypeVar

T = TypeVar("T", bound=Hashable)

#: Default search budget in branch-and-bound nodes. Exceeding it raises rather
#: than degrading to an approximation.
DEFAULT_BUDGET = 2_000_000


class CountingBudgetExceeded(RuntimeError):
    """The exact count could not be established within budget.

    Callers must treat this as a denial, not as a licence to guess.
    """


def _components(verts: list[int], adj: dict[int, set[int]]) -> list[set[int]]:
    seen: set[int] = set()
    out: list[set[int]] = []
    for start in verts:
        if start in seen:
            continue
        stack, comp = [start], set()
        while stack:
            v = stack.pop()
            if v in comp:
                continue
            comp.add(v)
            stack.extend(adj[v] - comp)
        seen |= comp
        out.append(comp)
    return out


def maximum_independent_set_size(
    items: Sequence[T],
    dependent: Callable[[T, T], bool],
    *,
    budget: int = DEFAULT_BUDGET,
) -> int:
    """Exact size of a maximum independent set. Raises rather than approximating."""
    n = len(items)
    if n == 0:
        return 0

    adj: dict[int, set[int]] = {i: set() for i in range(n)}
    for i in range(n):
        for j in range(i + 1, n):
            if dependent(items[i], items[j]):
                adj[i].add(j)
                adj[j].add(i)

    spent = 0

    def solve(verts: frozenset[int]) -> int:
        nonlocal spent
        spent += 1
        if spent > budget:
            raise CountingBudgetExceeded(
                f"exact independent-set count exceeded {budget} nodes for "
                f"{n} witnesses; refuse rather than approximate"
            )
        if not verts:
            return 0
        # Branch on the most-constrained vertex.
        v = max(verts, key=lambda x: len(adj[x] & verts))
        if not (adj[v] & verts):
            # No edges left in this subproblem: everything remaining is free.
            return len(verts)
        excluded = solve(verts - {v})
        included = 1 + solve(verts - {v} - adj[v])
        return max(excluded, included)

    return sum(solve(frozenset(c)) for c in _components(list(range(n)), adj))


def greedy_independent_set_size(
    items: Sequence[T], dependent: Callable[[T, T], bool]
) -> int:
    """Order-dependent lower bound. **Diagnostic only.**

    Retained so the order-dependence attack stays demonstrable in the test
    suite. It must never be used as a fallback when the exact count is
    unavailable -- see the module docstring.
    """
    chosen: list[T] = []
    for s in items:
        if all(not dependent(s, c) for c in chosen):
            chosen.append(s)
    return len(chosen)
