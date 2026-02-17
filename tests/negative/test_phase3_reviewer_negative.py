import pytest

from paperta.contracts import RetrievalResult, SectionInput
from paperta.pipeline import run_phase3_reviewer_pipeline
from paperta.reviewer import NOT_STATED, generate_claim_evidence_matrix


def test_phase3_pipeline_rejects_empty_review_query():
    with pytest.raises(ValueError):
        run_phase3_reviewer_pipeline(
            paper_id="rev-neg-1",
            sections=(SectionInput(label="Intro", text="content"),),
            review_query="",
            mode="reviewer",
            top_k=1,
        )


def test_phase3_pipeline_rejects_non_positive_top_k():
    with pytest.raises(ValueError):
        run_phase3_reviewer_pipeline(
            paper_id="rev-neg-topk",
            sections=(SectionInput(label="Intro", text="content"),),
            review_query="content",
            mode="reviewer",
            top_k=0,
        )


def test_phase3_pipeline_rejects_invalid_mode():
    with pytest.raises(ValueError):
        run_phase3_reviewer_pipeline(
            paper_id="rev-neg-mode",
            sections=(SectionInput(label="Intro", text="content"),),
            review_query="content",
            mode="teach",
            top_k=1,
        )


def test_claim_matrix_returns_not_stated_when_no_evidence():
    matrix = generate_claim_evidence_matrix(retrieval_result=RetrievalResult(query="q", hits=tuple()))
    assert len(matrix.rows) == 1
    assert matrix.rows[0].claim == NOT_STATED
    assert matrix.rows[0].support_grade == "unsupported"
