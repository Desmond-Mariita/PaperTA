import pytest

from paperta.contracts import SectionInput
from paperta.ingestion import ingest_document


def test_ingestion_rejects_duplicate_sections():
    with pytest.raises(ValueError):
        ingest_document(
            paper_id="paper-neg-dup",
            sections=(
                SectionInput(label="Intro", text="a"),
                SectionInput(label="Intro", text="b"),
            ),
        )
