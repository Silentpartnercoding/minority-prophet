# Research Hypothesis

## H1 — ancestry-aware recovery

**Question:** Can an ancestry-aware aggregation method recover independently grounded minority truth better than majority voting under copying pressure?

**Null hypothesis:** At matched abstention, ancestry-aware aggregation has no higher minority-truth recovery than majority voting.

**Metric:** Minority-truth recovery, truth accuracy, and Brier score, stratified by false-to-true coalition ratio and copy depth.

**Failure condition:** The improvement disappears in held-out seeds or the method incorrectly favors an ungrounded minority in control worlds.

**Success condition:** At least 15 percentage points higher recovery at coalition ratio ≥10, without more than 2 points lower accuracy in independently grounded majority controls.

The exploratory v0.1 pilot satisfied this criterion only in constructed worlds with declared correct lineage and failed under lineage corruption. It was not a blinded or fully preregistered confirmatory experiment. H1 therefore remains open for v0.2.

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
