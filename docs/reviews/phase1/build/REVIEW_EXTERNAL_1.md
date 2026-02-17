# External Review (gemini)

- Generated at: 2026-02-17T02:02:23+00:00
- Command: `gemini --output-format json`
- Input mode: `stdin`
- Exit code: 0
- Raw file: `REVIEW_EXTERNAL_1.raw.txt`
- Raw SHA256: `4779e80b4fdb5776321e2ac5a4855496e5f8555ae8f330747ada8785da03e377`

## Raw Output

```text
{
  "session_id": "6f81c672-5db0-451b-b4d4-f47950be7003",
  "response": "# Phase 1 Build Review - Grounded Summary Pipeline\n\n## Summary\nThe Phase 1 build provides a robust, deterministic implementation of the ingestion and grounded summary pipeline. The codebase strictly adheres to the defined runtime contract, specifically regarding content-hash-based chunk identification, lexical retrieval, and groundedness invariants. Core failure modes (empty inputs, duplicate labels, invalid modes) are correctly handled. However, there is a logical discrepancy in retrieval tie-breaking and a gap in the provided test evidence.\n\n## Findings\n\n### [MAJOR] Retrieval Tie-Break Logic vs. Document Flow\n- **Evidence**: `retrieval.py` line 44: `scored.sort(key=lambda hit: (-hit.score, hit.section, hit.chunk_id))`\n- **Detail**: When retrieval hits have identical scores, the system tie-breaks using the alphabetical order of the section label (`hit.section`). This contradicts the intuitive expectation of \"section association\" (Requirement 3) and the usual document flow (Ingestion Order). If a paper has sections in order `[\"Method\", \"Introduction\"]`, and both contain a hit with score 1, \"Introduction\" will appear first in the summary regardless of its position in the source text.\n- **Impact**: The summary may present information out of document order, potentially confusing users or misrepresenting the paper's logical structure.\n\n### [MAJOR] Integration Test `test_pipeline_uses_ingestion_section_order` is Invalid\n- **Evidence**: `tests/integration/test_phase1_pipeline.py`:\n```python\ndef test_pipeline_uses_ingestion_section_order():\n    result = run_phase1_pipeline(\n        paper_id=\"paper-int-2\",\n        sections=(\n            SectionInput(label=\"Zeta\", text=\"alpha beta\"),\n            SectionInput(label=\"Alpha\", text=\"alpha\"),\n        ),\n        query=\"alpha beta\",\n        mode=\"summary\",\n        top_k=2,\n    )\n    assert result.summary.bullets[0].text.startswith(\"Zeta:\")\n```\n- **Detail**: This test claims to verify ingestion section order, but it actually verifies score priority. \"Zeta\" has a score of 2 (matches \"alpha\" and \"beta\"), while \"Alpha\" has a score of 1. \"Zeta\" comes first because it is a better match, not because of its position in the input. \n- **Impact**: This test masks the alphabetical tie-breaking bug identified above. It gives a false sense of security regarding document-order preservation.\n\n### [MINOR] Incomplete Test Evidence in Snapshot\n- **Evidence**: Checklist items `T-INGEST-UNIT-001`, `T-RETRIEVE-UNIT-001`, `T-RETRIEVE-NEG-001`, and `F-003`.\n- **Detail**: The checklist refers to `tests/unit/test_ingestion.py`, `tests/unit/test_retrieval.py`, and `tests/negative/test_retrieval_negative.py`. However, the source code for these files is entirely absent from the provided build snapshot.\n- **Impact**: While the implementation code exists, the verification of these specific unit and negative tests cannot be performed as part of this external review.\n\n### [NIT] Citation Anchor Visibility in Summary Text\n- **Evidence**: `summary.py` line 38: `text = f\"{hit.section}: {_snippet(hit.text)}\"`\n- **Detail**: Requirement 7 states \"Summary output contains bullets with citation anchors to chunk IDs.\" While the `SummaryBullet` object contains the `chunk_ids` in its metadata, the actual text string rendered for the bullet does not include the ID (e.g., \"[abc12345]\"). \n- **Impact**: If \"output\" refers to the user-facing text, the citation anchor is technically missing from the display, although present in the data structure.\n\n## Open Questions\n1. **Tie-Break Preference**: Should retrieval tie-breaking be updated to use the `section_order` index from `IngestedPaper` to ensure summaries follow the original document's structure?\n2. **Anchor Rendering**: Is there a specific format required for the \"citation anchor\" within the bullet text string (e.g., Markdown brackets or superscripts)?\n\n## Final Verdict\n**PASS WITH FINDINGS**\n\nThe system is functional, deterministic, and safe. The identified major findings relate to logical consistency in ordering and testing gaps rather than functional crashes or security vulnerabilities. Addressing the tie-break logic will align the implementation with the expected behavior of a section-aware assistant.",
  "stats": {
    "models": {
      "gemini-2.5-flash-lite": {
        "api": {
          "totalRequests": 1,
          "totalErrors": 0,
          "totalLatencyMs": 4196
        },
        "tokens": {
          "input": 8026,
          "prompt": 8026,
          "candidates": 76,
          "total": 8480,
          "cached": 0,
          "thoughts": 378,
          "tool": 0
        }
      },
      "gemini-3-flash-preview": {
        "api": {
          "totalRequests": 1,
          "totalErrors": 0,
          "totalLatencyMs": 50134
        },
        "tokens": {
          "input": 12051,
          "prompt": 12051,
          "candidates": 1000,
          "total": 20933,
          "cached": 0,
          "thoughts": 7882,
          "tool": 0
        }
      }
    },
    "tools": {
      "totalCalls": 0,
      "totalSuccess": 0,
      "totalFail": 0,
      "totalDurationMs": 0,
      "totalDecisions": {
        "accept": 0,
        "reject": 0,
        "modify": 0,
        "auto_accept": 0
      },
      "byName": {}
    },
    "files": {
      "totalLinesAdded": 0,
      "totalLinesRemoved": 0
    }
  }
}
```
