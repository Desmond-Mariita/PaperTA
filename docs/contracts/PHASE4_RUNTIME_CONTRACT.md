# PHASE4 Runtime Contract

## Scope

Phase 4 delivers deterministic multi-paper intelligence artifacts on top of per-paper ingestion/retrieval.

## Functional Requirements

1. Multi-paper pipeline accepts a non-empty set of paper inputs and a cross-paper query.
2. Concept linker emits local concept entries with canonical global concept IDs.
3. Consensus output labels claims as one of: `supporting`, `contradicting`, `mixed`, `insufficient evidence`.
4. Cross-paper graph includes paper-concept and paper-paper relationship edges with evidence anchors.
5. Unsupported outputs use exact text `Not stated in the paper.` when evidence is missing.
6. Mode is constrained to `multi_paper`.

## Non-Functional Requirements

1. Determinism: identical paper set/query produces identical outputs.
2. Groundedness: all non-fallback entries include citation chunk IDs.
3. Auditability: result includes per-paper retrieval traces and aggregate counters.
4. Known limitation: contradiction detection is heuristic and may over-trigger on lexical negation terms (`no`, `not`).

## Interfaces

1. `run_phase4_multi_paper_pipeline(papers, query, mode="multi_paper", top_k) -> MultiPaperPipelineResult`
2. `link_concepts(paper_results) -> ConceptLinkResult`
3. `build_consensus_matrix(paper_results) -> ConsensusMatrix`
4. `build_cross_paper_graph(paper_results, concept_links) -> CrossPaperGraph`

## Invariants

1. Every non-fallback evidence reference maps to ingested chunk IDs from one of the input papers.
2. Consensus labels are restricted to declared enum values.
3. Fallback text is exact: `Not stated in the paper.`.

## Failure Modes

1. Empty paper set -> `ValueError`.
2. Empty query -> `ValueError`.
3. `top_k <= 0` -> `ValueError`.
4. Invalid mode (not `multi_paper`) -> `ValueError`.
5. Empty retrieval across all papers -> artifacts degrade gracefully with fallback entries.

## Observability

1. Multi-paper result includes:
- `mode`
- `paper_count`
- `per_paper_retrieval`
- `consensus_claim_count`
- `graph_edge_count`
- `unsupported_entry_count`

## Acceptance Gates

1. Unit + integration + negative tests pass.
2. Checklist verifies required files and tests.
3. Internal/external reviews complete with phase gate pass.
