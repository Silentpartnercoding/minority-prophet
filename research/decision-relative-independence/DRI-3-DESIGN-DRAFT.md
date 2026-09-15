# DRI-3 — is settling immune to stacked dependence?

Status: **DRAFT. NOT FROZEN. NOT RUN.** It becomes a preregistration only after the
owner settles the decisions in section 7, and the protocol, generator and runner are
committed and pinned before any world is generated.

## 1. Why this exists

In DRI-2 v1 and v2, every one of the method's 14 false settlements had the same
shape:

- the true causal units were tied 2-2;
- all five independence cuts nonetheless settled the same way, each overcounting
  the same side in a different way;
- the method treated that agreement as proof that the choice of cut did not matter,
  and settled without looking.

Every other arm that trusts agreement fell in the same worlds.

The mistake is a class, not those worlds: **agreement across a menu of dependence
readings is not robustness when dependencies stack.** The engine change in
`provenance/dependence_robustness.py` replaces "do the cuts agree?" with "does the
settlement survive every combination of the dependence the record shows as
possible?" DRI-3 tests whether that makes settling immune to the class, and what
immunity costs. It does not reuse DRI-2's worlds.

The owner's instruction governs the design: the engine is changed to be immune to
the mistake, not to pass a test. The 14 known worlds are therefore not part of the
test, and the world families below are built to break the new rule rather than to
confirm it.

## 2. Question

When dependence stacks in ways no single cut expresses, does settling only on a
robust settlement eliminate false settlements that the record's identities could
have revealed? What does it cost in extra looks, and in unneeded abstentions where
looking is impossible?

## 3. Arms

No human. An abstention supplies no answer, as in DRI-2 v2.

1. **Agreement rule:** the DRI-2 method unchanged. It settles when every cut agrees,
   looks when the cuts disagree, and abstains when looking is unavailable. This is
   the baseline that made the mistake.
2. **Robustness everywhere:** settles only when `assess_dependence_robustness`
   reports a robust settlement. Otherwise it looks, and abstains if looking is
   unavailable. It applies to every decision.
3. **Tiered rule, the method under test:** the owner's cost rule (section 3a).
   - **Irreversible decisions:** as robustness everywhere.
   - **Reversible decisions:** as the agreement rule, except that a settlement which
     is not robust is **stamped "not robust"**. It is never settled silently.
4. **Always look:** looks at every decision. This bounds the cost from above.
5. **Oracle (reference):** takes each decision's correct move.

## 3a. Cost rule (owner decision, 2026-09-15)

A look forced by non-robustness has a cost. Immunity is not bought at any price for
every decision.

- **Irreversible decisions: no ceiling.** A non-robust settlement is never made.
  Look, or abstain if looking is unavailable. Preventing a false irreversible
  settlement is what the programme exists to do.
- **Reversible decisions: a ceiling of 100 extra looks per prevented false
  settlement.** This treats a false reversible settlement as costing about 100
  lookups. The ratio is a stated choice.
  - At or below the ceiling, robustness everywhere is justified for reversible
    decisions.
  - Above it, the tiered rule's reversible behaviour is preferred: settle on
    agreement, but stamp every non-robust settlement "not robust" so it can be
    revisited.
- **Neither arm may ever make a false settlement that is not flagged.**

The run measures the reversible ratio under robustness everywhere, per family and
overall. That ratio decides which reversible policy the engine adopts. DRI-2 v2's
diagnostic, which is not part of this test, suggested roughly 700 extra looks per
prevented false settlement.

## 4. World families

Every family has lookup-available worlds and lookup-unavailable twins. Families 1
to 6 carry all their dependence in recorded identities, so the robustness rule
should never falsely settle in them. Family 7 is the declared boundary.

1. **Single domain:** as in DRI-2, on fresh seeds.
2. **Joint domain:** as in DRI-2, on fresh seeds.
3. **Separate control, shared origin:** as in DRI-2, on fresh seeds. DRI-2 v2's
   diagnostic flagged 69.7% of agreeing, correct decisions here, so this family is
   where the cost is measured.
4. **Three stacked dependencies:** copy, shared origin and shared component, all
   active at once and across different roots.
5. **Side-asymmetric dependence:** one side's sources share a dependence; the other
   side's sources share a different one, recorded at a different cut.
6. **Decoy shared identities:** truly independent sources carry shared identities,
   for example a common upstream component with no effect on their errors. This
   measures the censorship cost the repository warns about: an adversary who can add
   shared identities can force looks or abstention without changing the truth.
7. **Unrecorded dependence (expected failure):** a real dependence that no recorded
   identity carries. No rule that reads the record can detect it. The family is
   reported apart and must not count toward any success claim. Its purpose is to
   show the boundary honestly.

## 5. Scoring

Per decision:

- **correct settlement;**
- **false settlement;**
- **required abstention:** nothing available could settle it;
- **unneeded abstention:** looking would have settled it, but looking was
  unavailable, or the rule abstained anyway;
- **look.**

A settlement is also recorded as **stamped** when the arm marked it "not robust".
A false settlement that is stamped is **flagged**; one that is not stamped is
**silent**.

Per run:

- any false settlement;
- no false settlement and no unneeded abstention;
- no false settlement, but at least one unneeded abstention.

Time is measured and reported. It is not a criterion.

## 6. Candidate endpoints

- **Primary:**
  - silent false settlements by the tiered rule in families 1 to 6;
  - false settlements by the tiered rule on irreversible decisions in families 1 to 6;
  - the reduction in silent false settlements against the agreement rule in the
    families where the agreement rule falls.
- **Cost rule:** extra looks per prevented false settlement on reversible decisions
  under robustness everywhere, per family and overall, compared with the ceiling
  of 100.
- **Secondary, never pooled:**
  - extra looks against the agreement rule, per family;
  - unneeded abstentions in lookup-unavailable twins;
  - the decoy family's forced looks and abstentions;
  - family 7's false settlements, reported apart.

## 7. Decisions required before freezing

1. **Success criterion.** Proposed:
   - in each of families 1 to 6, the tiered rule makes zero silent false
     settlements, and zero false settlements on irreversible decisions, with the
     rule-of-three 95% upper bound below the chosen rate (decision 3);
   - it makes significantly fewer silent false settlements than the agreement rule
     in families 2, 4 and 5.
2. ~~The cost.~~ **Decided:** the tiered cost rule in section 3a. There is no
   ceiling for irreversible decisions. Reversible decisions have a ceiling of 100
   extra looks per prevented false settlement; above it, settlements are stamped
   "not robust" instead of forcing a look.
3. **Size.** Zero false settlements in N decisions bounds the rate below about
   3 / N at 95% confidence. Below 1 in 1,000 needs 2,995 decisions per family;
   below 1 in 10,000 needs 29,955. Pick one.
4. ~~Imperfect lookups.~~ **Decided:** a follow-up, not part of DRI-3. Lookups
   in DRI-3 return the true lineage or nothing. A later version tests partial and
   wrong lookups. That matters because arms that look more are exposed to more bad
   lookups, so imperfect lookups can change correctness, not only time.
5. **Family 7.** Confirm that unrecorded dependence is reported only as a declared
   expected failure.
6. **Authorship.** Families 4 to 7 are written by the same control domain as the
   rule. As in DRI-2, that limit is stated. Independent authors would be needed to
   remove it.

## 8. Not claimed

This draft claims nothing. A future positive result would be evidence only for its
frozen synthetic model. It would not show:

- that recorded identities in real systems carry the dependence that matters;
- immunity to dependence no identity records;
- that the cost is acceptable in any deployment;
- authority to act.
