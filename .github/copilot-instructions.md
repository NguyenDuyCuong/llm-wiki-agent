# LLM Wiki Agent — Copilot Instructions

## Shell efficiency

Always prefix shell commands with `wsl rtk` to filter/compress output (saves 60–90% tokens):

```bash
wsl rtk git status
wsl rtk git log -10
wsl rtk python tools/health.py
```

Meta commands: `wsl rtk gain`, `wsl rtk gain --history`, `wsl rtk discover`

---

## Token-efficient wiki operations

`wiki/index.md` and `wiki/overview.md` grow large over time. Apply these patterns per workflow:

### wiki-ingest
**Never `view` index.md or overview.md directly.** Dùng slug scan để tìm file chưa ingest, sau đó lấy context:

**Slug scan — tìm file raw chưa ingest (dùng đầu session hoặc batch)**  
`wiki/sources/<slug>.md` = cache phân tích đã lưu. Không đọc lại raw file đã ingest. Scan bằng `ctx_execute`:
```javascript
// ctx_execute (javascript) — so sánh raw/ vs wiki/sources/ để tìm pending
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
```

**Khi đã biết slug cụ thể**, lấy context liên quan:
```javascript
[
  { label: "Check source exists", command: "ls wiki/sources/ | grep <slug>" },
  { label: "Existing related concepts", command: "ls wiki/concepts/ | grep -i <topic>" },
  { label: "Log tail", command: "tail -5 wiki/log.md" }
]
```
Only `view` individual concept/source pages (small). Read index.md/overview.md with `ctx_execute_file` if you need to search them.

### wiki-query
**Never `view` index.md to find relevant pages.** Use `ctx_execute_file` to search it:
```python
# ctx_execute_file — path: wiki/index.md
topic = "<user question keywords>"
matches = [l for l in FILE_CONTENT.split('\n') if any(w in l.lower() for w in topic.lower().split())]
print('\n'.join(matches))
```
This returns only matching lines (~5–15 lines) instead of the full 130+ line index.

### wiki-lint
Structural checks (orphans, broken links) require scanning all pages — **use `ctx_batch_execute`** so grep output is indexed, not dumped into context:
```javascript
[
  { label: "All wikilinks", command: "grep -roh '\\[\\[[^]]*\\]\\]' wiki/ | sort | uniq -c | sort -rn | head -50" },
  { label: "All page slugs", command: "find wiki/ -name '*.md' | grep -v index | grep -v log | grep -v overview" },
  { label: "Pages with no inbound links", command: "grep -rL '\\[\\[' wiki/sources/ wiki/entities/ wiki/concepts/" }
]
```
Then use `ctx_search` to query the indexed results — no raw grep dump in context.

### wiki-graph
Always try `python tools/build_graph.py --open` first (runs entirely in shell, zero context cost). Only fall back to manual if Python deps are missing — in that case use `ctx_execute` to process wikilinks in sandbox:
```python
# ctx_execute — finds all edges without dumping raw grep to context
import subprocess, re, json
out = subprocess.check_output(['grep', '-roh', r'\[\[[^\]]*\]\]', 'wiki/'], text=True)
links = re.findall(r'\[\[([^\]]+)\]\]', out)
print(f"{len(set(links))} unique link targets found")
```

### Rule of thumb
| File / operation | Tool |
|-----------------|------|
| `wiki/index.md`, `wiki/overview.md` | `ctx_execute_file` (search in sandbox) |
| `wiki/sources/*.md`, `wiki/concepts/*.md` | `view` (small, fine) |
| Grep across all wiki pages | `ctx_batch_execute` → `ctx_search` |
| Check if slug exists | `ctx_batch_execute` with `ls \| grep` |
| Raw source files | `view` (read once) |

