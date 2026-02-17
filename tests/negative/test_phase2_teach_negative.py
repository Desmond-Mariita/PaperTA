import pytest

from paperta.contracts import SectionInput
from paperta.ingestion import ingest_document
from paperta.pipeline import run_phase2_teach_pipeline
from paperta.retrieval import retrieve
from paperta.teach import NOT_STATED, answer_socratic_question


def test_phase2_pipeline_rejects_empty_objective():
    with pytest.raises(ValueError):
        run_phase2_teach_pipeline(
            paper_id="teach-neg-1",
            sections=(SectionInput(label="Intro", text="content"),),
            objective="  ",
            mode="teach",
            top_k=1,
        )


def test_phase2_pipeline_rejects_non_positive_top_k():
    with pytest.raises(ValueError):
        run_phase2_teach_pipeline(
            paper_id="teach-neg-topk",
            sections=(SectionInput(label="Intro", text="content"),),
            objective="content",
            mode="teach",
            top_k=0,
        )


def test_phase2_pipeline_rejects_invalid_mode():
    with pytest.raises(ValueError):
        run_phase2_teach_pipeline(
            paper_id="teach-neg-mode",
            sections=(SectionInput(label="Intro", text="content"),),
            objective="content",
            mode="summary",
            top_k=1,
        )


def test_phase2_pipeline_rejects_empty_sections():
    with pytest.raises(ValueError):
        run_phase2_teach_pipeline(
            paper_id="teach-neg-sections",
            sections=tuple(),
            objective="anything",
            mode="teach",
            top_k=1,
        )


def test_socratic_returns_not_stated_when_unsupported():
    ingested = ingest_document(
        paper_id="teach-neg-2",
        sections=(SectionInput(label="Intro", text="This paper describes transformers."),),
    )
    retrieval = retrieve(query="transformers", ingested_paper=ingested, top_k=2)
    answer = answer_socratic_question(
        ingested_paper=ingested,
        question="What does the paper say about mitochondria?",
        retrieval_result=retrieval,
    )
    assert answer.text == NOT_STATED
    assert answer.chunk_ids == tuple()
