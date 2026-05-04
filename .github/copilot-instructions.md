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

---

xxxxxxxxxxxx
### **Communication Protocol:**
* **Language:** Ưu tiên Tiếng Việt tự nhiên, chuyên nghiệp cho các phần giải thích. Giữ nguyên thuật ngữ kỹ thuật tiếng Anh (ví dụ: *Microservices, Scalability, RAG, Embedding*).
* **Token-Saving Mode (Strict):**
    * **Caveman/RTK:** Loại bỏ các câu xã giao thừa thãi ("Chào bạn", "Tôi có thể giúp gì"). Đi thẳng vào vấn đề. Sử dụng cấu trúc Keywords hoặc Bullet points để nén thông tin.
    * **Context-Aware:** Chỉ truy xuất và xử lý dữ liệu liên quan trực tiếp đến Task. Nếu câu hỏi mơ hồ, hãy yêu cầu làm rõ thay vì phỏng đoán gây tốn token.

**Operational Guidelines:**
1.  **Technical Depth:** Đối với các khái niệm trừu tượng (như *Distributed Tracing, CAP Theorem, Vector Database architecture*), hãy trình bày bằng tư duy hệ thống cao cấp, sử dụng Markdown Table hoặc Sơ đồ Mermaid (nếu cần) để làm rõ thay vì viết đoạn văn dài.

---

### Tại sao bản này đáp ứng yêu cầu của anh?

* **Hỗ trợ tiếng Việt tối đa:** Tôi đã cấu hình để Copilot ưu tiên tiếng Việt nhưng vẫn giữ "chất" kỹ thuật bằng cách không dịch gượng ép các thuật ngữ chuyên ngành.
* **Xử lý khái niệm trừu tượng:** Bằng cách yêu cầu sử dụng **Markdown Table** và **Sơ đồ**, các vấn đề khó hiểu sẽ được trực quan hóa, giúp tiết kiệm hàng nghìn token so với việc giải thích bằng chữ thuần túy.
* **Tiết kiệm tuyệt đối:** Giao thức Caveman sẽ lọc bỏ các từ đệm, giúp mỗi tin nhắn của Copilot tập trung 100% vào giá trị nội dung.
* **Đúng "Gu" kỹ thuật:** Tập trung vào .NET 9, AWS và tránh xa Java đúng theo yêu cầu khắt khe của anh.

Anh có muốn tôi viết thêm một số bộ **Shorthand Triggers** (phím tắt lệnh) riêng cho Copilot để anh gọi nhanh các hàm xử lý trong dự án Document Manager không?

xxxxxxxxxxxx





## Architecture

This is an **agent-maintained knowledge wiki**. The agent (not humans) owns the `wiki/` layer. Users drop source documents into `raw/` and issue natural-language commands; the agent reads, extracts, and builds interlinked wiki pages.

```
raw/        ← immutable source documents — NEVER modify these
wiki/
  index.md          ← catalog of all pages — update on every ingest
  log.md            ← append-only record, grep-parseable
  overview.md       ← living synthesis, revised each ingest
  sources/          ← one .md page per source (kebab-case filenames)
  entities/         ← people, companies, projects (TitleCase filenames)
  concepts/         ← ideas, frameworks, methods (TitleCase filenames)
  syntheses/        ← saved query answers (kebab-case filenames)
graph/
  graph.json        ← node/edge data, SHA256-cached
  graph.html        ← self-contained vis.js visualization
tools/              ← standalone Python scripts (work without agent)
```

**Data flow:** `raw/` → ingest → `wiki/sources/` + entity/concept pages → `wiki/index.md` + `wiki/overview.md` + `wiki/log.md` → `graph/`

---

## Python tools

```bash
python tools/health.py              # structural checks (no LLM, fast — run every session)
python tools/health.py --save       # save report to wiki/health-report.md
python tools/health.py --json       # machine-readable output

python tools/build_graph.py         # full graph rebuild
python tools/build_graph.py --open  # build + open graph.html in browser
python tools/build_graph.py --no-infer   # skip semantic inference (faster)
python tools/build_graph.py --report     # graph health report
python tools/build_graph.py --report --save  # save to graph/graph-report.md

python tools/pdf2md.py 2401.12345   # arXiv paper by ID
python tools/pdf2md.py paper.pdf    # local PDF (auto-selects backend)
python tools/pdf2md.py paper.pdf -o raw/papers/my-paper.md

python tools/mark_it.py "raw/file.pdf"   # convert non-markdown files
python tools/file_to_md.py --input_dir ../raw/  # batch convert
```

Install deps: `pip install networkx litellm` (graph inference requires `ANTHROPIC_API_KEY`)

---

## Wiki workflows

### Ingest

Before ingesting, check `wiki/sources/` — only ingest NEW files. Steps:
1. Read source fully → read `wiki/index.md` + `wiki/overview.md`
2. Write `wiki/sources/<slug>.md`
3. Update `wiki/index.md`, `wiki/overview.md`
4. Create/update entity and concept pages
5. Flag contradictions with existing content
6. Append to `wiki/log.md`: `## [YYYY-MM-DD] ingest | <Title>`
7. Post-ingest: check for broken `[[wikilinks]]`, verify new pages are in `index.md`

### Query

1. Read `wiki/index.md` → identify relevant pages → read them
2. Synthesize answer with `[[PageName]]` wikilink citations
3. Offer to save as `wiki/syntheses/<slug>.md`

### Health (run first, every session)

`python tools/health.py` — deterministic, zero LLM calls. Checks:
- Empty/stub files (body < 100 chars after frontmatter)
- Index sync (`wiki/index.md` vs files on disk)
- Log coverage (source pages without a log entry)

### Lint (periodic, ~every 10–15 ingests)

Uses LLM. Checks: orphan pages, broken links, contradictions, stale summaries, missing entity pages, sparse pages (< 2 outbound links), data gaps.

### Graph

`python tools/build_graph.py --open` — two-pass:
1. Parse `[[wikilinks]]` → `EXTRACTED` edges
2. Infer implicit relationships → `INFERRED` (with confidence) or `AMBIGUOUS`

Runs Louvain community detection. SHA256 cache: only changed pages are reprocessed.

---

## Page format

Every wiki page must have this YAML frontmatter:

```yaml
---
title: "Page Title"
type: source | entity | concept | synthesis
tags: []
sources: []       # list of source slugs
last_updated: YYYY-MM-DD
---
```

Use `[[PageName]]` wikilinks to cross-reference. Every page needs ≥ 2 outbound wikilinks.

### Source page template

```markdown
---
title: "Source Title"
type: source
tags: []
date: YYYY-MM-DD
source_file: raw/...
---

## Summary
## Key Claims
## Key Quotes
## Connections
## Contradictions
```

Domain-specific templates exist for diary entries (`tags: [diary]`) and meeting notes (`tags: [meeting]`) — use those when applicable.

---

## Naming conventions

| Page type | Filename convention | Example |
|-----------|--------------------|---------| 
| Source | `kebab-case.md` | `attention-is-all-you-need.md` |
| Entity | `TitleCase.md` | `OpenAI.md`, `SamAltman.md` |
| Concept | `TitleCase.md` | `ReinforcementLearning.md`, `RAG.md` |
| Synthesis | `kebab-case.md` | `hallucination-approaches.md` |

## Log format

`## [YYYY-MM-DD] <operation> | <title>`  — grep-parseable with:
```bash
grep "^## \[" wiki/log.md | tail -10
```
Operations: `ingest`, `query`, `health`, `lint`, `graph`, `convert`

---

## Hard rules

- **NEVER modify files in `raw/`** — they are immutable source documents
- **Graph MUST NOT auto-create pages** from broken wikilinks — report only (HG-WA-01)
- **New commands MUST NOT duplicate** existing command coverage (HG-WA-02)
- Entity/concept pages are created as side-effects of ingest — they don't need their own log entries
- Only `wiki/sources/*.md` pages need corresponding log entries
