# PaperTA

**Evidence-grounded academic paper analysis with optional LLM enhancement.**

PaperTA is a Streamlit-based tool that turns academic papers into structured, citation-backed analyses. Upload a PDF (or paste text), and get bullet-point summaries, full pedagogical walkthroughs, peer-review-style critiques, or cross-paper comparisons -- all with every claim traced back to the source paragraph that supports it.

The core pipeline is fully deterministic: it chunks the paper, runs lexical retrieval against your query, and builds structured outputs with chunk-level citations. When an LLM provider is configured, results are optionally enhanced with richer prose while preserving the evidence grounding.

---

## Features

### Summary Mode
Generates evidence-grounded bullet-point summaries. Each bullet cites the specific text chunks it draws from, and unsupported claims are flagged automatically.

**What you get:** Numbered bullets with `[Section]` citations, unsupported-bullet count, and a downloadable Markdown export.

### Teach Mode
Produces a comprehensive A-to-Z paper walkthrough structured for pedagogical understanding. The paper's sections are reorganized into a learning-friendly order (Problem, Background, Method, Results, Discussion, Limitations) so you can understand the paper without reading the original.

**What you get:** Prerequisite concepts with evidence links, a step-by-step explanation, an auto-generated concept map (nodes + relationships), and quiz items (MCQ + short answer) for self-testing.

### Reviewer Mode
Generates a structured peer-review-style critique with three analysis layers:

- **Critique** -- Strengths, weaknesses, and threats to validity, each backed by source evidence
- **Reproducibility checklist** -- Evaluates dataset availability, code release, hyperparameter reporting, statistical testing, and more. Each item is graded pass/warning/fail with notes and citations
- **Claim-evidence matrix** -- Maps every major claim to its supporting evidence chunks and grades it as supported, mixed, or unsupported

**What you get:** A full reviewer report with evidence anchors, plus a Markdown export suitable for sharing with collaborators.

### Multi-Paper Comparison
Upload 2+ papers and get cross-paper intelligence:

- **Consensus matrix** -- Which claims are agreed upon across papers, which are contradicted, and which appear in only one paper
- **Concept links** -- Maps local terminology in each paper to canonical concept IDs so you can see when different papers discuss the same idea with different names
- **Cross-paper knowledge graph** -- Directed edges showing relationships between concepts across papers (e.g., Paper A's method *extends* Paper B's framework)

### BibTeX Lookup
Search DBLP by title (or auto-detect from uploaded filename) and fetch `.bib` entries with one click. Supports downloading individual BibTeX files.

### Dark Mode
Toggle between light and dark themes via the sidebar switch. All custom UI components (chips, badges, tables, buttons) adapt automatically.

---

## Quick Start

### Install

```bash
pip install -e .
```

To use LLM enhancement (optional):

```bash
pip install -e ".[llm]"
```

### Configure API Keys

Create a `.env` file in the project root (see `.env.example`):

```bash
# Set one or more -- only needed for LLM enhancement
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AI...
```

Or export them directly in your shell. The app works without any keys using the `local` provider (deterministic-only mode).

### Run

```bash
PYTHONPATH=src streamlit run src/paperta/webapp_streamlit_v2.py
```

Open http://localhost:8501 in your browser.

---

## How It Works

### Pipeline Architecture

Every analysis follows the same four-stage pipeline:

```
1. Ingestion        Upload (PDF/TXT/MD) -> section detection -> paragraph chunking
                    Each chunk gets a stable, content-derived ID for citation tracking.

2. Retrieval        Lexical overlap scoring against your query.
                    Returns the top-k most relevant chunks with scores.

3. Analysis         Deterministic structured output (mode-specific):
                    - Summary: grounded bullets with chunk citations
                    - Teach: prerequisites, explanation steps, concept map, quiz
                    - Reviewer: critique, reproducibility checklist, claim matrix
                    - Multi-paper: consensus matrix, concept links, cross-paper graph

4. Enhancement      (Optional) Send deterministic results + evidence to an LLM
                    for richer, more readable prose. Citations are preserved.
```

### Evidence Grounding

Every output -- bullets, critique items, checklist entries, concept nodes, graph edges -- carries `chunk_ids` pointing to the source paragraphs. The UI replaces raw IDs with human-readable labels like `[Introduction]` or `[Method, para 2]`. This lets you verify any claim against the original text.

### PDF Processing

The PDF parser uses `pypdf` for text extraction, then applies heuristic heading detection (numbered headings, Roman numerals, common section names, ALL-CAPS lines) to split text into labeled sections. Falls back to paragraph-based chunking when no headings are found. Noisy headers/footers and page numbers are stripped automatically.

---

## LLM Providers

| Provider | Env Variable | Models |
|----------|-------------|--------|
| OpenAI | `OPENAI_API_KEY` | gpt-4o, gpt-4o-mini, gpt-4.1, gpt-4.1-mini |
| Anthropic | `ANTHROPIC_API_KEY` | claude-3-haiku, claude-3.5-sonnet, claude-sonnet-4 |
| Google | `GOOGLE_API_KEY` | gemini-2.5-flash, gemini-2.5-pro, gemini-2.0-flash |
| Local | *(none)* | deterministic-core (no API key needed) |

Select your provider and model in the sidebar. The app auto-detects whether each provider's API key is configured and shows the status. When using `local`, you get the full deterministic analysis without any external API calls.

---

## Project Structure

```
src/paperta/
  contracts.py              Phase 1 data contracts (SectionInput, Chunk, PipelineResult)
  teach_contracts.py        Phase 2 contracts (PrerequisiteChecklist, ConceptMap, Quiz)
  reviewer_contracts.py     Phase 3 contracts (CritiqueArtifact, ClaimEvidenceMatrix)
  multi_paper_contracts.py  Phase 4 contracts (ConsensusMatrix, CrossPaperGraph)
  ingestion.py              Document chunking with stable content-derived IDs
  retrieval.py              Lexical overlap retrieval engine
  summary.py                Grounded summary generation
  teach.py                  Teach mode: prerequisites, explanation, concept map, quiz
  reviewer.py               Reviewer mode: critique, reproducibility, claim matrix
  multi_paper.py            Multi-paper: concept linking, consensus, cross-paper graph
  pipeline.py               Top-level pipeline orchestration (phases 1-4)
  pdf_utils.py              PDF extraction, section detection, heading heuristics
  llm_providers.py          OpenAI / Anthropic / Google integration + streaming
  webapp_streamlit_v2.py    Streamlit UI (single paper, multi-paper, BibTeX, dark mode)

scripts/
  check_docstrings.py       Google-style docstring linter (used in CI)

tests/
  unit/                     Fast unit tests for each module
  integration/              End-to-end pipeline tests
  negative/                 Boundary and error-case tests
```

---

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests (40 tests)
python3 -m pytest tests/ -v

# Run docstring linter
python3 scripts/check_docstrings.py --paths src/paperta
```

### CI

GitHub Actions runs on every push and PR to `main`:

1. **Docstring check** -- All public functions and classes must have Google-style docstrings with `Args:` and `Returns:`/`Yields:` sections
2. **Test suite** -- All tests in `tests/` must pass on Python 3.11 and 3.12

### Code Conventions

- Frozen dataclasses for all pipeline contracts (immutable, hashable)
- Tuple return types for all collection outputs (no mutable lists leak out)
- Every structured output carries `chunk_ids` for evidence tracing
- `_` prefix on internal helpers; only public API needs docstrings
- No runtime dependencies on LLM providers -- they're imported lazily inside functions

---

## License

MIT
