import pytest

from paperta.contracts import RetrievalResult, SectionInput
from paperta.multi_paper import build_consensus_matrix
from paperta.multi_paper_contracts import PaperInput, PerPaperRetrieval
from paperta.pipeline import run_phase4_multi_paper_pipeline


def test_phase4_pipeline_rejects_empty_paper_set():
    with pytest.raises(ValueError):
        run_phase4_multi_paper_pipeline(
            papers=tuple(),
            query="anything",
            mode="multi_paper",
            top_k=1,
        )


def test_consensus_returns_insufficient_when_no_evidence():
    results = (
        PerPaperRetrieval(
            paper_id="mp-none",
            retrieval_trace=RetrievalResult(query="q", hits=tuple()),
            retrieved_chunk_ids=tuple(),
        ),
    )
    consensus = build_consensus_matrix(results)
    assert consensus.rows[0].label == "insufficient evidence"


def test_phase4_pipeline_rejects_empty_query():
    with pytest.raises(ValueError):
        run_phase4_multi_paper_pipeline(
            papers=(
                PaperInput(
                    paper_id="mp-neg-query",
                    sections=(SectionInput(label="Intro", text="content"),),
                ),
            ),
            query="  ",
            mode="multi_paper",
            top_k=1,
        )


def test_phase4_pipeline_rejects_non_positive_top_k():
    with pytest.raises(ValueError):
        run_phase4_multi_paper_pipeline(
            papers=(
                PaperInput(
                    paper_id="mp-neg-topk",
                    sections=(SectionInput(label="Intro", text="content"),),
                ),
            ),
            query="content",
            mode="multi_paper",
            top_k=0,
        )


def test_phase4_pipeline_rejects_invalid_mode():
    with pytest.raises(ValueError):
        run_phase4_multi_paper_pipeline(
            papers=(
                PaperInput(
                    paper_id="mp-neg-mode",
                    sections=(SectionInput(label="Intro", text="content"),),
                ),
            ),
            query="content",
            mode="reviewer",
            top_k=1,
        )
