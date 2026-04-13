Convert a document (PDF, DOCX, HTML, etc.) to Markdown using Docling.

Usage: /wiki-mark $ARGUMENTS

$ARGUMENTS should be the path to a source document, e.g. `documents/report.pdf` or `raw/manual.docx`.

Follow the Ingest Workflow defined in CLAUDE.md exactly:
1. Check if a PDF already has a corresponding `.md` in `raw/` before converting.
2. Check for existing markdown: `Glob pattern: raw/*.md`
3. Check for unprocessed PDFs: `Glob pattern: raw/*.pdf`
4. Only run conversion if no `.md` counterpart exists
5. Run: `python tools/mark_it.py "raw/<filename>.pdf"`
6. Script outputs to `raw/` directory automatically
7. Append to wiki/log.md: ## [today's date] convert | <Title>
8. Confirm with user and propose running `ingest` for the new file

After the tool finishes, summarize:
- The source file processed.
- The destination path of the Markdown file.
- Any errors or warnings encountered during conversion.