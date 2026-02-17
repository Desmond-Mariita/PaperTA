from paperta.contracts import SectionInput
from paperta.ingestion import ingest_document
from paperta.retrieval import retrieve
from paperta.teach import generate_concept_map, generate_explanation, generate_prerequisites, generate_quiz


def test_generate_prerequisites_with_citations():
    ingested = ingest_document(
        paper_id="teach-unit-1",
        sections=(
            SectionInput(label="Intro", text="Transformers use attention."),
            SectionInput(label="Method", text="Cross-attention aligns context."),
        ),
    )
    retrieval = retrieve(query="attention", ingested_paper=ingested, top_k=3)
    prerequisites = generate_prerequisites(retrieval_result=retrieval)
    assert prerequisites.items
    assert all(item.chunk_ids for item in prerequisites.items)


def test_generate_concept_map_links_nodes():
    ingested = ingest_document(
        paper_id="teach-unit-2",
        sections=(
            SectionInput(label="Intro", text="Graph neural networks process nodes."),
            SectionInput(label="Results", text="Node features improve classification."),
        ),
    )
    retrieval = retrieve(query="nodes classification", ingested_paper=ingested, top_k=4)
    concept_map = generate_concept_map(retrieval_result=retrieval)
    assert len(concept_map.nodes) >= 2
    assert concept_map.edges
    assert all(edge.source != edge.target for edge in concept_map.edges)


def test_generate_explanation_orders_steps_with_citations():
    ingested = ingest_document(
        paper_id="teach-unit-3",
        sections=(
            SectionInput(label="Intro", text="Attention improves context handling."),
            SectionInput(label="Method", text="Residual connections stabilize training."),
        ),
    )
    retrieval = retrieve(query="attention residual", ingested_paper=ingested, top_k=3)
    explanation = generate_explanation(retrieval_result=retrieval)
    assert explanation.steps
    assert explanation.steps[0].text.startswith("Step 1:")
    assert all(step.chunk_ids for step in explanation.steps)


def test_generate_quiz_answer_key_matches_options():
    ingested = ingest_document(
        paper_id="teach-unit-4",
        sections=(
            SectionInput(label="Intro", text="Transformers use attention."),
            SectionInput(label="Results", text="Accuracy improves on benchmark data."),
        ),
    )
    retrieval = retrieve(query="attention accuracy", ingested_paper=ingested, top_k=3)
    quiz = generate_quiz(retrieval_result=retrieval)
    assert quiz.mcq_items
    assert quiz.short_answer_items
    mcq = quiz.mcq_items[0]
    assert mcq.answer_key in mcq.options
    assert mcq.chunk_ids
