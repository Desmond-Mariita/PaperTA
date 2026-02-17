from paperta.contracts import SectionInput
from paperta.pipeline import run_phase1_pipeline


def test_phase1_pipeline_generates_grounded_summary():
    result = run_phase1_pipeline(
        paper_id="paper-int-1",
        sections=(
            SectionInput(label="Intro", text="We present a transformer model."),
            SectionInput(label="Method", text="The method uses attention layers."),
        ),
        query="transformer attention",
        mode="summary",
        top_k=3,
    )
    assert result.summary_bullet_count >= 1
    assert result.unsupported_bullet_count == 0
    assert all(b.chunk_ids for b in result.summary.bullets)


def test_pipeline_uses_ingestion_section_order():
    result = run_phase1_pipeline(
        paper_id="paper-int-2",
        sections=(
            SectionInput(label="Zeta", text="alpha"),
            SectionInput(label="Alpha", text="alpha"),
        ),
        query="alpha",
        mode="summary",
        top_k=2,
    )
    # Tie score should preserve ingestion section order.
    assert result.summary.bullets[0].text.startswith("Zeta:")


def test_pipeline_retrieval_trace_contains_chunk_ids():
    result = run_phase1_pipeline(
        paper_id="paper-int-3",
        sections=(SectionInput(label="Body", text="graph neural network"),),
        query="graph",
        mode="summary",
        top_k=1,
    )
    assert len(result.retrieved_chunk_ids) == 1
    assert len(result.retrieval_trace.hits) == 1
