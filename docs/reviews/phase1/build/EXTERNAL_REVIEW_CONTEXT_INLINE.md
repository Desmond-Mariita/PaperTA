# Phase 1 Build Snapshot

Use only this inline content. Do not access tools or files.

## CONTRACT
# PHASE1 Runtime Contract

## Scope

Phase 1 delivers deterministic ingestion and grounded summary generation for a single paper.

## Functional Requirements

1. Ingestion accepts paper text and section labels.
2. Text is normalized deterministically.
3. Structural chunks preserve section association and stable chunk IDs.
4. Chunk ID generation uses content-hash scheme:
   - `sha256("{paper_id}|{section}|{normalized_chunk_text}")[:16]`
5. Duplicate section labels are invalid input and raise `ValueError`.
6. Retrieval returns top-k chunk matches for a query.
7. Summary output contains bullets with citation anchors to chunk IDs.
8. Unsupported statements are rendered as `Not stated in the paper.`
9. Phase 1 mode is constrained to `summary`.

## Non-Functional Requirements

1. Determinism: same input/config returns same chunk IDs and summary text.
2. Auditability: pipeline output includes retrieval trace and chunk IDs.
3. Fail-safe: invalid inputs raise explicit errors; no silent defaults.

## Interfaces

1. `ingest_document(paper_id, sections) -> IngestedPaper`
2. `retrieve(query, ingested_paper, top_k) -> RetrievalResult`
3. `generate_summary(ingested_paper, retrieval_result, mode="summary") -> GroundedSummary`
4. `run_phase1_pipeline(paper_id, sections, query, mode="summary", top_k) -> PipelineResult`

## Invariants

1. Every summary bullet has one or more `chunk_ids`, unless text is exactly `Not stated in the paper.`
2. Chunk IDs are stable across identical runs.
3. No bullet may cite a chunk ID absent from the ingested corpus.

## Failure Modes

1. Empty paper content -> `ValueError`.
2. Empty query -> `ValueError`.
3. `top_k <= 0` -> `ValueError`.
4. Retrieval empty set -> summary contains only `Not stated in the paper.`
5. Duplicate section labels -> `ValueError`.
6. Invalid mode (not `summary`) -> `ValueError`.

## Observability

1. Pipeline result includes:
- `paper_id`
- `mode`
- `retrieval_trace`
- `retrieved_chunk_ids`
- `summary_bullet_count`
- `unsupported_bullet_count`

## Acceptance Gates

1. Unit + integration + negative tests pass.
2. Checklist verifies required files and tests.
3. Internal/external reviews complete with phase gate pass.

## CHECKLIST
version: "1.1"
phase: 1

items:
  - id: D-001
    requirement: "Phase 1 ADR exists"
    evidence:
      type: file_exists
      path: docs/adr/ADR-001-phase1-ingestion-grounded-summary.md

  - id: D-002
    requirement: "Phase 1 runtime contract exists"
    evidence:
      type: file_exists
      path: docs/contracts/PHASE1_RUNTIME_CONTRACT.md

  - id: D-003
    requirement: "Phase 1 acceptance checklist exists"
    evidence:
      type: file_exists
      path: docs/checklists/PHASE1_ACCEPTANCE_CHECKLIST.yaml

  - id: C-001
    requirement: "Contracts module exists"
    evidence:
      type: file_exists
      path: src/paperta/contracts.py

  - id: C-002
    requirement: "Ingestion service module exists"
    evidence:
      type: file_exists
      path: src/paperta/ingestion.py

  - id: C-003
    requirement: "Retrieval service module exists"
    evidence:
      type: file_exists
      path: src/paperta/retrieval.py

  - id: C-004
    requirement: "Summary service module exists"
    evidence:
      type: file_exists
      path: src/paperta/summary.py

  - id: C-005
    requirement: "Pipeline module exists"
    evidence:
      type: file_exists
      path: src/paperta/pipeline.py

  # Three-Test Rule matrix (component-level)
  - id: T-INGEST-UNIT-001
    requirement: "Ingestion unit test exists"
    evidence:
      type: test_exists
      test_pattern: tests/unit/test_ingestion.py
      test_name: test_chunking_assigns_stable_chunk_ids

  - id: T-INGEST-INT-001
    requirement: "Ingestion integration test exists"
    evidence:
      type: test_exists
      test_pattern: tests/integration/test_phase1_pipeline.py
      test_name: test_pipeline_uses_ingestion_section_order

  - id: T-INGEST-NEG-001
    requirement: "Ingestion negative test exists"
    evidence:
      type: test_exists
      test_pattern: tests/negative/test_ingestion_negative.py
      test_name: test_ingestion_rejects_duplicate_sections

  - id: T-RETRIEVE-UNIT-001
    requirement: "Retrieval unit test exists"
    evidence:
      type: test_exists
      test_pattern: tests/unit/test_retrieval.py
      test_name: test_retrieval_orders_by_overlap_score

  - id: T-RETRIEVE-INT-001
    requirement: "Retrieval integration test exists"
    evidence:
      type: test_exists
      test_pattern: tests/integration/test_phase1_pipeline.py
      test_name: test_pipeline_retrieval_trace_contains_chunk_ids

  - id: T-RETRIEVE-NEG-001
    requirement: "Retrieval negative test exists"
    evidence:
      type: test_exists
      test_pattern: tests/negative/test_retrieval_negative.py
      test_name: test_retrieval_rejects_non_positive_top_k

  - id: T-SUMMARY-UNIT-001
    requirement: "Summary unit test exists"
    evidence:
      type: test_exists
      test_pattern: tests/unit/test_summary.py
      test_name: test_summary_bullets_include_citations

  - id: T-SUMMARY-UNIT-002
    requirement: "Summary enforces invariant 3 for unknown chunk IDs"
    evidence:
      type: test_exists
      test_pattern: tests/unit/test_summary.py
      test_name: test_summary_rejects_unknown_chunk_ids

  - id: T-SUMMARY-INT-001
    requirement: "Summary integration test exists"
    evidence:
      type: test_exists
      test_pattern: tests/integration/test_phase1_pipeline.py
      test_name: test_phase1_pipeline_generates_grounded_summary

  - id: T-SUMMARY-NEG-001
    requirement: "Summary negative test exists"
    evidence:
      type: test_exists
      test_pattern: tests/negative/test_summary_negative.py
      test_name: test_summary_returns_not_stated_when_no_evidence

  # Contract failure modes coverage
  - id: F-001
    requirement: "Failure mode: empty paper content raises ValueError"
    evidence:
      type: test_exists
      test_pattern: tests/negative/test_pipeline_negative.py
      test_name: test_pipeline_rejects_empty_paper

  - id: F-002
    requirement: "Failure mode: empty query raises ValueError"
    evidence:
      type: test_exists
      test_pattern: tests/negative/test_pipeline_negative.py
      test_name: test_pipeline_rejects_empty_query

  - id: F-003
    requirement: "Failure mode: top_k <= 0 raises ValueError"
    evidence:
      type: test_exists
      test_pattern: tests/negative/test_retrieval_negative.py
      test_name: test_retrieval_rejects_non_positive_top_k

  - id: F-004
    requirement: "Failure mode: empty retrieval yields Not stated in the paper"
    evidence:
      type: test_exists
      test_pattern: tests/negative/test_summary_negative.py
      test_name: test_summary_returns_not_stated_when_no_evidence

  - id: F-005
    requirement: "Failure mode: duplicate section labels raise ValueError"
    evidence:
      type: test_exists
      test_pattern: tests/negative/test_ingestion_negative.py
      test_name: test_ingestion_rejects_duplicate_sections

  - id: F-006
    requirement: "Failure mode: invalid mode raises ValueError"
    evidence:
      type: test_exists
      test_pattern: tests/negative/test_pipeline_negative.py
      test_name: test_pipeline_rejects_invalid_mode

## SOURCE contracts.py
"""Phase 1 runtime contracts for deterministic ingestion and grounded summary."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SectionInput:
    """Input section payload."""

    label: str
    text: str


@dataclass(frozen=True)
class Chunk:
    """Deterministic paragraph chunk."""

    chunk_id: str
    paper_id: str
    section: str
    text: str


@dataclass(frozen=True)
class IngestedPaper:
    """Ingestion output artifact."""

    paper_id: str
    chunks: tuple[Chunk, ...]
    section_order: tuple[str, ...]


@dataclass(frozen=True)
class RetrievalHit:
    """Single lexical retrieval hit."""

    chunk_id: str
    section: str
    score: int
    text: str


@dataclass(frozen=True)
class RetrievalResult:
    """Retrieval output."""

    query: str
    hits: tuple[RetrievalHit, ...]


@dataclass(frozen=True)
class SummaryBullet:
    """Grounded summary bullet with citations."""

    text: str
    chunk_ids: tuple[str, ...]


@dataclass(frozen=True)
class GroundedSummary:
    """Summary artifact."""

    mode: str
    bullets: tuple[SummaryBullet, ...]


@dataclass(frozen=True)
class PipelineResult:
    """End-to-end phase 1 result with observability metadata."""

    paper_id: str
    mode: str
    retrieval_trace: RetrievalResult
    retrieved_chunk_ids: tuple[str, ...]
    summary: GroundedSummary
    summary_bullet_count: int
    unsupported_bullet_count: int

## SOURCE ingestion.py
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

## SOURCE retrieval.py
"""Section-aware lexical retrieval."""

from __future__ import annotations

import re

from paperta.contracts import IngestedPaper, RetrievalHit, RetrievalResult


_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> set[str]:
    return set(_TOKEN_RE.findall(text.lower()))


def retrieve(query: str, ingested_paper: IngestedPaper, top_k: int) -> RetrievalResult:
    """Retrieve top-k chunks by lexical token overlap score."""
    if not query.strip():
        raise ValueError("query must be non-empty")
    if top_k <= 0:
        raise ValueError("top_k must be > 0")

    q_tokens = _tokenize(query)
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

    scored.sort(key=lambda hit: (-hit.score, hit.section, hit.chunk_id))
    return RetrievalResult(query=query, hits=tuple(scored[:top_k]))

## SOURCE summary.py
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

## SOURCE pipeline.py
"""Phase 1 end-to-end orchestration."""

from __future__ import annotations

from typing import Sequence

from paperta.contracts import PipelineResult, SectionInput
from paperta.ingestion import ingest_document
from paperta.retrieval import retrieve
from paperta.summary import NOT_STATED, generate_summary


def run_phase1_pipeline(
    paper_id: str,
    sections: Sequence[SectionInput],
    query: str,
    mode: str = "summary",
    top_k: int = 5,
) -> PipelineResult:
    """Execute deterministic ingestion -> retrieval -> grounded summary pipeline."""
    if mode != "summary":
        raise ValueError("invalid mode")

    ingested = ingest_document(paper_id=paper_id, sections=sections)
    retrieval_result = retrieve(query=query, ingested_paper=ingested, top_k=top_k)
    summary = generate_summary(ingested_paper=ingested, retrieval_result=retrieval_result, mode=mode)
    retrieved_chunk_ids = tuple(hit.chunk_id for hit in retrieval_result.hits)
    unsupported = sum(1 for b in summary.bullets if b.text == NOT_STATED)

    return PipelineResult(
        paper_id=paper_id,
        mode=mode,
        retrieval_trace=retrieval_result,
        retrieved_chunk_ids=retrieved_chunk_ids,
        summary=summary,
        summary_bullet_count=len(summary.bullets),
        unsupported_bullet_count=unsupported,
    )

## TESTS unit summary
import pytest

from paperta.contracts import RetrievalHit, RetrievalResult, SectionInput
from paperta.ingestion import ingest_document
from paperta.summary import generate_summary


def test_summary_bullets_include_citations():
    ingested = ingest_document(
        paper_id="sum-unit-1",
        sections=(SectionInput(label="Intro", text="Important finding."),),
    )
    chunk_id = ingested.chunks[0].chunk_id
    retrieval = RetrievalResult(
        query="q",
        hits=(RetrievalHit(chunk_id=chunk_id, section="Intro", score=2, text="Important finding."),),
    )
    summary = generate_summary(ingested_paper=ingested, retrieval_result=retrieval, mode="summary")
    assert summary.bullets
    assert summary.bullets[0].chunk_ids == (chunk_id,)


def test_summary_rejects_unknown_chunk_ids():
    ingested = ingest_document(
        paper_id="sum-unit-2",
        sections=(SectionInput(label="Intro", text="Known text."),),
    )
    retrieval = RetrievalResult(
        query="q",
        hits=(RetrievalHit(chunk_id="deadbeefdeadbeef", section="Intro", score=1, text="Known text."),),
    )
    with pytest.raises(ValueError):
        generate_summary(ingested_paper=ingested, retrieval_result=retrieval, mode="summary")

## TESTS integration
from paperta.contracts import SectionInput
from paperta.pipeline import run_phase1_pipeline


def test_phase1_pipeline_generates_grounded_summary():
    result = run_phase1_pipeline(
        paper_id="paper-int-1",
        sections=(
            SectionInput(label="Intro", text="We present a transformer model."),
            SectionInput(label="Method", text="The method uses attention layers."),
        ),
        query="transformer attention",
        mode="summary",
        top_k=3,
    )
    assert result.summary_bullet_count >= 1
    assert result.unsupported_bullet_count == 0
    assert all(b.chunk_ids for b in result.summary.bullets)


def test_pipeline_uses_ingestion_section_order():
    result = run_phase1_pipeline(
        paper_id="paper-int-2",
        sections=(
            SectionInput(label="Zeta", text="alpha beta"),
            SectionInput(label="Alpha", text="alpha"),
        ),
        query="alpha beta",
        mode="summary",
        top_k=2,
    )
    # First bullet should prefer higher overlap; tie-break is section then chunk_id.
    assert result.summary.bullets[0].text.startswith("Zeta:")


def test_pipeline_retrieval_trace_contains_chunk_ids():
    result = run_phase1_pipeline(
        paper_id="paper-int-3",
        sections=(SectionInput(label="Body", text="graph neural network"),),
        query="graph",
        mode="summary",
        top_k=1,
    )
    assert len(result.retrieved_chunk_ids) == 1
    assert len(result.retrieval_trace.hits) == 1

## TESTS negative
import pytest

from paperta.contracts import SectionInput
from paperta.pipeline import run_phase1_pipeline


def test_pipeline_rejects_empty_paper():
    with pytest.raises(ValueError):
        run_phase1_pipeline(
            paper_id="paper-neg-empty",
            sections=(SectionInput(label="Intro", text="   "),),
            query="token",
            mode="summary",
            top_k=1,
        )


def test_pipeline_rejects_empty_query():
    with pytest.raises(ValueError):
        run_phase1_pipeline(
            paper_id="paper-neg-query",
            sections=(SectionInput(label="Intro", text="content"),),
            query="",
            mode="summary",
            top_k=1,
        )


def test_pipeline_rejects_invalid_mode():
    with pytest.raises(ValueError):
        run_phase1_pipeline(
            paper_id="paper-neg-mode",
            sections=(SectionInput(label="Intro", text="content"),),
            query="content",
            mode="teach",
            top_k=1,
        )
from paperta.contracts import RetrievalResult, SectionInput
from paperta.ingestion import ingest_document
from paperta.summary import NOT_STATED, generate_summary


def test_summary_returns_not_stated_when_no_evidence():
    ingested = ingest_document(
        paper_id="sum-neg-1",
        sections=(SectionInput(label="Body", text="Some text."),),
    )
    summary = generate_summary(
        ingested_paper=ingested,
        retrieval_result=RetrievalResult(query="x", hits=tuple()),
        mode="summary",
    )
    assert len(summary.bullets) == 1
    assert summary.bullets[0].text == NOT_STATED
    assert summary.bullets[0].chunk_ids == tuple()
