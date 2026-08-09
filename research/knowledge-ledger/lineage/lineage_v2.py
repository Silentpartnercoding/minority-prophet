"""LIN-000 v0.2 reference: generator, worlds, canonical stream.

Written strictly from REGISTRATION-v0.2.md, which was committed first (7c8233c).
Every construct here restates a registered sentence; where the registration is
silent this module must not choose, it must fail.
"""
from __future__ import annotations

import hashlib
import struct
from typing import Iterator

SEED = 20260808
MAX_CLAIMS_EXHAUSTIVE = 6
RANDOMIZED_WORLDS = 100_000
PREFIX_EVERY = 1_000
DECLARED_EXHAUSTIVE_COUNT = 50_362


class Words:
    """The registered word sequence.

    block(m) = SHA-256(seed_be || uint64_be(m)); w(i) is the (i mod 8)-th
    big-endian 32-bit word of block(i // 8). Consumed strictly in order.
    """

    def __init__(self, seed: int = SEED) -> None:
        self._seed_be = struct.pack(">Q", seed)
        self._index = 0
        self._block_number = -1
        self._block = b""

    def next_word(self) -> int:
        block_number, offset = divmod(self._index, 8)
        if block_number != self._block_number:
            self._block = hashlib.sha256(
                self._seed_be + struct.pack(">Q", block_number)).digest()
            self._block_number = block_number
        self._index += 1
        return struct.unpack(">I", self._block[4 * offset:4 * offset + 4])[0]

    def uniform_below(self, n: int) -> int:
        """Registered rejection rule. n == 1 consumes exactly one word."""
        if n < 1:
            raise ValueError("uniform_below requires n >= 1")
        limit = (1 << 32) - ((1 << 32) % n)
        while True:
            word = self.next_word()
            if word < limit:
                return word % n

    @property
    def consumed(self) -> int:
        return self._index


def randomized_worlds(count: int = RANDOMIZED_WORLDS,
                      seed: int = SEED) -> Iterator[list[dict]]:
    words = Words(seed)
    for _ in range(count):
        k = 1 + words.uniform_below(20)
        world: list[dict] = []
        for i in range(k):
            if i == 0:
                is_root = True            # registered: no draw consumed at i == 0
            else:
                is_root = words.uniform_below(10) < 3
            if is_root:
                parent = None
                side = words.uniform_below(2)
            else:
                parent = words.uniform_below(i)
                keep = words.uniform_below(10) < 9
                side = world[parent]["side"] if keep else 1 - world[parent]["side"]
            world.append({"parentIndex": parent, "side": side})
        yield world


def _positions(k: int) -> Iterator[list[tuple[int | None, int]]]:
    """Odometer over positions 0..k-1 with position k-1 varying fastest;
    within a position, parent-major: parents null,0,..,i-1 and for each, side 0
    then 1."""
    choices = [[(p, s) for p in [None, *range(i)] for s in (0, 1)] for i in range(k)]
    odometer = [0] * k
    while True:
        yield [choices[i][odometer[i]] for i in range(k)]
        for i in range(k - 1, -1, -1):          # last position fastest
            odometer[i] += 1
            if odometer[i] < len(choices[i]):
                break
            odometer[i] = 0
            if i == 0:
                return


def exhaustive_worlds(max_claims: int = MAX_CLAIMS_EXHAUSTIVE) -> Iterator[list[dict]]:
    for k in range(1, max_claims + 1):          # ascending k
        for combination in _positions(k):
            yield [{"parentIndex": p, "side": s} for p, s in combination]


def declared_exhaustive_count(max_claims: int = MAX_CLAIMS_EXHAUSTIVE) -> int:
    total, factorial = 0, 1
    for k in range(1, max_claims + 1):
        factorial *= k
        total += factorial * (2 ** k)
    return total


def canonical_world(world: list[dict]) -> str:
    return ";".join(
        f"{'-' if c['parentIndex'] is None else c['parentIndex']}|{c['side']}"
        for c in world)


def stream_digests(worlds: Iterator[list[dict]]) -> tuple[str, list[str], int, int]:
    """Total digest, prefix digests every PREFIX_EVERY worlds, world count, bytes."""
    digest = hashlib.sha256()
    prefixes: list[str] = []
    count = byte_count = 0
    for world in worlds:
        chunk = (canonical_world(world) + "\n").encode("ascii")
        digest.update(chunk)
        count += 1
        byte_count += len(chunk)
        if count % PREFIX_EVERY == 0:
            prefixes.append(digest.copy().hexdigest())
    return digest.hexdigest(), prefixes, count, byte_count


# --- the properties under test ------------------------------------------------

def root_of(world: list[dict], index: int) -> int:
    seen = set()
    while world[index]["parentIndex"] is not None:
        if index in seen:
            raise ValueError("lineage cycle")
        seen.add(index)
        index = world[index]["parentIndex"]
    return index


def s_sets(world: list[dict]) -> tuple[frozenset[int], frozenset[int]]:
    sets: tuple[set[int], set[int]] = (set(), set())
    for i, claim in enumerate(world):
        sets[claim["side"]].add(root_of(world, i))
    return frozenset(sets[0]), frozenset(sets[1])


def verdict(world: list[dict]) -> str:
    s0, s1 = s_sets(world)
    if len(s1) > len(s0):
        return "1"
    if len(s0) > len(s1):
        return "0"
    return "abstain"


def is_side_consistent(world: list[dict]) -> bool:
    return all(claim["parentIndex"] is None
               or world[claim["parentIndex"]]["side"] == claim["side"]
               for claim in world)


def roots_asserting(world: list[dict], side: int) -> frozenset[int]:
    return frozenset(i for i, c in enumerate(world)
                     if c["parentIndex"] is None and c["side"] == side)
