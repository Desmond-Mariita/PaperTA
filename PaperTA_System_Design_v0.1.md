# PaperTA System Design Document

**Version:** 0.1\
**Status:** Draft (Design Loop Artifact)\
**Date:** 2026-02-16

------------------------------------------------------------------------

## 1. Executive Summary

PaperTA is an academic paper summarizer, reviewer, and tutor application
designed to produce grounded, reproducible, and evidence-linked outputs
from uploaded research papers (PDF or text).

It provides:

1.  Short / Medium / Long summaries\
2.  Teach Mode (guided explanation + quizzes + concept mapping)\
3.  Reviewer Mode (evidence-linked critique + claim--evidence table)

The system is designed with deterministic artifacts, strict grounding to
paper content, and reproducible outputs.

------------------------------------------------------------------------

## 2. Problem Definition

### 2.1 User Pain Points

-   Academic papers are dense and time-consuming to understand.
-   LLM summaries often hallucinate or omit limitations.
-   Review-style critiques are usually generic and not evidence-backed.
-   Outputs are non-deterministic and not reproducible.

### 2.2 Failure Modes to Eliminate

-   Hallucinated results not present in paper.
-   Overconfident interpretations without evidence references.
-   Generic review comments.
-   Inconsistent outputs across identical runs.

------------------------------------------------------------------------

## 3. Solution Overview

PaperTA treats each paper as a grounded knowledge base:

1.  Extract and structure the document.
2.  Chunk and embed the content.
3.  Generate outputs via retrieval-grounded generation.
4.  Link claims to evidence.
5.  Fail closed: if not stated in the paper, output "Not stated in the
    paper."

------------------------------------------------------------------------

## 4. Core Modes

### 4.1 Summarize Mode

-   Short (5--10 bullets)
-   Medium (1--2 pages structured)
-   Long (detailed walkthrough)
-   Executive vs Technical toggle
-   All major claims cite paper sections/chunks

### 4.2 Teach Mode

-   Prerequisite checklist
-   Concept map
-   Step-by-step explanation
-   Toy worked example (when applicable)
-   Quiz (MCQ + short answer)
-   Socratic Q&A chat grounded in paper

### 4.3 Reviewer Mode

-   Structured review report:
    -   Summary
    -   Strengths
    -   Weaknesses
    -   Threats to validity
    -   Reproducibility checklist
    -   Questions for authors
-   Claim--Evidence table:
    -   Claim
    -   Supporting section/chunk
    -   Strength rating
    -   Notes
-   Explicit "Not stated" handling

------------------------------------------------------------------------

## 5. Architecture Overview

### 5.1 Components

1.  Streamlit UI\
2.  Document Processing Service\
3.  Retrieval & Embedding Layer\
4.  LLM Orchestration Layer\
5.  Artifact Storage & Caching

### 5.2 Data Flow

Upload → Extract → Chunk → Embed → Index → Generate → Store Artifact

------------------------------------------------------------------------

## 6. System Invariants

1.  Groundedness: All claims must cite extracted content.
2.  No Guessing: If absent from paper, say so.
3.  Determinism: Same input + settings = same output.
4.  Reproducibility: Artifacts are versioned and stored.
5.  Separation of Concerns: Ingestion independent from generation.

------------------------------------------------------------------------

## 7. Phase Plan

### Phase 1

PDF ingestion + grounded summaries.

### Phase 2

Teach Mode implementation.

### Phase 3

Reviewer Mode with evidence linking.

### Phase 4

Glossary, figure/table explanation, export features.

------------------------------------------------------------------------

## 8. Definition of Done (MVP)

-   Upload a PDF.
-   Generate short/medium/long summary with citations.
-   Teach Mode produces lesson + quiz.
-   Reviewer Mode generates structured critique.
-   Export to Markdown and LaTeX.
