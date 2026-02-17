# External Review (gemini)

- Generated at: 2026-02-17T10:46:12+00:00
- Command: `gemini --output-format json`
- Input mode: `stdin`
- Exit code: 0
- Raw file: `REVIEW_EXTERNAL_1.raw.txt`
- Raw SHA256: `e84332c93804deb53626eb96bce37135a5b8ca1e213c6913ff03828144df6f82`

## Raw Output

```text
{
  "session_id": "49c2e2ed-3ee9-44ac-96ad-089f6a9d8619",
  "response": "**Summary**\n\nThe Phase 4 Build implementation for multi-paper intelligence is functionally complete and aligns rigorously with the `PHASE4_RUNTIME_CONTRACT.md`. The pipeline successfully integrates ingestion and retrieval across multiple papers, producing deterministic concept links, a consensus matrix, and a cross-paper relationship graph. Observability requirements and fallback text invariants are strictly respected.\n\n**Findings**\n\n- **MINOR: Incomplete Negative Test Coverage**\n  - **Evidence:** `tests/negative/test_phase4_multi_paper_negative.py` lacks tests for empty query strings and non-positive `top_k` values, despite these being explicitly defined as failure modes in the contract.\n  - **Contract Reference:** `docs/contracts/PHASE4_RUNTIME_CONTRACT.md` Failure Modes 2 & 3.\n  - **Code Reference:** `src/paperta/multi_paper.py` lines 145-148 correctly implement these checks, but they are not verified in the negative test suite.\n\n- **MINOR: Restricted Graph Edge Discovery**\n  - **Evidence:** `src/paperta/multi_paper.py` lines 121-122: `for left, right in zip(paper_results, paper_results[1:]):`. \n  - **Detail:** The `build_cross_paper_graph` function only checks for shared concepts between *adjacent* papers in the input sequence. If Paper 1 and Paper 3 share a concept but Paper 2 does not, no `shares_concept` edge is created between Paper 1 and Paper 3. This limits the completeness of the cross-paper graph.\n\n- **NIT: Semantic Ambiguity in Fallback Concept Linking**\n  - **Evidence:** `src/paperta/multi_paper.py` lines 68-75 and 124.\n  - **Detail:** When multiple papers have no retrieval hits, they are assigned the local name `Not stated in the paper.` and the global concept ID `g_not_stated_in`. Consequently, the graph generator creates `shares_concept` edges between these papers, effectively treating \"missing information\" as a shared topical concept.\n\n**Open Questions**\n\n1. Is the adjacent-only paper-paper edge discovery in the graph a deliberate optimization for large paper sets, or should it be expanded to all-pairs comparison to ensure a complete relationship graph?\n2. Should `g_not_stated_in` be explicitly excluded from triggering `shares_concept` edges in the graph to avoid semantically misleading relationships?\n\n**Final Verdict**\n\n**PASS**\n\nThe system is stable, deterministic, and contract-compliant. The identified findings are minor and do not compromise the core functionality or the phase's acceptance criteria. No critical findings.",
  "stats": {
    "models": {
      "gemini-2.5-flash-lite": {
        "api": {
          "totalRequests": 1,
          "totalErrors": 0,
          "totalLatencyMs": 4216
        },
        "tokens": {
          "input": 4087,
          "prompt": 4087,
          "candidates": 191,
          "total": 4634,
          "cached": 0,
          "thoughts": 356,
          "tool": 0
        }
      },
      "gemini-3-flash-preview": {
        "api": {
          "totalRequests": 4,
          "totalErrors": 0,
          "totalLatencyMs": 59145
        },
        "tokens": {
          "input": 20441,
          "prompt": 47947,
          "candidates": 901,
          "total": 54695,
          "cached": 27506,
          "thoughts": 5847,
          "tool": 0
        }
      }
    },
    "tools": {
      "totalCalls": 8,
      "totalSuccess": 8,
      "totalFail": 0,
      "totalDurationMs": 37,
      "totalDecisions": {
        "accept": 8,
        "reject": 0,
        "modify": 0,
        "auto_accept": 0
      },
      "byName": {
        "read_file": {
          "count": 8,
          "success": 8,
          "fail": 0,
          "durationMs": 37,
          "decisions": {
            "accept": 8,
            "reject": 0,
            "modify": 0,
            "auto_accept": 0
          }
        }
      }
    },
    "files": {
      "totalLinesAdded": 0,
      "totalLinesRemoved": 0
    }
  }
}
```
