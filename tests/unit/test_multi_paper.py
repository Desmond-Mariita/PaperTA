from paperta.contracts import RetrievalHit, RetrievalResult
from paperta.multi_paper import build_consensus_matrix, build_cross_paper_graph, link_concepts
from paperta.multi_paper_contracts import PerPaperRetrieval


def test_link_concepts_assigns_canonical_ids():
    results = (
        PerPaperRetrieval(
            paper_id="p1",
            retrieval_trace=RetrievalResult(
                query="q",
                hits=(RetrievalHit(chunk_id="c1", section="Intro", score=2, text="alpha beta"),),
            ),
            retrieved_chunk_ids=("c1",),
        ),
        PerPaperRetrieval(
            paper_id="p2",
            retrieval_trace=RetrievalResult(
                query="q",
                hits=(RetrievalHit(chunk_id="c2", section="Intro", score=1, text="alpha gamma"),),
            ),
            retrieved_chunk_ids=("c2",),
        ),
    )
    links = link_concepts(results)
    assert links.concepts
    assert all(link.global_concept_id.startswith("g_") for link in links.concepts)


def test_build_consensus_matrix_has_valid_labels():
    results = (
        PerPaperRetrieval(
            paper_id="p1",
            retrieval_trace=RetrievalResult(
                query="q",
                hits=(RetrievalHit(chunk_id="c1", section="Intro", score=2, text="supports claim"),),
            ),
            retrieved_chunk_ids=("c1",),
        ),
        PerPaperRetrieval(
            paper_id="p2",
            retrieval_trace=RetrievalResult(
                query="q",
                hits=(RetrievalHit(chunk_id="c2", section="Results", score=1, text="may support"),),
            ),
            retrieved_chunk_ids=("c2",),
        ),
    )
    consensus = build_consensus_matrix(results)
    assert consensus.rows
    assert consensus.rows[0].label in {"supporting", "contradicting", "mixed", "insufficient evidence"}


def test_build_cross_paper_graph_emits_expected_edges():
    results = (
        PerPaperRetrieval(
            paper_id="p1",
            retrieval_trace=RetrievalResult(
                query="q",
                hits=(RetrievalHit(chunk_id="c1", section="Intro", score=2, text="alpha beta"),),
            ),
            retrieved_chunk_ids=("c1",),
        ),
        PerPaperRetrieval(
            paper_id="p2",
            retrieval_trace=RetrievalResult(
                query="q",
                hits=(RetrievalHit(chunk_id="c2", section="Intro", score=2, text="alpha gamma"),),
            ),
            retrieved_chunk_ids=("c2",),
        ),
    )
    links = link_concepts(results)
    graph = build_cross_paper_graph(results, links)
    relations = {edge.relation for edge in graph.edges}
    assert "mentions" in relations
    assert "shares_concept" in relations
    assert all(edge.source and edge.target for edge in graph.edges)
