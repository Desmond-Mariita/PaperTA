import pytest

from paperta.contracts import RetrievalHit, RetrievalResult, SectionInput
from paperta.ingestion import ingest_document
from paperta.summary import generate_summary


def test_summary_bullets_include_citations():
    ingested = ingest_document(
        paper_id="sum-unit-1",
        sections=(SectionInput(label="Intro", text="Important finding."),),
    )
    chunk_id = ingested.chunks[0].chunk_id
    retrieval = RetrievalResult(
        query="q",
        hits=(RetrievalHit(chunk_id=chunk_id, section="Intro", score=2, text="Important finding."),),
    )
    summary = generate_summary(ingested_paper=ingested, retrieval_result=retrieval, mode="summary")
    assert summary.bullets
    assert summary.bullets[0].chunk_ids == (chunk_id,)


def test_summary_rejects_unknown_chunk_ids():
    ingested = ingest_document(
        paper_id="sum-unit-2",
        sections=(SectionInput(label="Intro", text="Known text."),),
    )
    retrieval = RetrievalResult(
        query="q",
        hits=(RetrievalHit(chunk_id="deadbeefdeadbeef", section="Intro", score=1, text="Known text."),),
    )
    with pytest.raises(ValueError):
        generate_summary(ingested_paper=ingested, retrieval_result=retrieval, mode="summary")
