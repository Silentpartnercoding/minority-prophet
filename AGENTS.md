# Working on Minority Prophet

Multiple agents are welcome. Keep ordinary exploration easy; apply stronger
controls only when work is promoted into trusted research or authority-sensitive
interfaces.

## Start here

This file is the single source of repository instructions for coding agents.
`CLAUDE.md` imports it directly; do not duplicate these rules in agent-specific
instruction files.

Read `CONTRIBUTING.md` and `PUBLIC-CLAIMS.md`. For experiments or results, also
read `CANONICAL-RECORDS.md` and
`research/knowledge-ledger/RESEARCH-METHOD.md`.

Choose and report one lane:

- **Routine:** documentation, adapters, maintenance, and ordinary code changes.
  Run the normal tests. No preregistration is required.
- **Exploratory:** inspect, falsify, prototype, or create clearly labeled
  fixtures. Exploratory output is not a canonical result.
- **Candidate:** freeze a protocol before confirmatory evidence is inspected.
  Development output remains non-confirmatory.
- **Canonical or imported record:** satisfy the repository's record, manifest,
  adverse-result, claim-boundary, and evidence-alignment requirements.
- **Authority-sensitive:** stop for explicit maintainer authorization. Evidence
  assessment never grants permission to execute an effect.

## Non-negotiable boundaries

1. Copies, transformations, aliases, and commonly controlled sources do not
   create independent evidence.
2. Different agents, models, prompts, keys, processes, branches, services,
   machines, or clean environments do not establish independent control.
   Agents directed by the same operator or orchestrator are one control domain
   unless supported external provenance establishes otherwise.
3. Same-controller agents may build, challenge, reproduce, and review work, but
   their agreement is internal replication, not independent validation.
4. Missing or conflicting provenance widens uncertainty or causes abstention or
   escalation. Failure to detect dependence is not evidence of independence.
5. Evidence assessment does not grant authority or permission to execute.
6. Do not present fixtures, generated evidence, development runs, or self-review
   as confirmatory evidence. Freeze the applicable protocol first.
7. Preserve null, adverse, failed, incomplete, and invalidated results. Never
   retrofit a preregistration or selectively delete inconvenient output.
8. Do not publish secrets, identifying field data, private contracts,
   non-public planning, or sensitive vulnerability details.
9. Agents may prepare branches and pull requests. Do not publish, merge, deploy,
   or make a live authority decision without the permission required by the
   repository owner and the relevant external system.

## Parallel-agent coordination

- Give each agent one bounded objective and branch or worktree.
- Do not let two agents edit the same canonical record concurrently.
- Preserve builder, runner, reviewer, operator, and control-domain provenance.
- A cross-agent review is valuable even when control is shared; label it
  accurately.
- When an expected outcome or confirmation label has been seen, do not tune the
  candidate against it. Start a newly registered run if remediation is needed.

## Before handoff

Report the lane, claim classification, changed files, tests, evidence exposure,
controller relationship among builder/runner/reviewer, limitations, and
unresolved uncertainty.

Run:

```text
PYTHONPATH=. python -m pytest -q
python scripts/check_public_boundary.py --base <trusted-base> --head HEAD
python scripts/check_research_integrity.py --base <trusted-base> --head HEAD
npm ci
npm run lint
npm test
```

Stop and request maintainer direction before consequential deployment, live
authority, undocumented canonical promotion, or sensitive publication.
