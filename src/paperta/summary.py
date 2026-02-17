"""Grounded summary generation."""

from __future__ import annotations

from paperta.contracts import GroundedSummary, IngestedPaper, RetrievalResult, SummaryBullet


NOT_STATED = "Not stated in the paper."


def _snippet(text: str, max_len: int = 120) -> str:
    """Render bounded-length snippet for bullet text.

    Args:
        text: Source text.
        max_len: Maximum output length.

    Returns:
        Snippet string with ellipsis when truncated.
    """
    if len(text) <= max_len:
        return text
    return text[: max_len - 3].rstrip() + "..."


def generate_summary(
    ingested_paper: IngestedPaper, retrieval_result: RetrievalResult, mode: str = "summary"
) -> GroundedSummary:
    """Generate deterministic grounded summary from retrieval hits.

    Args:
        ingested_paper: Source paper corpus used for citation validation.
        retrieval_result: Ranked retrieval hits.
        mode: Summary mode. Phase 1 supports only `summary`.

    Returns:
        Grounded summary artifact with bullet citations.

    Raises:
        ValueError: If mode is invalid or retrieval references unknown chunk IDs.
    """
    if mode != "summary":
        raise ValueError("mode must be 'summary' in phase 1")

    if not retrieval_result.hits:
        return GroundedSummary(
            mode=mode,
            bullets=(SummaryBullet(text=NOT_STATED, chunk_ids=tuple()),),
        )

    valid_ids = {chunk.chunk_id for chunk in ingested_paper.chunks}
    bullets = []
    for hit in retrieval_result.hits:
        if hit.chunk_id not in valid_ids:
            raise ValueError("retrieval hit references unknown chunk_id")
        text = f"{hit.section}: {_snippet(hit.text)}"
        bullets.append(SummaryBullet(text=text, chunk_ids=(hit.chunk_id,)))
    return GroundedSummary(mode=mode, bullets=tuple(bullets))
