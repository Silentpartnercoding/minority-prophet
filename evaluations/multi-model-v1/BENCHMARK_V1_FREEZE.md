# What remains before Benchmark v1 is scientifically frozen

- Add and peer-review at least five scenario families, then expand to 100–500+ worlds.
- Separate public development, private evaluation, and rotating challenge generators; custody hidden seeds outside the public repository.
- Implement adversarial Condition D worlds and provenance-fabrication detection.
- Validate semantic variation, parameter coverage, difficulty balance, and contamination monitoring.
- Pre-register hypotheses, exclusions, MP Score weights, primary endpoints, sample sizes, and stopping rules.
- Run power analysis and choose multiplicity corrections for model and scenario comparisons.
- Add bootstrap or hierarchical intervals across world families and repeated seeds.
- Calibrate abstention worlds and source-reliability histories independently of the MP engine.
- Security-review prompt construction, credential isolation, public APIs, and operator authorization.
- Add durable database/object storage, queue workers, distributed rate limiting, and crash recovery.
- Add provider price tables with effective dates and verify model version pinning where providers permit it.
- Obtain external review of leakage controls and manually audit a random sample of prompt artifacts.
- Freeze a signed benchmark manifest; never alter it in place. Corrections require a new version.
- Execute heterogeneous frontier-model runs with sufficient sample size and no demonstration adapters.
- Require clean validation, immutable artifacts, reproducibility reruns, and an independent publication approval.
- Integrate the verified snapshot into minorityprophet.org without exposing private worlds.

Until these are complete, all local results remain DEMO even when automated integrity validation passes.
