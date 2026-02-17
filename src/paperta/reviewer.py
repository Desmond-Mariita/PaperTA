"""Phase 3 Reviewer Mode runtime implementation."""

from __future__ import annotations

from typing import Sequence

from paperta.contracts import IngestedPaper, RetrievalResult, SectionInput
from paperta.ingestion import ingest_document
from paperta.retrieval import retrieve
from paperta.reviewer_contracts import (
    ClaimEvidenceMatrix,
    ClaimEvidenceRow,
    CritiqueArtifact,
    EvidenceStatement,
    ReproducibilityChecklist,
    ReproducibilityItem,
    ReviewerPipelineResult,
)


NOT_STATED = "Not stated in the paper."
_VALID_SUPPORT_GRADES = {"supported", "mixed", "unsupported"}


def _snippet(text: str, max_len: int = 96) -> str:
    """Render bounded-length snippet for deterministic reviewer text.

    Args:
        text: Source text.
        max_len: Maximum snippet length.

    Returns:
        Snippet with ellipsis when truncated.
    """
    if len(text) <= max_len:
        return text
    return text[: max_len - 3].rstrip() + "..."


def _validate_retrieval_hits(ingested_paper: IngestedPaper, retrieval_result: RetrievalResult) -> None:
    """Validate retrieval references against ingested chunk IDs.

    Args:
        ingested_paper: Ingested paper corpus.
        retrieval_result: Retrieval output.

    Raises:
        ValueError: If retrieval contains unknown chunk IDs.
    """
    valid_ids = {chunk.chunk_id for chunk in ingested_paper.chunks}
    for hit in retrieval_result.hits:
        if hit.chunk_id not in valid_ids:
            raise ValueError("retrieval hit references unknown chunk_id")


def generate_critique(retrieval_result: RetrievalResult) -> CritiqueArtifact:
    """Generate strengths/weaknesses/threats critique sections.

    Args:
        retrieval_result: Ranked retrieval hits.

    Returns:
        Critique artifact with evidence anchors or fallback entries.
    """
    if not retrieval_result.hits:
        fallback = (EvidenceStatement(text=NOT_STATED, chunk_ids=tuple()),)
        return CritiqueArtifact(
            strengths=fallback,
            weaknesses=fallback,
            threats_to_validity=fallback,
        )

    first = retrieval_result.hits[0]
    strengths = (
        EvidenceStatement(
            text=f"Strong evidence in {first.section}: {_snippet(first.text)}",
            chunk_ids=(first.chunk_id,),
        ),
    )

    weaknesses = tuple(
        EvidenceStatement(
            text=f"Potential weakness: limited scope in {hit.section}.",
            chunk_ids=(hit.chunk_id,),
        )
        for hit in retrieval_result.hits[1:2]
    ) or (EvidenceStatement(text=NOT_STATED, chunk_ids=tuple()),)

    threats = tuple(
        EvidenceStatement(
            text=f"Threat to validity: assumptions in {hit.section}.",
            chunk_ids=(hit.chunk_id,),
        )
        for hit in retrieval_result.hits[2:3]
    ) or (EvidenceStatement(text=NOT_STATED, chunk_ids=tuple()),)

    return CritiqueArtifact(
        strengths=strengths,
        weaknesses=weaknesses,
        threats_to_validity=threats,
    )


def generate_reproducibility_checklist(retrieval_result: RetrievalResult) -> ReproducibilityChecklist:
    """Generate reproducibility checklist with evidence-anchored statuses.

    Args:
        retrieval_result: Ranked retrieval hits.

    Returns:
        Reproducibility checklist artifact.
    """
    labels = ("data availability", "method detail", "evaluation detail")
    if not retrieval_result.hits:
        return ReproducibilityChecklist(
            items=tuple(
                ReproducibilityItem(
                    label=label,
                    status="not_stated",
                    notes=NOT_STATED,
                    chunk_ids=tuple(),
                )
                for label in labels
            )
        )

    items: list[ReproducibilityItem] = []
    for idx, label in enumerate(labels):
        if idx < len(retrieval_result.hits):
            hit = retrieval_result.hits[idx]
            items.append(
                ReproducibilityItem(
                    label=label,
                    status="pass" if hit.score >= 2 else "warning",
                    notes=f"{hit.section}: {_snippet(hit.text, max_len=72)}",
                    chunk_ids=(hit.chunk_id,),
                )
            )
        else:
            items.append(
                ReproducibilityItem(
                    label=label,
                    status="not_stated",
                    notes=NOT_STATED,
                    chunk_ids=tuple(),
                )
            )
    return ReproducibilityChecklist(items=tuple(items))


def generate_claim_evidence_matrix(retrieval_result: RetrievalResult) -> ClaimEvidenceMatrix:
    """Generate claim-evidence matrix with support grades.

    Args:
        retrieval_result: Ranked retrieval hits.

    Returns:
        Claim-evidence matrix artifact.

    Raises:
        ValueError: If an invalid support grade is produced.
    """
    if not retrieval_result.hits:
        return ClaimEvidenceMatrix(
            rows=(
                ClaimEvidenceRow(
                    claim=NOT_STATED,
                    evidence_chunk_ids=tuple(),
                    support_grade="unsupported",
                    notes=NOT_STATED,
                ),
            )
        )

    rows: list[ClaimEvidenceRow] = []
    for hit in retrieval_result.hits[:4]:
        grade = "supported" if hit.score >= 2 else "mixed"
        if grade not in _VALID_SUPPORT_GRADES:
            raise ValueError("invalid support grade")
        rows.append(
            ClaimEvidenceRow(
                claim=f"{hit.section} claim: {_snippet(hit.text, max_len=64)}",
                evidence_chunk_ids=(hit.chunk_id,),
                support_grade=grade,
                notes=f"Derived from {hit.section}.",
            )
        )
    return ClaimEvidenceMatrix(rows=tuple(rows))


def run_phase3_reviewer_pipeline(
    paper_id: str,
    sections: Sequence[SectionInput],
    review_query: str,
    mode: str = "reviewer",
    top_k: int = 5,
) -> ReviewerPipelineResult:
    """Execute deterministic Reviewer Mode pipeline.

    Args:
        paper_id: Paper identifier.
        sections: Ordered section inputs.
        review_query: Reviewer query objective.
        mode: Pipeline mode. Phase 3 supports only `reviewer`.
        top_k: Retrieval hit limit.

    Returns:
        End-to-end reviewer artifact bundle.

    Raises:
        ValueError: If mode/query/top_k are invalid or retrieval references unknown chunks.
    """
    if mode != "reviewer":
        raise ValueError("invalid mode")
    if not review_query.strip():
        raise ValueError("review_query must be non-empty")
    if top_k <= 0:
        raise ValueError("top_k must be > 0")

    ingested = ingest_document(paper_id=paper_id, sections=sections)
    retrieval_result = retrieve(query=review_query, ingested_paper=ingested, top_k=top_k)
    _validate_retrieval_hits(ingested, retrieval_result)

    critique = generate_critique(retrieval_result)
    reproducibility = generate_reproducibility_checklist(retrieval_result)
    claim_matrix = generate_claim_evidence_matrix(retrieval_result)

    retrieved_chunk_ids = tuple(hit.chunk_id for hit in retrieval_result.hits)
    unsupported_claim_count = sum(1 for row in claim_matrix.rows if row.support_grade == "unsupported")

    return ReviewerPipelineResult(
        paper_id=paper_id,
        mode=mode,
        retrieval_trace=retrieval_result,
        retrieved_chunk_ids=retrieved_chunk_ids,
        critique=critique,
        reproducibility=reproducibility,
        claim_matrix=claim_matrix,
        claim_count=len(claim_matrix.rows),
        unsupported_claim_count=unsupported_claim_count,
        reproducibility_item_count=len(reproducibility.items),
    )
