from paperta.contracts import SectionInput
from paperta.pipeline import run_phase3_reviewer_pipeline


def test_phase3_pipeline_returns_grounded_reviewer_artifact():
    result = run_phase3_reviewer_pipeline(
        paper_id="rev-int-1",
        sections=(
            SectionInput(label="Intro", text="We evaluate robustness under distribution shift."),
            SectionInput(label="Method", text="The method uses stratified sampling and ablation."),
            SectionInput(label="Results", text="Results show improved F1 across datasets."),
        ),
        review_query="evaluate robustness reproducibility",
        mode="reviewer",
        top_k=4,
    )
    assert result.mode == "reviewer"
    assert result.retrieved_chunk_ids
    assert result.claim_count >= 1
    assert result.reproducibility_item_count >= 1
    assert all(
        row.evidence_chunk_ids for row in result.claim_matrix.rows if row.claim != "Not stated in the paper."
    )
