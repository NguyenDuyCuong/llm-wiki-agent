# Copilot Instructions

## Working commands

The repository is driven by standalone Python tools in `tools/` plus agent-facing schema files.

```bash
pip install -r requirements.txt
```

```bash
python tools/ingest.py raw/path/to/source.md
python tools/ingest.py raw/path/to/folder
python tools/ingest.py "raw/**/*.md"
python tools/ingest.py --validate-only
```

```bash
python tools/lint.py
python tools/lint.py --save
```

```bash
python tools/build_graph.py
python tools/build_graph.py --no-infer
python tools/build_graph.py --report --save
python tools/build_graph.py --open
```

```bash
python tools/query.py "What are the main themes?"
python tools/query.py "How does X relate to Y?" --save
python tools/query.py "Summarize EntityName" --save syntheses/my-analysis.md
```

```bash
python tools/mark_it.py raw/path/to/document.pdf
python tools/refresh.py --dry-run
python tools/refresh.py --page sources/my-source
python tools/refresh.py --force
python tools/heal.py
```

There is no checked-in automated test suite. The narrowest built-in validation path is `python tools/refresh.py --page sources/<slug>` for a single source page, and the whole-wiki integrity check is `python tools/ingest.py --validate-only`.

## High-level architecture

This repo has two layers:

1. **Agent workflow definitions** in `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md`. These describe the ingest/query/lint/graph workflows and the wiki page schema for different assistants.
2. **Python automation tools** in `tools/` that execute those workflows against the local markdown wiki.

The main content flow is:

1. **`raw/` is the immutable staging area** for source material.
2. **`tools/ingest.py` is the main write path**. It reads a source document, injects the contents of `CLAUDE.md` as the schema/prompt contract, builds wiki context from `wiki/index.md`, `wiki/overview.md`, and recent source pages, then writes:
   - `wiki/sources/<slug>.md`
   - updates to `wiki/index.md`
   - optional updates to `wiki/overview.md`
   - entity pages in `wiki/entities/`
   - concept pages in `wiki/concepts/`
   - a log entry in `wiki/log.md`
   - post-ingest validation results for broken wikilinks and missing index entries
3. **`tools/query.py` is read-mostly**. It starts from `wiki/index.md`, selects relevant pages, expands context with high-confidence neighbors from `graph/graph.json` when available, and can optionally file answers into `wiki/syntheses/`.
4. **`tools/build_graph.py` turns wiki pages into graph artifacts**. It:
   - parses explicit `[[wikilinks]]` into deterministic `EXTRACTED` edges
   - asks the LLM for implicit `INFERRED` / `AMBIGUOUS` edges
   - caches semantic inference in `graph/.cache.json`
   - checkpoints per-page inference in `graph/.inferred_edges.jsonl`
   - runs Louvain community detection when `networkx` is installed
   - renders both `graph/graph.json` and the self-contained `graph/graph.html`
5. **Maintenance tools build on those same artifacts**:
   - `tools/lint.py` does deterministic link checks plus graph-aware checks against `graph/graph.json`
   - `tools/heal.py` uses lint results to generate missing entity pages
   - `tools/refresh.py` re-ingests stale source pages by following each source page's `source_file` frontmatter and tracking hashes in `graph/.refresh_cache.json`

## Key repository conventions

- `raw/` is input-only. Convert external documents into markdown there, but do not rewrite source material in place.
- The standalone tools use `CLAUDE.md` as the runtime schema source (`SCHEMA_FILE = REPO_ROOT / "CLAUDE.md"`), even though equivalent instructions also exist in `AGENTS.md` and `GEMINI.md`. If you change page formats or workflow rules, keep those files aligned.
- Wiki page naming is semantic, not arbitrary:
  - source pages use `kebab-case` slugs that match the source filename
  - entity and concept pages use `TitleCase.md`
  - log entries use `## [YYYY-MM-DD] <operation> | <title>`
- Source pages are expected to carry `source_file:` in frontmatter. `tools/refresh.py` depends on that field to find the raw document for re-ingestion.
- Ingest changes are expected to update the durable wiki surfaces together: source page, index, overview (if needed), related entity/concept pages, and log. `tools/ingest.py` already treats that as a single operation.
- Before ingesting a source, check whether a corresponding page already exists in `wiki/sources/`. Before converting a PDF, check whether a markdown counterpart already exists in `raw/`.
- `[[Wikilinks]]` are the primary connective tissue of the repo. They are consumed by ingest validation, lint, query expansion, and graph building, so avoid replacing them with plain text when editing wiki content.
- `graph/` holds generated outputs and caches, not hand-authored content. Treat `graph/graph.json`, `graph/.cache.json`, `graph/.inferred_edges.jsonl`, and `graph/.refresh_cache.json` as derived artifacts.
- Query results are meant to be shown first and only saved into `wiki/syntheses/` when explicitly requested.
