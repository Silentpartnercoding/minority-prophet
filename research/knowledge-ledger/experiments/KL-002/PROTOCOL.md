# KL-002: multi-agent AI

Status: **seeded, not preregistered or executed.**

## Question

Can agents avoid confidence inflation when many documents descend from one source?

## Null hypothesis

Root-aware aggregation does not improve calibration under source laundering.

## Target hypothesis

Lower confidently false answers without loss on genuinely independent evidence.

## Primary endpoint

Brier score under copied-source consensus

## First gate

Twenty paraphrases of one false source must remain one root.

## Completion route

Complete every field in `preregistration.json` under the shared
[`RESEARCH-METHOD.md`](../../RESEARCH-METHOD.md), commit the protocol
before confirmatory inspection, and advance only through recorded gates. This
file is a seed and supports no result claim.
