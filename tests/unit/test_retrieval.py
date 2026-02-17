from paperta.contracts import SectionInput
from paperta.ingestion import ingest_document
from paperta.retrieval import retrieve


def test_retrieval_orders_by_overlap_score():
    paper = ingest_document(
        paper_id="p2",
        sections=(
            SectionInput(label="A", text="transformer attention attention"),
            SectionInput(label="B", text="transformer"),
        ),
    )
    result = retrieve(query="transformer attention", ingested_paper=paper, top_k=2)
    assert len(result.hits) == 2
    assert result.hits[0].score >= result.hits[1].score
