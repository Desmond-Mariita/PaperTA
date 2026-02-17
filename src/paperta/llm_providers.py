"""LLM provider integration for enhanced paper analysis.

Supports OpenAI, Anthropic, and Google providers. Falls back to the
deterministic pipeline when no API keys are configured.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Generator

# Auto-load .env from project root if python-dotenv is available
_project_root = Path(__file__).resolve().parent.parent.parent
_env_file = _project_root / ".env"
if _env_file.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(_env_file)
    except ImportError:
        # Manual fallback: parse simple KEY=VALUE lines
        for line in _env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                key, value = key.strip(), value.strip()
                if key and value and key not in os.environ:
                    os.environ[key] = value

# Provider configuration
PROVIDERS: dict[str, tuple[str, ...]] = {
    "openai": ("gpt-4o", "gpt-4o-mini", "gpt-4.1", "gpt-4.1-mini"),
    "anthropic": ("claude-3-haiku-20240307", "claude-3-5-sonnet-20241022", "claude-sonnet-4-20250514"),
    "google": ("gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash"),
    "local": ("deterministic-core",),
}


def get_available_providers() -> dict[str, tuple[str, ...]]:
    """Return providers with their available models.

    Checks for API keys and marks which providers are configured.

    Returns:
        Dict mapping provider name to tuple of model names.
    """
    return PROVIDERS.copy()


def is_provider_configured(provider: str) -> bool:
    """Check if a provider has its API key configured.

    Args:
        provider: Provider name (openai, anthropic, google, local).

    Returns:
        True if the provider's API key is set or provider is 'local'.
    """
    if provider == "local":
        return True
    key_map = {
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "google": "GOOGLE_API_KEY",
    }
    env_var = key_map.get(provider, "")
    return bool(os.environ.get(env_var, "").strip())


def _to_primitive(value: Any) -> Any:
    """Convert dataclass outputs to JSON-serializable primitives.

    Args:
        value: Arbitrary runtime output value.

    Returns:
        JSON-serializable representation.
    """
    if is_dataclass(value) and not isinstance(value, type):
        return _to_primitive(asdict(value))
    if isinstance(value, dict):
        return {k: _to_primitive(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_primitive(v) for v in value]
    return value


def _build_system_prompt(mode: str) -> str:
    """Build system prompt for LLM-enhanced analysis.

    Args:
        mode: Pipeline mode (summary, teach, reviewer, multi_paper).

    Returns:
        System prompt string.
    """
    base = (
        "You are PaperTA, an academic paper analysis assistant. "
        "You produce evidence-grounded outputs with citations to specific text chunks. "
        "Always cite evidence using [chunk_id] notation. "
        "Be precise, scholarly, and faithful to the source material."
    )
    mode_prompts = {
        "summary": (
            f"{base}\n\nGenerate a grounded summary of the paper based on the retrieved evidence. "
            "Each bullet point must cite the chunk(s) it draws from."
        ),
        "teach": (
            f"{base}\n\nGenerate a comprehensive A-to-Z walkthrough of this paper. "
            "The reader should gain a complete understanding without reading the original. "
            "Structure your response with these sections:\n"
            "## TL;DR\n2-3 sentence overview\n"
            "## Problem & Motivation\nWhat problem is addressed and why it matters\n"
            "## Background & Prerequisites\nKey concepts needed\n"
            "## Core Approach\nThe methodology or system proposed\n"
            "## Experimental Setup\nHow it was evaluated\n"
            "## Key Results\nMain findings with specific numbers\n"
            "## Discussion & Implications\nWhat the results mean\n"
            "## Limitations & Future Work\nShortcomings and future directions\n"
            "## Key Takeaways\n3-5 bullet points\n\n"
            "Be thorough - length is not a concern. Cover all important aspects. "
            "Cite sections using [Section Name] notation. "
            "Write in clear, accessible prose."
        ),
        "reviewer": (
            f"{base}\n\nProvide a scholarly review of this paper: "
            "1) Strengths with evidence, "
            "2) Weaknesses with evidence, "
            "3) Threats to validity, "
            "4) Reproducibility assessment, "
            "5) Claim-evidence matrix showing which claims are supported/mixed/unsupported."
        ),
        "multi_paper": (
            f"{base}\n\nAnalyze the relationship between multiple papers: "
            "1) Shared concepts across papers, "
            "2) Consensus and disagreement matrix, "
            "3) Cross-paper knowledge graph."
        ),
    }
    return mode_prompts.get(mode, base)


def _build_user_prompt(mode: str, query: str, evidence: Any) -> str:
    """Build user prompt with evidence context for LLM.

    Args:
        mode: Pipeline mode.
        query: User's query/objective.
        evidence: Deterministic pipeline result (will be serialized).

    Returns:
        User prompt string with evidence context.
    """
    evidence_json = json.dumps(_to_primitive(evidence), indent=2)
    return (
        f"Query: {query}\n\n"
        f"Evidence from deterministic analysis:\n```json\n{evidence_json}\n```\n\n"
        f"Based on this evidence, provide an enhanced {mode} analysis. "
        f"Cite chunk IDs from the evidence in your response."
    )


def enhance_with_llm(
    mode: str,
    query: str,
    deterministic_result: Any,
    provider: str = "openai",
    model: str = "gpt-4o",
) -> str:
    """Enhance deterministic pipeline results with LLM analysis.

    Args:
        mode: Pipeline mode.
        query: User's query/objective.
        deterministic_result: Result from deterministic pipeline.
        provider: LLM provider name.
        model: Model name.

    Returns:
        LLM-enhanced analysis text (Markdown).

    Raises:
        ValueError: If provider is not configured or unsupported.
    """
    if provider == "local":
        return ""

    if not is_provider_configured(provider):
        raise ValueError(
            f"Provider '{provider}' is not configured. "
            f"Set the appropriate API key environment variable."
        )

    system_prompt = _build_system_prompt(mode)
    user_prompt = _build_user_prompt(mode, query, deterministic_result)

    if provider == "openai":
        return _call_openai(model, system_prompt, user_prompt)
    elif provider == "anthropic":
        return _call_anthropic(model, system_prompt, user_prompt)
    elif provider == "google":
        return _call_google(model, system_prompt, user_prompt)
    else:
        raise ValueError(f"Unsupported provider: {provider}")


def stream_with_llm(
    mode: str,
    query: str,
    deterministic_result: Any,
    provider: str = "openai",
    model: str = "gpt-4o",
) -> Generator[str, None, None]:
    """Stream LLM-enhanced analysis token by token.

    Args:
        mode: Pipeline mode.
        query: User's query/objective.
        deterministic_result: Result from deterministic pipeline.
        provider: LLM provider name.
        model: Model name.

    Yields:
        Text chunks as they are generated.
    """
    if provider == "local":
        yield ""
        return

    if not is_provider_configured(provider):
        yield f"[Provider '{provider}' not configured - showing deterministic results only]"
        return

    system_prompt = _build_system_prompt(mode)
    user_prompt = _build_user_prompt(mode, query, deterministic_result)

    if provider == "openai":
        yield from _stream_openai(model, system_prompt, user_prompt)
    elif provider == "anthropic":
        yield from _stream_anthropic(model, system_prompt, user_prompt)
    elif provider == "google":
        yield from _stream_google(model, system_prompt, user_prompt)
    else:
        yield f"[Unsupported provider: {provider}]"


def _call_openai(model: str, system_prompt: str, user_prompt: str) -> str:
    """Call OpenAI API for completion.

    Args:
        model: Model name.
        system_prompt: System message.
        user_prompt: User message.

    Returns:
        Generated text.
    """
    from openai import OpenAI

    client = OpenAI()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        max_tokens=8192,
    )
    return response.choices[0].message.content or ""


def _stream_openai(
    model: str, system_prompt: str, user_prompt: str
) -> Generator[str, None, None]:
    """Stream from OpenAI API.

    Args:
        model: Model name.
        system_prompt: System message.
        user_prompt: User message.

    Yields:
        Text chunks.
    """
    from openai import OpenAI

    client = OpenAI()
    stream = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        max_tokens=8192,
        stream=True,
    )
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


def _call_anthropic(model: str, system_prompt: str, user_prompt: str) -> str:
    """Call Anthropic API for completion.

    Args:
        model: Model name.
        system_prompt: System message.
        user_prompt: User message.

    Returns:
        Generated text.
    """
    import anthropic

    client = anthropic.Anthropic()
    response = client.messages.create(
        model=model,
        max_tokens=8192,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return response.content[0].text


def _stream_anthropic(
    model: str, system_prompt: str, user_prompt: str
) -> Generator[str, None, None]:
    """Stream from Anthropic API.

    Args:
        model: Model name.
        system_prompt: System message.
        user_prompt: User message.

    Yields:
        Text chunks.
    """
    import anthropic

    client = anthropic.Anthropic()
    with client.messages.stream(
        model=model,
        max_tokens=8192,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    ) as stream:
        for text in stream.text_stream:
            yield text


def _call_google(model: str, system_prompt: str, user_prompt: str) -> str:
    """Call Google Gemini API via OpenAI-compatible endpoint.

    Args:
        model: Model name.
        system_prompt: System message.
        user_prompt: User message.

    Returns:
        Generated text.
    """
    from openai import OpenAI

    client = OpenAI(
        api_key=os.environ.get("GOOGLE_API_KEY", ""),
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        max_tokens=8192,
    )
    return response.choices[0].message.content or ""


def _stream_google(
    model: str, system_prompt: str, user_prompt: str
) -> Generator[str, None, None]:
    """Stream from Google Gemini API via OpenAI-compatible endpoint.

    Args:
        model: Model name.
        system_prompt: System message.
        user_prompt: User message.

    Yields:
        Text chunks.
    """
    from openai import OpenAI

    client = OpenAI(
        api_key=os.environ.get("GOOGLE_API_KEY", ""),
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )
    stream = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        max_tokens=8192,
        stream=True,
    )
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


def teach_enhance_with_llm(
    sections: Any,
    query: str,
    provider: str = "openai",
    model: str = "gpt-4o",
) -> str:
    """Generate comprehensive teach walkthrough using full paper sections.

    Sends the entire paper text to the LLM for a thorough pedagogical
    walkthrough, rather than just serialized pipeline snippets.

    Args:
        sections: Paper sections (sequence of SectionInput or similar).
        query: Learning objective.
        provider: LLM provider name.
        model: Model name.

    Returns:
        LLM-generated comprehensive walkthrough (Markdown).

    Raises:
        ValueError: If provider is not configured or unsupported.
    """
    if provider == "local":
        return ""

    if not is_provider_configured(provider):
        raise ValueError(
            f"Provider '{provider}' is not configured. "
            f"Set the appropriate API key environment variable."
        )

    system_prompt = (
        "You are PaperTA, an expert academic paper analyst and educator. "
        "Your task is to produce a comprehensive walkthrough of a research paper "
        "so that a reader can fully understand the paper without reading the original. "
        "Write in clear, accessible prose while maintaining scholarly accuracy.\n\n"
        "Structure your walkthrough as follows:\n"
        "## TL;DR\n2-3 sentence overview of the entire paper.\n\n"
        "## Problem & Motivation\n"
        "What problem is addressed and why it matters to the field.\n\n"
        "## Background & Prerequisites\n"
        "Key concepts and prior knowledge needed to understand this work.\n\n"
        "## Core Approach\n"
        "The methodology, framework, or system proposed. Explain step by step.\n\n"
        "## Experimental Setup\n"
        "How the approach was evaluated: datasets, baselines, metrics.\n\n"
        "## Key Results\n"
        "Main findings with specific numbers, tables, or comparisons when available.\n\n"
        "## Discussion & Implications\n"
        "What the results mean and their broader significance.\n\n"
        "## Limitations & Future Work\n"
        "Acknowledged shortcomings and directions for future research.\n\n"
        "## Key Takeaways\n"
        "3-5 bullet points summarizing the paper's contribution.\n\n"
        "Be thorough - length is not a concern. Cover all important aspects. "
        "Cite specific paper sections using [Section Name] notation throughout."
    )

    section_parts = []
    for sec in sections:
        if hasattr(sec, "label"):
            label, text = sec.label, sec.text
        elif isinstance(sec, dict):
            label, text = sec.get("label", ""), sec.get("text", "")
        else:
            continue
        text = str(text).strip()
        if text:
            section_parts.append(f"### {label}\n{text}")

    full_text = "\n\n".join(section_parts)

    user_prompt = (
        f"Learning Objective: {query}\n\n"
        f"=== FULL PAPER CONTENT ===\n\n{full_text}\n\n"
        f"=== END OF PAPER ===\n\n"
        f"Based on the complete paper above, provide a comprehensive "
        f"walkthrough following the structure specified. Cover every important "
        f"aspect so the reader gains complete understanding."
    )

    if provider == "openai":
        return _call_openai(model, system_prompt, user_prompt)
    elif provider == "anthropic":
        return _call_anthropic(model, system_prompt, user_prompt)
    elif provider == "google":
        return _call_google(model, system_prompt, user_prompt)
    else:
        raise ValueError(f"Unsupported provider: {provider}")
