"""Phase 1 runtime contracts for deterministic ingestion and grounded summary."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SectionInput:
    """Input section payload."""

    label: str
    text: str


@dataclass(frozen=True)
class Chunk:
    """Deterministic paragraph chunk."""

    chunk_id: str
    paper_id: str
    section: str
    text: str


@dataclass(frozen=True)
class IngestedPaper:
    """Ingestion output artifact."""

    paper_id: str
    chunks: tuple[Chunk, ...]
    section_order: tuple[str, ...]


@dataclass(frozen=True)
class RetrievalHit:
    """Single lexical retrieval hit."""

    chunk_id: str
    section: str
    score: int
    text: str


@dataclass(frozen=True)
class RetrievalResult:
    """Retrieval output."""

    query: str
    hits: tuple[RetrievalHit, ...]


@dataclass(frozen=True)
class SummaryBullet:
    """Grounded summary bullet with citations."""

    text: str
    chunk_ids: tuple[str, ...]


@dataclass(frozen=True)
class GroundedSummary:
    """Summary artifact."""

    mode: str
    bullets: tuple[SummaryBullet, ...]


@dataclass(frozen=True)
class PipelineResult:
    """End-to-end phase 1 result with observability metadata."""

    paper_id: str
    mode: str
    retrieval_trace: RetrievalResult
    retrieved_chunk_ids: tuple[str, ...]
    summary: GroundedSummary
    summary_bullet_count: int
    unsupported_bullet_count: int
