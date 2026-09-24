---
name: zotero-fetch
description: Fetch a Zotero collection's items and PDFs to a local folder so Claude can read them. Use when the user wants to read, analyze, summarize, or reference papers from a specific Zotero collection by name (e.g., "read my Zotero collection link_sudip", "fetch papers from my twins collection and summarize"). Creates an index.json with metadata and downloads all PDFs.
---

# Zotero Fetch

Pulls items and PDFs from a named Zotero collection to a local folder. Produces `index.json` with metadata and a folder of PDFs Claude can read.

## One-time setup

The user needs to have set these environment variables (via `~/.zshrc` or equivalent):

- `ZOTERO_API_KEY` — from https://www.zotero.org/settings/keys (read-only is fine)
- `ZOTERO_USER_ID` — shown on the same page

If the skill fails with "ZOTERO_API_KEY not set", walk the user through getting a key.

## How to use

When the user asks for papers from a Zotero collection:

1. **Run the fetch script** from the current working directory:

   ```bash
   python ~/.claude/skills/zotero-fetch/fetch_collection.py <collection_name>
   ```

   Replace `<collection_name>` with the name the user mentioned. Partial matches work; if there's no match the script lists close matches.

2. **Optional flags:**
   - `--output <dir>` — custom output directory (default: `./zotero_cache/<collection>/`)
   - `--group <id>` — fetch from a group library instead of the personal library

3. **After the script runs**, read `<output>/index.json` to see all items. Each entry has:
   - `key` — Zotero item key
   - `title`, `year`, `authors`
   - `abstract`, `doi`, `url`
   - `pdf_path` — local path to the PDF (or `null` if no PDF)

4. **Read PDFs** the user wants analyzed. Don't read all of them at once unless the user asks — pick the relevant ones based on their question.

## Typical workflow

User: "Fetch my zotero collection link_sudip and summarize each paper"

Claude:
1. Runs `python ~/.claude/skills/zotero-fetch/fetch_collection.py link_sudip`
2. Reads the resulting `zotero_cache/link_sudip/index.json`
3. For each entry with a `pdf_path`, reads the PDF and writes a short summary
4. Produces a synthesis

## Notes

- Already-downloaded PDFs are not re-downloaded (checked by filename)
- Items without PDFs are kept in the index with abstract/metadata only — Claude can still work with those
- Only `application/pdf` attachments are downloaded. Supplementary Word docs etc. are ignored.
- Zotero API rate limit is generous (~1000 req / 10s); typical collections are fine
