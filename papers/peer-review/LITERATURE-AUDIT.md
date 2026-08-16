# Literature audit for the v1.1.0 peer-review candidate

Status: complete for every external literature claim retained in the focused manuscript.

This audit applies only to `minority-prophet-peer-review-v1.1.0.md`. It does not certify the broader literature synthesis in paper v1.0.7. The focused paper removes claims whose primary-source wording or comparative basis has not been closed.

| Ref. | Primary source inspected | Claim retained | Audit result |
|---|---|---|---|
| [1] | Kaniovski author PDF and journal metadata, DOI `10.1007/s11238-008-9120-4` | Positive vote correlation can reduce competence and make enlargement detrimental over part of the range. | Supported by abstract and article metadata. |
| [2] | Author manuscript/journal metadata, DOI `10.1093/mind/fzt074` | Opinion independence has multiple probabilistic meanings connected to causal belief-formation structure. | Supported by abstract. |
| [3] | Publisher abstract and article metadata, DOI `10.1016/j.jet.2009.01.006` | Generated and interpreted signals have different independence behavior. | Supported by abstract. |
| [4] | KDD Explorations primary PDF, DOI `10.1145/2897350.2897352` | Truth discovery combines conflicting information while estimating source reliability. | Supported by abstract and survey scope. |
| [5] | PVLDB primary PDF, volume 2, pages 550-561 | Source-dependence methods infer copying and incorporate it into truth discovery. | Supported by paper abstract and method description. |
| [6] | PVLDB primary PDF, volume 3, pages 1617-1620 | SOLOMON detects copying and uses the result in truth discovery. | Supported by abstract. |
| [7] | Microsoft Research primary publication page/PDF and proceedings DOI | Multiplying identities can defeat redundancy without an external identity constraint. | Supported by abstract; manuscript wording is narrower than the paper's impossibility result. |
| [8] | Springer proceedings metadata, DOI `10.1007/978-3-319-21401-6_26` | Lean is the proof assistant used by the artifact. | Bibliographic use only. |
| [9] | ACM proceedings metadata, DOI `10.1145/3372885.3373824` | Mathlib is the formal library used by the artifact. | Bibliographic use only. |

## Deliberate removals from the submission candidate

The following v1.0.7 topics are not relied on by the focused manuscript: information-cascade correction claims, peer-prediction equilibria, LLM debate results, agent identity proposals, market measurements, comparative E8/E8b performance, PHEME lineage inference, and the dual-ledger research direction. Their records remain preserved in the repository. Removal here is a scope decision, not an invalidation or deletion of those programs.

## Citation policy

- External claims use primary papers, publisher pages, or official proceedings records.
- The manuscript does not claim a complete survey.
- The absence of a head-to-head benchmark is stated as a limitation.
- Repository-internal results are linked by path and evidence class rather than turned into independent literature citations.

