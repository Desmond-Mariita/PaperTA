from paperta.contracts import RetrievalResult, SectionInput
from paperta.ingestion import ingest_document
from paperta.summary import NOT_STATED, generate_summary


def test_summary_returns_not_stated_when_no_evidence():
    ingested = ingest_document(
        paper_id="sum-neg-1",
        sections=(SectionInput(label="Body", text="Some text."),),
    )
    summary = generate_summary(
        ingested_paper=ingested,
        retrieval_result=RetrievalResult(query="x", hits=tuple()),
        mode="summary",
    )
    assert len(summary.bullets) == 1
    assert summary.bullets[0].text == NOT_STATED
    assert summary.bullets[0].chunk_ids == tuple()
