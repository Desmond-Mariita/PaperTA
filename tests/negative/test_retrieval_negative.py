import pytest

from paperta.contracts import SectionInput
from paperta.ingestion import ingest_document
from paperta.retrieval import retrieve


def test_retrieval_rejects_non_positive_top_k():
    paper = ingest_document(
        paper_id="paper-neg-topk",
        sections=(SectionInput(label="Body", text="token"),),
    )
    with pytest.raises(ValueError):
        retrieve(query="token", ingested_paper=paper, top_k=0)
