"""Phase 2 runtime contracts for deterministic Teach Mode artifacts."""

from __future__ import annotations

from dataclasses import dataclass

from paperta.contracts import RetrievalResult


@dataclass(frozen=True)
class PrerequisiteItem:
    """Single prerequisite concept with evidence."""

    concept: str
    reason: str
    chunk_ids: tuple[str, ...]


@dataclass(frozen=True)
class PrerequisiteChecklist:
    """Prerequisite checklist artifact."""

    items: tuple[PrerequisiteItem, ...]


@dataclass(frozen=True)
class ConceptNode:
    """Evidence-anchored concept node."""

    label: str
    chunk_ids: tuple[str, ...]


@dataclass(frozen=True)
class ConceptEdge:
    """Directed concept-map edge with evidence anchors."""

    source: str
    target: str
    relation: str
    chunk_ids: tuple[str, ...]


@dataclass(frozen=True)
class ConceptMap:
    """Concept map artifact."""

    nodes: tuple[ConceptNode, ...]
    edges: tuple[ConceptEdge, ...]


@dataclass(frozen=True)
class ExplanationStep:
    """Single ordered explanation step."""

    text: str
    chunk_ids: tuple[str, ...]


@dataclass(frozen=True)
class Explanation:
    """Step-by-step explanation artifact."""

    steps: tuple[ExplanationStep, ...]


@dataclass(frozen=True)
class MCQItem:
    """Multiple-choice quiz item."""

    prompt: str
    options: tuple[str, ...]
    answer_key: str
    chunk_ids: tuple[str, ...]


@dataclass(frozen=True)
class ShortAnswerItem:
    """Short-answer quiz item."""

    prompt: str
    answer_key: str
    chunk_ids: tuple[str, ...]


@dataclass(frozen=True)
class Quiz:
    """Quiz artifact with MCQ and short-answer items."""

    mcq_items: tuple[MCQItem, ...]
    short_answer_items: tuple[ShortAnswerItem, ...]


@dataclass(frozen=True)
class SocraticAnswer:
    """Socratic response constrained to retrieved context."""

    text: str
    chunk_ids: tuple[str, ...]


@dataclass(frozen=True)
class TeachPipelineResult:
    """End-to-end phase 2 result with observability metadata."""

    paper_id: str
    mode: str
    retrieval_trace: RetrievalResult
    retrieved_chunk_ids: tuple[str, ...]
    prerequisites: PrerequisiteChecklist
    concept_map: ConceptMap
    explanation: Explanation
    quiz: Quiz
    socratic_answer: SocraticAnswer
    concept_count: int
    quiz_item_count: int
    unsupported_response_count: int
