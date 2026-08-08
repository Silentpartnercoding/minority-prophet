# KL-001 first check (FC1) — preregistration

Registered before execution by RUN-20260807-6. This is the narrow first
check KL-001's record has named since RUN-20260807-1: *"construct one
repository whose mandatory file coverage is incomplete and show the pipeline
cannot emit a clean conclusion for it. If it can, KL-001's first gate fails
immediately."* The only pipeline component that exists is the KL-000
reference evaluator (`knowledge_ledger/transaction.py`,
`sha256:15dfd500…3a3e21f`, unchanged since v1.0.0); FC1 runs against it.

## The worlds, fixed here

**W1 — the check.** Repository `example-svc`; claim: absence — "No hardcoded
credential exists in the mandatory files of repository example-svc."
Mandatory files as the declared search space:

| location (mandatory file) | status |
|---|---|
| `src/config.py` | searched |
| `README.md` | searched |
| `.env.example` | **not_searched** |
| `deploy/secrets.tpl` | **unavailable** |

Evidence: two scanner runs supporting cleanliness — `scanner-A` (two records,
a duplicate) and `scanner-B` (one record); no opposing roots.

**W2 — coverage control.** W1 with all four files `searched`. Shows the gate
is coverage and nothing else.

**W3 — the under-declaration twin (demonstration, not a pass/fail item).**
The same repository with `.env.example` and `deploy/secrets.tpl` simply
omitted from the declaration: declared 2, searched 2.

**W4 — the structural twin of W1 in KL-000's vocabulary.** Same structure,
KL-000's enumeration strings (locations `loc-1..loc-4` with W1's statuses;
records `r1`×2 + `r2`, all support; the standard absence proposition). W4 is
inside KL-000's declared bounds (4 locations, 3 records, 2 roots) and is
therefore one of the 176,120 enumerated worlds, whose conclusion two
independent implementations have already confirmed.

## Preregistered expectations

| # | Expectation | Falsifies |
|---|---|---|
| E1 | W1 concludes `not_established` — **not** `absent_within_declared_scope` — with reason "The declared search space was not exhaustively searched." | KL-001's named first gate fails if W1 gets a clean conclusion |
| E2 | W2 concludes `absent_within_declared_scope` | that the refusal in E1 is about coverage, not something else |
| E3 | W3 concludes `absent_within_declared_scope` — the same repository reality reaches "clean" by under-declaring scope | nothing; this is ADV-001 restated in repository costume, demonstrated on purpose |
| E4 | W4's receipt is **identical to W1's in every structural field** (`conclusion`, all of `search`, all of `evidence`); the receipts differ only in the echoed strings and therefore in digest | the I2-in-costume hypothesis, if W1 and W4 diverge structurally |

## The epistemic question, both verdicts stated before running

**(a) If E1–E4 all hold:** FC1 is I2 restated. "Mandatory file" maps to
"declared location" by pure renaming; the evaluator sees structure only; W1's
structural class is already inside KL-000's enumeration (fixture C08 is this
shape); the check produces **no new evidence about the evaluator**, and
KL-001's named first gate was already paid by KL-000. The record will say
exactly that, and KL-001's real first gate becomes the next one: the
planted-defect corpus with frozen generation, the false-clean endpoint, and
the pipeline that maps repository reality into ledgers — the layer where
scope-declaration honesty (ADV-001, demonstrated by W3) actually lives.

**(b) If any expectation fails:** the repository framing exposed behaviour
the abstract worlds did not, the divergence is the finding, and it localises
what "mandatory file coverage" means that "declared locations" did not.

Verdict (a) is not a failure and will not be dressed up as more than it is;
verdict (b) will not be hand-waved.

## Invalidation

Evaluator hash differing from the registered value; W4 falling outside
KL-000's declared bounds; any expectation judged by inspecting anything
other than the emitted receipts.

## Boundary

FC1 supports no claim about real repositories, real scanners, or real
credentials. All four worlds are synthetic. FC1 does not advance KL-001 past
`seeded` under verdict (a); whether it could under (b) is moot unless (b)
occurs.
