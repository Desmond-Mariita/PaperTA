"""Grounded summary generation."""

from __future__ import annotations

from paperta.contracts import GroundedSummary, IngestedPaper, RetrievalResult, SummaryBullet


NOT_STATED = "Not stated in the paper."


def _snippet(text: str, max_len: int = 120) -> str:
    if len(text) <= max_len:
        return text
    return text[: max_len - 3].rstrip() + "..."


def generate_summary(
    ingested_paper: IngestedPaper, retrieval_result: RetrievalResult, mode: str = "summary"
) -> GroundedSummary:
    """Generate a deterministic grounded summary from retrieval hits."""
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
