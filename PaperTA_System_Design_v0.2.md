# PaperTA System Design Document v0.2

**Version:** 0.2\
**Status:** Design Loop Artifact\
**Date:** 2026-02-16

------------------------------------------------------------------------

# 1. Problem Definition

## 1.1 Core Objective

PaperTA is a deterministic, evidence-grounded academic paper analysis
system that provides:

1.  Structured summaries (short / medium / long)
2.  Teach Mode (guided explanation + concept mapping + quizzes)
3.  Reviewer Mode (evidence-linked peer-review style critique)

The system must operate under strict grounding, reproducibility, and
provider-agnostic LLM routing.

------------------------------------------------------------------------

## 1.2 Key Challenges

-   PDF extraction inconsistencies (multi-column, footnotes, figures)
-   Hallucination risk in LLM-generated content
-   Generic or unsupported review critiques
-   Non-deterministic LLM outputs
-   Provider-specific behavior differences

------------------------------------------------------------------------

# 2. System Invariants

1.  Groundedness Invariant\
    Every factual claim must cite extracted chunk IDs.

2.  No-Guessing Invariant\
    If information is absent, output: "Not stated in the paper."

3.  Determinism Invariant\
    Same input + same configuration + same provider version → identical
    artifact.

4.  Auditability Invariant\
    Every run generates a run record including:

    -   input hash
    -   chunk hashes
    -   provider
    -   model version
    -   temperature
    -   retrieved chunk IDs
    -   output hash

5.  Fail-Closed Invariant\
    If ingestion or retrieval fails, generation must halt.

------------------------------------------------------------------------

# 3. High-Level Architecture

## 3.1 Core Subsystems

1.  Streamlit UI Layer\
2.  Document Ingestion Service\
3.  Chunking + Embedding Layer\
4.  Retrieval Engine (Vector + Section-aware search)\
5.  LLM Orchestration Layer (Provider-Agnostic)\
6.  Artifact Storage + Run Registry

------------------------------------------------------------------------

# 4. Provider-Agnostic LLM Layer

## 4.1 Supported Providers

-   OpenAI
-   Anthropic
-   Google (Gemini)

## 4.2 Provider Interface Contract

All providers must implement:

generate_structured( system_prompt, user_prompt, temperature,
max_tokens, json_schema ) -\> JSON

Required guarantees: - Deterministic mode when temperature=0 - Strict
JSON output enforcement - Version tracking

------------------------------------------------------------------------

## 4.3 Provider Routing Policy

Configuration file: `configs/provider_policy.yaml`

Example:

default_provider: openai allowed_providers: - openai - anthropic -
google

routing_rules: summarize: preferred: openai teach: preferred: anthropic
review: preferred: openai

------------------------------------------------------------------------

## 4.4 Reproducibility Controls

-   Provider name stored in artifact metadata
-   Model version stored
-   Temperature logged
-   Seed (if supported) stored
-   Strong caching keyed by: paper_hash + provider + model + mode +
    params

------------------------------------------------------------------------

# 5. Data Model

## 5.1 Paper

-   id
-   title
-   authors
-   year
-   pdf_path
-   text_path
-   section_map
-   hash

## 5.2 Chunk

-   chunk_id
-   paper_id
-   section
-   text
-   embedding_vector_hash

## 5.3 Artifact

-   artifact_id
-   paper_id
-   mode (summary_short / teach / review)
-   provider
-   model_version
-   params
-   output_markdown
-   output_json
-   created_at
-   output_hash

------------------------------------------------------------------------

# 6. Execution Flow

Upload → Extract → Normalize → Chunk → Embed → Index

Then:

User selects mode → Retrieve top-K chunks → Generate structured output →
Validate schema → Store artifact → Render

------------------------------------------------------------------------

# 7. Mode Specifications

## 7.1 Summarize Mode

Lengths: - Short (5--10 bullets) - Medium (1--2 pages structured) - Long
(detailed section walkthrough)

Each section must cite chunk IDs.

------------------------------------------------------------------------

## 7.2 Teach Mode

Pipeline:

1.  Prerequisite checklist
2.  Concept map
3.  Step-by-step explanation (section-linked)
4.  Toy example
5.  Quiz (MCQ + short answer)
6.  Socratic Q&A chat (retrieval-constrained)

------------------------------------------------------------------------

## 7.3 Reviewer Mode

Outputs:

-   Summary
-   Strengths (evidence-linked)
-   Weaknesses (evidence-linked)
-   Threats to validity
-   Reproducibility checklist
-   Claim--Evidence matrix

Matrix columns:

| Claim \| Evidence Chunk IDs \| Strength \| Notes \|

------------------------------------------------------------------------

# 8. Security & Safety

-   Prompt injection defense: retrieval only from extracted chunks
-   No external browsing unless explicitly enabled
-   File upload size limits
-   Sandboxed extraction

------------------------------------------------------------------------

# 9. Phase Plan

Phase 1 -- Ingestion + Grounded Summaries\
Phase 2 -- Teach Mode\
Phase 3 -- Reviewer Mode\
Phase 4 -- Multi-paper comparison + exports

------------------------------------------------------------------------

# 10. Definition of Done (MVP)

A user can:

-   Upload a PDF
-   Generate summary with citations
-   Enter Teach Mode with quizzes
-   Generate Reviewer report with claim-evidence matrix
-   Export Markdown and LaTeX
-   Select provider (OpenAI / Anthropic / Google)
