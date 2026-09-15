# DRI-5 — a content fingerprint as a backstop for missing lineage

Status: **DRAFT.** It becomes a preregistration only when the protocol, generator
and runner are committed and pinned before any confirmatory world is generated.

## 1. Why this exists

DRI-4 (`results/dri4-v1/`) showed that the tiered rule's protection erodes as true
shared identities go missing from the lineage record. It never made more silent
false settlements than the agreement rule, but at half the identities missing it
prevented only 10–26% of them.

Ledger DR3 (`no_record_rule_is_immune`) proves this is not a weakness of the rule.
One record can come from two groupings that settle differently. So no rule that
reads only the lineage record can be immune. Immunity needs an observable the loss
does not remove.

The owner asked, on 2026-09-15, for the engine to catch missing pages. DRI-5 tests
the most direct candidate: a **content fingerprint**. Copies of one source usually
repeat its content even when the lineage record forgets they are copies.

## 2. Questions

1. **Recovery:** when lineage is missing, how many of the tiered rule's silent false
   settlements does counting content as possible dependence remove?
2. **Paraphrase:** does that survive when half of all copies are reworded?
3. **Collisions:** what does it cost when independent sources share wording by
   chance?
4. **Blind spot:** which silent false settlements remain? Content cannot reveal roots
   that share a component or origin without being copies of each other.

## 3. Worlds

- **Base:** DRI-4's five families and base worlds, on a new salt, with DRI-4's
  missing-lineage degradation at m ∈ {0, 0.25, 0.5} and nothing spurious. The low
  rate 0.1 is dropped because DRI-4 left few errors to recover there.
- **Content:** each observation gets a fingerprint at a new `content` cut.
  - **Copies:** every copy repeats its root's fingerprint, except that with
    paraphrase rate p ∈ {0, 0.5} each copy after the first gets its own.
  - **Collisions:** with collision rate q ∈ {0, 0.2}, a root reuses the fingerprint
    of an earlier root on the same side.
  - **Same unit, not copies:** such roots get independent fingerprints.
  - **Untouched by lineage loss:** content is identical at every m.
- **Cells:** 12 (m × p × q), with common random numbers across cells.
- **Size:** 2,000 base worlds per family, which is 6,000 decisions per family per
  cell.

## 4. Arms

- **Frozen DRI-3 arms:** agreement rule, robustness everywhere, tiered rule, always
  look.
- **Content robustness everywhere:** robustness judged over lineage and content.
- **Content tiered rule (method under test):**
  - the tiered rule, with robustness judged over lineage and content;
  - the decision to settle without looking still comes from agreement over lineage
    cuts, so content can only add a stamp or a look.
- **Oracle reference.**

## 5. What is guaranteed, and what is not

**Guaranteed.** These are checked as implementation checks, not claimed as findings.

- Adding shared identities only widens the reachable settlements. So the content
  tiered rule is never silently wrong where the tiered rule is not.
- By DR2, the content tiered rule is never silently wrong on a decision where the
  true grouping is admissible over lineage and content, including every decision at
  m = 0.

**Not guaranteed, and what DRI-5 measures.** How many of the tiered rule's silent
false settlements fall on decisions where content restores admissibility. That
depends on how much of the lost dependence is copying rather than a shared
component, and on paraphrase.

## 6. Proposed criterion

Supported only if all hold:

1. **Complete lineage (m = 0), every family and cell:** the content tiered rule makes
   zero silent false settlements, with the 95% bound below 0.001.
2. **Every family and cell:**
   - the content tiered rule is never silently wrong where the tiered rule is not;
   - it is never silently wrong where lineage and content make the true grouping
     admissible.
3. **Recovery, m ∈ {0.25, 0.5}:** in every family and cell where the tiered rule
   makes at least 12 silent false settlements, the content tiered rule makes
   significantly fewer. The test is exact McNemar, Holm-corrected over up to 40
   comparisons.
4. **Reproducibility:** two executions are identical.

Item 3 covers every family and both paraphrase and collision rates. That includes
families whose lost dependence is mostly a shared component, where content may
recover little. The criterion is not narrowed to the families where content is
expected to work.

## 7. Endpoints reported with no pass mark

- **Admissibility:** the share of decisions whose true grouping is admissible over
  lineage, and over lineage plus content.
- **Recoverable errors:** the tiered rule's silent false settlements that fall where
  content restores admissibility.
- **Cost of collisions:**
  - stamped correct settlements;
  - looks;
  - unneeded abstentions;
  - irreversible false settlements for both tiered arms.

## 8. Limits

- **Content model:** fingerprints are exact and synthetic. Real content similarity is
  fuzzy, and the paraphrase and collision rates are stated, not estimated.
- **Lineage model:** only DRI-4's missing-lineage model is used, and lookups stay
  truthful. Imperfect lookups are DRI-6.
- **Authorship:** everything is authored in the same control domain as the engine.
- **No authority claim.**
