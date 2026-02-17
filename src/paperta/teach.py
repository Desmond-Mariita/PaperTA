"""Phase 2 Teach Mode runtime implementation."""

from __future__ import annotations

import re
from typing import Sequence

from paperta.contracts import IngestedPaper, RetrievalResult, SectionInput
from paperta.ingestion import ingest_document
from paperta.retrieval import retrieve
from paperta.teach_contracts import (
    ConceptEdge,
    ConceptMap,
    ConceptNode,
    Explanation,
    ExplanationStep,
    MCQItem,
    PrerequisiteChecklist,
    PrerequisiteItem,
    Quiz,
    ShortAnswerItem,
    SocraticAnswer,
    TeachPipelineResult,
)


NOT_STATED = "Not stated in the paper."
_TOKEN_RE = re.compile(r"[a-z0-9]+")
_STOPWORDS = {
    "a",
    "an",
    "about",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "does",
    "for",
    "from",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "paper",
    "say",
    "the",
    "this",
    "to",
    "what",
}


def _snippet(text: str, max_len: int = 96) -> str:
    """Render bounded-length snippet for deterministic text fields.

    Args:
        text: Source text.
        max_len: Maximum snippet length.

    Returns:
        Snippet with ellipsis when truncated.
    """
    if len(text) <= max_len:
        return text
    return text[: max_len - 3].rstrip() + "..."


def _tokenize(text: str) -> set[str]:
    """Tokenize text into lowercase alphanumeric terms.

    Args:
        text: Input text.

    Returns:
        Set of unique tokens.
    """
    return set(_TOKEN_RE.findall(text.lower()))


def _validate_retrieval_hits(ingested_paper: IngestedPaper, retrieval_result: RetrievalResult) -> None:
    """Validate that retrieval hits reference known ingested chunk IDs.

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


def generate_prerequisites(retrieval_result: RetrievalResult) -> PrerequisiteChecklist:
    """Generate prerequisite checklist from retrieved evidence.

    Args:
        retrieval_result: Ranked retrieval hits.

    Returns:
        Prerequisite checklist with evidence anchors.
    """
    if not retrieval_result.hits:
        return PrerequisiteChecklist(
            items=(PrerequisiteItem(concept=NOT_STATED, reason=NOT_STATED, chunk_ids=tuple()),)
        )

    items: list[PrerequisiteItem] = []
    for idx, hit in enumerate(retrieval_result.hits[:3], start=1):
        items.append(
            PrerequisiteItem(
                concept=f"{hit.section} prerequisite {idx}",
                reason=f"Grounded in retrieved evidence: {_snippet(hit.text, max_len=72)}",
                chunk_ids=(hit.chunk_id,),
            )
        )
    return PrerequisiteChecklist(items=tuple(items))


def generate_concept_map(retrieval_result: RetrievalResult) -> ConceptMap:
    """Generate concept map nodes and edges from retrieval hits.

    Args:
        retrieval_result: Ranked retrieval hits.

    Returns:
        Evidence-anchored concept map.
    """
    if not retrieval_result.hits:
        return ConceptMap(nodes=(ConceptNode(label=NOT_STATED, chunk_ids=tuple()),), edges=tuple())

    nodes: list[ConceptNode] = []
    for idx, hit in enumerate(retrieval_result.hits[:4], start=1):
        nodes.append(
            ConceptNode(
                label=f"{hit.section} concept {idx}",
                chunk_ids=(hit.chunk_id,),
            )
        )

    edges: list[ConceptEdge] = []
    for left, right in zip(nodes, nodes[1:]):
        edges.append(
            ConceptEdge(
                source=left.label,
                target=right.label,
                relation="builds_on",
                chunk_ids=(left.chunk_ids[0], right.chunk_ids[0]),
            )
        )
    return ConceptMap(nodes=tuple(nodes), edges=tuple(edges))


def generate_explanation(retrieval_result: RetrievalResult) -> Explanation:
    """Generate ordered explanation steps from retrieval hits.

    Args:
        retrieval_result: Ranked retrieval hits.

    Returns:
        Step-by-step explanation with evidence anchors.
    """
    if not retrieval_result.hits:
        return Explanation(steps=(ExplanationStep(text=NOT_STATED, chunk_ids=tuple()),))

    steps: list[ExplanationStep] = []
    for idx, hit in enumerate(retrieval_result.hits[:4], start=1):
        steps.append(
            ExplanationStep(
                text=f"Step {idx}: In {hit.section}, {_snippet(hit.text)}",
                chunk_ids=(hit.chunk_id,),
            )
        )
    return Explanation(steps=tuple(steps))


def generate_quiz(retrieval_result: RetrievalResult) -> Quiz:
    """Generate deterministic MCQ and short-answer quiz items.

    Args:
        retrieval_result: Ranked retrieval hits.

    Returns:
        Quiz artifact with answer keys and evidence anchors.
    """
    if not retrieval_result.hits:
        return Quiz(
            mcq_items=tuple(),
            short_answer_items=(
                ShortAnswerItem(
                    prompt="What does the paper state about the objective?",
                    answer_key=NOT_STATED,
                    chunk_ids=tuple(),
                ),
            ),
        )

    first_hit = retrieval_result.hits[0]
    section_names = tuple(dict.fromkeys(hit.section for hit in retrieval_result.hits))
    distractors = tuple(name for name in section_names if name != first_hit.section)
    options = (first_hit.section,) + distractors[:2] + (NOT_STATED,)

    mcq = MCQItem(
        prompt=f"Which section most directly supports: {_snippet(first_hit.text, max_len=48)}?",
        options=options,
        answer_key=first_hit.section,
        chunk_ids=(first_hit.chunk_id,),
    )
    short = ShortAnswerItem(
        prompt="Give one grounded teaching point from the paper.",
        answer_key=f"{first_hit.section}: {_snippet(first_hit.text, max_len=72)}",
        chunk_ids=(first_hit.chunk_id,),
    )
    return Quiz(mcq_items=(mcq,), short_answer_items=(short,))


def answer_socratic_question(
    ingested_paper: IngestedPaper, question: str, retrieval_result: RetrievalResult
) -> SocraticAnswer:
    """Answer a follow-up question constrained to retrieval context.

    Args:
        ingested_paper: Ingested paper corpus.
        question: Follow-up learner question.
        retrieval_result: Ranked retrieval hits used as answer context.

    Returns:
        Grounded Socratic response or `Not stated in the paper.` when unsupported.
    """
    if not question.strip():
        return SocraticAnswer(text=NOT_STATED, chunk_ids=tuple())

    _validate_retrieval_hits(ingested_paper, retrieval_result)
    q_tokens = {token for token in _tokenize(question) if token not in _STOPWORDS}
    if not q_tokens:
        return SocraticAnswer(text=NOT_STATED, chunk_ids=tuple())
    for hit in retrieval_result.hits:
        hit_tokens = {token for token in _tokenize(hit.text) if token not in _STOPWORDS}
        if q_tokens.intersection(hit_tokens):
            return SocraticAnswer(
                text=f"{hit.section}: {_snippet(hit.text)}",
                chunk_ids=(hit.chunk_id,),
            )
    return SocraticAnswer(text=NOT_STATED, chunk_ids=tuple())


def run_phase2_teach_pipeline(
    paper_id: str,
    sections: Sequence[SectionInput],
    objective: str,
    mode: str = "teach",
    top_k: int = 5,
) -> TeachPipelineResult:
    """Execute deterministic Teach Mode pipeline with observability metadata.

    Args:
        paper_id: Paper identifier.
        sections: Ordered section inputs.
        objective: Learning objective query.
        mode: Pipeline mode. Phase 2 supports only `teach`.
        top_k: Retrieval hit limit.

    Returns:
        End-to-end Teach Mode artifact bundle.

    Raises:
        ValueError: If mode/objective/top_k are invalid or retrieval references unknown chunks.
    """
    if mode != "teach":
        raise ValueError("invalid mode")
    if not objective.strip():
        raise ValueError("objective must be non-empty")
    if top_k <= 0:
        raise ValueError("top_k must be > 0")

    ingested = ingest_document(paper_id=paper_id, sections=sections)
    retrieval_result = retrieve(query=objective, ingested_paper=ingested, top_k=top_k)
    _validate_retrieval_hits(ingested, retrieval_result)

    prerequisites = generate_prerequisites(retrieval_result)
    concept_map = generate_concept_map(retrieval_result)
    explanation = generate_explanation(retrieval_result)
    quiz = generate_quiz(retrieval_result)
    socratic = answer_socratic_question(
        ingested_paper=ingested,
        question=objective,
        retrieval_result=retrieval_result,
    )

    retrieved_chunk_ids = tuple(hit.chunk_id for hit in retrieval_result.hits)
    unsupported_count = 0
    unsupported_count += sum(1 for item in prerequisites.items if item.reason == NOT_STATED)
    unsupported_count += sum(1 for step in explanation.steps if step.text == NOT_STATED)
    unsupported_count += sum(1 for item in quiz.short_answer_items if item.answer_key == NOT_STATED)
    unsupported_count += 1 if socratic.text == NOT_STATED else 0

    concept_count = sum(1 for node in concept_map.nodes if node.label != NOT_STATED)
    quiz_item_count = len(quiz.mcq_items) + len(quiz.short_answer_items)

    return TeachPipelineResult(
        paper_id=paper_id,
        mode=mode,
        retrieval_trace=retrieval_result,
        retrieved_chunk_ids=retrieved_chunk_ids,
        prerequisites=prerequisites,
        concept_map=concept_map,
        explanation=explanation,
        quiz=quiz,
        socratic_answer=socratic,
        concept_count=concept_count,
        quiz_item_count=quiz_item_count,
        unsupported_response_count=unsupported_count,
    )
