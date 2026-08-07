# Contributing

Counterexamples, reproducibility failures, adversarial tests, and narrowly
scoped corrections are welcome. Open an issue before a large change so its
claim, boundary, and required evidence can be agreed first.

Every contribution must:

- distinguish a hypothesis, model result, implementation result, and
  deployment claim;
- state the relevant preconditions and failure condition;
- preserve uncertainty rather than converting missing evidence into support;
- include tests or reproducible artifacts when behavior changes;
- avoid secrets, private provider contracts, customer policy, and identifying
  field data.

Before opening a pull request, run:

```text
PYTHONPATH=. python -m pytest -q
npm ci
npm run lint
npm test
```

Use public issues only for non-sensitive material. Report vulnerabilities
through GitHub's private security-advisory interface.
