# External Review (gemini)

- Generated at: 2026-02-17T10:22:37+00:00
- Command: `gemini --output-format json`
- Input mode: `stdin`
- Exit code: 0
- Raw file: `REVIEW_EXTERNAL_1.raw.txt`
- Raw SHA256: `7a769fdb9b0b972b71419be007c20e6b13e6bcef3801479bc29156a5076ac17a`

## Raw Output

```text
{
  "session_id": "8b303ccb-3044-4277-80c2-b1d051e9dd39",
  "response": "# Summary\n\nPhase 2 build artifacts for the `PaperTA` system successfully implement the \"Teach Mode Core\" requirements as defined in `docs/contracts/PHASE2_RUNTIME_CONTRACT.md`. The implementation provides deterministic, grounded generation of prerequisites, concept maps, explanations, and quizzes, along with a Socratic question-answering capability. Verification results (18 tests passing, 10/10 checklist items) confirm that the delivery meets the defined acceptance criteria.\n\n# Findings\n\n### MAJOR: Quiz Quality with Limited Context\nIn `src/paperta/teach.py`, the `generate_quiz` function constructs multiple-choice options by collecting unique section names from retrieval hits. If the retrieval returns hits from only one or two sections, the resulting quiz has fewer than the typical four distractors, potentially degrading the educational value.\n> **Evidence:** `src/paperta/teach.py:186-189`\n> ```python\n> section_names = tuple(dict.fromkeys(hit.section for hit in retrieval_result.hits))\n> distractors = tuple(name for name in section_names if name != first_hit.section)\n> options = (first_hit.section,) + distractors[:2] + (NOT_STATED,)\n> ```\n\n### MINOR: Linear Concept Map Simplification\nThe `generate_concept_map` implementation creates a strictly linear chain of edges between sequential nodes. While this satisfies the contract requirement for \"nodes and edges,\" it may oversimplify the conceptual structure of complex papers.\n> **Evidence:** `src/paperta/teach.py:134-142`\n> ```python\n> edges: list[ConceptEdge] = []\n> for left, right in zip(nodes, nodes[1:]):\n>     edges.append(\n>         ConceptEdge(\n>             source=left.label,\n>             target=right.label,\n>             relation=\"builds_on\",\n>             chunk_ids=(left.chunk_ids[0], right.chunk_ids[0]),\n>         )\n>     )\n> ```\n\n### NIT: Socratic Stopword List\nThe stopword list in `src/paperta/teach.py` is manually defined and relatively small. While sufficient for a \"Core\" implementation, it may lead to false-positive matches for very short or common-word queries that bypass the `_STOPWORDS` filter.\n> **Evidence:** `src/paperta/teach.py:27-52`\n\n# Open Questions\n\n1. **Scalability of Grounding**: The current implementation limits retrieval to `top_k` (default 5) and artifacts to the first 3-4 hits. Is this heuristic sufficient for very long papers where prerequisites might be spread across many sections?\n2. **Deterministic Snippets**: The `_snippet` function uses simple truncation. Has there been consideration for sentence-boundary-aware truncation to improve the readability of the generated teaching points?\n\n# Final Verdict\n\n**PASS**\n\nThe Phase 2 build is robust, adheres strictly to the runtime contract, and maintains the high standard of grounding and observability established in Phase 1. The identified findings are primarily related to heuristic simplifications suitable for a \"Core\" phase and do not violate any functional or non-functional requirements.",
  "stats": {
    "models": {
      "gemini-2.5-flash-lite": {
        "api": {
          "totalRequests": 1,
          "totalErrors": 0,
          "totalLatencyMs": 3407
        },
        "tokens": {
          "input": 3395,
          "prompt": 3395,
          "candidates": 115,
          "total": 3875,
          "cached": 0,
          "thoughts": 365,
          "tool": 0
        }
      },
      "gemini-3-flash-preview": {
        "api": {
          "totalRequests": 3,
          "totalErrors": 1,
          "totalLatencyMs": 58776
        },
        "tokens": {
          "input": 15750,
          "prompt": 21280,
          "candidates": 907,
          "total": 27572,
          "cached": 5530,
          "thoughts": 5385,
          "tool": 0
        }
      }
    },
    "tools": {
      "totalCalls": 8,
      "totalSuccess": 8,
      "totalFail": 0,
      "totalDurationMs": 71,
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
          "durationMs": 71,
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
