name: latex-gdoc-roundtrip
description: Roundtrip a LaTeX manuscript to Google Docs for coauthor feedback and back. Reads the compiled PDF, writes clean text + figures + tables into a Google Doc via `gws`, and can pull comments/edits back into the LaTeX source.
---

# LaTeX ↔ Google Docs Roundtrip

Push a LaTeX manuscript to Google Docs for coauthor review, then pull feedback back.

---

## When to use

Trigger phrases: "put it on Drive", "send to coauthors", "Google Doc version", "share the paper", "pull comments back from Docs"

---

## Phase 1: LaTeX → Google Docs ("push")

### Step 1: Read the compiled PDF

Read the compiled PDF (not the .tex source) to get the final rendered text with all macros resolved, numbers filled in, and figures visible. This is the source of truth.

```
Read the PDF: paper/main.pdf (or wherever the compiled PDF lives)
Read ALL pages — request pages in batches of 20 if needed.
```

Also read the LaTeX numbers file (e.g., `output/*/numbers/results.tex`) to have exact values for cross-checking.

### Step 2: Identify figures

Find all figure files referenced in the manuscript:

```bash
# Find figure PDFs/PNGs
grep -r 'includegraphics' paper/sections/*.tex paper/main.tex | grep -oP '\{[^}]+\}'
```

Convert PDF figures to high-res PNG for Google Docs:

```bash
# pdftoppm gives better results than sips
pdftoppm -png -r 300 -singlefile "$fig_pdf" "/tmp/${basename}"
```

### Step 3: Create the Google Doc

```bash
gws docs documents create --json '{"title": "Paper Title — Draft (YYYY-MM-DD)"}'
```

Save the document ID.

### Step 4: Write the text

Use `gws docs +write` to insert text. Key rules:

1. **One `\n` per paragraph** — never double `\n` (that creates blank lines Google Docs doesn't need)
2. **Resolve all LaTeX macros** — replace `\N{}`, `\WarmthTimeB{}` etc. with actual numbers from the PDF
3. **Convert LaTeX formatting** to plain text:
   - `\textbf{...}` → mark for bold formatting
   - `\textit{...}` / `\emph{...}` → mark for italic formatting
   - `\citep{Foo2020}` → `[1]` (use the numbered refs from the PDF)
   - `---` → em dash (—)
   - `--` → en dash (–)
   - Math: `$d = 0.55$` → `d = 0.55` (plain text)
4. **Section structure**: Write sections in order from the PDF. Each section heading gets its own paragraph.
5. **Figure placeholders**: Insert a unique placeholder string (e.g., `IMG_FIG1`) on its own line where each figure goes. Put the caption on the NEXT line (not same paragraph).
6. **Table placeholders**: Insert `TABLE_N_PLACEHOLDER` where tables go; we'll replace with real tables.
7. **Block quotes**: Write as regular paragraphs; we'll indent them in formatting.
8. **Abstract**: Write as its own paragraph, separate from the introduction. Start with "Abstract. " (bold the label).
9. **Authors**: Include author names centered below the title/subtitle.

Write the full text using `gws docs +write --document DOC_ID --text "..."`. For large manuscripts, write in chunks (one section per call) — the `+write` helper appends automatically.

### Step 5: Apply formatting via batchUpdate

After all text is inserted, get the doc structure to find character positions:

```bash
gws docs documents get --params '{"documentId": "DOC_ID"}'
```

Then apply formatting in one batchUpdate call:

**Paragraph styles:**
- Title → `namedStyleType: "TITLE"`, centered
- Subtitle/draft notice → `namedStyleType: "SUBTITLE"`, centered
- Section headings → `namedStyleType: "HEADING_1"`
- Subsection headings → `namedStyleType: "HEADING_2"`
- Block quotes → indent left and right by 36pt, italic

**Text styles (bold, italic):**
- "Abstract." label → bold
- Inline run-in headings (e.g., "Participants.", "Design.") → bold
- Limitation labels (e.g., "No behavioral outcomes.") → bold
- Figure captions ("Fig. 1. ...") → italic, smaller font (9pt)
- First mention of key term "synthetic contact" in intro → italic
- Journal names in references → italic

### Step 6: Insert figures

For each figure placeholder:
1. Upload the PNG to Drive: `gws drive files create --upload /tmp/fig.png`
2. Make it publicly readable: `gws drive permissions create ... '{"role": "reader", "type": "anyone"}'`
3. In the doc, delete the placeholder paragraph and insert an inline image:

```json
{"deleteContentRange": {"range": {"startIndex": X, "endIndex": Y}}},
{"insertInlineImage": {"uri": "https://drive.google.com/uc?id=FILE_ID", "location": {"index": X}, "objectSize": {"width": {"magnitude": 400, "unit": "PT"}}}}
```

Process images in **reverse document order** (highest index first) to avoid shifting positions.

After insertion, clean up the temp images from Drive.

### Step 7: Insert tables

For each table placeholder:
1. Delete the placeholder paragraph
2. Insert a caption paragraph (bold the "Table N." prefix)
3. Insert a table structure: `{"insertTable": {"rows": N, "columns": M, "location": {"index": X}}}`
4. Populate cells by finding each cell's startIndex and inserting text
5. Format: bold the header row only, not the entire table. Row labels (first column) can be bold for readability.

### Step 8: Set sharing permissions

```bash
gws drive permissions create \
  --params '{"fileId": "DOC_ID"}' \
  --json '{"role": "commenter", "type": "anyone"}'
```

### Step 9: Clean up

- Delete all temp PNGs from `/tmp/`
- Delete uploaded image files from Drive (they're embedded in the doc now — BUT check first that images still render; if Google Docs references them by URL, keep them)
- Remove any helper scripts from `/tmp/`

### Output

Return the shareable link: `https://docs.google.com/document/d/DOC_ID/edit`

---

## Phase 2: Google Docs → LaTeX ("pull")

### Step 1: Export the Google Doc as plain text

```bash
gws drive files export --params '{"fileId": "DOC_ID", "mimeType": "text/plain"}' --output /tmp/gdoc_export.txt
```

### Step 2: Diff against the original

Read both the exported text and the original LaTeX sections. Identify:
- Text edits (wording changes, sentence rewrites)
- Structural changes (moved paragraphs, new sections)
- Comments (if exported via Docs API — use `gws docs documents get` to find comment anchors)

### Step 3: Apply changes to LaTeX source

For each change:
1. Find the corresponding location in the `.tex` source file
2. Apply the edit using the Edit tool
3. Preserve all LaTeX formatting (macros, citations, cross-references)
4. Do NOT replace macro-generated numbers with hardcoded values

### Step 4: Recompile and verify

```bash
make paper  # or whatever the project's build command is
```

Open the PDF and verify the changes rendered correctly.

---

## Known Limitations

1. **Images may break** if the source Drive files are deleted before the doc caches them. Check rendering before cleanup.
2. **Complex tables** (multi-level headers, merged cells, SE in parentheses below coefficients) are hard to represent in Docs tables. For review purposes, a simplified single-row-per-variable format is acceptable.
3. **LaTeX math** renders as plain text in Docs. Complex equations should be noted as "[see PDF for equation]" or written in Unicode approximation.
4. **Citations** become `[N]` numbered references. The bibliography section preserves full references.
5. **Appendix/supplementary** sections can be included or omitted depending on what coauthors need to review — ask the user.

---

## Checklist

### Push (LaTeX → Docs)
- [ ] Read compiled PDF (all pages)
- [ ] Convert figures to PNG (300 dpi via pdftoppm)
- [ ] Create Google Doc with date in title
- [ ] Write text: no extra line breaks, all macros resolved
- [ ] Separate abstract from intro (own paragraph)
- [ ] Figure captions on their own line (not inline with figure)
- [ ] Apply heading styles (TITLE, H1, H2)
- [ ] Apply bold/italic formatting
- [ ] Insert figures as inline images
- [ ] Insert tables as real Docs tables (bold header row only)
- [ ] Add authors below title
- [ ] Set sharing to "anyone with link can comment"
- [ ] Return shareable link
- [ ] Clean up temp files

### Pull (Docs → LaTeX)
- [ ] Export doc as plain text
- [ ] Diff against original
- [ ] Apply text edits to .tex source
- [ ] Preserve all macros and citations
- [ ] Recompile and verify PDF
