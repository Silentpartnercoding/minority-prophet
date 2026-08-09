# LIR-1 dataset catalog

Checked 2026-08-08. URLs identify the intended upstream source; every actual
pull must record retrieval metadata and raw hashes.

| Dataset | Intended source | Best available lineage label | Pilot role | Main limitation |
| --- | --- | --- | --- | --- |
| Retraction cascades | Crossref production API / Retraction Watch GitLab; OpenAlex; Semantic Scholar | heuristic proxy | exploratory | retraction status and citation stance do not establish citation ancestry or independence |
| Rumor cascades | PHEME Figshare; separately verified Twitter15/16 or MIT access path | explicit edge | secondary | platform trees record interactions, not all causal evidence; text rehydration may be restricted |
| MemeTracker | Stanford SNAP phrase clusters | explicit cluster, inferred parent | secondary | clusters are observed; exact mutation parents are not ground truth |
| Churnalism | licensed press-release/news pair corpus, else GDELT/Common Crawl acquisition | adjudicated or heuristic, depending corpus | secondary only after adjudication gate | similarity is not by itself proof of copying; “novel” prose is not proof of independence |
| Wikipedia citogenesis | Wikimedia revision API plus archived external pages | adjudicated lineage | secondary | small selected case set; archived pages may be missing |
| Prediction markets | Metaculus and Polymarket public APIs; GDELT event join | heuristic proxy | exploratory | absence of a matched event does not prove herding; timing cannot prove causal lineage |
| Multi-agent LLM echo | generated under logged construction | constructed exact | primary | requires model/retrieval access and measures the frozen construction only |

## Source corrections to the original acquisition brief

- Crossref's former Labs Retraction Watch path is stale. Use the production
  `/works` update fields or the Crossref-hosted GitLab CSV.
- OpenAlex API access currently requires a free key and has a metered free
  allowance; the snapshot is the full-scale alternative.
- Semantic Scholar citation metadata and contexts are availability-dependent;
  an API response lacking context is `unknown`, not a negative label.
- MemeTracker supplies phrase clusters and timestamps, not true parent trees.
- PHEME is a released rumor/veracity corpus; other Twitter-derived collections
  require separate license and rehydration review before inclusion.
- Prediction-market `herding` is not ground truth in this design and therefore
  cannot support a confirmatory causal claim.

