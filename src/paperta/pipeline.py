"""End-to-end pipeline orchestration across phases."""

from __future__ import annotations

from typing import Sequence

from paperta.contracts import PipelineResult, SectionInput
from paperta.ingestion import ingest_document
from paperta.retrieval import retrieve
from paperta.summary import NOT_STATED, generate_summary
from paperta.multi_paper import run_phase4_multi_paper_pipeline as _run_phase4_multi_paper_pipeline
from paperta.multi_paper_contracts import MultiPaperPipelineResult, PaperInput
from paperta.reviewer import run_phase3_reviewer_pipeline as _run_phase3_reviewer_pipeline
from paperta.reviewer_contracts import ReviewerPipelineResult
from paperta.teach import run_phase2_teach_pipeline as _run_phase2_teach_pipeline
from paperta.teach_contracts import TeachPipelineResult


def run_phase1_pipeline(
    paper_id: str,
    sections: Sequence[SectionInput],
    query: str,
    mode: str = "summary",
    top_k: int = 5,
) -> PipelineResult:
    """Execute deterministic ingestion, retrieval, and grounded summary.

    Args:
        paper_id: Paper identifier.
        sections: Ordered section inputs.
        query: User query.
        mode: Pipeline mode. Phase 1 supports only `summary`.
        top_k: Retrieval result count limit.

    Returns:
        End-to-end pipeline result with observability metadata.

    Raises:
        ValueError: If mode is invalid or upstream services reject inputs.
    """
    if mode != "summary":
        raise ValueError("invalid mode")

    ingested = ingest_document(paper_id=paper_id, sections=sections)
    retrieval_result = retrieve(query=query, ingested_paper=ingested, top_k=top_k)
    summary = generate_summary(ingested_paper=ingested, retrieval_result=retrieval_result, mode=mode)
    retrieved_chunk_ids = tuple(hit.chunk_id for hit in retrieval_result.hits)
    unsupported = sum(1 for b in summary.bullets if b.text == NOT_STATED)

    return PipelineResult(
        paper_id=paper_id,
        mode=mode,
        retrieval_trace=retrieval_result,
        retrieved_chunk_ids=retrieved_chunk_ids,
        summary=summary,
        summary_bullet_count=len(summary.bullets),
        unsupported_bullet_count=unsupported,
    )


def run_phase2_teach_pipeline(
    paper_id: str,
    sections: Sequence[SectionInput],
    objective: str,
    mode: str = "teach",
    top_k: int = 5,
) -> TeachPipelineResult:
    """Execute the Phase 2 Teach Mode pipeline.

    Args:
        paper_id: Paper identifier.
        sections: Ordered section inputs.
        objective: Learning objective query.
        mode: Pipeline mode. Phase 2 supports only `teach`.
        top_k: Retrieval result count limit.

    Returns:
        End-to-end Teach Mode pipeline result with observability metadata.

    Raises:
        ValueError: If mode/objective/top_k are invalid or ingestion/retrieval validation fails.
    """
    return _run_phase2_teach_pipeline(
        paper_id=paper_id,
        sections=sections,
        objective=objective,
        mode=mode,
        top_k=top_k,
    )


def run_phase3_reviewer_pipeline(
    paper_id: str,
    sections: Sequence[SectionInput],
    review_query: str,
    mode: str = "reviewer",
    top_k: int = 5,
) -> ReviewerPipelineResult:
    """Execute the Phase 3 Reviewer Mode pipeline.

    Args:
        paper_id: Paper identifier.
        sections: Ordered section inputs.
        review_query: Reviewer query objective.
        mode: Pipeline mode. Phase 3 supports only `reviewer`.
        top_k: Retrieval result count limit.

    Returns:
        End-to-end Reviewer Mode pipeline result with observability metadata.

    Raises:
        ValueError: If mode/review_query/top_k are invalid or ingestion/retrieval validation fails.
    """
    return _run_phase3_reviewer_pipeline(
        paper_id=paper_id,
        sections=sections,
        review_query=review_query,
        mode=mode,
        top_k=top_k,
    )


def run_phase4_multi_paper_pipeline(
    papers: Sequence[PaperInput],
    query: str,
    mode: str = "multi_paper",
    top_k: int = 5,
) -> MultiPaperPipelineResult:
    """Execute the Phase 4 multi-paper pipeline.

    Args:
        papers: Non-empty paper payload list.
        query: Cross-paper query.
        mode: Pipeline mode. Phase 4 supports only `multi_paper`.
        top_k: Retrieval result count limit per paper.

    Returns:
        End-to-end multi-paper pipeline result with observability metadata.

    Raises:
        ValueError: If mode/query/top_k/paper set are invalid or ingestion/retrieval validation fails.
    """
    return _run_phase4_multi_paper_pipeline(
        papers=papers,
        query=query,
        mode=mode,
        top_k=top_k,
    )
