# HGD-1 canonical result

HGD-1 tested whether interval-valued dependency accounting can preserve
distinct measurements while reducing false confidence caused by shared sensor
context and common-mode failure.

The primary claim was **rejected**. Six of seven frozen hypotheses passed.
HGD-1g failed because the largest absolute observational false-confident-error
reduction was 4.23 percentage points, below the preregistered 5-point
requirement. The criterion remains unchanged.

In 5,000 synthetic common-mode worlds, head counting was confidently wrong in
100% of worlds. Interval accounting was confidently wrong in 75.78% and
abstained in 24.22%; the paired interval-minus-head error difference had a 95%
bootstrap interval of -25.44 to -23.04 percentage points.

The EPA track used 50,978 confirmatory collocated-site cases paired with a
nearby separate-site reference. At injected shifts of 5, 10, and 20
micrograms per cubic meter, respectively:

- head-count false-confident error was 0.220%, 0.651%, and 4.349%;
- interval-accounting error was 0.055%, 0.078%, and 0.122%; and
- interval answered coverage was 99.56%, 99.00%, and 93.97%.

These results show a strong directional safety signal but do not satisfy the
frozen absolute-effect threshold. They support no claim that collocation alone
proves causal dependence, that historical EPA measurements were wrong, or that
the method may grant authority.

Two runs at implementation commit
`1921c1a525a8ae8625d3db0610b3734b584818b9` produced byte-identical scientific
JSON. The second run used a detached worktree.

