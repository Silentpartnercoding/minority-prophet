# Six proposed answers to weighting, each measured against ground truth

`probe.py` measured when weighting changes a verdict. `frames.py` measures whether it
changes it *correctly*, which is what decides between the proposals. Worlds have a
truth; each source has a hidden competence; aggregators see votes and, per frame, some
estimate of that competence.

The oracle is log-odds weighting, which is optimal for independent sources of known
competence, so every frame is measured against the best achievable rather than a
strawman. Nine sources, competence uniform in 0.45 to 0.95, forty thousand trials a
cell. Exploratory, not preregistered, and the generator is uniform and independent
unless a run says otherwise.

**The prize is small and real.** Counting everyone equally scores 0.9031. The oracle
scores 0.9543. **Every argument about weighting is an argument about five accuracy
points.** Worth having, not worth wrecking a proof for.

**Frame five, the crossover, now has a number.** You must know each source's competence
to within roughly fifteen percentage points before weighting is worth doing.

| estimate error | accuracy | verdict |
|---|---|---|
| plus or minus 0.05 | 0.9466 | beats counting |
| plus or minus 0.10 | 0.9288 | beats counting |
| plus or minus 0.15 | 0.9069 | barely beats counting |
| plus or minus 0.20 | 0.8856 | **worse than counting** |
| plus or minus 0.30 | 0.8351 | **much worse** |

That is the whole answer to "should we weight". Below the line, weighting is not a
refinement; it actively destroys accuracy by amplifying the wrong voice.

**Frame three survives, with a sharp cold-start rule.** A weight earned from a track
record works, but a *short* track record is far worse than none.

| outcomes scored | accuracy |
|---|---|
| 0, uniform | 0.9013 |
| 1 | 0.7783 |
| 3 | 0.8623 |
| 10 | 0.9215 |
| 30 | 0.9410 |
| 100 | 0.9498 |

One observation is catastrophic, costing twelve points against simply counting. So a new
source must sit at uniform and stay there until it has roughly **ten scored outcomes**.
There is no gentle ramp: the early estimates are confident and wrong.

**Frame two does not survive as a principle.** Weighting by stake is only useful if
stake actually tracks competence, and that is an empirical claim about the world rather
than something the sacrifice guarantees.

| how strongly stake tracks competence | accuracy |
|---|---|
| not at all | 0.8404 |
| a quarter | 0.8972 |
| half | 0.9291 |
| perfectly | 0.9528 |

At no correlation, weighting by stake is six points *worse* than counting. Money at risk
proves the holder believes it, and belief is not accuracy. A stake makes a weight
expensive to assert, which is a defence against lying, and does nothing about being
sincerely wrong. Those are different failures and only the first is addressed.

**Frame six was refuted and is now partly rehabilitated, and both results are true
because they measure different things.** On accuracy with a correct classifier, a gate
works: admit above a threshold, count equally, and every threshold tried beats counting,
peaking at 0.9314 for admit-above-0.7. That captures a little over half the available
headroom with no multiplier for anyone to capture and every counting theorem intact.

But `probe.py` showed the same gate is *more brittle than weighting when the classifier
itself is uncertain*, because a source near the threshold is worth a whole vote or
nothing. Doubt at the boundary costs a full unit under a gate and only its own size under
a weight. So the gate is the better instrument when you can classify confidently and the
worse one when you cannot, and the two findings do not conflict.

**Frame four terminates, and the answer came from our own tool.** Running a weight's
justification chain through `canon/authority_debt.py`:

| how the weight is justified | terminates in |
|---|---|
| a scored track record | evidence |
| a bonded stake | mechanism |
| an owner assigned it, named, uncertainty stated | judgment |
| nobody can justify it, and we say so | unknown |
| convention: everyone gets one | judgment |
| reputation, from consensus, from weight | **loop** |

No fifth ending is needed. Weight-provenance terminates exactly the four ways authority
does, and the circular case is detected rather than accepted as support. The last row is
the one worth remembering: reputation justified by consensus justified by reputation is
the ordinary way weights are set in the world, and it grounds in nothing.

**The observation about independence is half right, and the half that is wrong matters.**
Weighting and independence are not substitutes. With a bloc of copies all repeating one
member:

| share copied | counting | oracle-weighted | weighting buys |
|---|---|---|---|
| none | 0.9015 | 0.9542 | +0.053 |
| a third | 0.8732 | 0.9288 | +0.056 |
| two thirds | 0.7017 | 0.7698 | +0.068 |

Weighting buys slightly *more* when copying is present, not less, so handling
independence does not remove the appetite for weights. But look at the left column
instead: copying costs counting twenty points, and perfect weighting recovers seven of
them. **Independence is roughly three times the problem that weighting is.** The
observation is right about priority and wrong about substitution.

**What this means for stripping weights.** Discarding an incoming weight is not
neutrality; it is choosing uniform, and uniform is a real estimator with a real score of
0.9031. The frame four table says why it is defensible: convention terminates in
*judgment*, which is an honest ending provided somebody owns it and publishes it. And
frame five says when it is not merely defensible but correct: any weighting whose
competence estimates are worse than about fifteen points is beaten by uniform. Uniform is
not a refusal to weigh. It is the right weighting under ignorance, and it stops being
right the moment you can estimate competence well enough.
