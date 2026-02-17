from paperta.contracts import SectionInput
from paperta.ingestion import ingest_document


def test_chunking_assigns_stable_chunk_ids():
    sections = (
        SectionInput(label="Intro", text="A B C.\n\nD E."),
        SectionInput(label="Method", text="Token overlap retrieval."),
    )
    first = ingest_document(paper_id="p1", sections=sections)
    second = ingest_document(paper_id="p1", sections=sections)
    assert tuple(c.chunk_id for c in first.chunks) == tuple(c.chunk_id for c in second.chunks)
