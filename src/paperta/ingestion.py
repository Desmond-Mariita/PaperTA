"""Deterministic ingestion and structural chunking."""

from __future__ import annotations

import hashlib
import re
from typing import Sequence

from paperta.contracts import Chunk, IngestedPaper, SectionInput


_TOKEN_SPACE_RE = re.compile(r"\s+")
_PARAGRAPH_SPLIT_RE = re.compile(r"\n\s*\n+")


def _normalize_text(text: str) -> str:
    stripped = text.strip()
    return _TOKEN_SPACE_RE.sub(" ", stripped)


def _chunk_id(paper_id: str, section: str, chunk_text: str) -> str:
    payload = f"{paper_id}|{section}|{chunk_text}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]


def ingest_document(paper_id: str, sections: Sequence[SectionInput]) -> IngestedPaper:
    """Ingest paper sections into deterministic paragraph chunks."""
    if not paper_id.strip():
        raise ValueError("paper_id must be non-empty")
    if not sections:
        raise ValueError("sections must be non-empty")

    labels = [s.label for s in sections]
    if any(not label.strip() for label in labels):
        raise ValueError("section label must be non-empty")
    if len(set(labels)) != len(labels):
        raise ValueError("duplicate section labels are not allowed")

    chunks: list[Chunk] = []
    section_order: list[str] = []

    any_content = False
    for section in sections:
        section_order.append(section.label)
        normalized_section_text = section.text.replace("\r\n", "\n")
        paragraphs = [p for p in _PARAGRAPH_SPLIT_RE.split(normalized_section_text) if p.strip()]
        for paragraph in paragraphs:
            normalized_chunk = _normalize_text(paragraph)
            if not normalized_chunk:
                continue
            any_content = True
            cid = _chunk_id(paper_id, section.label, normalized_chunk)
            chunks.append(
                Chunk(
                    chunk_id=cid,
                    paper_id=paper_id,
                    section=section.label,
                    text=normalized_chunk,
                )
            )

    if not any_content:
        raise ValueError("paper content is empty")

    return IngestedPaper(
        paper_id=paper_id,
        chunks=tuple(chunks),
        section_order=tuple(section_order),
    )
