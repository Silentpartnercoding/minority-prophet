# HGD-2 canonical result

HGD-2 tested graded dependency accounting on activated common-mode failures in
two domains: EPA collocated PM2.5 measurements and NIST SARD software-analysis
cases. It added untouched controls so abstention alone could not count as
success.

The primary claim was **rejected**. Five of seven frozen hypotheses passed.
Safety, control accuracy, interval calibration, and uncertainty escalation
passed. Control coverage and attacked usefulness failed.

## Environmental evidence

On activated cases, head counting was confidently wrong by definition.
Interval false-confident error was 27.95% for negative shifts and 4.78% for
positive shifts. The corresponding 95% relative-risk upper bounds were 0.3595
and 0.0607, passing HGD-2a. Untouched interval accuracy was 100% and coverage
was 99.71%.

The safety gain came primarily through abstention: interval accounting answered
only 27.95% of activated negative cases and 4.78% of activated positive cases.
That failed the frozen 50% usefulness floor.

## Software evidence

The confirmatory software sample contained 18 reciprocal good/bad NIST pairs
and seven detector configurations across compiler, Flawfinder, and lexical
families. On 56 activated family failures, pooled interval false-confident
error was 32.14% versus head count's 100%; the paired 95% upper bound was 0.50.
All nine family/failure cells stayed at or below the frozen 0.75 point-risk
ceiling, passing HGD-2b.

Untouched interval accuracy retained 95.24% of head-count accuracy, but
answered coverage fell from 100% to 25%. Activated coverage was 32.14%. These
failed HGD-2d and HGD-2e.

## Interpretation

The method is a strong brake but not yet a strong steering system. It prevents
many confident errors by recognizing shared failure domains, but frequently
cannot resolve the remaining independent evidence. The next research target
is evidence-seeking escalation: obtain another independent measurement or
review rather than merely stop.

Two executions at implementation commit
`c8ab8ce55aa80c2bff0ab7d9e85a35ee5b76b598` produced byte-identical scientific
JSON. The result does not certify analyzers, establish historical EPA errors,
discover hidden dependencies, or grant authority.

