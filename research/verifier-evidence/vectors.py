#!/usr/bin/env python3
"""Negative vectors for draft-he-agentproto-verifier-evidence.

Each vector supplies a positive population and a negative control, and runs two
checks over both: one that cannot distinguish them and one that can. The point
of every vector is the PAIR. A vector that only ran the sound check would show
a check passing and prove nothing; a vector that only ran the degenerate check
would show a check accepting everything and prove nothing either.

Deterministic. No inference, no randomness, no network. Every function total.
"""

from __future__ import annotations

from dataclasses import dataclass

# Outcome vocabulary from the draft.
ACCEPT = "accept"
REJECT = "reject"
IMPLEMENTED = "implemented"
UNEXERCISED = "implemented-unexercised"

# Completeness vocabulary from CMP-1 and CMP-2.
ESTABLISHED = "established"
UNESTABLISHED = "unestablished"
FAILED = "failed"


def exercise_status(outcomes_positive, outcomes_negative) -> str:
    """EXR-1: a check is implemented only if its rejecting outcome occurred.

    Returns UNEXERCISED when the check returned one value everywhere, which is
    the case whether that value was accept or reject.
    """
    seen = set(outcomes_positive) | set(outcomes_negative)
    return IMPLEMENTED if REJECT in seen and ACCEPT in seen else UNEXERCISED


# --------------------------------------------------------------------------
# V1: a check comparing too little
# --------------------------------------------------------------------------

BASELINE = {"a": 1, "b": 2, "c": 3, "d": 4}

# The defect is a divergence in field "d". The narrow check never reads it.
#
# EXR-1 requires the expected outcome on each half of a discriminating pair to be
# stated before the check runs, and warns that it is NOT implied by the labels.
# This check asserts that the record matches the baseline, so it is the population
# WITH the defect that must reject. Naming that here rather than leaving it to the
# word "positive" is the point of the requirement.
V1_DEFECT_PRESENT = [{"a": 1, "b": 2, "c": 3, "d": 99}, {"a": 1, "b": 2, "c": 3, "d": 77}]
V1_DEFECT_ABSENT = [{"a": 1, "b": 2, "c": 3, "d": 4}, {"a": 1, "b": 2, "c": 3, "d": 4}]
V1_EXPECTED = {"defectPresent": REJECT, "defectAbsent": ACCEPT}

# Back-compat aliases; the pair is what matters, not which half is called positive.
V1_POSITIVE, V1_NEGATIVE = V1_DEFECT_PRESENT, V1_DEFECT_ABSENT

NARROW_FIELDS = ("a", "b")
FULL_FIELDS = ("a", "b", "c", "d")


def compare(record, fields) -> str:
    return ACCEPT if all(record[f] == BASELINE[f] for f in fields) else REJECT


def v1():
    narrow_pos = [compare(r, NARROW_FIELDS) for r in V1_POSITIVE]
    narrow_neg = [compare(r, NARROW_FIELDS) for r in V1_NEGATIVE]
    full_pos = [compare(r, FULL_FIELDS) for r in V1_POSITIVE]
    full_neg = [compare(r, FULL_FIELDS) for r in V1_NEGATIVE]
    return {
        "id": "V1",
        "name": "check comparing too little",
        "expectedOutcomes": dict(V1_EXPECTED),
        "expectationsDeclaredBeforeRun": True,
        "fieldsRead": {"narrow": list(NARROW_FIELDS), "sound": list(FULL_FIELDS)},
        "narrow": {
            "positive": narrow_pos,
            "negativeControl": narrow_neg,
            "status": exercise_status(narrow_pos, narrow_neg),
        },
        "sound": {
            "positive": full_pos,
            "negativeControl": full_neg,
            "status": exercise_status(full_pos, full_neg),
        },
    }


# --------------------------------------------------------------------------
# V2: a constant probe against a declared minimum
# --------------------------------------------------------------------------

DECLARED_MINIMUM = 1
# This probe asserts that the property is PRESENT at or above a minimum, so the
# population lacking it is the one that must reject. Opposite polarity to V1, and
# stated for the same reason.
V2_PROPERTY_PRESENT = ["marker", "marker", "marker", "marker", "marker"]
V2_PROPERTY_ABSENT: list[str] = []
V2_EXPECTED = {"propertyPresent": ACCEPT, "propertyAbsent": REJECT}

V2_POSITIVE, V2_NEGATIVE = V2_PROPERTY_PRESENT, V2_PROPERTY_ABSENT


def probe_constant(_population) -> int:
    """Reports a large number for anything. The vacuity EXR-1 exists to catch."""
    return 999


def probe_counting(population) -> int:
    return sum(1 for item in population if item == "marker")


def meets(value) -> str:
    return ACCEPT if value >= DECLARED_MINIMUM else REJECT


def v2():
    const_pos, const_neg = probe_constant(V2_POSITIVE), probe_constant(V2_NEGATIVE)
    count_pos, count_neg = probe_counting(V2_POSITIVE), probe_counting(V2_NEGATIVE)
    return {
        "id": "V2",
        "name": "constant probe",
        "expectedOutcomes": dict(V2_EXPECTED),
        "expectationsDeclaredBeforeRun": True,
        "declaredMinimum": DECLARED_MINIMUM,
        "constant": {
            "positive": [meets(const_pos)],
            "negativeControl": [meets(const_neg)],
            "reported": {"positive": const_pos, "negativeControl": const_neg},
            "status": exercise_status([meets(const_pos)], [meets(const_neg)]),
        },
        "counting": {
            "positive": [meets(count_pos)],
            "negativeControl": [meets(count_neg)],
            "reported": {"positive": count_pos, "negativeControl": count_neg},
            "status": exercise_status([meets(count_pos)], [meets(count_neg)]),
        },
    }


# --------------------------------------------------------------------------
# V4: a withheld record under a completeness claim
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Use:
    identifier: str
    signature_valid: bool
    disclosed: bool


# Two uses occurred. Every signature is valid. One is not disclosed.
V4_USES = (
    Use("use-1", True, True),
    Use("use-2", True, False),
)
# A world where single use genuinely holds, for the negative control.
V4_USES_SINGLE = (Use("use-1", True, True),)


def evaluate_single_use(uses, detector_sees_undisclosed: bool) -> str:
    """CMP-1 and CMP-2.

    detector_sees_undisclosed is the stated basis for coverage of the
    consumption domain. Where it is False the detector is confined to what the
    effecting party chose to disclose, which is the material-party case.
    """
    visible = [u for u in uses if u.disclosed or detector_sees_undisclosed]
    if not all(u.signature_valid for u in visible):
        return FAILED
    if len(visible) > 1:
        return FAILED
    if not detector_sees_undisclosed:
        # Every disclosed artifact is valid and there is exactly one. That is
        # consistent with single use and with an omitted second use, and the
        # record cannot separate them.
        return UNESTABLISHED
    return ESTABLISHED


def v4():
    return {
        "id": "V4",
        "name": "withheld record under a completeness claim",
        "materialPartyDetector": {
            "twoUsesOneWithheld": evaluate_single_use(V4_USES, False),
            "genuinelySingleUse": evaluate_single_use(V4_USES_SINGLE, False),
        },
        "independentDetector": {
            "twoUsesOneWithheld": evaluate_single_use(V4_USES, True),
            "genuinelySingleUse": evaluate_single_use(V4_USES_SINGLE, True),
        },
        "allDisclosedSignaturesValid": all(
            u.signature_valid for u in V4_USES if u.disclosed
        ),
    }


ALL = (v1, v2, v4)
