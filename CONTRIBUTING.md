# Contributing

Counterexamples, reproducibility failures, adversarial tests, and narrowly
scoped corrections are welcome. Open an issue before a large change so its
claim, boundary, and required evidence can be agreed first.

New contributors can start with `CONTRIBUTOR-QUICKSTART.md`. It provides one
command for validation and copyable examples for every contribution lane.

Every contribution must:

- distinguish a hypothesis, model result, implementation result, and
  deployment claim;
- state the relevant preconditions and failure condition;
- preserve uncertainty rather than converting missing evidence into support;
- include tests or reproducible artifacts when behavior changes;
- avoid secrets, private provider contracts, customer policy, and identifying
  field data.

## Graduated lanes

Routine maintenance, documentation, adapters, and exploratory work use the
normal test suite. They do not require preregistration. Clearly label fixtures
and exploratory output; passing tests do not promote a research claim.

Candidate research freezes its protocol before confirmatory evidence is
inspected. Canonical and imported records additionally use one lifecycle file
under `research/records/`, preserve adverse outcomes, bind their artifacts, and
update the applicable evidence ledger. See `AGENTS.md` and
`research/integrity/README.md`.

Agents sharing an operator or orchestrator are one control domain. Their
cross-review is useful internal replication, not independent validation.

Before opening a pull request, run:

```text
make verify
```

Run `make setup` once when local development dependencies are absent.

Use public issues only for non-sensitive material. Report vulnerabilities
through GitHub's private security-advisory interface.
