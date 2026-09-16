/-
# AxiomAudit — the ledger's axiom claim, checked by the build

`formal/THEOREM-LEDGER.json` states that every compiled claim depends only on
`propext`, `Classical.choice` and `Quot.sound`. Until now that was a note
recording what someone ran once, on whatever toolchain they had. DR1-DR3 were
audited on 4.32.2 while the repository pinned 4.33.1, which is exactly the gap
that let a non-building proof sit in the ledger as `proved_compiled`.

`#guard_msgs` turns the claim into a build failure: if a proof gains an axiom,
or loses one, this file stops compiling on the pinned kernel. A ledger entry
that cannot be checked by the build is a note; this is the check.

Whitespace matching is lax because the axiom list wraps across lines once it is
long enough, and the wrapping is a pretty-printer detail rather than part of the
claim. The axiom names are matched exactly.

Only the DependenceRobustness claims are covered here. Extending it to the other
ledgered theorems is a mechanical follow-up.
-/
import MinorityProphetCore.DependenceRobustness

namespace MinorityProphetCore.AxiomAudit

/-- info: 'MinorityProphetCore.DependenceRobustness.reading_mem_reachable' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs (whitespace := lax) in
#print axioms MinorityProphetCore.DependenceRobustness.reading_mem_reachable

/-- info: 'MinorityProphetCore.DependenceRobustness.robust_settlement_is_true' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs (whitespace := lax) in
#print axioms MinorityProphetCore.DependenceRobustness.robust_settlement_is_true

/-- info: 'MinorityProphetCore.DependenceRobustness.no_record_rule_is_immune' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs (whitespace := lax) in
#print axioms MinorityProphetCore.DependenceRobustness.no_record_rule_is_immune

/-- info: 'MinorityProphetCore.DependenceRobustness.settle_corners' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs (whitespace := lax) in
#print axioms MinorityProphetCore.DependenceRobustness.settle_corners

/-- info: 'MinorityProphetCore.DependenceRobustness.fewest_le_sideRoots' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs (whitespace := lax) in
#print axioms MinorityProphetCore.DependenceRobustness.fewest_le_sideRoots

/-- info: 'MinorityProphetCore.DependenceRobustness.witness_merged_not_admissible' depends on axioms: [propext] -/
#guard_msgs (whitespace := lax) in
#print axioms MinorityProphetCore.DependenceRobustness.witness_merged_not_admissible

/-- info: 'MinorityProphetCore.DependenceRobustness.witness_distinct_admissible' does not depend on any axioms -/
#guard_msgs (whitespace := lax) in
#print axioms MinorityProphetCore.DependenceRobustness.witness_distinct_admissible

end MinorityProphetCore.AxiomAudit
