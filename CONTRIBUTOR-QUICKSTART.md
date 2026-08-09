# Contributor quickstart

Minority Prophet welcomes small fixes, adapters, counterexamples, replications,
and carefully bounded research. Choose the lightest lane that honestly describes
the work. A stronger claim needs stronger evidence; ordinary contributions do
not inherit research paperwork.

## First setup

```sh
make setup
make verify
```

`make verify` runs the same Python, evidence-integrity, public-boundary, and site
checks used by CI. Use `make help` to run one group at a time.

## Choose one lane

| Lane | Use it for | Required before the PR |
|---|---|---|
| Routine | Code, adapters, documentation, maintenance | Normal tests and a bounded description |
| Exploratory | Prototypes, fixtures, falsification attempts | Label output exploratory; do not promote a claim |
| Candidate | A confirmatory question | Commit the protocol and candidate record before inspecting outcomes |
| Canonical | Closing a repository-native candidate | Bind result and manifest, preserve the honest verdict, update evidence indexes |
| Imported | Recording an out-of-tree result | Bind the imported packet and declare source/control limits |
| Authority-sensitive | Anything that could permit a live effect | Stop and obtain explicit maintainer authorization |

## Copyable examples

### Routine: improve an adapter

Change the smallest relevant code and tests, select **Routine** in the PR
template, then run:

```sh
make verify
```

### Exploratory: test an idea without making a claim

```sh
python scripts/new_research_record.py exploratory EX-101
git add research/records/EX-101.json
```

Keep generated output clearly labeled exploratory. Passing output does not make
the result canonical.

### Candidate: freeze the question before seeing the answer

```sh
mkdir -p experiments/EX-102
# Write experiments/EX-102/PROTOCOL.md, including failure conditions.
git add experiments/EX-102/PROTOCOL.md
git commit -m "freeze EX-102 protocol"
python scripts/new_research_record.py candidate EX-102 \
  --protocol experiments/EX-102/PROTOCOL.md
git add research/records/EX-102.json
git commit -m "register EX-102 candidate"
```

Only after the candidate commit should a confirmatory runner inspect outcomes.

### Canonical: close the candidate without rewriting it

Commit the result and manifest, then promote the existing candidate:

```sh
python scripts/new_research_record.py canonical EX-102 \
  --result results/ex-102-v1/result.json \
  --manifest results/ex-102-v1/manifest.json \
  --verdict rejected
```

`supported`, `rejected`, `incomplete`, and `invalidated` are all legitimate
verdicts. Update `CANONICAL-RECORDS.md` and `EVIDENCE-ALIGNMENT.md`, then run
`make verify`.

### Imported: preserve what happened elsewhere

```sh
python scripts/new_research_record.py imported EXT-101 \
  --protocol imports/ext-101/protocol.md \
  --result imports/ext-101/result.json \
  --manifest imports/ext-101/manifest.json \
  --verdict incomplete \
  --source-repository https://example.test/research.git \
  --source-commit 0123456789abcdef0123456789abcdef01234567 \
  --control-relationship unknown
```

An import records provenance. It is not automatically an independent
verification or a repository-native rerun.

### Authority-sensitive: stop before the effect

Describe the proposed boundary without executing it. Ask the maintainer for
explicit authorization before changing live permission, deployment, signing,
revocation, or enforcement behavior. Evidence assessment never grants that
authority by itself.

## If a check fails

Read the `Fix:` line printed beneath the failure. The integrity checker does not
silently repair evidence because doing so could rewrite the research boundary.
If the fix would change a frozen protocol, expected outcome, canonical record,
or live authority decision, stop and ask the maintainer instead.
