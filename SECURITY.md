# Security policy

Minority Prophet is a research implementation, not a production authorization
system. Its machine-checked properties hold only under their stated models and
preconditions. They do not establish the trustworthiness, independence, or
authority of real-world evidence producers.

The central threat is manufactured independence. Different names, keys,
services, signatures, or network locations do not prove independent control.
A compromised issuer with unbounded issuance may create many apparent roots.
Deployments must establish stable root identity, constrain issuance, preserve
lineage, check freshness and revocation, and keep evidence assessment separate
from authority and execution.

The included fixtures, synthetic keys, and reference verifiers are for
research and conformance testing only. Do not commit production secrets,
private keys, customer policies, complete provider profiles, or private API
contracts.

Report suspected vulnerabilities through this repository's private security
advisory interface. Public issues are appropriate for non-sensitive
counterexamples, model limitations, and reproducibility questions.
