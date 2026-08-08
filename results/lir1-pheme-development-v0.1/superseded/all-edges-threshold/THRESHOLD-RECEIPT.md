# PHEME development threshold receipt

The registered grid was evaluated on the 70 development cases (1,083 claims)
only. Confirmatory cases were not scored.

The frozen selection rule chose threshold **0.80**, with exact-parent F1
`0.7557436518` at 40% hidden edges. At the same threshold, root-pair precision
was `1.0`, recall was `0.1692675703`, F1 was `0.2895275207`, and mean absolute
root-count error was `5.3142857143` roots per case.

That divergence is not hidden: exact immediate-parent recovery and root-family
recovery are different targets. The confirmatory run will use 0.80 without
change and report both.
