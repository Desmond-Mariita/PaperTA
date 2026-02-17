# PaperTA

Evidence-grounded academic paper analysis with optional LLM enhancement.

## Features

- **Summary** -- Bullet-point summaries with chunk-level citations linking every claim to source text
- **Teach** -- Comprehensive A-to-Z paper walkthrough structured for pedagogical understanding
- **Reviewer** -- Strengths, weaknesses, reproducibility checklist, and claim-evidence matrix
- **Multi-Paper** -- Cross-paper consensus matrix, concept links, and knowledge graph
- **BibTeX Lookup** -- Search DBLP by title or uploaded filename and fetch `.bib` entries

All modes produce deterministic, evidence-grounded output first, then optionally enhance with an LLM.

## Quick Start

```bash
# Install core dependencies
pip install -e .

# (Optional) Install LLM provider support
pip install -e ".[llm]"

# Configure at least one LLM provider (or use local/deterministic mode)
export OPENAI_API_KEY="sk-..."
# or
export ANTHROPIC_API_KEY="sk-ant-..."
# or
export GOOGLE_API_KEY="AI..."

# Run the app
PYTHONPATH=src streamlit run src/paperta/webapp_streamlit_v2.py
```

Open http://localhost:8501 in your browser.

## Usage

### Single Paper

1. Upload a PDF, TXT, or Markdown file (or paste text directly)
2. Choose a pipeline mode: **Summary**, **Teach**, or **Reviewer**
3. Optionally set a focus query (sensible defaults are provided)
4. Click **Run Analysis**
5. Download results as Markdown

### Multi-Paper Comparison

1. Switch to the **Multi-Paper Comparison** tab
2. Upload 2+ papers
3. Click **Run Cross-Paper Analysis** to get consensus/disagreement matrices and a cross-paper knowledge graph

### BibTeX Lookup

1. Switch to the **BibTeX Lookup** tab
2. Upload a paper (title is auto-detected from filename) or type a title
3. Click **Search DBLP**, then **Get BibTeX** on the matching result

## LLM Providers

| Provider | Env Variable | Models |
|----------|-------------|--------|
| OpenAI | `OPENAI_API_KEY` | gpt-4o, gpt-4o-mini, gpt-4.1, gpt-4.1-mini |
| Anthropic | `ANTHROPIC_API_KEY` | claude-3-haiku, claude-3.5-sonnet, claude-sonnet-4 |
| Google | `GOOGLE_API_KEY` | gemini-2.5-flash, gemini-2.5-pro, gemini-2.0-flash |
| Local | *(none)* | deterministic-core (no API needed) |

You can also create a `.env` file in the project root with your keys.

## Architecture

```
Upload (PDF/TXT/MD)
  -> Section detection (pdf_utils)
  -> Chunking & retrieval (contracts, pipeline)
  -> Deterministic analysis (pipeline phases 1-4)
  -> [Optional] LLM enhancement (llm_providers)
  -> Streamlit UI (webapp_streamlit_v2)
```

Key source files:

| File | Purpose |
|------|---------|
| `src/paperta/pipeline.py` | Phase 1-4 deterministic pipelines |
| `src/paperta/contracts.py` | Data contracts (SectionInput, etc.) |
| `src/paperta/llm_providers.py` | OpenAI / Anthropic / Google integration |
| `src/paperta/pdf_utils.py` | PDF text extraction and section detection |
| `src/paperta/webapp_streamlit_v2.py` | Streamlit web application |

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
python3 -m pytest tests/ -v

# Run docstring checker
python3 scripts/check_docstrings.py --paths src/paperta
```

### CI Gates

- **Docstrings**: All public functions/classes must have Google-style docstrings with `Args:` and `Returns:`/`Yields:` sections
- **Tests**: All tests in `tests/` must pass

## License

MIT
