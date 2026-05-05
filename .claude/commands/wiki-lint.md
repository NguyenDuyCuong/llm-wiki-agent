Health-check the LLM Wiki for issues.

Usage: /wiki-lint

## Token-efficient workflow

Structural checks scan all wiki pages — **use `ctx_batch_execute`** so grep output is indexed in the sandbox, not dumped into context. Then use `ctx_search` to query results.

```javascript
// Run all structural checks in one sandbox call
[
  { label: "All wikilinks", command: "grep -roh '\\[\\[[^]]*\\]\\]' wiki/ | sort | uniq -c | sort -rn | head -80" },
  { label: "All page paths", command: "find wiki/ -name '*.md' | grep -Ev '(index|log|overview|lint-report|health-report)\\.md'" },
  { label: "Pages missing inbound links", command: "grep -rL '\\[\\[' wiki/sources/ wiki/entities/ wiki/concepts/ 2>/dev/null" },
  { label: "Index entries", command: "grep -E '^- \\[' wiki/index.md" }
]
```

For semantic checks (contradictions, stale content), `view` only the specific pages flagged by the structural pass — not all pages at once.

## Checks (in order)

Structural (use `ctx_batch_execute` → `ctx_search`):
1. **Orphan pages** — wiki pages with no inbound `[[wikilinks]]` from other pages
2. **Broken links** — `[[WikiLinks]]` pointing to pages that don't exist
3. **Missing entity pages** — names referenced in 3+ pages but lacking their own page

Semantic (read flagged pages with `view`):
4. **Contradictions** — claims that conflict between pages
5. **Stale summaries** — pages not updated after newer sources changed the picture
6. **Data gaps** — important questions the wiki can't answer; suggest specific sources to find

Output a structured markdown lint report. At the end, ask if the user wants it saved to `wiki/lint-report.md`.

Append to wiki/log.md: `## [today's date] lint | Wiki health check`
