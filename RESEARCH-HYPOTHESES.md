# Research Hypothesis

## H1 — ancestry-aware recovery

**Question:** Can an ancestry-aware aggregation method recover independently grounded minority truth better than majority voting under copying pressure?

**Null hypothesis:** At matched abstention, ancestry-aware aggregation has no higher minority-truth recovery than majority voting.

**Metric:** Minority-truth recovery, truth accuracy, and Brier score, stratified by false-to-true coalition ratio and copy depth.

**Failure condition:** The improvement disappears in held-out seeds or the method incorrectly favors an ungrounded minority in control worlds.

**Success condition:** At least 15 percentage points higher recovery at coalition ratio ≥10, without more than 2 points lower accuracy in independently grounded majority controls.

The exploratory v0.1 pilot satisfied this criterion only in constructed worlds with declared correct lineage and failed under lineage corruption. It was not a blinded or fully preregistered confirmatory experiment. H1 therefore remains open for v0.2.

## DRI-1 — decision-relative independence cuts

**Question:** Does selecting an evidence-independence cut from a declared
decision and failure domain reduce false settlement relative to agent headcount
or one fixed global root definition, without causing prohibitive unnecessary
abstention?

**Null hypothesis:** At matched abstention, a decision-relative cut has no lower
false-settlement rate than the best fixed-cut baseline.

**Unit of independence:** The proximal root at the preregistered causal boundary
relevant to the decision's failure domain. The complete lineage is retained and
the proximal root is not asserted to be the ultimate causal or human root.

**Experimental design:** Freeze evidence graphs that each support multiple
decision contexts: machine-specific compatibility versus controller consensus;
agent diversity versus source diversity; device diversity versus common-cause
sensor failure; and low-consequence reversible action versus high-consequence
irreversible action. Compare agent headcount, a fixed evidence-origin cut, a
fixed controller cut, an oracle preregistered cut, and a model or rules engine
selecting the cut from decision context. Score cut selection before aggregation.

**Metrics:** False-settlement rate; unnecessary abstention; minority
preservation; selected-cut accuracy; material-sensitivity precision and recall;
decision error at matched abstention; latency; and the fraction of cases where
reasonable alternative cuts change settlement.

**Failure condition:** The best fixed-cut baseline matches the oracle policy;
the selector fails to beat a trivial most-common-cut baseline; expert agreement
on the registered failure domain and cut falls below the preregistered bound; or
required metadata is predominantly self-reported and cannot support the claimed
distinction.

**Success condition:** On held-out matched contexts, the oracle cut reduces
false settlement by at least 15 percentage points against every fixed-cut
baseline, and an implementable selector retains at least 80% of that reduction
without increasing unnecessary abstention by more than 10 percentage points.
These thresholds are proposals and must be frozen before data generation.

**Boundary:** This experiment tests a single selected cut and sensitivity to
declared alternatives. It does not establish joint independence across multiple
simultaneous failure domains, discover undisclosed causal structure, or grant
action authority. A positive oracle result with a failed selector supports the
concept but not runtime deployability.

**Current evidence:** A noncanonical DRI-1A candidate run evaluated all 8,192
preregistered synthetic worlds and failed its joint success criterion. The
decision-relative oracle achieved
90.99% correct settlement versus 60.78% for agent headcount and 68.32% for the
best fixed-cut correct-settlement rate, and recovered 100% of registered
minority reversals. But it did not reduce false settlement by the required 15
points against every fixed cut: the coarsest fixed cut reached 3.26% false
settlement by abstaining 40.23% of the time, and three fixed cuts could not be
abstention-matched within tolerance. The explicit rules engine equalled the
oracle by construction and therefore demonstrates deterministic execution in
this fixture, not causal cut inference or deployment readiness. The protocol
lacked several fields required for canonical promotion, so this result remains
a content-bound candidate diagnostic. See `results/dri1a-v1/`.

## HVI-1 — verifier independence under shared control

**Question:** Can explicit creator, verifier, and controller provenance prevent
one controlling party from increasing evidential mass by splitting its work
across multiple identities, keys, services, or organizational labels?

**Null hypothesis:** At matched abstention, a control-domain-aware method does
not reduce falsely accepted independent roots relative to signature validation
alone.

**Unit of independence:** A supported control domain, not an account name,
public key, signature count, service boundary, or third-party label.

**Experimental design:** Construct matched worlds containing (a) genuinely
separate evidence producers and verifiers, (b) one controller operating many
keys and labels, (c) self-produced and self-verified evidence, (d) partially
shared control, and (e) unknown control relationships. Compare head count,
signature-only validation, identity-distinct counting, and control-domain
collapse under identical evidence and abstention budgets.

**Baselines:** Head count; signature-only validation; identity-distinct
counting; scalar validator-score mean and median; median with outlier clipping;
and control-domain-aware evidence-root aggregation. The score baselines test
whether robust aggregation alone can resist correlated or commonly controlled
validators without independently supported control provenance.

**Metrics:** False-independent-root acceptance rate, retention of supported
independent roots, decision error, abstention rate, and the change in root mass
caused solely by renaming identities or rotating keys.

**Failure condition:** A name, key, service, or label split increases independent
root mass without new separation evidence; unknown control is converted into
permission; or the method collapses genuinely separate roots often enough to
erase its advantage at matched abstention.

**Success condition:** Declared common-control and self-verification cases add
zero independent roots; identity and key substitutions do not change root
mass; unknown control always abstains or escalates; and supported independent
roots are retained at least 95% of the time in the preregistered synthetic
controls.

**Required artifacts before a canonical run:** A versioned independence-receipt
schema, control-domain threat model, frozen world generator, baseline
implementations, adversarial conformance vectors, preregistered thresholds,
and content-bound results with an explicit null/adverse-result path.

**Boundary:** This experiment can test how declared or externally supported
control relationships affect aggregation. It cannot discover undisclosed
real-world common control without trustworthy external evidence. A signature
proves key use, not organizational independence; the resulting assessment does
not itself grant authority.

**Canonical result:** Supported in HVI-1 v1 across all six frozen hypotheses.
Representation laundering and self-verification added zero control-aware roots,
and unknown control always escalated. The matched separate-controller condition
also demonstrated the boundary: organizational separation does not establish
causal evidence independence or truth. See `results/hvi1-v1/`.

## HRI-1 — root identity under shared observation

**Question:** Does one distinct evidence root correspond to one distinct
underlying observation, when every issuer is honest and every issuance rule is
obeyed?

**Null hypothesis:** The number of distinct `mp-root-v1` identities per
underlying observation is 1. Root identity tracks observation identity.

**Unit of independence:** An underlying observation event — the thing that was
witnessed — not an issuer, key, control domain, signature, or root identifier.

**Why this is not HVI-1.** HVI-1 asks whether *one controller* can inflate
evidential mass by splitting across identities: an adversary, defeated by
collapsing to control domains. HRI-1 asks the honest-actor counterpart. Five
genuinely separate organisations, five distinct control domains, no shared
control to discover, each authenticating correctly and each inside its R1.4
quota — all reporting one upstream observation they did not independently make.
HVI-1 counts five and is right by its own definition. The aggregator counts five
and is wrong. No adversary is present and no rule is broken, so nothing in the
current stack raises an alarm.

**Why it matters more than an ordinary open question.** `margin` counts distinct
root identities. `flip_budget`, `conversions_to_reverse` and every security
statement denominated in them inherit whatever ratio holds between root
identities and observations. If that ratio is systematically above 1, published
budgets are overstated by that factor and no existing check detects it. This is
the only open item in `formal/THEOREM-LEDGER.json` capable of silently
invalidating numbers the project already reports; the others (U3 weighted roots,
CE-07 edge polarity) limit what the model can express rather than corrupt what
it currently says.

**Metric:** Split factor — distinct `mp-root-v1` identities divided by distinct
labelled observations, per proposition. Reported as a distribution, with the
median as the primary endpoint. Merge rate — distinct labelled observations
collapsed into one root identity — reported alongside, since it fails in the
opposite direction and destroys margin rather than inflating it.

**Failure condition:** Inter-rater agreement on "same underlying observation"
falls below the registered threshold, meaning the ground truth is not
establishable on this corpus and the measurement cannot be made. This ends the
run and is reported as such; it is not retried on a corpus chosen because it
agrees better.

**Success condition:** This hypothesis succeeds by being *answered*, in either
direction, on a frozen corpus with blinded labelling. A median split factor
indistinguishable from 1.0 is the strongest available evidence that the
independence claim survives contact with real reporting. A median materially
above 1.0 is a quantified correction to every published budget. Both are
results. A design that can only produce the first is not this design.

**First gate:** Until HRI-1 is answered, `flip_budget` may be published as a
count of root-set units — which is what it provably is — but not as an
operational security budget, because the mapping from root identities to
independent evidence is unmeasured. See `formal/CLAIM-SCOPE.md`.

**Required artifacts before a canonical run:** a frozen corpus manifest, a
labelling protocol with the root identifiers withheld from labellers, a
registered inter-rater threshold, and a sensitivity demonstration that the
measure detects a known split in constructed cases. Registered as KL-014.

## HRI-2 — do evidence roots mark where new evidence entered?

**Question:** Does the set of claims an aggregator treats as evidence roots
correspond to the work that actually introduced new observation, rather than to
work that merely failed to record its ancestry?

**Null hypothesis:** Root status is uncorrelated with whether a work introduced
new observation.

**Depends on KL-014 v0.3.** This question is not interpretable until a root
criterion is shown to recover known-independent observations. If v0.3 finds that
no reference-based criterion does, HRI-2 is answered vacuously — roots would not
mark anything, because the criterion producing them is not measuring
independence — and that dependency is registered rather than discovered later.

**Unit:** A work, and whether it contributed an observation that did not exist
in the literature before it.

**Ground truth, taken from metadata rather than judgement:**
- *Structurally non-originative:* a review or meta-analysis introduces no new
  observation by definition. A review appearing as an evidence root is a false
  root, and no opinion is required to say so.
- *Retroactively phantom:* a retracted work whose retraction concerns the data
  or result is a root whose evidence was never there. OpenAlex flags 78,465
  retracted articles.

**Metric:** False-root rate — the proportion of works classified as evidence
roots that are structurally non-originative. Secondary: retraction-cascade
depth, the number of works transitively depending on a retracted root.

**Why the retraction arm matters beyond this hypothesis.** A retraction is a
root-set error occurring in the world rather than in a constructed witness. T5
(`root_error_tolerance`) states what a margin survives when the root set is
disturbed by `k`; retraction cascades are the first opportunity to observe that
disturbance empirically instead of by assumption.

**Failure condition:** The root criterion inherited from KL-014 v0.3 does not
recover known-independent observations, making root status uninterpretable; or
retraction reasons cannot be separated into data-related and administrative,
making "phantom" unassignable.

**Success condition:** Answered in either direction on a frozen corpus. A false-
root rate near zero would mean root structure tracks originative work and is a
genuinely positive result. A high rate would mean the aggregator's roots mark
absent provenance rather than present evidence — which is CE-01 restated as a
property of a real corpus rather than a constructed witness.

**Prohibited overstatement:** "Retracted" is not "was wrong"; some retractions
are authorship or ethics disputes with sound underlying data. Any phantom-root
claim must rest on retraction *reason*, not on retraction alone.
