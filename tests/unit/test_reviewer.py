from paperta.contracts import RetrievalResult, SectionInput
from paperta.ingestion import ingest_document
from paperta.retrieval import retrieve
from paperta.reviewer import NOT_STATED, generate_claim_evidence_matrix, generate_critique, generate_reproducibility_checklist


def test_generate_claim_matrix_has_valid_support_grades():
    ingested = ingest_document(
        paper_id="rev-unit-1",
        sections=(
            SectionInput(label="Intro", text="The method improves precision and recall."),
            SectionInput(label="Results", text="Precision improves in ablation tests."),
        ),
    )
    retrieval = retrieve(query="precision recall", ingested_paper=ingested, top_k=3)
    matrix = generate_claim_evidence_matrix(retrieval_result=retrieval)
    assert matrix.rows
    assert all(row.support_grade in {"supported", "mixed", "unsupported"} for row in matrix.rows)
    assert all(row.evidence_chunk_ids for row in matrix.rows if row.claim != "Not stated in the paper.")


def test_generate_reproducibility_checklist_with_citations():
    ingested = ingest_document(
        paper_id="rev-unit-2",
        sections=(
            SectionInput(label="Method", text="Training data split and hyperparameters are reported."),
            SectionInput(label="Eval", text="Evaluation metrics include F1 and accuracy."),
        ),
    )
    retrieval = retrieve(query="data hyperparameters evaluation", ingested_paper=ingested, top_k=3)
    checklist = generate_reproducibility_checklist(retrieval_result=retrieval)
    assert checklist.items
    assert all(item.status in {"pass", "warning", "not_stated"} for item in checklist.items)
    assert any(item.chunk_ids for item in checklist.items)


def test_generate_critique_handles_evidence_and_fallback():
    ingested = ingest_document(
        paper_id="rev-unit-3",
        sections=(SectionInput(label="Intro", text="The method shows strong empirical results."),),
    )
    retrieval = retrieve(query="method results", ingested_paper=ingested, top_k=2)
    critique = generate_critique(retrieval_result=retrieval)
    assert critique.strengths
    assert critique.strengths[0].chunk_ids

    empty_critique = generate_critique(retrieval_result=RetrievalResult(query="none", hits=tuple()))
    assert empty_critique.strengths[0].text == NOT_STATED
    assert empty_critique.weaknesses[0].text == NOT_STATED
    assert empty_critique.threats_to_validity[0].text == NOT_STATED
