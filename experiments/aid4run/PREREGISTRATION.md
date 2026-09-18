# AID-4 — preregistration, protocol v1

**Status: FROZEN, protocol v1. NOT RUN.** Frozen before any confirmatory
campaign is generated or scored. The two policies, the five arms and both
criterion sets were named in
`research/attested-independence/AID-4-DESIGN-DRAFT.md` before this world
existed. This file is the world and the scoring, written by someone other than
the author of the policies.

No confirmatory outcome had been computed when this was frozen, and there is no
runner in this package: a confirmatory run needs a registration of its own.
Same control domain as the rest of the series. Author separation, not
independent validation.

## 1. Identifier

AID-4, protocol v1. Fourth confirmatory experiment of the attested-independence
series, and the first to score two policies at once against two criterion sets.

## 2. Why this exists

Three experiments closed one road. Requiring witnesses to prove how deep they
went — and discounting those who cannot — was rejected by AID-1, by AID-2 after
repair, and by AID-3 on the adversarial review's own world, where the
suppression was total and rate-independent: 4,800 of 4,800 decisions settled
against a true contrary claim.

Two roads were named at that junction. The draft specifies both and fixes their
criteria before any world exists. My job is the world, and the world is built so
that **both policies can lose**. No trap here has been softened because it
looked harsh, and no criterion has been renumbered, weakened or added.

## 3. The two policies, copied from the draft

> **Policy B — collapse-robust margin.** Count every witness, discount nobody.
> Settle only when the settlement **survives the worst case the record cannot
> rule out**: if `j` witnesses on the winning side are unattested, they might
> all be one source, so the winning count could be as low as `n − j + 1`. Settle
> only if the side still wins at that floor. [...] In a tie it abstains, as the
> baseline does.

> **Policy C — priced exposure.** Count every witness and settle exactly as the
> baseline settles. C changes no decision. It attaches to each settlement a
> published figure — how much of it rests on witnesses who stated nothing —
> reusing `unattested_exposure`, already shipped.

## 4. Arms, and the three operational choices this world had to make

1. **`ladder`** — `canon.proximity` unchanged. Baseline.
2. **`margin`** — policy B. Primary for the decision criteria.
3. **`priced`** — policy C. Settles identically to `ladder`; carries an exposure
   figure per decision.
4. **`attested`** — the rejected policy, as a known-bad reference point.
5. **`refuse_all_unrecorded`** — refuse on any unrecorded pair. Cost ceiling.

The draft left three operational questions open. They are answered here, before
any salt is read, and never revisited after a number is seen.

**(a) What "unattested" means for B.** The draft's reason for the floor is that
`j` unattested witnesses "might all be one source". Being countable apart is an
identity question, not a completeness question — the repaired policy's own
docstring says a witness may not attest to what it does not know it shares. So a
witness is unattested for B when the record cannot count it apart from another:
`identity is ANONYMOUS`. B's floor is then exactly the lower bound that
`aggregation.independence_axes.effective_witness_bounds` already computes
(`identified + 1`), restricted to the winning side. Keying B to the completeness
tick instead would rebuild the inference the repair removed.

**(b) What B does when the floor fails.** The draft says settle "only if the side
still wins at that floor", and abstain in a tie as the baseline does. The floor
is therefore a **gate on the baseline's answer**, not a second election: B never
re-decides which side won at the floor. **Consequence, stated in advance: B's
settlements are a subset of the baseline's, in the same direction, so B cannot
settle against a claim the baseline did not settle against, and criterion 4
cannot fail on this world or on any other.** That is a property of the criterion
as worded, not a finding about the policy, and writing the world does not
entitle me to repair it. The world instead carries `minority_wins`, where the
baseline settles *for* a true minority claim and B does not, and reports
`settlesForTruth` alongside criterion 4 so the gap the criterion cannot see is
on the record.

**(c) What C's exposure figure is.** `unattested_exposure` returns four counts.
The one the draft describes — "how much of it rests on witnesses who stated
nothing" — is `ancestry_not_attested`, over every witness in the decision, both
sides. The share variant is computed and **reported as a diagnostic only**,
because a raw count confounds exposure with decision size and the reader is
entitled to see whether that confound carries the result. The shipped function
refuses a rate on purpose, so the count is the criterion.

## 5. Adoption

`alpha` is the probability that a witness which *can* attest presents its
credentials for a decision. A witness that presents them appears with the
backing it really has and ticks `ancestry_complete`; one that does not appears
as what the record then holds — a bare declaration from a source it cannot tell
apart from any other. Witnesses who cannot attest never present credentials at
any rate. Copies holding a device key present them at every rate.

This is a stronger adoption model than AID-3's, which moved only the
completeness tick, and it is chosen so `alpha` moves all three policies rather
than only the rejected one. **Flagged in advance: at `alpha = 0` every witness
in this world is anonymous, so B's floor is 1 on every side and B settles
nothing at threshold 2.** That is what B does when nobody attests, not a trap
inserted to defeat it, and every `alpha = 0` cell should be read with it in mind.

## 6. Generated worlds

300 campaigns per family, 12 decisions, `alpha ∈ {0.0, 0.5, 1.0}`, threshold 2,
`FABRICATION`, reversible decisions. Eight families, 7,200 campaigns.

**No family records ancestry or idiosyncratic markers.** Nothing connects the
copies — that is DR3's case — and the consequence is that
`refuse_all_unrecorded` abstains on every decision in the world. That is what a
cost ceiling is, and criterion 3 is sharp because of it: the ceiling prevents
every silent false settlement by settling nothing at all.

| Family | What is true | What it is built to break |
|---|---|---|
| `hidden_source` | Two copies of one hidden parent plus three honest attestable witnesses; noisy voting. The copies hold real credentials about themselves and present them at rate `alpha`; no credential speaks to the parent they share. | B's criterion 1 on the adoption curve. While the copies are silent B's floor collapses them; once they attest B counts them apart and hands back the independence it was withholding — AID-1's finding, on B. |
| `backed_hidden_source` | Three copies of one hidden parent, each with a device key and a verified identity, attesting at every rate, plus two honest attestable witnesses; noisy voting. | B's criterion 1 at **every** rate, and C. A device attestation earns depth and says nothing about shared origin (AID-2). B's floor never fires, so it prevents nothing; C's exposure reads near zero on exactly the settlements that are false. |
| `honest_unattestable` | Five witnesses who went to the world and left nothing. Three against two, baseline always right. | Criterion 5, and C's criterion 2. B's floor collapses the winning side to 1 and B abstains on everything; exposure is constant and separates nothing. |
| `wide_margin_unattested` | Four against one, unattested witnesses on the winning side, three attested ones beside them. Baseline always right. | Criterion 5 from the other side. B *can* settle here, so a world where B looks like refusal everywhere is not this world's doing. |
| `silent_but_correct` | Settlements resting on silence that are nonetheless correct, in two shapes: hidden dependence on the **losing** side, which does not make the settlement wrong; and a winning side that is entirely unattested and entirely right. | C. Without these, high exposure and falsity coincide and discrimination is trivially perfect. |
| `minority_suppression` | AID-3's construction unchanged in substance: two unattestable witnesses hold the true claim, two backed attesters hold the false one, the ladder ties and abstains. | Criterion 4. This killed policy A. B faces it unchanged. |
| `minority_wins` | The minority is the winning side **and** the side carrying every unattested witness: three unattestable witnesses hold the true claim and beat two backed attesters, so the baseline settles for them and is right. | The asymmetry no previous world exhibited. Collapsing the winning side is not symmetric when the minority is the winning side. Criterion 4 records no loss; `settlesForTruth` records the vindication B gives up. |
| `mixed_populations` | Hidden copies, attestable witnesses, unattestable witnesses and one honest restater in one decision; noisy voting. | C, without any cross-family confound: both outcome classes arise from one layout, so exposure is asked to separate them within a single population. The restater also keeps the exposure figure's axes from collapsing onto one number — it is unattested and does not overclaim. |

Margin-critical means what it has meant since AID-1: collapsing the family's
focus group moves the baseline settlement. Families with no hidden group have an
empty focus and no critical decisions.

## 7. Scoring

Baseline outcomes are the reference for prevention; the **reference settlement**
is taken over true causal units, so a hidden pair is one unit. A settlement is
silently false when it settles a direction the reference does not, an abstention
is unneeded when the reference settled, and a true contrary claim survives when
the decision is not settled against it.

- Criteria 1 and 3 are scored on the hidden-source cells — the cells where
  prevention is defined — powered when the baseline makes at least 12
  margin-critical silent false settlements, Holm-corrected across powered cells,
  failing closed when none is powered.
- Criterion 2 is self-scoping, exactly as worded: a pass mark in every family
  where the baseline makes at least one margin-critical silent false settlement,
  and a reported figure everywhere else.
- Criterion 4 is scored in both minority families.
- Criterion 5 is scored in the families where the baseline is already right and
  nothing is hidden: `honest_unattestable` and `wide_margin_unattested`.
- C's cells are (family, adoption rate), as everywhere else in this series, and
  a cell is powered for C only when the baseline produces at least 12
  settlements of **both** outcome classes in it. The figure pooled across
  families is computed and reported and is **not** a pass mark: pooling would
  let the balance of families I chose set the AUC.

## 8. Success criteria, copied verbatim from the frozen draft

Criteria are not renumbered, softened or added to. Section 5, for policy B:

> Scored on reversible decisions. Powered cells only, Holm-corrected, fail
> closed when underpowered. Two executions semantically identical.
>
> **B is supported only if all hold:**
>
> 1. **Prevention.** In every powered hidden-source cell, prevents at least 40%
>    of the baseline's margin-critical silent false settlements. The same floor
>    used since DRI-9; not chosen for this run.
> 2. **Cost is bounded by benefit, where benefit is possible.** Correct
>    settlements lost do not exceed silent false settlements prevented, in every
>    family where the baseline makes at least one margin-critical silent false
>    settlement. Where it makes none, cost is reported and is not a pass mark.
> 3. **It is not worse than refusing.** Strictly more correct settlements than
>    `refuse_all_unrecorded`, with prevention no more than 10 points below it.
> 4. **It does not suppress.** In every minority-suppression cell, the true
>    contrary claim survives **at least as often** as under the baseline. Any
>    loss fails the experiment outright. This is the criterion that killed policy
>    A and it is not relaxed.
> 5. **It is not refusal with extra steps.** Where the baseline is already right
>    and nothing is hidden, B settles at least half of what the baseline settles.

Section 6, for policy C:

> C is scored on discrimination, not on decisions.
>
> 1. **It discriminates.** Among the baseline's settlements in every powered
>    cell, exposure must rank silent false settlements above correct ones with
>    **AUC ≥ 0.70**. A coin flip is 0.50; a number that cannot beat 0.70 is not
>    worth publishing as a warning.
> 2. **It is not constant.** At least 20% of settlements must carry an exposure
>    figure different from the modal value. A figure that never varies has not
>    discriminated anything, whatever its AUC computes to.
> 3. **It changes nothing.** C's settlements must be identical to the baseline's
>    in every cell. Any divergence is a construction error, not a result — C is a
>    disclosure rule and must not become a decision rule by accident.

Kill criteria, section 8 of the draft, unchanged: if B suppresses the margin road
closes; if C fails to discriminate the pricing road closes as a warning
mechanism; if both fail the programme has no remaining constructive proposal.

## 9. Frozen inputs

This protocol, `EXECUTION-CONFIG.json`, `experiments/aid4run/world.py`,
`arms.py`, `scoring.py`, `aggregation/attested_independence.py`,
`aggregation/independence_axes.py`, `canon/proximity.py`,
`canon/independent_set.py`, `experiments/dri2/stats.py`. A confirmatory runner
must pin all ten by digest before it runs.

## 10. Disclosure

- **Written by someone other than the author of both policies**, which is the
  only reason these criteria bite. Same control domain; author separation, not
  independent validation.
- **Development salt only.** The confirmatory salt is passed to nothing:
  `scoring.evaluate` refuses it unless `confirmatory` is set explicitly, nothing
  in this repository sets it, and there is no runner in this package.
  `tests/test_aid4_protocol.py` asserts the refusal fires.
- **Criterion 4 cannot fail on this world, or on any world.** See section 4(b).
  Disclosed before the run rather than discovered after it.
- **At `alpha = 0` policy B settles nothing.** See section 5. Every `alpha = 0`
  cell is a statement about B under total non-adoption and should be read as one.
- **`refuse_all_unrecorded` abstains on every decision here**, because nothing in
  this world records ancestry. Criterion 3 is correspondingly sharp: it asks B to
  come within 10 points of the prevention rate of an arm that settles nothing.
  The same objection was raised against AID-1's criterion 4 in `results/aid3-v1/`.
- **C's per-family AUC is the criterion; the pooled figure is not**, because I
  chose the families and pooling would let that choice set the number. Both are
  reported.
- **The exposure scalar is a choice** (section 4(c)). The share-based variant is
  reported so a reader can see whether the count's size confound is load-bearing.
- **Every rate is synthetic.** Nothing here measures real adoption, and the
  census in `experiments/aid1/` found zero records in this estate stating a
  witness depth.
- **No authority claim.** Evidence assessment never grants permission to act.
