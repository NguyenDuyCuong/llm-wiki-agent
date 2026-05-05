Query the LLM Wiki and synthesize an answer.

Usage: /wiki-query $ARGUMENTS

$ARGUMENTS is the question to answer, e.g. `What are the main themes across all sources?`

## Token-efficient workflow

**NEVER `view` wiki/index.md directly** — use `ctx_execute_file` to search it by keyword so only matching lines enter context:

```python
# ctx_execute_file — path: wiki/index.md
keywords = "<extract key terms from the user's question>".lower().split()
matches = [l for l in FILE_CONTENT.split('\n') if any(kw in l.lower() for kw in keywords)]
print('\n'.join(matches))
```

This returns ~5–15 lines instead of 130+. Then `view` only the pages identified as relevant.

## Steps (in order)

1. **Search index** — `ctx_execute_file` on wiki/index.md with keywords from the question
2. **Read relevant pages** — `view` up to ~10 most relevant pages identified in step 1
3. **Synthesize** a thorough markdown answer with `[[PageName]]` wikilink citations
4. **Include** a `## Sources` section at the end listing pages you drew from
5. **Ask** the user if they want the answer saved as `wiki/syntheses/<slug>.md`

If the wiki is empty, say so and suggest running /wiki-ingest first.
