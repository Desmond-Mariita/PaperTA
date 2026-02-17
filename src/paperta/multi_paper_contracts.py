"""Phase 4 runtime contracts for deterministic multi-paper artifacts."""

from __future__ import annotations

from dataclasses import dataclass

from paperta.contracts import RetrievalResult, SectionInput


@dataclass(frozen=True)
class PaperInput:
    """Single paper payload for multi-paper workflows."""

    paper_id: str
    sections: tuple[SectionInput, ...]


@dataclass(frozen=True)
class PerPaperRetrieval:
    """Per-paper retrieval trace bundle."""

    paper_id: str
    retrieval_trace: RetrievalResult
    retrieved_chunk_ids: tuple[str, ...]


@dataclass(frozen=True)
class LocalConcept:
    """Local concept mapped to canonical global concept ID."""

    paper_id: str
    local_name: str
    global_concept_id: str
    chunk_ids: tuple[str, ...]


@dataclass(frozen=True)
class ConceptLinkResult:
    """Cross-paper concept-linking result."""

    concepts: tuple[LocalConcept, ...]


@dataclass(frozen=True)
class ConsensusRow:
    """Single consensus row across papers."""

    claim: str
    label: str
    paper_ids: tuple[str, ...]
    evidence_chunk_ids: tuple[str, ...]
    notes: str


@dataclass(frozen=True)
class ConsensusMatrix:
    """Cross-paper consensus matrix."""

    rows: tuple[ConsensusRow, ...]


@dataclass(frozen=True)
class GraphEdge:
    """Cross-paper graph edge."""

    source: str
    target: str
    relation: str
    evidence_chunk_ids: tuple[str, ...]


@dataclass(frozen=True)
class CrossPaperGraph:
    """Cross-paper graph artifact."""

    edges: tuple[GraphEdge, ...]


@dataclass(frozen=True)
class MultiPaperPipelineResult:
    """End-to-end phase 4 result with observability metadata."""

    mode: str
    paper_count: int
    per_paper_retrieval: tuple[PerPaperRetrieval, ...]
    concept_links: ConceptLinkResult
    consensus: ConsensusMatrix
    graph: CrossPaperGraph
    consensus_claim_count: int
    graph_edge_count: int
    unsupported_entry_count: int
