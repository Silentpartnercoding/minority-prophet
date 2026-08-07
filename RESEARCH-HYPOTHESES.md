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
