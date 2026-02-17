"""Phase 3 runtime contracts for deterministic Reviewer Mode artifacts."""

from __future__ import annotations

from dataclasses import dataclass

from paperta.contracts import RetrievalResult


@dataclass(frozen=True)
class EvidenceStatement:
    """Reviewer statement with evidence anchors."""

    text: str
    chunk_ids: tuple[str, ...]


@dataclass(frozen=True)
class CritiqueArtifact:
    """Reviewer critique sections."""

    strengths: tuple[EvidenceStatement, ...]
    weaknesses: tuple[EvidenceStatement, ...]
    threats_to_validity: tuple[EvidenceStatement, ...]


@dataclass(frozen=True)
class ReproducibilityItem:
    """Single reproducibility checklist item."""

    label: str
    status: str
    notes: str
    chunk_ids: tuple[str, ...]


@dataclass(frozen=True)
class ReproducibilityChecklist:
    """Reproducibility checklist artifact."""

    items: tuple[ReproducibilityItem, ...]


@dataclass(frozen=True)
class ClaimEvidenceRow:
    """Single claim-evidence matrix row."""

    claim: str
    evidence_chunk_ids: tuple[str, ...]
    support_grade: str
    notes: str


@dataclass(frozen=True)
class ClaimEvidenceMatrix:
    """Reviewer claim-evidence matrix."""

    rows: tuple[ClaimEvidenceRow, ...]


@dataclass(frozen=True)
class ReviewerPipelineResult:
    """End-to-end phase 3 result with observability metadata."""

    paper_id: str
    mode: str
    retrieval_trace: RetrievalResult
    retrieved_chunk_ids: tuple[str, ...]
    critique: CritiqueArtifact
    reproducibility: ReproducibilityChecklist
    claim_matrix: ClaimEvidenceMatrix
    claim_count: int
    unsupported_claim_count: int
    reproducibility_item_count: int
