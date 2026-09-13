# The wheel, decomposed: one instrument holding a vocabulary, a schedule and a theory

A flavour wheel for pu-erh tea fermented with *Monascus purpureus*. Its vocabulary sits
on a national standard; the wheel itself is a research artifact built on top of that
vocabulary. See the provenance note at the end, which corrects an earlier draft. It is a beautiful object, and it is a complete epistemology in one
diagram, which is why it is the clearest teaching case this programme has. Everything the
canon argues about observation surfaces is visible in it at once, and three separate
things have been fused into a single artifact where only the first announces itself.

Companion to `U1-WORKED-EXAMPLE.md`. That one shows a record disagreeing with content
about independence. This one shows an instrument that cannot record the finding that
would refute it.

**What the object is.** Five sectors radiate from the centre: aroma, taste, appearance,
soup colour, tea residue. Inside each runs a ring of numbers, one to forty-two, sampled
at seven points, which is the fermentation clock. Outside the ring each cell holds one
permitted descriptor, and the descriptors advance in a fixed order. Aroma runs fresh,
floral fruity, ripe fruity, fruit-fungus, fungus-stale, stale-qu. Soup colour runs
green-yellow, yellow, orange, red, brownish-red. Taste runs from brisk astringency to
sweet mellow. Around the rim sit physical reference samples, dry leaf and liquor, so a
taster calibrates against the object rather than against the word.

That last detail is genuinely good practice and worth saying plainly before the critique.
The rim is a rung assignment made physical: it pins the vocabulary to something outside
the vocabulary. Most instruments do not do that.

**Layer one, the vocabulary. It fixes what may be said.** Five dimensions, and the tea is
permitted no others. Within each dimension, a closed list of descriptors. This is the
observation surface, and it is a choice, not a discovery. Nothing in the tea decided that
appearance and soup colour are two dimensions rather than one, or that mouthfeel is not a
sixth.

**Layer two, the sampling schedule. It fixes when you look.** Forty-two units of
fermentation, observed at seven points. A continuous process is collapsed into seven
observations, and everything between two observations is not merely unmeasured, it is
unaskable. A transient that rises and resolves between sample four and sample five did
not happen as far as any record built on this instrument is concerned.

**Layer three, the asserted trajectory. It is a causal model wearing a diagram's
clothes.** The descriptors do not merely exist, they are *ordered*, and their order is
aligned to the clock. Saying that aroma proceeds fresh, then floral fruity, then ripe
fruity, then fruit-fungus, then fungus-stale, is a claim about how fermentation actually
proceeds. It is a theory. It is the least visible of the three layers and the only one
that could be wrong in an interesting way.

**Why the fusion matters.** A tea that departs from the trajectory does not produce
contrary evidence. It produces *no* evidence, because the instrument has no cell for it.
The tasting note comes back on-wheel because off-wheel is unrecordable. The finding is
not disproved; it is unrepresentable, and nothing downstream can distinguish a process
that behaved from a process whose misbehaviour had nowhere to go.

That is the whole point, and it generalises past tea: **an instrument that fuses its
vocabulary to its theory can never return evidence against its theory.** Every reading
confirms, and confirmation is worthless, because refutation was never on the menu.

**Where the canon already says this.** `ASSAYER.md` A4 states that a test must be able to
fail and must have failed, and that a gate which has never rejected anything is not known
to be a gate. The wheel is a gate that cannot reject. A5 states that silence in the
instrument is reported as silence in the instrument, which is exactly the report the wheel
cannot produce, because it has no way to say "this tea went somewhere I have no word for".

The shipped enforcement is `scripts/check_effect_reachability.py`, written for a different
case with the same shape: an experiment that froze its protocol, instrumented both arms
identically, and produced an honest number that could not have come out any other way,
because its corpus contained zero instances of the feature its mechanism acts on. The
check asks the author to name the population property their mechanism depends on, then
verifies the population contains it. Applied to the wheel, the question is: name a tea
this instrument would refuse to score, and show one.

**What separating the layers buys you.** Each layer fails differently and is fixed
differently, and fused they are indistinguishable.

- A vocabulary that is too narrow produces silence, and the fix is another cell.
- A schedule that is too coarse produces aliasing, and the fix is more samples.
- A trajectory that is wrong produces confident, well-formed, false readings, and the fix
  is a different theory.

The third failure is the dangerous one because its output looks exactly like success. If
the layers are not named separately, a practitioner who notices something is off will
reach for the first two fixes, add descriptors and sample more often, and make the
instrument more precise about the wrong trajectory.

**What this specifies.** The programme wants a decomposition primitive, and this is its
first specification and its first test at once. The primitive must be able to take one
artifact and return its layers separately, marking the ones it cannot fill as empty rather
than skipping them, because an unfilled layer is a finding and not an omission. The wheel
is a good first input precisely because the right answer is already known: three layers,
fused, with the theory least visible.

**What is not settled, stated rather than implied.**

**Provenance, and a correction.** An earlier draft called this "a published Chinese
industry instrument". That overstated what was known, and the two halves have now come
apart.

The *vocabulary* is standardised, and the standards are real and checkable. China
maintains a national tea standards system published at `openstd.samr.gov.cn`. Three
are relevant: `GB/T 30766-2014` **Classification of tea**, which carries an official
English translation; `GB/T 14487-2017` **Tea vocabulary for sensory evaluation**,
maintained by the National Tea Standardization Technical Committee, SAC/TC339, and
effective 2018-05-01; and `GB/T 23776-2018` **Methodology for sensory evaluation of
tea**. The vocabulary standard's own evaluation dimensions -- dry tea shape and colour,
soup colour, aroma, taste, and leaf bottom -- correspond closely to the wheel's five
sectors, with "leaf bottom" being what the wheel calls tea residue. So the five
coordinates are almost certainly inherited from the standard rather than invented by
the wheel.

The *wheel* is not a standard. The published literature describes a dynamic flavour
wheel built from the volatile compounds tracked across artificial fermentation of
pu-erh with *Monascus purpureus*, which is a research artifact and not a normative
document. That distinction matters here more than usual: a research figure asserting a
trajectory is a hypothesis, whereas a national standard asserting one is a rule that
downstream graders are obliged to follow.

**What is still not closed.** The specific figure has not been matched to a specific
paper, so the wheel itself remains uncited and this document still describes it at
second hand. That is an A3-adjacent weakness and it must close before the wheel is used
as evidence rather than as a teaching case.

**What did get corroborated, and it is worth noting how.** The descriptor trajectories
recorded here were read off the figure. Independent published work on the same
fermentation reports the same progressions: soup colour green through yellow, orange,
red to brown; taste from astringent and brisk, through thick, to mellow and sweet; aroma
from fresh through floral-fruity. Three sequences, from a source that did not supply the
figure. By this corpus's own rule that is a second witness to the content, not to the
citation, and it is recorded as such.

The descriptor sequences above are given as short factual examples of the ordering, not as
a reproduction of the instrument.

Whether three is the right number of layers is open. Three is what this object shows.
Another instrument may fuse four, or fuse two of these differently, and the decomposition
primitive should be allowed to discover that rather than be built to assume it.
