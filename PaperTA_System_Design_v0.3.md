# PaperTA System Design Document v0.3

**Version:** 0.3  
**Status:** Proposed Design Update  
**Date:** 2026-02-16

---

# 1. Scope and Objectives

PaperTA is an evidence-grounded academic paper analysis system with three primary user modes:

1. Summary Mode (short, medium, long)
2. Teach Mode (guided explanation, concept map, quiz, Socratic workspace)
3. Reviewer Mode (evidence-linked critique and reproducibility checks)

Core goals:

- High trust through verifiable citations.
- Reproducible artifacts across runs.
- Responsive UX for long-running ingestion and analysis.
- Provider-agnostic LLM orchestration with quality/cost/latency controls.

---

# 2. Personas and Core UX Outcomes

## 2.1 Personas

- Student: needs quick, trustworthy understanding and tutoring.
- TA/Instructor: needs teach-ready explanations and assessments.
- Researcher/Reviewer: needs rigorous, evidence-linked critique.

## 2.2 UX Outcomes

- Users can click any citation and see source evidence immediately.
- Users always see job progress and status during ingestion/generation.
- Users can inspect confidence and unsupported claims before export.

---

# 3. System Invariants and Reproducibility Contract

1. Groundedness Invariant  
   Every factual claim must include one or more evidence anchors.

2. No-Guessing Invariant  
   If evidence is missing, output exactly: `Not stated in the paper.`

3. Reproducibility Contract  
   Exact replay is guaranteed for cached artifacts with identical:
   - paper hash
   - extraction version
   - embedding version
   - prompt version
   - provider + model version
   - generation params  
   For uncached live calls, outputs are expected to be within bounded variation and validated by grounding checks.

4. Auditability Invariant  
   Every run stores full run provenance and validation outcomes.

5. Fail-Safe Invariant  
   Irrecoverable failures halt generation. Recoverable failures produce degraded output with explicit warnings.

---

# 4. Non-Functional Requirements (NFRs)

## 4.1 Performance and Reliability Targets

- Summary draft p95 latency (post-ingestion, pre-verification): <= 15s
- Summary verified p95 latency (post-ingestion, after verification markers): <= 30s
- Teach/Reviewer mode p95 end-to-end latency: <= 30s
- Ingestion success rate: >= 99% for supported PDFs
- Service availability: 99.9%
- Background job retry success (within 3 retries): >= 99%

## 4.2 Quality Targets

- Citation support precision: >= 0.95
- Unsupported-claim rate in final artifacts: <= 0.02
- Faithfulness score threshold (RAG evaluation): >= 0.85

## 4.3 Cost Targets

- Token and processing cost tracked per run and per mode.
- Policy routing enforces configurable per-run budget ceiling.

---

# 5. End-to-End Architecture

## 5.1 Logical Components

1. Frontend (React/Next.js)
2. API Gateway + Backend (FastAPI)
3. AuthN/AuthZ Service (RBAC + tenant isolation)
4. Ingestion Pipeline Service (layout-aware parsing + OCR fallback)
5. Retrieval Service (hybrid retrieval + reranking + parent context)
6. LLM Orchestration Service (provider abstraction + routing policy)
7. Verification Service (citation and claim support auditing)
8. Artifact/Run Registry Service
9. Async Worker Queue (Celery/Redis or equivalent)
10. Observability Stack (logs, metrics, traces, alerts)

## 5.2 Deployment Pattern

- Frontend and backend are independently deployable.
- Long-running tasks are asynchronous jobs.
- Storage:
  - relational DB for metadata/run registry
  - object storage for PDFs/artifacts
  - vector index for chunk embeddings

---

# 6. Ingestion and Structural Intelligence

## 6.1 Parsing Strategy

- Primary parser: layout-aware parser preserving reading order and structure.
- OCR fallback for scanned PDFs.
- Equation capture with LaTeX when available.
- Table extraction into structured Markdown/JSON representation.
- Vision-to-text pass for key figures/plots to produce `virtual_chunks` for non-text evidence.

## 6.2 Structural Chunking

Chunk boundaries follow document structure, not fixed token windows:

- Never split formulas/tables mid-unit.
- Preserve subsection boundaries where possible.
- Tag chunk roles:
  - `is_figure_caption`
  - `is_table`
  - `is_footnote`
  - `is_methodology_step`
  - `is_result_claim`

## 6.3 Provenance Anchors

Each chunk stores:

- page number(s)
- sentence-level bounding box or span offsets
- `coordinate_map` for PDF highlight synchronization
- `json_path` (or equivalent extraction path) for traceable parser alignment
- extraction confidence
- parser/extractor version

---

# 7. Retrieval Strategy (Advanced RAG)

## 7.1 Hybrid Retrieval Pipeline

1. Query preparation
   - user query + mode-specific system query
   - optional multi-query expansion (3-5 rewrites)
2. Candidate recall
   - vector search
   - lexical search (BM25)
   - section priors
3. Cross-encoder reranking
4. Parent-document/context expansion
   - retrieve precise child chunks
   - include parent subsection context for final prompt

Recommended depth defaults:

- Recall top 50 candidates from hybrid retrieval.
- Rerank top 20 candidates with cross-encoder.
- Pass top 5-10 evidence bundles (with parent context) to generation.

## 7.2 Retrieval Guarantees

- Return evidence bundle with ranked citations and score.
- Track all retrieved IDs in run registry.
- Expose retrieval trace for debugging.

---

# 8. LLM Orchestration and Provider Routing

## 8.1 Provider Interface

All providers must implement:

`generate_structured(system_prompt, user_prompt, temperature, max_tokens, json_schema, seed?) -> JSON`

## 8.2 Routing Policy

Routing is policy-driven, not static preference-only:

- quality-first, latency-first, or cost-first mode
- fallback chain per task
- circuit breaker for elevated error rates
- dynamic disable for degraded providers

## 8.3 Prompt and Model Versioning

- Every template has `prompt_version`.
- Model version snapshots are persisted.
- Config changes are hash-versioned.

---

# 9. Verification Loop and Quality Control

## 9.1 Chain-of-Verification

Before final render:

1. Extract claims from draft output.
2. For each claim, verify support against cited evidence.
3. Mark claim as `supported`, `weakly_supported`, or `unsupported`.
4. Regenerate or annotate unsupported claims.

## 9.2 Automated Evaluation

- Run faithfulness/relevance metrics for applicable modes.
- Store metric scores in run registry.
- Flag low-confidence output if thresholds are not met.

## 9.3 User-Facing Confidence

- Confidence badge at artifact and section level.
- Inline warnings for weakly supported/unsupported claims.

## 9.4 Asynchronous Verification UX

- Stream draft output as soon as first-pass generation completes.
- Run claim verification in background workers.
- Update support markers (`supported`/`weakly_supported`/`unsupported`) incrementally in UI.
- Preserve both draft and verified timestamps in run metadata.

---

# 10. Mode Specifications

## 10.1 Summary Mode

- Short: 5-10 bullets
- Medium: 1-2 pages, section-structured
- Long: section-by-section walkthrough

Requirements:

- Every factual statement includes evidence anchors.
- Provide unsupported-claims section if present.

## 10.2 Teach Mode

Pipeline:

1. Prerequisite checklist
2. Concept map
3. Stepwise explanation linked to sections
4. Toy examples
5. Quiz (MCQ + short answer)
6. Socratic workspace with retrieval-constrained chat

Socratic workspace capability:

- User highlights PDF text and asks contextual follow-up.
- Responses are constrained to highlighted span + related evidence.

## 10.3 Reviewer Mode

Outputs:

- Summary
- Strengths/weaknesses with evidence
- Threats to validity
- Reproducibility checklist
- Claim-evidence matrix

Required matrix columns:

| Claim | Evidence Anchors | Support Grade | Notes |

---

# 11. UX Specification

## 11.1 Side-by-Side Evidence View

- Left: generated artifact
- Right: PDF viewer
- Citation click auto-scrolls and highlights source text
- Highlight rendering is based on `coordinate_map` overlays on the original PDF (implementation class: `react-pdf-highlighter` compatible).

## 11.2 Live Progress

Show fine-grained processing status, for example:

- Parsing layout
- Extracting equations/tables
- Building index
- Retrieving evidence
- Verifying claims

## 11.3 Error and Degraded States

- Partial extraction warnings
- Missing evidence warnings
- Provider fallback notices
- Retry actions for failed jobs

---

# 12. Data Model (Expanded)

## 12.1 Core Entities

- `Paper`
- `Chunk`
- `Artifact`
- `RunRecord`
- `RetrievalTrace`
- `ClaimVerification`
- `UserAnnotation`
- `Concept`

## 12.2 Key New Fields

### Chunk

- `chunk_id`
- `paper_id`
- `section_path`
- `text`
- `page_start`
- `page_end`
- `char_start`
- `char_end`
- `bbox`
- `role_tags[]`
- `extractor_version`
- `embedding_version`
- `embedding_hash`

### Artifact

- `artifact_id`
- `paper_id`
- `run_id`
- `mode`
- `provider`
- `model_version`
- `prompt_version`
- `params`
- `output_markdown`
- `output_json`
- `confidence_score`
- `created_at`
- `output_hash`

### UserAnnotation

- `annotation_id`
- `artifact_id`
- `run_id`
- `user_id`
- `target_claim_id`
- `annotation_type` (`correction`, `note`, `flag`)
- `payload`
- `created_at`

### Concept

- `concept_id`
- `scope` (`local`, `global`)
- `global_concept_id` (nullable for local-only concepts)
- `name`
- `paper_id`
- `definition_span`
- `aliases[]`
- `embedding_hash`

---

# 13. Security, Privacy, and Compliance

- RBAC and tenant isolation.
- Encryption in transit and at rest.
- Secret management with rotation.
- Data retention TTL and hard-delete API.
- Access audit logs for sensitive operations.
- Prompt-injection defenses at retrieval and generation layers.
- Retrieved paper content is always treated as untrusted data, never as executable instruction.
- System prompts enforce strict instruction/data separation for all generation and verification calls.
- Configurable external browsing policy (default disabled).

---

# 14. Observability and Operations

- Structured logs with `run_id` correlation.
- Metrics:
  - latency per stage
  - retrieval recall proxy
  - unsupported-claim rate
  - provider error rates
  - cost per run
- Distributed tracing across ingestion/retrieval/generation/verification.
- Alerts on SLO breach and provider degradation.

---

# 15. Evaluation and Testing Strategy

## 15.1 Offline Evaluation

- Golden dataset of papers across domains and PDF types.
- Regression tests for extraction quality and retrieval quality.
- Mode-specific quality scorecards.

## 15.2 Online Evaluation

- A/B tests for retrieval/routing variants.
- User feedback capture via annotation and rating.
- Continuous threshold tuning for confidence warnings.

---

# 16. Phase Plan

## Phase 1: Grounded Summaries + Core Ingestion

- Layout-aware extraction + structural chunking
- Hybrid retrieval baseline
- Summary mode + citation validation

## Phase 2: Teach Mode + Socratic Workspace

- Concept map + quiz pipeline
- Highlight-to-explain interaction
- Confidence and evidence UI

## Phase 3: Reviewer Mode + Verification Loop

- Full reviewer artifact schema
- Claim verification and support grading
- Reproducibility checklist automation

## Phase 4: Multi-Paper Intelligence

- Cross-paper concept tracking
- Knowledge graph links (citation, support, contradiction)
- Concept linker service to map local concepts to canonical global concepts
- Comparative reviewer workflows

---

# 17. Definition of Done (MVP v0.3)

A user can:

- Upload a PDF and see ingestion progress states.
- Generate summary/teach/reviewer artifacts with clickable evidence anchors.
- Inspect confidence and unsupported claims.
- Export Markdown and LaTeX with provenance metadata.
- Choose provider policy profile (quality/latency/cost).

Acceptance criteria:

- Citation support precision >= 0.95 on evaluation set.
- p95 post-ingestion summary latency <= 15s.
- Run registry captures full provenance and verification metrics.

---

# 18. Open Decisions

1. Final parser stack selection for equations/tables across domains.
   Recommended starting point: Docling as primary parser, Nougat fallback for complex scientific PDFs.
2. Exact reranker model and hosting strategy.
   Recommended starting point: BGE-Reranker-v2-m3 (self-hosted) or Cohere Rerank (managed API) based on latency/cost envelope.
3. Queue technology and scaling limits per tenant.
4. Optional human-in-the-loop review gate before export in strict mode.

---

# 19. Competitive Differentiation and Parity Gaps

Based on current literature-assistant products, PaperTA should keep its core differentiator as verifiable claim-evidence auditing while closing feature parity gaps in discovery and collaboration.

## 19.1 Differentiators to Preserve

- Chain-of-Verification with explicit support grading.
- Sentence-level evidence anchors with PDF coordinate overlays.
- Reviewer-mode claim-evidence matrix with reproducibility framing.

## 19.2 Parity Gaps to Close

1. Consensus intelligence across multiple papers (support/contradict/mixed views).
2. Guided systematic-review workflow (screening + extraction templates).
3. Citation network exploration and related-work discovery graphs.
4. Saved searches and monitor alerts for new publications.
5. Team collaboration primitives (shared collections, comments, assignments).
6. Reference-manager interoperability (Zotero/Mendeley/EndNote, RIS/BibTeX round-trip).
7. Multimodal ingestion (slides, audio/video transcripts) for teaching and review context.

---

# 20. v0.3.1 Prioritized Backlog

## P0 (Immediate)

1. Add cross-paper claim consensus panel (`supporting`, `contradicting`, `mixed`, `insufficient evidence`).
2. Add saved query + watchlist alerts with scheduled retrieval jobs.
3. Add Zotero integration and RIS/BibTeX import-export.
4. Add reviewer collaboration features: shared workspace, comments, assignment, artifact lock/versioning.

## P1 (Next)

1. Add systematic review workflow template:
   - research question
   - inclusion/exclusion criteria
   - screening queue
   - extraction schema
   - exportable evidence table
2. Add citation/related-work graph view for paper exploration.
3. Add table/figure evidence cards in Reviewer Mode output.

## P2 (Later)

1. Add multimodal source ingestion and transcript grounding.
2. Add enterprise knowledge repositories with fine-grained permissioning.
3. Add configurable analysis-depth profiles (`quick`, `balanced`, `deep-verified`).
