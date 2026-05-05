Ingest a source document into the LLM Wiki.

Usage: /wiki-ingest $ARGUMENTS

$ARGUMENTS should be the path to a file in raw/, e.g. `raw/articles/my-article.md`

## Token-efficient workflow

**NEVER `view` wiki/index.md or wiki/overview.md directly** — they grow large and dump everything into context. Use `ctx_batch_execute` instead:

```javascript
// Step 1 — Slug scan: tìm tất cả file raw chưa ingest (O(1) call)
// Dùng ctx_execute thay vì grep từng file
const { execSync } = require('child_process');
const ingested = new Set(
  execSync('ls wiki/sources/').toString().trim().split('\n')
    .map(f => f.replace(/\.md$/, ''))
);
const rawFiles = execSync('ls raw/*.md 2>/dev/null || true').toString()
  .trim().split('\n').filter(Boolean)
  .map(f => f.replace('raw/', '').replace(/\.md$/, ''));
const pending = rawFiles.filter(f => !ingested.has(f));
console.log(pending.length > 0 ? 'Pending:\n' + pending.join('\n') : 'All ingested ✓');

// Step 2 — khi đã biết slug cụ thể, lấy context liên quan:
[
  { label: "Check source exists", command: "ls wiki/sources/ | grep <slug>" },
  { label: "Existing related concepts", command: "ls wiki/concepts/ | grep -i <topic>" },
  { label: "Log tail", command: "tail -5 wiki/log.md" }
]
```

Only `view` small individual pages (concept/entity/source pages are fine). Use `ctx_execute_file` if you need to search index.md or overview.md.

## Steps (in order)

1. **Check existence** — run `ctx_batch_execute` as above; abort if source slug already exists in wiki/sources/
2. **Read source** — `view` the raw source file at the given path
3. **Get wiki context** — use `ctx_execute_file` on wiki/index.md and wiki/overview.md (search, don't dump)
4. **Write** `wiki/sources/<slug>.md` — source page format per CLAUDE.md
5. **Update** `wiki/index.md` — add entry under Sources
6. **Update** `wiki/overview.md` — revise synthesis if warranted
7. **Create/update** entity pages (wiki/entities/) for key people, companies, projects
8. **Create/update** concept pages (wiki/concepts/) for key ideas and frameworks
9. **Flag** any contradictions with existing wiki content
10. **Append** to wiki/log.md: `## [today's date] ingest | <Title>`

After completing all writes, summarize: what was added, which pages were created or updated, and any contradictions found.
