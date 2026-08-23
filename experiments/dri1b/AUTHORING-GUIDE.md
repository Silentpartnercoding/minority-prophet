# DRI-1B case authoring and neutral review guide

Status: protocol support artifact. This guide creates no authority and contains
no confirmatory cases.

## Author task

Create one decision case in which the same evidence is represented at five
lineage cuts: agent, machine, controller, evidence origin, and upstream
component. State the proposed action, proposition, consequence, reversibility,
deadline, and evidence threshold.

The public packet must make all material facts available without naming the
answer. Do not write “the correct cut is…”, expose a stratum name, or use an ID
that contains the target label. The withheld packet must name exactly one target
from the six-label vocabulary and demonstrate the disposition at every cut.

A minority signal must never be declared correct merely because it is a
minority. Show which shared failures collapse apparent support and whether the
remaining independent roots materially settle the decision.

## Required counterfactual

For each candidate cut answer:

1. Which observations collapse to the same root?
2. Which roots conflict?
3. What disposition results at the fixed consequence threshold?
4. Which shared failure remains unaccounted for?
5. Why is this cut too fine, sufficient, too coarse, or jointly insufficient?

The target is the nearest sufficient recorded boundary. If no single cut removes
all material shared failure without erasing required independent evidence, use
`joint_or_insufficient`.

## Neutral test-reviewer instruction

You are given one proposed decision and an unchanged evidence graph with root
identity at several lineage cuts. Select the nearest available cut at which the
evidence is independent enough for this decision's material failure domain. Do
not reward or suppress a claim because it is a minority. Do not infer permission
to act. If multiple cuts are jointly required, lineage is materially missing, or
no single cut is defensible, select `joint_or_insufficient`.

Return exactly the fields required by `selector-response.schema.json`. Cite one
material failure visible in the packet and explain why the nearest rejected
alternative is not sufficient. Do not search externally, communicate with
another reviewer, or use an AI assistant.

## Prohibited content

- live commands or authority decisions;
- customer-identifying or private operational data;
- secrets, credentials, personal information, or sensitive vulnerabilities;
- unverifiable “human root” assertions;
- a target justified only by the desired vote outcome; or
- a case derived from DRI-1A worlds.
