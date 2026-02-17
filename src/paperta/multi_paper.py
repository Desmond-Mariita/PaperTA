"""Phase 4 multi-paper intelligence runtime implementation."""

from __future__ import annotations

import re
from typing import Sequence

from paperta.ingestion import ingest_document
from paperta.multi_paper_contracts import (
    ConceptLinkResult,
    ConsensusMatrix,
    ConsensusRow,
    CrossPaperGraph,
    GraphEdge,
    LocalConcept,
    MultiPaperPipelineResult,
    PaperInput,
    PerPaperRetrieval,
)
from paperta.retrieval import retrieve


NOT_STATED = "Not stated in the paper."
_TOKEN_RE = re.compile(r"[a-z0-9]+")
_VALID_LABELS = {"supporting", "contradicting", "mixed", "insufficient evidence"}


def _tokenize(text: str) -> tuple[str, ...]:
    """Tokenize text into deterministic lowercase alphanumeric terms.

    Args:
        text: Input text.

    Returns:
        Ordered tuple of tokens.
    """
    return tuple(_TOKEN_RE.findall(text.lower()))


def _concept_id(name: str) -> str:
    """Build deterministic global concept ID from concept text.

    Args:
        name: Local concept name.

    Returns:
        Canonical global concept ID.
    """
    tokens = _tokenize(name)
    stem = "_".join(tokens[:3]) if tokens else "unknown"
    return f"g_{stem}"


def link_concepts(paper_results: Sequence[PerPaperRetrieval]) -> ConceptLinkResult:
    """Link local concepts from each paper to canonical concept IDs.

    Args:
        paper_results: Per-paper retrieval bundles.

    Returns:
        Concept link result with evidence anchors.
    """
    concepts: list[LocalConcept] = []
    for result in paper_results:
        if not result.retrieval_trace.hits:
            concepts.append(
                LocalConcept(
                    paper_id=result.paper_id,
                    local_name=NOT_STATED,
                    global_concept_id=_concept_id(NOT_STATED),
                    chunk_ids=tuple(),
                )
            )
            continue
        hit = result.retrieval_trace.hits[0]
        local_name = f"{hit.section} concept"
        concepts.append(
            LocalConcept(
                paper_id=result.paper_id,
                local_name=local_name,
                global_concept_id=_concept_id(local_name),
                chunk_ids=(hit.chunk_id,),
            )
        )
    return ConceptLinkResult(concepts=tuple(concepts))


def build_consensus_matrix(paper_results: Sequence[PerPaperRetrieval]) -> ConsensusMatrix:
    """Build cross-paper consensus matrix with deterministic labels.

    Args:
        paper_results: Per-paper retrieval bundles.

    Returns:
        Consensus matrix artifact.

    Raises:
        ValueError: If generated consensus labels are outside the declared enum.
    """
    all_hits = [hit for result in paper_results for hit in result.retrieval_trace.hits]
    if not all_hits:
        row = ConsensusRow(
            claim=NOT_STATED,
            label="insufficient evidence",
            paper_ids=tuple(result.paper_id for result in paper_results),
            evidence_chunk_ids=tuple(),
            notes=NOT_STATED,
        )
        return ConsensusMatrix(rows=(row,))

    scores = [hit.score for hit in all_hits]
    labels = []
    texts = " ".join(hit.text.lower() for hit in all_hits)
    # Conservative contradiction heuristic: lexical negation tokens may cause false positives.
    if " no " in f" {texts} " or " not " in f" {texts} ":
        labels.append("contradicting")
    if any(score >= 2 for score in scores):
        labels.append("supporting")
    if not labels:
        labels.append("mixed")
    label = "mixed" if len(labels) > 1 else labels[0]
    if label not in _VALID_LABELS:
        raise ValueError("invalid consensus label")

    row = ConsensusRow(
        claim="Cross-paper consensus claim",
        label=label,
        paper_ids=tuple(result.paper_id for result in paper_results),
        evidence_chunk_ids=tuple(hit.chunk_id for hit in all_hits[:4]),
        notes=f"Computed from {len(all_hits)} retrieval hits.",
    )
    return ConsensusMatrix(rows=(row,))


def build_cross_paper_graph(
    paper_results: Sequence[PerPaperRetrieval], concept_links: ConceptLinkResult
) -> CrossPaperGraph:
    """Build deterministic cross-paper graph edges.

    Args:
        paper_results: Per-paper retrieval bundles.
        concept_links: Canonical concept-link output.

    Returns:
        Cross-paper graph artifact.
    """
    edges: list[GraphEdge] = []
    link_by_paper = {link.paper_id: link for link in concept_links.concepts}

    for result in paper_results:
        link = link_by_paper[result.paper_id]
        edges.append(
            GraphEdge(
                source=result.paper_id,
                target=link.global_concept_id,
                relation="mentions",
                evidence_chunk_ids=link.chunk_ids,
            )
        )

    for left, right in zip(paper_results, paper_results[1:]):
        left_link = link_by_paper[left.paper_id]
        right_link = link_by_paper[right.paper_id]
        if left_link.global_concept_id == right_link.global_concept_id:
            evidence = tuple(dict.fromkeys(left_link.chunk_ids + right_link.chunk_ids))
            edges.append(
                GraphEdge(
                    source=left.paper_id,
                    target=right.paper_id,
                    relation="shares_concept",
                    evidence_chunk_ids=evidence,
                )
            )
    return CrossPaperGraph(edges=tuple(edges))


def run_phase4_multi_paper_pipeline(
    papers: Sequence[PaperInput],
    query: str,
    mode: str = "multi_paper",
    top_k: int = 5,
) -> MultiPaperPipelineResult:
    """Execute deterministic multi-paper pipeline with aggregate observability.

    Args:
        papers: Non-empty paper payload list.
        query: Cross-paper query.
        mode: Pipeline mode. Phase 4 supports only `multi_paper`.
        top_k: Per-paper retrieval hit limit.

    Returns:
        End-to-end multi-paper artifact bundle.

    Raises:
        ValueError: If mode/query/top_k/paper set are invalid.
    """
    if mode != "multi_paper":
        raise ValueError("invalid mode")
    if not papers:
        raise ValueError("papers must be non-empty")
    if not query.strip():
        raise ValueError("query must be non-empty")
    if top_k <= 0:
        raise ValueError("top_k must be > 0")

    per_paper: list[PerPaperRetrieval] = []
    for paper in papers:
        ingested = ingest_document(paper_id=paper.paper_id, sections=paper.sections)
        retrieval_result = retrieve(query=query, ingested_paper=ingested, top_k=top_k)
        per_paper.append(
            PerPaperRetrieval(
                paper_id=paper.paper_id,
                retrieval_trace=retrieval_result,
                retrieved_chunk_ids=tuple(hit.chunk_id for hit in retrieval_result.hits),
            )
        )

    concept_links = link_concepts(per_paper)
    consensus = build_consensus_matrix(per_paper)
    graph = build_cross_paper_graph(per_paper, concept_links)

    unsupported_entries = 0
    unsupported_entries += sum(1 for row in consensus.rows if row.label == "insufficient evidence")
    unsupported_entries += sum(1 for link in concept_links.concepts if link.local_name == NOT_STATED)

    return MultiPaperPipelineResult(
        mode=mode,
        paper_count=len(papers),
        per_paper_retrieval=tuple(per_paper),
        concept_links=concept_links,
        consensus=consensus,
        graph=graph,
        consensus_claim_count=len(consensus.rows),
        graph_edge_count=len(graph.edges),
        unsupported_entry_count=unsupported_entries,
    )
