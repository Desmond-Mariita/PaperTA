"""Section-aware lexical retrieval."""

from __future__ import annotations

import re

from paperta.contracts import IngestedPaper, RetrievalHit, RetrievalResult


_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> set[str]:
    """Tokenize text into lowercase alphanumeric terms.

    Args:
        text: Input text.

    Returns:
        Set of unique tokens.
    """
    return set(_TOKEN_RE.findall(text.lower()))


def retrieve(query: str, ingested_paper: IngestedPaper, top_k: int) -> RetrievalResult:
    """Retrieve top-k chunks by lexical token overlap score.

    Args:
        query: User query string.
        ingested_paper: Ingested paper corpus.
        top_k: Maximum number of retrieval hits to return.

    Returns:
        Retrieval result with ranked hits.

    Raises:
        ValueError: If query is empty or top_k is not positive.
    """
    if not query.strip():
        raise ValueError("query must be non-empty")
    if top_k <= 0:
        raise ValueError("top_k must be > 0")

    q_tokens = _tokenize(query)
    section_rank = {name: idx for idx, name in enumerate(ingested_paper.section_order)}
    scored: list[RetrievalHit] = []
    for chunk in ingested_paper.chunks:
        c_tokens = _tokenize(chunk.text)
        score = len(q_tokens.intersection(c_tokens))
        if score > 0:
            scored.append(
                RetrievalHit(
                    chunk_id=chunk.chunk_id,
                    section=chunk.section,
                    score=score,
                    text=chunk.text,
                )
            )

    scored.sort(
        key=lambda hit: (
            -hit.score,
            section_rank.get(hit.section, 10**9),
            hit.chunk_id,
        )
    )
    return RetrievalResult(query=query, hits=tuple(scored[:top_k]))
