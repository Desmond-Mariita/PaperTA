from paperta.contracts import SectionInput
from paperta.multi_paper_contracts import PaperInput
from paperta.pipeline import run_phase4_multi_paper_pipeline


def test_phase4_pipeline_returns_grounded_multi_paper_artifact():
    result = run_phase4_multi_paper_pipeline(
        papers=(
            PaperInput(
                paper_id="mp-1",
                sections=(SectionInput(label="Intro", text="Transformers support sequence modeling."),),
            ),
            PaperInput(
                paper_id="mp-2",
                sections=(SectionInput(label="Results", text="Sequence models improve with attention."),),
            ),
        ),
        query="sequence attention",
        mode="multi_paper",
        top_k=3,
    )
    assert result.mode == "multi_paper"
    assert result.paper_count == 2
    assert result.consensus_claim_count >= 1
    assert result.graph_edge_count >= 1
    assert result.per_paper_retrieval[0].retrieved_chunk_ids
