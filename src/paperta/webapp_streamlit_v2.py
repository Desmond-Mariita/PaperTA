"""PaperTA Studio -- Streamlit web app for academic paper analysis.

Clean light-theme UI with evidence-grounded analysis, LLM enhancement,
human-readable citations, and comprehensive teach mode walkthrough.
"""

from __future__ import annotations

import datetime
import json
import re
import urllib.parse
import urllib.request
from typing import Any

import streamlit as st

from paperta.contracts import SectionInput
from paperta.llm_providers import (
    PROVIDERS,
    enhance_with_llm,
    is_provider_configured,
    teach_enhance_with_llm,
    _to_primitive,
)
from paperta.multi_paper_contracts import PaperInput
from paperta.pdf_utils import (
    detect_sections,
    extract_text_from_upload,
    sections_to_display,
)
from paperta.pipeline import (
    run_phase1_pipeline,
    run_phase2_teach_pipeline,
    run_phase3_reviewer_pipeline,
    run_phase4_multi_paper_pipeline,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Pedagogical category ordering for teach mode
_PEDAGOGY_ORDER: list[tuple[str, str, str]] = [
    (
        "abstract",
        "At a Glance",
        "A brief overview of this paper's purpose, approach, and findings.",
    ),
    (
        "introduction",
        "Problem & Motivation",
        "What problem does this paper address, and why does it matter?",
    ),
    (
        "background",
        "Background & Prerequisites",
        "Key concepts and prior knowledge needed to understand this work.",
    ),
    (
        "related_work",
        "Related Work",
        "How this work relates to and builds upon existing research.",
    ),
    (
        "method",
        "Core Approach",
        "The methodology, framework, or system proposed by the authors.",
    ),
    (
        "experiments",
        "Experimental Setup",
        "How the authors tested and evaluated their approach.",
    ),
    (
        "results",
        "Key Results & Findings",
        "What the experiments revealed.",
    ),
    (
        "discussion",
        "Discussion & Implications",
        "What the results mean and their broader significance.",
    ),
    (
        "limitations",
        "Limitations & Future Work",
        "Acknowledged shortcomings and directions for future research.",
    ),
    (
        "conclusion",
        "Conclusion",
        "The paper's final summary and takeaways.",
    ),
    (
        "other",
        "Additional Sections",
        "Other content from the paper.",
    ),
]


# ---------------------------------------------------------------------------
# Custom CSS (minimal -- let Streamlit light theme handle the rest)
# ---------------------------------------------------------------------------

_CSS_LIGHT = """
<style>
/* Container width */
.main .block-container {
  max-width: 960px;
  padding-top: 1rem;
  padding-bottom: 2rem;
}

/* Chips */
.chip {
  display: inline-block;
  border-radius: 999px;
  padding: 0.18rem 0.6rem;
  font-size: 0.73rem;
  font-weight: 600;
  margin-right: 0.3rem;
  margin-bottom: 0.3rem;
}
.chip-teal { background: rgba(37, 99, 235, 0.08); color: #1d4ed8; }
.chip-amber { background: rgba(245, 158, 11, 0.10); color: #92400e; }
.chip-muted { background: rgba(107, 114, 128, 0.10); color: #6b7280; }

/* Status badge */
.status-ok {
  display: inline-block;
  padding: 0.2rem 0.7rem;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 600;
  background: rgba(16, 185, 129, 0.12);
  color: #065f46;
}
.status-warn {
  display: inline-block;
  padding: 0.2rem 0.7rem;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 600;
  background: rgba(245, 158, 11, 0.10);
  color: #92400e;
}

/* Section preview table */
.section-preview-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.84rem;
}
.section-preview-table th {
  text-align: left;
  padding: 0.4rem 0.6rem;
  border-bottom: 2px solid #e5e7eb;
  color: #6b7280;
  font-weight: 600;
  font-size: 0.76rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.section-preview-table td {
  padding: 0.35rem 0.6rem;
  border-bottom: 1px solid #e5e7eb;
  vertical-align: top;
}
.section-preview-table td.label-cell {
  font-weight: 600;
  white-space: nowrap;
  color: #2563eb;
}
.section-preview-table td.preview-cell {
  color: #6b7280;
  font-size: 0.82rem;
  max-width: 500px;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
"""

_CSS_DARK = """
<style>
/* Container width */
.main .block-container {
  max-width: 960px;
  padding-top: 1rem;
  padding-bottom: 2rem;
}

/* Dark mode overrides */
.stApp { background-color: #0f172a; color: #e2e8f0; }
section[data-testid="stSidebar"] { background-color: #1e293b; }

/* Chips */
.chip {
  display: inline-block;
  border-radius: 999px;
  padding: 0.18rem 0.6rem;
  font-size: 0.73rem;
  font-weight: 600;
  margin-right: 0.3rem;
  margin-bottom: 0.3rem;
}
.chip-teal { background: rgba(96, 165, 250, 0.15); color: #60a5fa; }
.chip-amber { background: rgba(251, 191, 36, 0.15); color: #fbbf24; }
.chip-muted { background: rgba(156, 163, 175, 0.15); color: #9ca3af; }

/* Status badge */
.status-ok {
  display: inline-block;
  padding: 0.2rem 0.7rem;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 600;
  background: rgba(52, 211, 153, 0.15);
  color: #34d399;
}
.status-warn {
  display: inline-block;
  padding: 0.2rem 0.7rem;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 600;
  background: rgba(251, 191, 36, 0.15);
  color: #fbbf24;
}

/* Section preview table */
.section-preview-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.84rem;
}
.section-preview-table th {
  text-align: left;
  padding: 0.4rem 0.6rem;
  border-bottom: 2px solid #374151;
  color: #9ca3af;
  font-weight: 600;
  font-size: 0.76rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.section-preview-table td {
  padding: 0.35rem 0.6rem;
  border-bottom: 1px solid #374151;
  vertical-align: top;
}
.section-preview-table td.label-cell {
  font-weight: 600;
  white-space: nowrap;
  color: #60a5fa;
}
.section-preview-table td.preview-cell {
  color: #9ca3af;
  font-size: 0.82rem;
  max-width: 500px;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _init_session_state() -> None:
    """Initialize session state keys if absent."""
    if "history" not in st.session_state:
        st.session_state.history = []


def _add_to_history(
    mode: str, query: str, provider: str, model: str, md_export: str
) -> None:
    """Append a run record to session history.

    Args:
        mode: Pipeline mode name.
        query: User query.
        provider: Provider used.
        model: Model used.
        md_export: Markdown export string.
    """
    st.session_state.history.append(
        {
            "time": datetime.datetime.now(tz=datetime.timezone.utc).strftime(
                "%H:%M:%S"
            ),
            "mode": mode,
            "query": query[:80],
            "provider": provider,
            "model": model,
            "md_export": md_export,
        }
    )


def _build_citation_labels(payload: dict[str, Any]) -> dict[str, str]:
    """Map chunk_ids to human-readable section-based labels.

    Args:
        payload: Serialized pipeline result containing retrieval_trace.

    Returns:
        Dict mapping chunk_id to label like '[Introduction]' or '[Method, para 2]'.
    """
    labels: dict[str, str] = {}
    if "retrieval_trace" not in payload:
        return labels

    section_chunks: dict[str, list[str]] = {}
    for hit in payload["retrieval_trace"]["hits"]:
        sec = hit.get("section", "")
        cid = hit.get("chunk_id", "")
        if sec and cid:
            section_chunks.setdefault(sec, []).append(cid)

    for sec, cids in section_chunks.items():
        if len(cids) == 1:
            labels[cids[0]] = f"[{sec}]"
        else:
            for i, cid in enumerate(cids, 1):
                labels[cid] = f"[{sec}, para {i}]"

    return labels


def _format_citations(
    chunk_ids: list[str] | tuple[str, ...],
    labels: dict[str, str],
) -> str:
    """Format a list of chunk_ids as human-readable citation string.

    Args:
        chunk_ids: Raw chunk ID strings.
        labels: Mapping from chunk_id to readable label.

    Returns:
        Formatted citation string.
    """
    if not chunk_ids:
        return ""
    parts = [labels.get(cid, f"[{cid[:8]}...]") for cid in chunk_ids]
    return ", ".join(parts)


def _classify_sections(
    sections: tuple[SectionInput, ...],
) -> dict[str, list[SectionInput]]:
    """Classify paper sections into pedagogical categories.

    Args:
        sections: Detected paper sections.

    Returns:
        Dict mapping category to list of matching sections.
    """
    categories: dict[str, list[SectionInput]] = {
        "abstract": [],
        "introduction": [],
        "background": [],
        "method": [],
        "experiments": [],
        "results": [],
        "discussion": [],
        "limitations": [],
        "related_work": [],
        "conclusion": [],
        "other": [],
    }

    for sec in sections:
        name = sec.label.lower().strip()
        if "abstract" in name:
            categories["abstract"].append(sec)
        elif "intro" in name:
            categories["introduction"].append(sec)
        elif any(w in name for w in ("background", "preliminar", "notation")):
            categories["background"].append(sec)
        elif any(
            w in name
            for w in (
                "method", "approach", "model", "framework",
                "algorithm", "architecture", "system", "design",
            )
        ):
            categories["method"].append(sec)
        elif any(
            w in name
            for w in (
                "experiment", "setup", "dataset", "benchmark",
                "evaluation", "implementation",
            )
        ):
            categories["experiments"].append(sec)
        elif any(w in name for w in ("result", "finding", "performance", "analysis")):
            categories["results"].append(sec)
        elif "discussion" in name:
            categories["discussion"].append(sec)
        elif any(w in name for w in ("limitation", "threat", "future")):
            categories["limitations"].append(sec)
        elif any(w in name for w in ("related", "prior", "previous")):
            categories["related_work"].append(sec)
        elif any(w in name for w in ("conclusion", "summary", "closing")):
            categories["conclusion"].append(sec)
        else:
            categories["other"].append(sec)

    return categories


def _replace_hash_citations(text: str, labels: dict[str, str]) -> str:
    """Replace raw hex chunk_id hashes in text with readable labels.

    Args:
        text: LLM output text potentially containing hex chunk_ids.
        labels: Mapping from chunk_id to readable label.

    Returns:
        Text with hashes replaced by readable section names.
    """
    for cid, label in labels.items():
        # Replace [chunk_id], chunk_id, and partial matches
        text = text.replace(f"[{cid}]", label)
        text = text.replace(cid, label.strip("[]"))
    return text


def _chips_html(pairs: list[tuple[str, str, str]]) -> str:
    """Build HTML for a row of chips.

    Args:
        pairs: List of (label, value, color_class) tuples.

    Returns:
        HTML string.
    """
    parts = []
    for label, value, cls in pairs:
        parts.append(f'<span class="chip {cls}">{label}: {value}</span>')
    return "".join(parts)


def _section_card(icon: str, icon_cls: str, title: str) -> None:
    """Render a result-section header using native Streamlit.

    Args:
        icon: Unused (kept for API compat).
        icon_cls: Unused (kept for API compat).
        title: Section title text.
    """
    st.subheader(title)


def _sections_table_html(sections: tuple[SectionInput, ...]) -> str:
    """Build an HTML table showing detected sections.

    Args:
        sections: Parsed section inputs.

    Returns:
        HTML table string.
    """
    rows = ""
    for s in sections:
        preview = s.text[:160].replace("\n", " ").replace("<", "&lt;").strip()
        if len(s.text) > 160:
            preview += "..."
        label = s.label.replace("<", "&lt;")
        chars = f"{len(s.text):,}"
        rows += (
            f"<tr>"
            f'<td class="label-cell">{label}</td>'
            f'<td class="preview-cell">{preview}</td>'
            f"<td>{chars}</td>"
            f"</tr>"
        )
    return (
        '<table class="section-preview-table">'
        "<thead><tr><th>Section</th><th>Preview</th><th>Chars</th></tr></thead>"
        f"<tbody>{rows}</tbody></table>"
    )


# ---------------------------------------------------------------------------
# Markdown export builders
# ---------------------------------------------------------------------------


def _export_summary(payload: dict[str, Any], query: str) -> str:
    """Build Markdown export for summary mode with readable citations.

    Args:
        payload: Serialized pipeline result.
        query: User query.

    Returns:
        Markdown string.
    """
    labels = _build_citation_labels(payload)
    lines = [
        f"# PaperTA Summary\n",
        f"**Paper:** {payload['paper_id']}  ",
        f"**Query:** {query}\n",
        "## Evidence-Grounded Summary\n",
    ]
    for idx, b in enumerate(payload["summary"]["bullets"], 1):
        cits = _format_citations(b["chunk_ids"], labels) or "none"
        lines.append(f"{idx}. {b['text']}  \n   *Sources: {cits}*\n")
    lines.append(
        f"\n---\n*Bullets: {payload['summary_bullet_count']} | "
        f"Unsupported: {payload['unsupported_bullet_count']}*\n"
    )
    return "\n".join(lines)


def _export_teach(
    payload: dict[str, Any],
    query: str,
    sections: tuple[SectionInput, ...] = (),
) -> str:
    """Build Markdown export for teach mode (pedagogical walkthrough).

    Args:
        payload: Serialized pipeline result.
        query: User query.
        sections: Original paper sections.

    Returns:
        Markdown string.
    """
    labels = _build_citation_labels(payload)
    lines = [
        f"# PaperTA -- Comprehensive Paper Walkthrough\n",
        f"**Paper:** {payload['paper_id']}  ",
        f"**Objective:** {query}\n",
    ]

    if sections:
        classified = _classify_sections(sections)
        section_num = 0
        for cat_key, cat_title, cat_desc in _PEDAGOGY_ORDER:
            cat_sections = classified.get(cat_key, [])
            if not cat_sections:
                continue
            section_num += 1
            lines.append(f"\n## {section_num}. {cat_title}\n")
            lines.append(f"*{cat_desc}*\n")
            for sec in cat_sections:
                text = sec.text.strip()
                if not text:
                    continue
                if len(cat_sections) > 1:
                    lines.append(f"### {sec.label}\n")
                lines.append(f"{text}\n")
                # Evidence citations
                matching = []
                if "retrieval_trace" in payload:
                    for hit in payload["retrieval_trace"]["hits"]:
                        if hit.get("section", "") == sec.label:
                            matching.append(hit["chunk_id"])
                if matching:
                    cits = _format_citations(matching, labels)
                    lines.append(f"*Evidence: {cits}*\n")
    else:
        lines.append("## Key Background\n")
        for item in payload["prerequisites"]["items"]:
            cits = _format_citations(item["chunk_ids"], labels) or "none"
            lines.append(
                f"- **{item['concept']}**: {item['reason']}  \n  *Sources: {cits}*\n"
            )
        lines.append("## Main Ideas\n")
        for idx, s in enumerate(payload["explanation"]["steps"], 1):
            cits = _format_citations(s["chunk_ids"], labels)
            line = f"{idx}. {s['text']}"
            if cits:
                line += f"  \n   *Sources: {cits}*"
            lines.append(line)

    if payload["concept_map"]["nodes"]:
        lines.append("\n## Key Concepts\n")
        for n in payload["concept_map"]["nodes"]:
            cits = _format_citations(n["chunk_ids"], labels)
            entry = f"- **{n['label']}**"
            if cits:
                entry += f" {cits}"
            lines.append(entry)
        if payload["concept_map"]["edges"]:
            lines.append("\n**Relationships:**\n")
            for e in payload["concept_map"]["edges"]:
                lines.append(f"- {e['source']} *{e['relation']}* {e['target']}")

    lines.append(
        f"\n---\n*Concepts: {payload['concept_count']} | "
        f"Unsupported: {payload['unsupported_response_count']}*\n"
    )
    return "\n".join(lines)


def _export_reviewer(payload: dict[str, Any], query: str) -> str:
    """Build Markdown export for reviewer mode with readable citations.

    Args:
        payload: Serialized pipeline result.
        query: User query.

    Returns:
        Markdown string.
    """
    labels = _build_citation_labels(payload)
    lines = [
        f"# PaperTA Reviewer Report\n",
        f"**Paper:** {payload['paper_id']}  ",
        f"**Query:** {query}\n",
    ]
    for section_name in ("strengths", "weaknesses", "threats_to_validity"):
        title = section_name.replace("_", " ").title()
        lines.append(f"## {title}\n")
        for item in payload["critique"][section_name]:
            cits = _format_citations(item["chunk_ids"], labels) or "none"
            lines.append(f"- {item['text']}  \n  *Evidence: {cits}*\n")
    lines.append("## Reproducibility Checklist\n")
    lines.append("| Item | Status | Notes | Evidence |")
    lines.append("|------|--------|-------|----------|")
    for r in payload["reproducibility"]["items"]:
        cits = _format_citations(r.get("chunk_ids", []), labels) or "--"
        lines.append(
            f"| {r['label']} | {r['status']} | {r['notes']} | {cits} |"
        )
    lines.append("\n## Claim-Evidence Matrix\n")
    lines.append("| Claim | Grade | Notes | Evidence |")
    lines.append("|-------|-------|-------|----------|")
    for row in payload["claim_matrix"]["rows"]:
        cits = _format_citations(
            row.get("evidence_chunk_ids", []), labels
        ) or "--"
        lines.append(
            f"| {row['claim']} | {row['support_grade']} "
            f"| {row['notes']} | {cits} |"
        )
    lines.append(
        f"\n---\n*Claims: {payload['claim_count']} | "
        f"Unsupported: {payload['unsupported_claim_count']}*\n"
    )
    return "\n".join(lines)


def _export_multi(payload: dict[str, Any], query: str) -> str:
    """Build Markdown export for multi-paper mode with readable citations.

    Args:
        payload: Serialized pipeline result.
        query: User query.

    Returns:
        Markdown string.
    """
    labels = _build_multi_citation_labels(payload)
    lines = [
        "# PaperTA Multi-Paper Analysis\n",
        f"**Query:** {query}  ",
        f"**Papers:** {payload['paper_count']}\n",
        "## Consensus Matrix\n",
    ]
    for row in payload["consensus"]["rows"]:
        pids = ", ".join(row["paper_ids"])
        cits = _format_citations(row.get("evidence_chunk_ids", []), labels) or "--"
        lines.append(f"- **{row['claim']}** ({row['label']})")
        lines.append(f"  Papers: {pids} | Evidence: {cits}")
        if row["notes"]:
            lines.append(f"  {row['notes']}")
        lines.append("")
    lines.append("\n## Concept Links\n")
    for c in payload["concept_links"]["concepts"]:
        cits = _format_citations(c.get("chunk_ids", []), labels)
        entry = (
            f"- **{c['local_name']}** ({c['paper_id']}) "
            f"-> `{c['global_concept_id']}`"
        )
        if cits:
            entry += f"  \n  Evidence: {cits}"
        lines.append(entry)
    lines.append("\n## Cross-Paper Graph\n")
    for e in payload["graph"]["edges"]:
        cits = _format_citations(e.get("evidence_chunk_ids", []), labels)
        entry = f"- {e['source']} **{e['relation']}** {e['target']}"
        if cits:
            entry += f"  \n  Evidence: {cits}"
        lines.append(entry)
    lines.append(
        f"\n---\n*Consensus claims: {payload['consensus_claim_count']} | "
        f"Graph edges: {payload['graph_edge_count']} | "
        f"Unsupported: {payload['unsupported_entry_count']}*\n"
    )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Result renderers
# ---------------------------------------------------------------------------


def _render_summary(payload: dict[str, Any]) -> None:
    """Render summary mode results with readable citations.

    Args:
        payload: Serialized PipelineResult.
    """
    labels = _build_citation_labels(payload)
    _section_card("S", "teal", "Evidence-Grounded Summary")
    for idx, bullet in enumerate(payload["summary"]["bullets"], 1):
        cits = _format_citations(bullet["chunk_ids"], labels)
        st.markdown(f"**{idx}.** {bullet['text']}")
        if cits:
            st.caption(f"Sources: {cits}")
    st.markdown(
        f'<span class="status-ok">Bullets: {payload["summary_bullet_count"]}</span> '
        f'<span class="status-warn">Unsupported: {payload["unsupported_bullet_count"]}</span>',
        unsafe_allow_html=True,
    )


def _render_teach(
    payload: dict[str, Any], sections: tuple[SectionInput, ...] = ()
) -> None:
    """Render teach mode as a pedagogically structured paper walkthrough.

    Organizes paper sections into a pedagogical structure (Problem,
    Background, Method, Results, etc.) so the reader gains complete
    understanding without reading the original paper.

    Args:
        payload: Serialized TeachPipelineResult.
        sections: Original paper sections for full walkthrough.
    """
    labels = _build_citation_labels(payload)
    _section_card("T", "teal", "Comprehensive Paper Walkthrough")
    st.caption(
        "Read through the sections below for a complete understanding "
        "of this paper from start to finish."
    )

    if sections:
        classified = _classify_sections(sections)
        section_num = 0

        for cat_key, cat_title, cat_desc in _PEDAGOGY_ORDER:
            cat_sections = classified.get(cat_key, [])
            if not cat_sections:
                continue

            section_num += 1
            st.markdown(f"### {section_num}. {cat_title}")
            st.caption(cat_desc)

            for sec in cat_sections:
                text = sec.text.strip()
                if not text:
                    continue

                # Show original section label when there are multiple
                # sections in the same category
                if len(cat_sections) > 1:
                    st.markdown(f"**{sec.label}**")

                # Render full text as readable paragraphs
                paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
                for para in paragraphs if paragraphs else [text]:
                    st.markdown(para)

                # Show readable evidence citations for this section
                matching = []
                if "retrieval_trace" in payload:
                    for hit in payload["retrieval_trace"]["hits"]:
                        if hit.get("section", "") == sec.label:
                            matching.append(hit["chunk_id"])
                if matching:
                    cits = _format_citations(matching, labels)
                    st.caption(f"Evidence: {cits}")

            st.markdown("")  # spacing between categories
    else:
        # Fallback: use deterministic pipeline results with readable citations
        st.markdown("### Key Background")
        for item in payload["prerequisites"]["items"]:
            cits = _format_citations(item["chunk_ids"], labels)
            st.markdown(f"- **{item['concept']}**: {item['reason']}")
            if cits:
                st.caption(f"Evidence: {cits}")

        st.markdown("### Main Ideas")
        for idx, step in enumerate(payload["explanation"]["steps"], 1):
            cits = _format_citations(step["chunk_ids"], labels)
            st.markdown(f"**{idx}.** {step['text']}")
            if cits:
                st.caption(f"Evidence: {cits}")

    # Key concepts at the end
    if payload["concept_map"]["nodes"]:
        st.markdown("---")
        _section_card("K", "teal", "Key Concepts")
        for node in payload["concept_map"]["nodes"]:
            cits = _format_citations(node["chunk_ids"], labels)
            entry = f"- **{node['label']}**"
            if cits:
                entry += f" {cits}"
            st.markdown(entry)
        if payload["concept_map"]["edges"]:
            st.markdown("**Relationships:**")
            for e in payload["concept_map"]["edges"]:
                st.markdown(f"- {e['source']} *{e['relation']}* {e['target']}")

    st.markdown(
        f'<span class="status-ok">Sections: '
        f'{len(sections) if sections else payload["concept_count"]}</span> '
        f'<span class="status-ok">Concepts: {payload["concept_count"]}</span> '
        f'<span class="status-warn">Unsupported: '
        f'{payload["unsupported_response_count"]}</span>',
        unsafe_allow_html=True,
    )


def _render_reviewer(payload: dict[str, Any]) -> None:
    """Render reviewer mode results with readable citations.

    Args:
        payload: Serialized ReviewerPipelineResult.
    """
    labels = _build_citation_labels(payload)
    section_meta = [
        ("strengths", "teal", "+"),
        ("weaknesses", "amber", "-"),
        ("threats_to_validity", "amber", "!"),
    ]
    for section_name, cls, icon in section_meta:
        title = section_name.replace("_", " ").title()
        _section_card(icon, cls, title)
        for item in payload["critique"][section_name]:
            cits = _format_citations(item["chunk_ids"], labels)
            st.markdown(f"- {item['text']}")
            if cits:
                st.caption(f"Evidence: {cits}")
        st.write("")

    # Reproducibility checklist -- render as formatted list instead of
    # raw dataframe so chunk_ids are replaced with readable labels.
    st.markdown("---")
    _section_card("R", "teal", "Reproducibility Checklist")
    for r in payload["reproducibility"]["items"]:
        status = r["status"]
        if status == "pass":
            icon = "+"
        elif status == "warning":
            icon = "~"
        else:
            icon = "-"
        cits = _format_citations(r.get("chunk_ids", []), labels)
        st.markdown(f"**[{icon}] {r['label'].title()}** -- {status}")
        st.caption(r["notes"])
        if cits:
            st.caption(f"Evidence: {cits}")

    # Claim-evidence matrix -- render as formatted list instead of
    # raw dataframe so evidence_chunk_ids are replaced with readable labels.
    st.markdown("---")
    _section_card("M", "amber", "Claim-Evidence Matrix")
    for row in payload["claim_matrix"]["rows"]:
        grade = row["support_grade"]
        if grade == "supported":
            badge = "status-ok"
        else:
            badge = "status-warn"
        cits = _format_citations(row.get("evidence_chunk_ids", []), labels)
        st.markdown(f"**{row['claim']}**")
        st.markdown(
            f'<span class="{badge}">{grade}</span>',
            unsafe_allow_html=True,
        )
        if row["notes"]:
            st.caption(row["notes"])
        if cits:
            st.caption(f"Evidence: {cits}")
        st.write("")

    st.markdown(
        f'<span class="status-ok">Claims: {payload["claim_count"]}</span> '
        f'<span class="status-warn">Unsupported: {payload["unsupported_claim_count"]}</span> '
        f'<span class="status-ok">Repro items: {payload["reproducibility_item_count"]}</span>',
        unsafe_allow_html=True,
    )


def _build_multi_citation_labels(payload: dict[str, Any]) -> dict[str, str]:
    """Build citation labels across all papers in a multi-paper result.

    Args:
        payload: Serialized MultiPaperPipelineResult.

    Returns:
        Dict mapping chunk_id to readable label like '[paper-a / Intro]'.
    """
    labels: dict[str, str] = {}
    for ppr in payload.get("per_paper_retrieval", []):
        pid = ppr["paper_id"]
        section_chunks: dict[str, list[str]] = {}
        for hit in ppr["retrieval_trace"]["hits"]:
            sec = hit.get("section", "")
            cid = hit.get("chunk_id", "")
            if sec and cid:
                section_chunks.setdefault(sec, []).append(cid)
        for sec, cids in section_chunks.items():
            if len(cids) == 1:
                labels[cids[0]] = f"[{pid} / {sec}]"
            else:
                for i, cid in enumerate(cids, 1):
                    labels[cid] = f"[{pid} / {sec}, para {i}]"
    return labels


def _render_multi(payload: dict[str, Any]) -> None:
    """Render multi-paper mode results with readable citations.

    Args:
        payload: Serialized MultiPaperPipelineResult.
    """
    labels = _build_multi_citation_labels(payload)

    # Consensus Matrix
    _section_card("C", "teal", "Consensus Matrix")
    for row in payload["consensus"]["rows"]:
        pids = ", ".join(row["paper_ids"])
        cits = _format_citations(row.get("evidence_chunk_ids", []), labels)
        grade_badge = "status-ok" if row["label"] == "consensus" else "status-warn"
        st.markdown(f"**{row['claim']}**")
        st.markdown(
            f'<span class="{grade_badge}">{row["label"]}</span> '
            f'<span class="chip chip-muted">Papers: {pids}</span>',
            unsafe_allow_html=True,
        )
        if row["notes"]:
            st.caption(row["notes"])
        if cits:
            st.caption(f"Evidence: {cits}")
        st.write("")

    # Concept Links
    st.markdown("---")
    _section_card("L", "teal", "Concept Links")
    for c in payload["concept_links"]["concepts"]:
        cits = _format_citations(c.get("chunk_ids", []), labels)
        st.markdown(
            f"- **{c['local_name']}** ({c['paper_id']}) "
            f"&rarr; `{c['global_concept_id']}`"
        )
        if cits:
            st.caption(f"Evidence: {cits}")

    # Cross-Paper Graph
    st.markdown("---")
    _section_card("G", "amber", "Cross-Paper Graph")
    for e in payload["graph"]["edges"]:
        cits = _format_citations(e.get("evidence_chunk_ids", []), labels)
        st.markdown(f"- {e['source']} **{e['relation']}** {e['target']}")
        if cits:
            st.caption(f"Evidence: {cits}")

    st.markdown(
        f'<span class="status-ok">Papers: {payload["paper_count"]}</span> '
        f'<span class="status-ok">Consensus claims: {payload["consensus_claim_count"]}</span> '
        f'<span class="status-ok">Graph edges: {payload["graph_edge_count"]}</span> '
        f'<span class="status-warn">Unsupported: {payload["unsupported_entry_count"]}</span>',
        unsafe_allow_html=True,
    )


def _try_llm_enhance(
    mode: str, query: str, result: Any, provider: str, model: str
) -> str | None:
    """Attempt LLM enhancement and return Markdown or None.

    Args:
        mode: Pipeline mode.
        query: User query.
        result: Deterministic pipeline result.
        provider: LLM provider name.
        model: Model name.

    Returns:
        Enhanced Markdown string, or None if skipped/failed.
    """
    if provider == "local":
        return None
    if not is_provider_configured(provider):
        return None
    try:
        return enhance_with_llm(
            mode=mode,
            query=query,
            deterministic_result=result,
            provider=provider,
            model=model,
        )
    except Exception as exc:  # noqa: BLE001
        st.warning(f"LLM enhancement failed: {exc}")
        return None


def _try_teach_llm_enhance(
    sections: tuple[SectionInput, ...],
    query: str,
    provider: str,
    model: str,
) -> str | None:
    """Attempt teach-specific LLM enhancement using full paper sections.

    Args:
        sections: Full paper sections.
        query: Learning objective.
        provider: LLM provider name.
        model: Model name.

    Returns:
        LLM-generated comprehensive walkthrough, or None if skipped/failed.
    """
    if provider == "local":
        return None
    if not is_provider_configured(provider):
        return None
    try:
        return teach_enhance_with_llm(
            sections=sections,
            query=query,
            provider=provider,
            model=model,
        )
    except Exception as exc:  # noqa: BLE001
        st.warning(f"LLM teach enhancement failed: {exc}")
        return None


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------


def _render_sidebar() -> tuple[str, str, int, bool]:
    """Render sidebar controls and return selected provider, model, top_k, dark_mode.

    Returns:
        Tuple of (provider, model, top_k, dark_mode).
    """
    with st.sidebar:
        st.markdown("**PaperTA Studio**")
        st.caption("Academic Paper Analysis")

        dark_mode = st.toggle("Dark mode", value=False, key="dark_mode")

        st.markdown("### Provider")
        provider = st.selectbox(
            "LLM Provider",
            list(PROVIDERS.keys()),
            label_visibility="collapsed",
        )
        configured = is_provider_configured(provider)
        if provider != "local":
            if configured:
                st.markdown(
                    '<span class="status-ok">API key configured</span>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<span class="status-warn">API key not set</span>',
                    unsafe_allow_html=True,
                )
                st.caption(
                    "Set the relevant environment variable to enable LLM enhancement."
                )

        st.markdown("### Model")
        model = st.selectbox(
            "Model",
            PROVIDERS[provider],
            label_visibility="collapsed",
        )

        st.markdown("### Retrieval")
        top_k = st.slider("top_k", min_value=1, max_value=20, value=5)
        st.caption(
            "Number of evidence chunks retrieved for grounding."
        )

        st.markdown("---")
        st.markdown("### Run History")
        if st.session_state.history:
            for entry in reversed(st.session_state.history[-10:]):
                st.markdown(
                    f'<div class="history-card">'
                    f'<span class="chip chip-teal">{entry["mode"]}</span>'
                    f'<span class="chip chip-muted">{entry["provider"]}</span>'
                    f'<br><span class="history-time">{entry["time"]}</span> '
                    f'{entry["query"]}'
                    f"</div>",
                    unsafe_allow_html=True,
                )
        else:
            st.caption("No runs yet. Results will appear here.")

    return provider, model, top_k, dark_mode


# ---------------------------------------------------------------------------
# Single Paper Tab
# ---------------------------------------------------------------------------


def _render_single_tab(provider: str, model: str, top_k: int) -> None:
    """Render the single-paper analysis tab.

    Args:
        provider: Selected LLM provider.
        model: Selected model.
        top_k: Retrieval top-k.
    """
    # -- Upload section (full width) --
    st.subheader("Upload Source")

    upload = st.file_uploader(
        "Upload a paper (PDF, TXT, or MD)",
        type=["pdf", "txt", "md"],
        key="single_upload",
    )

    text_fallback = st.text_area(
        "Or paste text directly",
        value="",
        height=100,
        placeholder="Paste paper text here if not uploading a file...",
    )

    # Extract text
    parse_error = None
    source_text = text_fallback
    if upload is not None:
        try:
            source_text = extract_text_from_upload(
                upload.name, upload.getvalue()
            )
            st.markdown(
                f'<span class="status-ok">Loaded: {upload.name} '
                f"({len(source_text):,} chars)</span>",
                unsafe_allow_html=True,
            )
        except Exception as exc:  # noqa: BLE001
            parse_error = str(exc)

    sections = detect_sections(source_text)

    if parse_error:
        st.error(parse_error)

    # Section preview
    with st.expander(
        f"Detected sections ({len(sections)})", expanded=False
    ):
        st.markdown(
            _sections_table_html(sections), unsafe_allow_html=True
        )

    # -- Analysis controls (full width) --
    st.markdown("---")

    mode = st.selectbox(
        "Pipeline Mode",
        ["summary", "teach", "reviewer"],
        format_func=lambda m: {
            "summary": "Summary -- Evidence-grounded bullets",
            "teach": "Teach -- Comprehensive A-Z paper walkthrough",
            "reviewer": "Reviewer -- Critique, reproducibility, claims",
        }[m],
    )

    # Auto-derive paper ID from filename; fall back to generic ID
    if upload is not None:
        paper_id = upload.name.rsplit(".", 1)[0].replace(" ", "_")
    else:
        paper_id = "paper-paste-1"

    # Smart per-mode default queries
    _MODE_DEFAULTS = {
        "summary": "key findings and contributions",
        "teach": "comprehensive understanding of the entire paper",
        "reviewer": "claims, evidence quality, and methodology",
    }
    query = st.text_input(
        "Focus (optional -- leave blank for automatic)",
        value="",
        placeholder=_MODE_DEFAULTS.get(mode, ""),
    )
    if not query.strip():
        query = _MODE_DEFAULTS.get(mode, "key findings")

    run_btn = st.button(
        "Run Analysis", use_container_width=True, key="run_single"
    )

    # -- Results (full width below) --
    if run_btn:
        st.markdown("---")
        with st.spinner("Running deterministic pipeline..."):
            try:
                if mode == "summary":
                    result = run_phase1_pipeline(
                        paper_id=paper_id,
                        sections=sections,
                        query=query,
                        top_k=top_k,
                    )
                elif mode == "teach":
                    result = run_phase2_teach_pipeline(
                        paper_id=paper_id,
                        sections=sections,
                        objective=query,
                        top_k=top_k,
                    )
                else:
                    result = run_phase3_reviewer_pipeline(
                        paper_id=paper_id,
                        sections=sections,
                        review_query=query,
                        top_k=top_k,
                    )
            except Exception as exc:  # noqa: BLE001
                st.error(f"Pipeline error: {exc}")
                return

        payload = _to_primitive(result)

        # Chips row
        st.markdown(
            _chips_html(
                [
                    ("mode", mode, "chip-teal"),
                    ("provider", provider, "chip-teal"),
                    ("model", model, "chip-muted"),
                    ("top_k", str(top_k), "chip-muted"),
                ]
            ),
            unsafe_allow_html=True,
        )
        st.write("")

        # Render deterministic results
        if mode == "summary":
            _render_summary(payload)
            md_export = _export_summary(payload, query)
        elif mode == "teach":
            _render_teach(payload, sections)
            md_export = _export_teach(payload, query, sections)
        else:
            _render_reviewer(payload)
            md_export = _export_reviewer(payload, query)

        # LLM enhancement
        if provider != "local":
            st.markdown("---")
            if mode == "teach":
                # Teach mode: send full paper sections for comprehensive walkthrough
                with st.spinner(
                    f"Generating comprehensive walkthrough with {provider}/{model}..."
                ):
                    llm_text = _try_teach_llm_enhance(
                        sections, query, provider, model
                    )
            else:
                with st.spinner(f"Enhancing with {provider}/{model}..."):
                    llm_text = _try_llm_enhance(
                        mode, query, result, provider, model
                    )
            if llm_text:
                # Replace raw hex chunk_ids with readable section labels
                llm_text = _replace_hash_citations(
                    llm_text, _build_citation_labels(payload)
                )
                if mode == "teach":
                    st.subheader("LLM-Generated Comprehensive Walkthrough")
                else:
                    st.subheader("LLM-Enhanced Analysis")
                st.caption(f"{provider} / {model}")
                st.markdown(llm_text)
                md_export += (
                    f"\n\n---\n\n## LLM-Enhanced Analysis\n\n{llm_text}\n"
                )

        # Evidence trace with readable labels
        with st.expander("Evidence Trace"):
            if "retrieval_trace" in payload:
                trace_labels = _build_citation_labels(payload)
                for hit in payload["retrieval_trace"]["hits"]:
                    label = trace_labels.get(
                        hit["chunk_id"], hit["chunk_id"]
                    )
                    st.markdown(
                        f"**{label}** (score: {hit['score']}, "
                        f"section: {hit['section']})"
                    )
                    st.caption(hit["text"][:300])

        # Debug JSON
        with st.expander("Debug JSON"):
            st.json({"result": payload})

        # Export
        st.download_button(
            label="Download as Markdown",
            data=md_export,
            file_name=f"paperta_{mode}_{paper_id}.md",
            mime="text/markdown",
        )

        _add_to_history(mode, query, provider, model, md_export)


# ---------------------------------------------------------------------------
# Multi Paper Tab
# ---------------------------------------------------------------------------


def _render_multi_tab(provider: str, model: str, top_k: int) -> None:
    """Render the multi-paper analysis tab.

    Args:
        provider: Selected LLM provider.
        model: Selected model.
        top_k: Retrieval top-k.
    """
    st.subheader("Upload Multiple Papers")
    st.caption("Upload 2+ papers (PDF, TXT, or MD) for cross-paper analysis")

    uploads = st.file_uploader(
        "Upload papers (PDF, TXT, or MD)",
        type=["pdf", "txt", "md"],
        accept_multiple_files=True,
        key="multi_upload",
    )

    # Build papers from uploads
    paper_inputs: list[PaperInput] = []

    if uploads:
        for idx, f in enumerate(uploads):
            try:
                text = extract_text_from_upload(f.name, f.getvalue())
                secs = detect_sections(text)
                pid = f.name.rsplit(".", 1)[0].replace(" ", "_")
                paper_inputs.append(PaperInput(paper_id=pid, sections=secs))
                st.markdown(
                    f'<span class="status-ok">{f.name}: '
                    f"{len(secs)} sections, {len(text):,} chars</span>",
                    unsafe_allow_html=True,
                )
            except Exception as exc:  # noqa: BLE001
                st.error(f"Error processing {f.name}: {exc}")

    st.markdown("---")

    query_multi = st.text_input(
        "Focus (optional -- leave blank for automatic)",
        value="",
        placeholder="shared findings, consensus, and disagreements",
        key="multi_query",
    )
    if not query_multi.strip():
        query_multi = "shared findings, consensus, and disagreements"

    run_multi = st.button(
        "Run Cross-Paper Analysis",
        use_container_width=True,
        key="run_multi",
    )

    if run_multi:
        if len(paper_inputs) < 2:
            st.warning("Please upload at least 2 papers.")
            return

        papers = tuple(paper_inputs)

        st.markdown("---")
        with st.spinner("Running multi-paper pipeline..."):
            try:
                result = run_phase4_multi_paper_pipeline(
                    papers=papers,
                    query=query_multi,
                    top_k=top_k,
                )
            except Exception as exc:  # noqa: BLE001
                st.error(f"Pipeline error: {exc}")
                return

        payload = _to_primitive(result)

        # Chips
        st.markdown(
            _chips_html(
                [
                    ("mode", "multi_paper", "chip-teal"),
                    ("papers", str(payload["paper_count"]), "chip-teal"),
                    ("provider", provider, "chip-muted"),
                    ("model", model, "chip-muted"),
                ]
            ),
            unsafe_allow_html=True,
        )
        st.write("")

        _render_multi(payload)

        md_export = _export_multi(payload, query_multi)

        # LLM enhancement
        if provider != "local":
            st.markdown("---")
            with st.spinner(f"Enhancing with {provider}/{model}..."):
                llm_text = _try_llm_enhance(
                    "multi_paper", query_multi, result, provider, model
                )
            if llm_text:
                multi_labels = _build_multi_citation_labels(payload)
                llm_text = _replace_hash_citations(llm_text, multi_labels)
                st.subheader("LLM-Enhanced Analysis")
                st.caption(f"{provider} / {model}")
                st.markdown(llm_text)
                md_export += (
                    f"\n\n---\n\n## LLM-Enhanced Analysis\n\n{llm_text}\n"
                )

        # Per-paper retrieval traces with readable labels
        with st.expander("Per-Paper Retrieval Traces"):
            multi_labels = _build_multi_citation_labels(payload)
            for ppr in payload.get("per_paper_retrieval", []):
                st.markdown(f"**{ppr['paper_id']}**")
                for hit in ppr["retrieval_trace"]["hits"]:
                    label = multi_labels.get(
                        hit["chunk_id"], hit["chunk_id"]
                    )
                    st.markdown(
                        f"- {label} (score: {hit['score']})"
                    )
                    st.caption(hit["text"][:200])

        # Debug JSON
        with st.expander("Debug JSON"):
            st.json({"result": payload})

        # Export
        st.download_button(
            label="Download as Markdown",
            data=md_export,
            file_name="paperta_multi_paper.md",
            mime="text/markdown",
        )

        _add_to_history(
            "multi_paper", query_multi, provider, model, md_export
        )


# ---------------------------------------------------------------------------
# DBLP BibTeX lookup
# ---------------------------------------------------------------------------


def _clean_title_for_search(filename: str) -> str:
    """Extract a search-friendly title from a filename.

    Strips extension, replaces underscores/separators with spaces,
    and removes non-alphanumeric clutter.

    Args:
        filename: Uploaded file name.

    Returns:
        Cleaned title string suitable for DBLP search.
    """
    # Strip extension
    name = filename.rsplit(".", 1)[0] if "." in filename else filename
    # Replace common separators with spaces
    name = name.replace("___", " ").replace("__", " ").replace("_", " ")
    name = name.replace("-", " ")
    # Remove non-alphanumeric except spaces
    name = re.sub(r"[^a-zA-Z0-9 ]", " ", name)
    # Collapse whitespace
    name = re.sub(r"\s+", " ", name).strip()
    return name


def _dblp_search(query: str, max_results: int = 5) -> list[dict[str, Any]]:
    """Search DBLP for publications matching query.

    Args:
        query: Search query string.
        max_results: Maximum number of results to return.

    Returns:
        List of hit dicts with keys: title, authors, venue, year, key, doi, url.
    """
    encoded = urllib.parse.quote(query)
    api_url = (
        f"https://dblp.org/search/publ/api"
        f"?q={encoded}&format=json&h={max_results}"
    )
    req = urllib.request.Request(
        api_url, headers={"User-Agent": "PaperTA-Studio/1.0"}
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    hits_container = data.get("result", {}).get("hits", {})
    raw_hits = hits_container.get("hit", [])
    if isinstance(raw_hits, dict):
        raw_hits = [raw_hits]

    results = []
    for hit in raw_hits:
        info = hit.get("info", {})
        # Parse authors
        authors_data = info.get("authors", {}).get("author", [])
        if isinstance(authors_data, dict):
            authors_data = [authors_data]
        author_names = [a.get("text", "") for a in authors_data]

        results.append(
            {
                "title": info.get("title", ""),
                "authors": author_names,
                "venue": info.get("venue", ""),
                "year": info.get("year", ""),
                "key": info.get("key", ""),
                "doi": info.get("doi", ""),
                "url": info.get("ee", ""),
                "type": info.get("type", ""),
            }
        )
    return results


def _dblp_fetch_bibtex(key: str) -> str:
    """Fetch BibTeX entry from DBLP by record key.

    Args:
        key: DBLP record key (e.g. 'conf/acl/JacoviG20').

    Returns:
        BibTeX string.
    """
    bib_url = f"https://dblp.org/rec/{key}.bib"
    req = urllib.request.Request(
        bib_url, headers={"User-Agent": "PaperTA-Studio/1.0"}
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.read().decode("utf-8")


def _render_bibtex_tab() -> None:
    """Render the DBLP BibTeX lookup tab."""
    st.subheader("DBLP BibTeX Lookup")
    st.caption(
        "Upload a paper or enter a title to fetch its BibTeX citation from DBLP."
    )

    upload = st.file_uploader(
        "Upload a paper to auto-detect title",
        type=["pdf", "txt", "md"],
        key="bibtex_upload",
    )

    # When a new file is uploaded, push the cleaned title into the
    # text_input's session state so it actually updates the widget.
    if upload is not None:
        new_title = _clean_title_for_search(upload.name)
        prev = st.session_state.get("_prev_bibtex_file", "")
        if upload.name != prev:
            st.session_state["_prev_bibtex_file"] = upload.name
            st.session_state["bibtex_title"] = new_title
            # Clear stale results from previous search
            st.session_state.pop("dblp_results", None)
            st.session_state.pop("dblp_bibtex", None)
            st.rerun()

    title_query = st.text_input(
        "Paper title",
        placeholder="Enter paper title to search DBLP...",
        key="bibtex_title",
    )

    search_btn = st.button(
        "Search DBLP", use_container_width=True, key="bibtex_search"
    )

    # Persist search results and fetched bibtex in session state
    if search_btn and title_query.strip():
        with st.spinner("Searching DBLP..."):
            try:
                st.session_state["dblp_results"] = _dblp_search(
                    title_query.strip()
                )
                st.session_state["dblp_bibtex"] = {}
            except Exception as exc:  # noqa: BLE001
                st.error(f"DBLP search failed: {exc}")
                st.session_state["dblp_results"] = []
    elif search_btn:
        st.warning("Please enter a paper title or upload a file.")

    # Display results
    results = st.session_state.get("dblp_results", [])
    if not results:
        return

    st.markdown(f"**Found {len(results)} result(s):**")
    st.markdown("---")

    for idx, hit in enumerate(results):
        authors_str = (
            ", ".join(hit["authors"]) if hit["authors"] else "Unknown"
        )
        st.markdown(
            f"**{idx + 1}. {hit['title']}**  \n"
            f"{authors_str} -- *{hit['venue']}* ({hit['year']})"
        )
        if hit.get("url"):
            st.caption(hit["url"])

        bib_key = hit.get("key", "")
        fetched = st.session_state.get("dblp_bibtex", {})

        if bib_key in fetched:
            # Already fetched -- show it
            st.code(fetched[bib_key], language="bibtex")
            st.download_button(
                label="Download .bib",
                data=fetched[bib_key],
                file_name=f"{bib_key.replace('/', '_')}.bib",
                mime="application/x-bibtex",
                key=f"dl_bib_{idx}",
            )
        else:
            if st.button("Get BibTeX", key=f"bib_{idx}"):
                with st.spinner(f"Fetching BibTeX..."):
                    try:
                        bibtex = _dblp_fetch_bibtex(bib_key)
                        st.session_state.setdefault("dblp_bibtex", {})[
                            bib_key
                        ] = bibtex
                        st.rerun()
                    except Exception as exc:  # noqa: BLE001
                        st.error(f"Failed to fetch BibTeX: {exc}")

        st.markdown("---")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    """Render the PaperTA Studio web application."""
    st.set_page_config(
        page_title="PaperTA Studio",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    _init_session_state()

    # Sidebar (rendered first so dark_mode is available for CSS)
    provider, model, top_k, dark_mode = _render_sidebar()

    st.markdown(_CSS_DARK if dark_mode else _CSS_LIGHT, unsafe_allow_html=True)

    # Hero banner
    st.title("PaperTA Studio")
    st.caption(
        "Upload academic papers and run evidence-grounded analysis. "
        "Summary, Teach, Reviewer, and Multi-Paper workflows "
        "with optional LLM enhancement."
    )

    # Main tabs
    tab_single, tab_multi, tab_bib = st.tabs(
        ["Single Paper", "Multi-Paper Comparison", "BibTeX Lookup"]
    )

    with tab_single:
        _render_single_tab(provider, model, top_k)

    with tab_multi:
        _render_multi_tab(provider, model, top_k)

    with tab_bib:
        _render_bibtex_tab()


if __name__ == "__main__":
    main()
