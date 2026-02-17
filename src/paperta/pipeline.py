"""Phase 1 end-to-end orchestration."""

from __future__ import annotations

from typing import Sequence

from paperta.contracts import PipelineResult, SectionInput
from paperta.ingestion import ingest_document
from paperta.retrieval import retrieve
from paperta.summary import NOT_STATED, generate_summary


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
