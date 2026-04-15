---
name: gws
description: Interact with Google Workspace (Drive, Docs, Sheets, Gmail, Calendar, etc.) using the `gws` CLI. Use this skill when the user wants to read, create, edit, or search Google Docs, Sheets, Drive files, or any Google Workspace resource.
---

# Google Workspace CLI (`gws`)

Installed globally at `/opt/homebrew/bin/gws` (v0.11.1+). Authenticated as `lira.benjamin@gmail.com`. Credentials stored in `~/.config/gws/`.

## Command Pattern

```
gws <service> <resource> <method> [--params '<JSON>'] [--json '<JSON>']
```

- `--params` = URL/query parameters (GET requests, filters)
- `--json` = request body (POST/PATCH/PUT)
- `--format table` for human-readable output
- `--page-all` to auto-paginate through all results

## Services

| Service | What it does |
|---------|-------------|
| `drive` | Files, folders, shared drives |
| `docs` | Google Docs (read/write) |
| `sheets` | Spreadsheets |
| `gmail` | Email |
| `calendar` | Calendars and events |
| `slides` | Presentations |
| `tasks` | Task lists |
| `people` | Contacts |
| `chat` | Chat spaces/messages |
| `forms` | Google Forms |
| `keep` | Google Keep notes |

## Common Operations

### Drive — Search & List Files
```bash
# List recent files
gws drive files list --params '{"pageSize": 10}'

# Search by name
gws drive files list --params '{"q": "name contains '\''my doc'\''", "pageSize": 10}'

# Search Google Docs only
gws drive files list --params '{"q": "mimeType='\''application/vnd.google-apps.document'\''", "pageSize": 10}'

# Search Sheets only
gws drive files list --params '{"q": "mimeType='\''application/vnd.google-apps.spreadsheet'\''", "pageSize": 10}'

# Get file metadata
gws drive files get --params '{"fileId": "FILE_ID"}'

# Download/export a Google Doc as plain text
gws drive files export --params '{"fileId": "FILE_ID", "mimeType": "text/plain"}' --output out.txt

# Download/export as PDF
gws drive files export --params '{"fileId": "FILE_ID", "mimeType": "application/pdf"}' --output out.pdf
```

### Docs — Read & Write
```bash
# Get full document content (JSON structure with paragraphs, tables, etc.)
gws docs documents get --params '{"documentId": "DOC_ID"}'

# Append text to a document (helper command)
gws docs +write --params '{"documentId": "DOC_ID"}' --json '{"text": "Hello world"}'

# Batch update a document (insertText, deleteContent, etc.)
gws docs documents batchUpdate --params '{"documentId": "DOC_ID"}' --json '{
  "requests": [
    {"insertText": {"location": {"index": 1}, "text": "New text at beginning"}}
  ]
}'
```

### Sheets — Read & Write
```bash
# Get spreadsheet metadata
gws sheets spreadsheets get --params '{"spreadsheetId": "SHEET_ID"}'

# Read a range
gws sheets spreadsheets.values get --params '{"spreadsheetId": "SHEET_ID", "range": "Sheet1!A1:D10"}'

# Write to a range
gws sheets spreadsheets.values update --params '{"spreadsheetId": "SHEET_ID", "range": "Sheet1!A1", "valueInputOption": "USER_ENTERED"}' --json '{
  "values": [["Header1", "Header2"], ["val1", "val2"]]
}'
```

### Gmail
```bash
# List messages
gws gmail users messages list --params '{"userId": "me", "maxResults": 5}'

# Search messages
gws gmail users messages list --params '{"userId": "me", "q": "from:someone@example.com", "maxResults": 5}'

# Read a message
gws gmail users messages get --params '{"userId": "me", "id": "MSG_ID"}'
```

### Calendar
```bash
# List upcoming events
gws calendar events list --params '{"calendarId": "primary", "maxResults": 10, "timeMin": "2026-03-11T00:00:00Z", "orderBy": "startTime", "singleEvents": true}'

# Create an event
gws calendar events insert --params '{"calendarId": "primary"}' --json '{
  "summary": "Meeting",
  "start": {"dateTime": "2026-03-12T10:00:00-05:00"},
  "end": {"dateTime": "2026-03-12T11:00:00-05:00"}
}'
```

## Discovering API Methods

If unsure about the exact method or parameters:
```bash
# List available methods for a resource
gws <service> <resource> --help

# Get full API schema for a method
gws schema <service>.<resource>.<method>
```

## Google Docs batchUpdate — Index Safety

When inserting content into a Google Doc (especially tables), character indices shift after every mutation. Stale indices cause text to land in the wrong location, corrupting paragraphs.

**Rules:**
1. **Re-read the document after every structural change** (inserting/deleting tables, large text blocks). Never reuse indices from before the mutation.
2. **Insert text in reverse index order** (highest index first) within a single batchUpdate call — this prevents earlier insertions from shifting later indices.
3. **After inserting a table structure, re-fetch the doc** to get the actual cell indices before populating cells. The cell indices returned by `insertTable` are not reliable for subsequent inserts in the same batch.
4. **Skip empty cells** when applying `updateTextStyle` — a range where `endIndex - startIndex <= 1` (just a newline) will error with "range should not be empty."
5. **`updateTableCellStyle`** uses `tableRange` with `tableCellLocation.tableStartLocation` inside it — do NOT also set a top-level `tableStartLocation` (oneOf conflict).
6. **`+write` helper** only appends plain text. For any formatting, use `batchUpdate` with `updateParagraphStyle` / `updateTextStyle`.
7. **Large JSON payloads**: pass via Python `subprocess.run()` rather than shell `$(cat ...)` to avoid shell escaping and argument length limits.
8. **gws stdout** prefixes output with `Using keyring backend: keyring` — skip the first line before parsing JSON.

## Troubleshooting

- If auth fails with "decrypt" errors: user must run `gws auth logout && gws auth login` from their own terminal (keychain-bound).
- The `--format table` flag is useful for quick human-readable output.
- Use `--dry-run` to validate a request without sending it.
- Drive file IDs can be extracted from Google Docs/Sheets URLs: `https://docs.google.com/document/d/{FILE_ID}/edit`

## MIME Types for Drive Queries
- Google Docs: `application/vnd.google-apps.document`
- Google Sheets: `application/vnd.google-apps.spreadsheet`
- Google Slides: `application/vnd.google-apps.presentation`
- Google Forms: `application/vnd.google-apps.form`
- Folders: `application/vnd.google-apps.folder`
