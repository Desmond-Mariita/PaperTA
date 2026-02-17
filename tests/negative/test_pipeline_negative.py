import pytest

from paperta.contracts import SectionInput
from paperta.pipeline import run_phase1_pipeline


def test_pipeline_rejects_empty_paper():
    with pytest.raises(ValueError):
        run_phase1_pipeline(
            paper_id="paper-neg-empty",
            sections=(SectionInput(label="Intro", text="   "),),
            query="token",
            mode="summary",
            top_k=1,
        )


def test_pipeline_rejects_empty_query():
    with pytest.raises(ValueError):
        run_phase1_pipeline(
            paper_id="paper-neg-query",
            sections=(SectionInput(label="Intro", text="content"),),
            query="",
            mode="summary",
            top_k=1,
        )


def test_pipeline_rejects_invalid_mode():
    with pytest.raises(ValueError):
        run_phase1_pipeline(
            paper_id="paper-neg-mode",
            sections=(SectionInput(label="Intro", text="content"),),
            query="content",
            mode="teach",
            top_k=1,
        )
