# Multi-agent LLM echo — labels

Exact parentage is known only for explicit copy/mutation operations performed by
the generator. Shared retrieval is a declared dependency, not necessarily a
copy. Disjoint retrieval is a designed separation, not proof of statistical or
causal independence between pretrained models. Labels therefore distinguish
`direct_parent`, `record_root`, and `evidence_independence` scope.

For LIR-1E, separate supplied source packets are distinct constructed record
roots. They are not claimed to represent independent physical observations or
independent model pretraining. Two answers generated from identical source
bytes share a constructed evidence root but have no direct parent edge between
them. Only the local copy and mutation operations assert exact direct parents.
