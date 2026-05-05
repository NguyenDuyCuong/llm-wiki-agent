Build the LLM Wiki knowledge graph.

Usage: /wiki-graph

## Token-efficient workflow

**Always try the Python script first** — it runs entirely in the shell, zero context cost:

```bash
python tools/build_graph.py --open
```

Only fall back to manual build if Python/deps are unavailable.

## Manual fallback (if Python fails)

**NEVER pipe raw `grep` output into context** — use `ctx_execute` to process wikilinks in the sandbox:

```python
# ctx_execute — extract all edges without dumping raw output to context
import subprocess, re, json, os

out = subprocess.check_output(
    ['grep', '-roh', r'\[\[[^\]]*\]\]', 'wiki/'],
    text=True, stderr=subprocess.DEVNULL
)
links = re.findall(r'\[\[([^\]]+)\]\]', out)
pages = subprocess.check_output(
    'find wiki/ -name "*.md" | grep -Ev "(index|log|overview)"',
    shell=True, text=True
).strip().split('\n')
print(f"Pages: {len(pages)}, Link targets: {len(set(links))}, Total edges: {len(links)}")
# Then write graph/graph.json and graph/graph.html from these variables
```

## Manual build steps (only if Python fails)

1. Run `ctx_execute` above to extract nodes + edges in sandbox
2. Build nodes list: one node per wiki page (id=relative-path, label=title, type from frontmatter)
3. Build edges list: one edge per `[[wikilink]]`, tagged EXTRACTED
4. Infer implicit relationships — tag INFERRED with confidence 0.0–1.0; low-confidence → AMBIGUOUS
5. Write `graph/graph.json` with `{nodes, edges, built: today}`
6. Write `graph/graph.html` as a self-contained vis.js page (nodes colored by type, interactive, searchable)

After building, summarize: node count, edge count, breakdown by type, and the most connected hubs.

Append to wiki/log.md: `## [today's date] graph | Knowledge graph rebuilt`
