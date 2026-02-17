from paperta.contracts import SectionInput
from paperta.pipeline import run_phase2_teach_pipeline


def test_phase2_pipeline_returns_grounded_teach_artifact():
    result = run_phase2_teach_pipeline(
        paper_id="teach-int-1",
        sections=(
            SectionInput(label="Intro", text="A transformer model uses self-attention."),
            SectionInput(label="Method", text="The training objective minimizes cross entropy loss."),
        ),
        objective="teach transformer attention objective",
        mode="teach",
        top_k=3,
    )
    assert result.mode == "teach"
    assert result.retrieved_chunk_ids
    assert result.concept_count >= 1
    assert result.quiz_item_count >= 1
    assert all(item.chunk_ids for item in result.prerequisites.items if item.concept != "Not stated in the paper.")
