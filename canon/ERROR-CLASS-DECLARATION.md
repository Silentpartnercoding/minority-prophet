# Error-class declaration, version 1

Declared 2026-09-14. Machine-readable copy: `ERROR-CLASS-DECLARATION.json`.

This is the list of error kinds declared before any sample, as `ASSAYER.md` A3
requires. When the junction loop works out which error kind blocks an action, it
may only name a kind declared here. By owner decision, every condensed kind and
every newly named kind is declared for now.

It is condensed from 189 named entries across this repository and
`minority-prophet-gate`. Research-process errors, which describe how our own
experiments can go wrong rather than how evidence can, and refusal codes from
retracted modules are not declared here. `gate:` paths refer to
`Silentpartnercoding/minority-prophet-gate`.

## How this list changes

The declaration is versioned. A kind discovered during a run joins only the next
version; a version is never edited to cover the run that exposed the gap. Held-back
test worlds must be built from kinds that are **not** in the current version, so the
gap between this list and the world is measured rather than assumed to be zero.

## Defence vocabulary

- **defended:** the record itself shows the error and the code refuses or escalates
- **conditional:** defended only when a stated condition holds
- **bounded:** limited by margin, quota or cost, not prevented
- **undetectable:** leaves no mark in the record; only an outside witness or the margin helps
- **unassessed:** newly named; no defence assessed yet

The defence column is not a reason to include or exclude a kind. It tells the
junction loop which move is available: settle, gather evidence, or rely on the
margin and hand over.

## Where the error enters

| ID | Kind | What goes wrong | Defence | Sources |
|---|---|---|---|---|
| E-1 | Fabrication | The world was never consulted: a root backed by nothing real. | undetectable | inventory E-1; `canon/proximity.py:66`; `research/adversarial-weighting/two_failure_classes.py:2-17`; `provenance/graph.py:65-74` |
| E-2 | Biased method | The method itself is biased. | conditional | inventory E-2; `canon/proximity.py:59-67`; `canon/rungs.py:36-41` |
| E-3 | Instrument error | Miscalibration or random measurement error. | conditional | inventory E-3; `canon/proximity.py:68`; `formal/CLAIM-SCOPE.md:95-97` |
| E-4 | Processing error | The pipeline from raw data mangles it. | conditional | inventory E-4; `canon/proximity.py:69` |
| E-5 | Analysis error | Wrong test, arithmetic slip, or coding bug. | conditional | inventory E-5; `canon/proximity.py:70`; `formal/CLAIM-SCOPE.md:95-96` |
| E-6 | Transcription error | A digit changed on the way to the page. | conditional | inventory E-6; `canon/proximity.py:71` |

## Count too high

| ID | Kind | What goes wrong | Defence | Sources |
|---|---|---|---|---|
| I-1 | Unrecorded copy | A copy with no recorded parent is counted as an independent root. | undetectable | inventory I-1; `formal/COUNTEREXAMPLES.md:51-80`; `research/knowledge-ledger/experiments/KL-014/OVERCOUNT-BOUND-20260814.md:14-19`; `provenance/graph.py:18-20` |
| I-2 | Laundered provenance | Faked re-derivation plus scrubbed shared markers remove dependence edges and inflate the count. | bounded | inventory I-2; `canon/U1-PROXIMATE-ROOTS.md:116-131`; `canon/root_identity.py:94-98` |
| I-3 | Fake identities (Sybil) | Many fabricated identities, each minting roots. | bounded | inventory I-3; `PROVENANCE-REQUIREMENTS.md:23-24`; `research/adversarial-weighting/NOT-A-VIBE.md:43-53` |
| I-4 | Stolen signing key | One compromised root-signing key issues roots at will. | bounded | inventory I-4; `formal/COUNTEREXAMPLES.md:214-231`; `provenance/root_registry.py:302-309` |
| I-6 | One observation split into many roots | Honest, separate issuers each re-issue the same upstream observation as their own root. | undetectable | inventory I-6; `RESEARCH-HYPOTHESES.md:124-160`; `research/knowledge-ledger/experiments/KL-014/CORRECTION-20260813-quota.md:38-49` |
| I-7 | Restated or translated copies | Paraphrases, translations, summaries and model rewrites are not recognised as copies. | conditional | inventory I-7; `results/heo1-v1/README.md:7-16`; `results/exp007a-v1/README.md:11-13` |
| I-8 | Honest citation of one source | Five honest readers of one paper count as five roots. | conditional | inventory I-8; `research/adversarial-weighting/citation_is_not_ancestry.py:2-14`; `provenance/graph.py:140-156` |
| I-14+I-17 | One controller posing as many | Aliases, rotated keys, split services, or undisclosed common ownership behind apparently separate sources. | conditional | inventory I-14, I-17; `results/hvi1-v1/README.md:7-13`; `experiments/hvi1/THREAT-MODEL.md:13-17` |
| I-15 | Self-verification | A producer verifies or mints its own evidence. | defended | inventory I-15; `experiments/HVI-1-PREREGISTRATION.md:62`; `FOUNDATIONS.md:42-47` |
| I-19 | Shared component or common-mode failure | Distinct measurements share one upstream failure cause. | bounded | inventory I-19; `results/hgd1-v1/README.md:3-15`; `results/hgd2-v1/README.md:3-22` |
| I-23 | A model agreeing with a model | One model reviewing another model's output is taken as corroboration. | defended | inventory I-23; `canon/rungs.py:91-96`; `ASSAYER.md:103-106` |
| I-22 | Partial dependence | Partly correlated observers are treated as either fully independent or fully dependent. | undetectable | inventory I-22; `provenance/graph.py:441-443`; `PROVENANCE-REQUIREMENTS.md:180-182` |

## Count too low

| ID | Kind | What goes wrong | Defence | Sources |
|---|---|---|---|---|
| I-5 | Independent roots merged | Genuinely independent roots are merged into one, which destroys margin. | undetectable | inventory I-5; `formal/COUNTEREXAMPLES.md:284-300`; `formal/EXTENSION-SOCKETS.md:186-196` |
| I-10 | Count depends on presentation order | An approximate count lets whoever controls the order deflate it. | defended | inventory I-10; `canon/independent_set.py:3-24` |
| I-12 | Chained ancestry collapses the count | Treating shared ancestry as an equivalence drives the count toward 1. | defended | inventory I-12; `canon/U1-PROXIMATE-ROOTS.md:15-34` |
| I-13 | Anonymous witnesses cannot be told apart | Collapsing anonymous roots asserts identity; stripping identity deflates the count. | bounded | inventory I-13; `aggregation/independence_axes.py:306-354` |

## Wrong frame

| ID | Kind | What goes wrong | Defence | Sources |
|---|---|---|---|---|
| I-20 | Counting at the wrong level | Counting at a finer or coarser cut than the decision's failure domain needs. | undetectable | inventory I-20; `provenance/decision_relative.py:169-178`; `results/dri1a-v1/README.md:66-81` |
| I-21 | Joint failure domains | Two failure domains active at once, which a single cut cannot represent. | undetectable | inventory I-21; `research/decision-relative-independence/README.md:161-167` |
| I-18 | Separate sources repeating one wrong claim | Truly separate controllers or origins carry the same wrong claim. | undetectable | inventory I-18; `results/hvi1-v1/README.md:15-18` |
| S-1+S-2 | Universal or existential claim counted as symmetric | A claim that one root settles is decided by comparing root counts. | conditional | inventory S-1, S-2; `formal/COUNTEREXAMPLES.md:391-451`; `aggregation/root_vote.py:140-145` |
| M-1+M-3 | Conclusion carried into another vocabulary untested | A result established in one ontology is assumed to hold in another, or flips under a change of category scheme. | defended | inventory M-1, M-2, M-3; `canon/bounded_truth.py:10-19`; `canon/ontology_perturbation.py:9-22` |

## Coverage

| ID | Kind | What goes wrong | Defence | Sources |
|---|---|---|---|---|
| C-1 | Absence without a complete search | Absence is concluded from a partial or unknown-coverage search. | defended | inventory C-1; `knowledge_ledger/transaction_v2.py:156-159`; `interop/memory-evidence-profile-v0.1/adversarial-cases.json:6` |
| C-4 | Empty search counted as opposition | An unsuccessful search is filed as contrary evidence. | undetectable | inventory C-4; `formal/COUNTEREXAMPLES.md:453-477` |
| C-10 | Unattributed claims silently dropped | Claims with no root get zero influence, or full influence, without anyone deciding. | defended | inventory C-10; `formal/COUNTEREXAMPLES.md:347-360`; `aggregation/root_vote.py:352-363` |

## Time

| ID | Kind | What goes wrong | Defence | Sources |
|---|---|---|---|---|
| T-1 | Stale or expired evidence | Evidence past its lifetime, or with no timestamp under a freshness policy. | defended | inventory T-1; `gate:minority_prophet/adapter_acp.py:143-153`; `gate:minority_prophet/memory_evidence.py:91-92` |
| T-3+T-4 | Revoked, or revocation unknown | Evidence or authority has been revoked, or its revocation status cannot be determined. | defended | inventory T-3, T-4; `gate:minority_prophet/memory_evidence.py:96-100` |
| T-5 | Replay | The same evidence, nonce or delivery is presented again. | conditional | inventory T-5; `provenance/root_registry.py:248-250`; `gate:README.md:212-214` |
| T-7 | Fresh restatement of an old observation | A recent restatement carries the freshness of the restatement, not of the observation it rests on. | undetectable | inventory T-7; `interop/memory-evidence-profile-v0.1/README.md:17-22` |

## Binding and authority

| ID | Kind | What goes wrong | Defence | Sources |
|---|---|---|---|---|
| A-1+L-5 | Evidence bound to the wrong proposition or action | Evidence is attached to a different claim, subject, request or action than the one being decided. | defended | inventory A-1, L-5; `gate:minority_prophet/memory_evidence.py:81-85`; `provenance/graph.py:344-354` |
| A-4 | Evidence treated as permission | An evidence assessment, evidence request, or collection right is read as authority to act. | defended | inventory A-4; `AGENTS.md:43`; `gate:minority_prophet/control_plane.py:164` |
| A-7 | Coordination authority mistaken for knowledge | Deferring to whoever coordinates is treated as deferring to whoever knows. | conditional | inventory A-7; `canon/authority_debt.py:35-65` |

## Social pressure

| ID | Kind | What goes wrong | Defence | Sources |
|---|---|---|---|---|
| P-1+P-5 | Social pressure | Belief or action moves with who is speaking, how many appear to agree, how the question is framed, repetition, or emotional loading, while the evidence stays fixed. | conditional | inventory P-1 to P-5; `canon/susceptibility.py:9-10`; `canon/susceptibility.py:35-42` |

## Reflexive

| ID | Kind | What goes wrong | Defence | Sources |
|---|---|---|---|---|
| R-1+R-5 | Acting on a conclusion changes what is true | The conclusion is self-invalidating or self-fulfilling, observing is intervening, the footprint exceeds the mandate, or a forecast confirms our own effect. | conditional | inventory R-1 to R-5; `canon/reflexive_brake.py:41-54`; `canon/reflexive_brake.py:57-72` |

## Weighting

| ID | Kind | What goes wrong | Defence | Sources |
|---|---|---|---|---|
| W-9 | Self-declared weight gaming | A source declares its own confidence or competence to gain weight. | conditional | inventory W-9; `research/adversarial-weighting/PREREGISTRATION.md:56-58`; `research/adversarial-weighting/RESULTS.md:16-19` |
| W-10 | Sleeper and reputation attacks | A source earns weight honestly, then defects; reputation selects for the attacker it exists to deter. | undetectable | inventory W-10; `research/adversarial-weighting/RESULTS.md:40-53`; `research/adversarial-weighting/TWO-CORRECTIONS.md:47-78` |
| W-7 | Weight concentration | A coordinated block of merely heavy sources controls the outcome. | bounded | inventory W-7; `research/adversarial-weighting/RESULTS.md:20-28`; `canon/U3-WHAT-TRANSFERS.md:84-87` |

## Newly named in this declaration

| ID | Kind | What goes wrong | Defence | Sources |
|---|---|---|---|---|
| N-1 | Selective withholding inside a searched scope | A producer holds opposing roots in a location it reports as searched. Coverage rules only cover locations that were not searched. | unassessed | none |
| N-2 | Abstention-forcing flood | Injecting unattributed claims up to the flip budget triggers abstain_if_decisive (aggregation/root_vote.py:465-474). Only mandate denial of service is named. | unassessed | none |
| N-3 | Timestamp forged inside the accepted clock window | ClockError fires only outside the window (provenance/root_registry.py:148, 332), so an observed_at moved within it passes. | unassessed | none |
| N-4 | Assertion mapped to the wrong side at ingest | Only unmappable assertions are named; polarity laundering covers edges, not assertions. | unassessed | none |
| N-5 | Two propositions sharing one proposition id | CE-10 checks that edges do not cross propositions, not that one id names one proposition. | unassessed | none |
| N-6 | Time-of-check versus time-of-use on the main decision path | Addressed only in the continuity-receipt lane, not on decide(). | unassessed | none |

## Known inconsistencies

Places where two sources in the repositories classify the same point differently.
They are recorded here so the declaration does not silently pick a side; each should
be resolved in the source files.

- **Is the root-evidence gate on by default?** The KL-014 decision says off by default and that a source of "trust me" passes; the graph code says on by default since 2026-08-13 and refuses the same input. (`research/knowledge-ledger/experiments/KL-014/DECISION-20260813.md:63, 115-117`; `provenance/graph.py:111-116`)
- **When did U1 close, and is it closed?** Claim scope and extension sockets say 2026-09-07; the U1 doctrine and counterexamples say 2026-09-14; the public claims page and provenance requirements still list it as an open boundary. (`formal/CLAIM-SCOPE.md:86`; `canon/U1-PROXIMATE-ROOTS.md:3`; `PUBLIC-CLAIMS.md:51`; `PROVENANCE-REQUIREMENTS.md:176`)
- **Is the laundering residual bounded or undetectable?** Claim scope says R3 absorbs it; the HRI-1 hypothesis says no existing check detects it; under weights it is not established. (`formal/CLAIM-SCOPE.md:104-105`; `RESEARCH-HYPOTHESES.md:149-154`; `canon/U3-WHAT-TRANSFERS.md:80-82`)
- **Is under-counting conservative?** The retracted narrow gate calls it a conservative lower bound; the independent-set and independence-axes modules call it a censorship primitive, directional rather than conservative. (`canon/narrow_gate.py:189-191`; `canon/independent_set.py:13-16`; `aggregation/independence_axes.py:320`)
- **The copy-invariance slogan** Gate's README says duplicating a claim can never change the verdict; claim scope says that is false without the recorded-parent hypothesis. (`gate:README.md:85`; `formal/CLAIM-SCOPE.md:116-122`)
- **CE-14 presence semantics** Recorded as settled by owner decision A3 in one place, and as still open elsewhere in the same file and in the aggregator. (`formal/COUNTEREXAMPLES.md:27`; `formal/COUNTEREXAMPLES.md:529-531`; `aggregation/root_vote.py:157-158`)
- **Is U2 fixed?** Open in the theorem ledger; fixed in a new module according to the counterexamples. (`formal/THEOREM-LEDGER.json:364-373`; `formal/COUNTEREXAMPLES.md:25`)
- **Is Sybil excluded from the threat model?** Provenance requirements list Sybil root manufacturing as an excluded threat; extension sockets call it exactly where R1's cryptography does not reach. (`PROVENANCE-REQUIREMENTS.md:23`; `formal/EXTENSION-SOCKETS.md:184-186`)
- **Is the weighted baseline a defect?** U3 calls it a defect already shipped; the baseline module calls it the doctrine being demonstrated, not a defect to repair. (`canon/U3-WHAT-TRANSFERS.md:14`; `aggregation/baselines.py:46-47`)
- **The single ranking of independence bases** Labelled a known defect, yet it still drives the weakest-basis and attested-margin calculations; the axes module says the error is the single ordering. (`aggregation/root_vote.py:72, 392-410`; `aggregation/independence_axes.py:24-25`)
- **What happens to malformed input** Gate escalates it; the knowledge transaction raises and never returns a receipt; the authority-evidence contract fails closed. (`gate:README.md:206`; `gate:conformance/knowledge-transaction-fail-closed.md:19`; `contracts/authority-evidence-v0.1/README.md:38`)
- **Unknown vocabulary** Refused at the boundary as a refusal, not a downgrade, but read inside the aggregator as absent rather than raising. (`aggregation/independence_axes.py:526-527`; `aggregation/root_vote.py:262-265`)
- **Replay means two things** HES-1's stale replay is a partly recovered attack; in the memory, continuity and registry code, replay is an always-blocked nonce reuse. (`results/hes1-v1/README.md:31`; `provenance/root_registry.py:248-250`)

## Described but never named

For reference. These appear in prose without a name and are not declared.

- Several observations published as one work, or preprint and published versions folded into one work id, under-count because the indexer merges them. (`research/knowledge-ledger/experiments/KL-014/HRI1-BLOCKER-20260816.md:36-39`)
- Under attack, a worse estimate scores better: precision helps the attacker. (`research/adversarial-weighting/RESULTS.md:67-69`)
- An implementation artefact misread as a finding (the median tracking the capped aggregator). (`research/adversarial-weighting/RESULTS.md:71-74`)
- An endpoint that does not count the cost of refusing clean items. (`CLAIMS.md:134-136`)
- Undeclared category fusion inside an instrument: nothing on the diagram says which two were merged. (`canon/decompositions/wheel.py:24-28`; `canon/bounded_truth.py:64-66`)
- Evidence-request challenge state is forgeable: its hash is not a signature and cannot authenticate state supplied by an untrusted agent. (`gate:README.md:396-399`)
- A legitimate reference format the resolvable-reference check does not recognise causes false refusals. (`provenance/graph.py:192-198`)
- Self-reported root metadata destroys its own evidentiary value. (`research/decision-relative-independence/README.md:157-158`)
- A generator that cannot produce the hard case (0 of 71 files carry two defects). (`research/knowledge-ledger/experiments/KL-001/corpus/TAXONOMY-NOTE.md:38-43`)
- Proximity misread as correctness. (`results/hes1-v1/README.md:20-22`)
- A vocabulary collision between proceed and act. (`canon/decision_sensitivity.py:41-45`)
