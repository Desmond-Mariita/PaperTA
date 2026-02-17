"""Smart PDF section detection and text extraction utilities."""

from __future__ import annotations

import re
from io import BytesIO
from typing import Sequence

from paperta.contracts import SectionInput


# Common academic paper section headings
_HEADING_PATTERNS = [
    r"^(?:abstract)\s*$",
    r"^\d+\.?\s+\w",           # "1 Introduction", "2. Method"
    r"^[IVXLC]+\.?\s+\w",     # Roman numerals: "I. Introduction"
    r"^(?:introduction|background|related\s*work|methodology|method|methods|"
    r"approach|model|experiments?|results?|discussion|conclusion|conclusions|"
    r"acknowledgment|acknowledgement|acknowledgements|references|appendix|"
    r"appendices|supplementary|abstract|evaluation|analysis|limitations|"
    r"future\s*work|ethics|broader\s*impact)\s*$",
]
_HEADING_RE = re.compile("|".join(_HEADING_PATTERNS), re.IGNORECASE | re.MULTILINE)

# Page number / header/footer noise
_PAGE_NUM_RE = re.compile(r"^\s*\d{1,5}\s*$", re.MULTILINE)
_PROCEEDINGS_RE = re.compile(
    r"^.*(?:proceedings|conference|journal|volume|pages?\s+\d).*$",
    re.IGNORECASE | re.MULTILINE,
)


def extract_text_from_pdf(content: bytes) -> str:
    """Extract plain text from PDF bytes using pypdf.

    Args:
        content: Raw PDF file bytes.

    Returns:
        Extracted text content.

    Raises:
        ValueError: If PDF parsing fails.
    """
    from pypdf import PdfReader

    try:
        reader = PdfReader(BytesIO(content))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n\n".join(pages)
    except Exception as exc:
        raise ValueError(f"Unable to parse PDF: {exc}") from exc


def extract_text_from_upload(name: str, content: bytes) -> str:
    """Extract plain text from an uploaded file.

    Args:
        name: File name with extension.
        content: Uploaded file bytes.

    Returns:
        Extracted text content.

    Raises:
        ValueError: If file format is unsupported.
    """
    lower = name.lower()
    if lower.endswith((".txt", ".md")):
        return content.decode("utf-8", errors="ignore")
    if lower.endswith(".pdf"):
        return extract_text_from_pdf(content)
    raise ValueError("Unsupported file type. Use PDF, TXT, or MD.")


def _clean_text(text: str) -> str:
    """Remove common PDF extraction noise.

    Args:
        text: Raw extracted text.

    Returns:
        Cleaned text.
    """
    text = _PAGE_NUM_RE.sub("", text)
    lines = text.splitlines()
    cleaned = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            cleaned.append("")
            continue
        if _PROCEEDINGS_RE.match(stripped) and len(stripped) < 200:
            continue
        cleaned.append(line)
    return "\n".join(cleaned)


def detect_sections(text: str) -> tuple[SectionInput, ...]:
    """Detect academic paper sections from extracted text.

    Uses heuristic heading detection to split text into labeled sections.
    Falls back to paragraph-based chunking if no headings are found.

    Args:
        text: Extracted paper text.

    Returns:
        Tuple of SectionInput with detected labels and text content.
    """
    cleaned = _clean_text(text)
    lines = cleaned.splitlines()

    sections: list[tuple[str, list[str]]] = []
    current_label = "Preamble"
    current_lines: list[str] = []

    for line in lines:
        stripped = line.strip()
        if stripped and _is_heading(stripped):
            if current_lines:
                body = "\n".join(current_lines).strip()
                if body:
                    sections.append((current_label, current_lines[:]))
            current_label = _normalize_heading(stripped)
            current_lines = []
        else:
            current_lines.append(line)

    if current_lines:
        body = "\n".join(current_lines).strip()
        if body:
            sections.append((current_label, current_lines))

    if not sections:
        return _fallback_chunking(cleaned)

    # Deduplicate labels
    seen: dict[str, int] = {}
    result: list[SectionInput] = []
    for label, body_lines in sections:
        body = "\n".join(body_lines).strip()
        if not body or len(body) < 20:
            continue
        if label in seen:
            seen[label] += 1
            label = f"{label} ({seen[label]})"
        else:
            seen[label] = 1
        result.append(SectionInput(label=label, text=body))

    if not result:
        return _fallback_chunking(cleaned)

    # Cap at 20 sections
    return tuple(result[:20])


def _is_heading(line: str) -> bool:
    """Check if a line looks like a section heading.

    Args:
        line: Stripped text line.

    Returns:
        True if the line matches heading patterns.
    """
    if len(line) > 120:
        return False
    if _HEADING_RE.match(line):
        return True
    # Check for short all-caps lines (common heading style)
    if line.isupper() and 3 < len(line) < 60:
        return True
    return False


def _normalize_heading(heading: str) -> str:
    """Normalize a heading string to a clean label.

    Args:
        heading: Raw heading text.

    Returns:
        Cleaned heading label.
    """
    # Remove leading numbers like "1.", "2.1", "III."
    cleaned = re.sub(r"^[\dIVXLC]+[\.\)]\s*", "", heading.strip())
    if not cleaned:
        cleaned = heading.strip()
    return cleaned.strip().title() if len(cleaned) < 80 else cleaned[:77].strip() + "..."


def _fallback_chunking(text: str) -> tuple[SectionInput, ...]:
    """Fall back to paragraph-based chunking when no headings detected.

    Args:
        text: Cleaned text content.

    Returns:
        Tuple of SectionInput based on paragraph splits.
    """
    parts = [p.strip() for p in re.split(r"\n\s*\n+", text) if p.strip()]
    if not parts:
        return (SectionInput(label="Content", text=text.strip() or "(empty)"),)

    # Merge very short paragraphs
    merged: list[str] = []
    buffer = ""
    for part in parts:
        if len(buffer) + len(part) < 1500:
            buffer = f"{buffer}\n\n{part}".strip() if buffer else part
        else:
            if buffer:
                merged.append(buffer)
            buffer = part
    if buffer:
        merged.append(buffer)

    if not merged:
        merged = parts

    return tuple(
        SectionInput(label=f"Section {idx}", text=part)
        for idx, part in enumerate(merged[:20], start=1)
    )


def sections_to_display(sections: Sequence[SectionInput]) -> list[dict[str, str]]:
    """Convert sections to a display-friendly list of dicts.

    Args:
        sections: Parsed section inputs.

    Returns:
        List of dicts with 'label', 'preview', and 'chars' keys.
    """
    result = []
    for s in sections:
        preview = s.text[:200].replace("\n", " ").strip()
        if len(s.text) > 200:
            preview += "..."
        result.append({
            "label": s.label,
            "preview": preview,
            "chars": f"{len(s.text):,}",
        })
    return result
