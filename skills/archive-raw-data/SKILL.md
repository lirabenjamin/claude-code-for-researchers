---
name: archive-raw-data
description: End-of-data-collection workflow. Exports raw MongoDB data as JSONL, writes a companion README documenting schema + provenance, commits both to the repo, and archives the raw dataset to Zenodo with a permanent DOI. Use when the user says "data collection is done", "freeze the data", "archive the raw data", "post the raw data to Zenodo", "collection is complete", or is closing out a study.
---

# Archive Raw Data — End-of-Collection Workflow

Runs when the user has finished collecting data on a self-hosted study (e.g., MongoDB Atlas backing a Render-deployed app). Goal: produce a permanent, publicly-timestamped, tamper-evident snapshot of the raw data with clear provenance, linked to the exact code version that produced it.

## When to invoke

Trigger phrases: "data collection is done", "freeze the data", "archive the raw data", "post raw data to Zenodo", "collection is complete", "close out the study".

Do NOT invoke for cleaned/processed data — this skill is explicitly for the RAW, pre-exclusion dump. A separate workflow handles the publication-time cleaned dataset (see "Related workflows" at the bottom).

---

## Step 0 — Precondition checks (MANDATORY)

Run these and stop on any failure. Do not proceed to collection/export until all pass.

### 0a. Zenodo token configured

Check, in order:
1. `.env` in the current directory contains `ZENODO_TOKEN=...`
2. Exported env var: `echo $ZENODO_TOKEN`

If neither is set, stop and tell the user:
> I need a Zenodo API token. Create one at https://zenodo.org/account/settings/applications/tokens/ with scopes `deposit:write` and `deposit:actions`. Add it to `.env` as `ZENODO_TOKEN=...`. Do NOT paste it in chat — I will not store it anywhere. I'll read it from the environment.

**Never** write the token into any file other than `.env` (which must be gitignored). Never echo or log the token. Never include it in commit messages, Zenodo metadata, READMEs, or error output.

### 0b. Mongo connection configured

Check for `MONGODB_URI` in `.env` or env. If missing, ask the user for it. Do not hardcode. Treat it with the same sensitivity as the Zenodo token.

### 0c. mongoexport installed

```bash
which mongoexport
```

If missing, tell the user:
> `mongoexport` is part of the MongoDB Database Tools. Install via:
> - macOS: `brew install mongodb-database-tools`
> - Linux: https://www.mongodb.com/try/download/database-tools

### 0d. Git state is clean

```bash
git status --porcelain
```

If there are uncommitted changes, stop. The raw data dump must be committed against a known, clean commit — we'll link the Zenodo record to that SHA.

### 0e. `.env` is in `.gitignore`

```bash
grep -E "^\.env$|^\.env\b" .gitignore
```

If `.env` is not gitignored, STOP and add it before doing anything else. Uploading tokens to a public repo via `.env` is a common way to leak credentials.

### 0f. `requests` (Python) or `curl` available

We'll use `curl` by default — it's always present. Scripts in this skill use `curl` unless the user specifically wants Python.

---

## Step 1 — Gather study context

Ask the user (all required — do not guess):

1. **Study / collection name.** Used for the file basename and Zenodo title.
2. **Which Mongo collection(s)** to export. If multiple, export each to its own JSONL and include all in the Zenodo record.
3. **Collection window.** Start date, end date (ISO format preferred).
4. **Participant source.** Prolific study ID(s), MTurk HIT ID(s), lab pool, etc. Include completion counts if available.
5. **Any exclusions applied DURING collection** (e.g., bot-detection rejections, server-side attention-check fails that were never stored). These should be noted in the README, not silently dropped.
6. **License for the Zenodo record.** Default to CC-BY-4.0. Offer CC0 as an alternative for users who want maximum openness. Warn that behavioral data with any identifying information (even Prolific IDs) should follow the user's IRB data-sharing provisions.
7. **Authors for the Zenodo record.** Names + ORCIDs + affiliations. Default to the current git user + whatever's in the repo's `CLAUDE.md` if those fields exist.
8. **Related identifiers.** The GitHub repo URL for the materials. We'll attach this to the Zenodo record as a `isSupplementTo` or `isDerivedFrom` relation.

Also auto-gather (no need to ask):
- Current git commit SHA (`git rev-parse HEAD`)
- GitHub remote URL (`git config --get remote.origin.url`)
- Rough size/row count per collection (run `mongoexport ... --dryRun` or a quick `db.coll.countDocuments()` via a short script)

---

## Step 2 — Export raw data

For each collection:

```bash
mkdir -p data/raw
SHA=$(git rev-parse --short HEAD)
mongoexport \
  --uri "$MONGODB_URI" \
  --collection "<collection_name>" \
  --out "data/raw/<study_name>_<collection>_${SHA}.jsonl"
```

`mongoexport` writes **JSONL by default** (one JSON document per line). This is the desired format — human-readable, streamable, diff-friendly, and an open format Zenodo explicitly prefers.

After each export:
- Compute SHA256: `shasum -a 256 data/raw/<file>.jsonl > data/raw/<file>.jsonl.sha256`
- Count rows: `wc -l < data/raw/<file>.jsonl`
- Note the first and last server-side timestamps (head + tail on the file, parse timestamp field)

If the file is over ~50 MB, consider gzipping: `gzip -k data/raw/<file>.jsonl` (keeps the original; upload both). Zenodo accepts files up to 50 GB, but smaller + gzipped uploads are friendlier for people downloading the dataset.

---

## Step 3 — Generate the companion README

Write `data/raw/README.md` (create if doesn't exist, append new study block if it does). Template:

```markdown
# Raw data archive — <STUDY NAME>

## Dataset

- **File:** `<study>_<collection>_<sha>.jsonl`
- **Format:** JSONL (one document per row, UTF-8)
- **Row count:** <N>
- **SHA256:** `<hash>`
- **Collection window:** <start> to <end> (server-side timestamps)
- **Time zone:** UTC (server-side)

## Provenance

- **Materials commit:** `<full git SHA>`
- **Repository:** <github URL>
- **Collection platform:** <Render / Heroku / self-hosted / ...>
- **Participant pool:** <Prolific study ID / MTurk HIT / lab pool>
- **Participants enrolled:** <N> (submitted); <N> (approved on platform)
- **Bot / attention rejections during collection:** <N> — not stored in raw data

## Schema

For each field, include: name, type, description. Infer from a sample of the first 5 rows and confirm with the user.

<fields table>

## Exclusions NOT applied

This dataset is pre-exclusion. The following exclusions were documented in the pre-registration and will be applied in analysis:
- <exclusion 1>
- <exclusion 2>

## Zenodo record

- **DOI:** <filled in after publish>
- **URL:** <filled in after publish>

## License

<CC-BY-4.0 / CC0 / Custom>

## Citation

<filled in with full Zenodo-style citation after publish>
```

**Critical:** Have the user confirm the schema table before uploading. If you infer a type wrong in the README, it's a lot harder to fix after publication.

---

## Step 4 — Create Zenodo draft deposit

Create an unpublished deposit first. Do NOT publish yet.

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ZENODO_TOKEN" \
  -d '{}' \
  https://zenodo.org/api/deposit/depositions
```

Parse the response. Save:
- `id` — deposition ID for subsequent calls
- `links.bucket` — URL for file uploads
- `links.html` — draft web URL (show this to the user in Step 7)

**Always test against the sandbox first** if the user has a sandbox token (`ZENODO_TOKEN_SANDBOX` in env): base URL is `https://sandbox.zenodo.org/api/...`. Sandbox deposits don't create real DOIs. Suggest this for first-time use.

---

## Step 5 — Upload files

For each file (JSONL, README, SHA256 files, gzipped copies if present):

```bash
curl -X PUT \
  -H "Authorization: Bearer $ZENODO_TOKEN" \
  --upload-file data/raw/<file>.jsonl \
  "<bucket_url>/<file>.jsonl"
```

---

## Step 6 — Set metadata

```bash
curl -X PUT \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ZENODO_TOKEN" \
  -d @metadata.json \
  https://zenodo.org/api/deposit/depositions/<id>
```

`metadata.json` structure:

```json
{
  "metadata": {
    "upload_type": "dataset",
    "title": "<Study Title> — Raw data",
    "creators": [
      {"name": "Lastname, Firstname", "affiliation": "Wharton, UPenn", "orcid": "0000-..."}
    ],
    "description": "Raw, pre-exclusion data from <study>. Collected <window> via <platform> using materials at <github repo> commit <sha>. Row count: <N>. See README.md in this record for full provenance and schema.",
    "access_right": "open",
    "license": "cc-by-4.0",
    "keywords": ["<domain>", "behavioral", "preregistered", "raw data"],
    "related_identifiers": [
      {"relation": "isSupplementTo", "identifier": "<github URL at commit>", "resource_type": "software"},
      {"relation": "isDocumentedBy", "identifier": "<preregistration URL if any>"}
    ],
    "publication_date": "<YYYY-MM-DD>",
    "version": "1.0.0-raw"
  }
}
```

Key relations:
- `isSupplementTo`: GitHub repo URL (pin to the commit SHA, not `main`)
- `isDocumentedBy`: AsPredicted / OSF pre-registration URL, if applicable

---

## Step 7 — USER CONFIRMATION GATE (critical)

Before publishing, STOP and show the user the draft URL (`links.html` from Step 4). Say:

> I've prepared the Zenodo deposit as a draft. Review it here: <URL>
>
> Before I publish, confirm:
> - Title, description, and creators are correct
> - Files list is complete (JSONL + README + checksums)
> - License is right (<current license>)
> - Related identifiers resolve correctly
>
> **Publishing is irreversible.** Once I publish, the DOI is permanent. I can create new versions later, but I cannot delete the original.
>
> Say "publish" to proceed, or tell me what to change.

Wait for explicit "publish" / "go ahead" / "ship it" confirmation. Never auto-publish.

---

## Step 8 — Publish

```bash
curl -X POST \
  -H "Authorization: Bearer $ZENODO_TOKEN" \
  https://zenodo.org/api/deposit/depositions/<id>/actions/publish
```

Parse the response. Extract:
- `doi` — the permanent DOI
- `conceptdoi` — the concept-level DOI (same across all versions)
- `links.record_html` — public URL for the record
- `links.latest_html` — URL always pointing to the latest version

---

## Step 9 — Commit the raw data + README + DOI to git

```bash
# Update README.md with the published DOI
# Commit everything to the repo at the SAME SHA that Zenodo references
git add data/raw/
git commit -m "Archive raw data: <study>, DOI <doi>

Zenodo record: <record URL>
Row count: <N>
Collection window: <start> to <end>"
git push
```

**This commit must be a child of the commit referenced in Zenodo metadata** — the Zenodo record points at a commit that was clean BEFORE the data was added. That's correct: the data file is downstream of the materials SHA, not part of it.

---

## Step 10 — Update tracking files

- `comms.md`: prepend a dated entry noting the archive event, DOI, and record URL.
- `todo.md`: mark any "freeze data" / "archive collection" items as done.
- `CLAUDE.md` (if the project has one): add the DOI under an "Archived datasets" section so future sessions know the raw data is frozen.

---

## Step 11 — Decide on MongoDB deletion

**Default: do NOT delete.** Surface the decision to the user with the real considerations on both sides.

### Reasons to delete the Mongo data

- **Cost.** Atlas free tier is 512 MB; paid clusters charge per GB. If the study is done and data is on Zenodo, Mongo is redundant.
- **Surface area.** A live database is a credential-leak vector. A frozen Zenodo record isn't.
- **Clarity.** Removes the temptation to silently re-query live data after publication.

### Reasons to keep the Mongo data

- **Prolific approval window.** Prolific gives submitters up to 14 days to request reviews of rejected submissions, and you may want the live payload to adjudicate. Do not delete until the study is fully closed on Prolific and all approvals are final.
- **Late submissions.** Some platforms allow stragglers. Confirm no one can still be submitting.
- **Analysis dependencies.** If your analysis pipeline points directly at Mongo (not at the Zenodo file), deleting breaks analysis. Update the pipeline to read from `data/raw/<file>.jsonl` first.
- **Piloting / future waves.** If this is one wave of a longitudinal or multi-wave study, deleting may kill continuity.
- **Legal hold / IRB.** Some protocols require retention for a specified period. Check the protocol.

### Recommended prompt to user

After Step 10, ask:

> Raw data is now on Zenodo (DOI: <doi>) and committed to the repo. Do you want to delete the collection from MongoDB Atlas?
>
> I'd recommend keeping it for now if ANY of the following apply:
> - Study is still open on Prolific (or approvals aren't finalized — usually 14 days after last submission)
> - Your analysis code reads from Mongo rather than `data/raw/<file>.jsonl`
> - This is a wave of a longitudinal study with more waves planned
> - Your IRB protocol specifies a retention period
>
> Otherwise, deletion is safe — the Zenodo copy is permanent and your analysis can point at the local JSONL.
>
> Say "delete" to drop the collection, "keep" to leave it, or ask me anything about the tradeoffs.

### If user confirms deletion

Require a second confirmation with a typed keyword:

> To confirm, type DROP-<collection_name> exactly.

Then:

```bash
mongosh "$MONGODB_URI" --eval 'db.<collection>.drop()'
```

Verify with `db.<collection>.countDocuments()` (should be 0 or "collection not found"). Report result.

If user says "keep": log the decision in `comms.md` with a reminder to revisit after Prolific approvals close.

---

## Related workflows (NOT this skill)

- **Publication-time cleaned dataset post.** At manuscript submission, upload the cleaned/processed dataset (post-exclusion, analysis-ready) as a **new version** of the same Zenodo record (or a linked record). Use `POST /api/deposit/depositions/<id>/actions/newversion`. Build a separate skill (`archive-cleaned-data`) when you need it.
- **Ongoing longitudinal archiving.** For multi-wave studies, create one Zenodo record per wave with `isPartOf` relations linking them.

---

## Anti-patterns to flag loudly

1. **Publishing before confirmation.** Zenodo publish is irreversible. Always Step 7.
2. **Writing the token into any file other than gitignored `.env`.** Including in metadata, commit messages, URLs, logs, error output — all forbidden.
3. **Auto-deleting Mongo data.** Never. Always ask, with the pros/cons list.
4. **Uploading cleaned data as the "raw" archive.** The Zenodo raw record should be pre-exclusion. If the user conflates these, stop and clarify — the raw archive is a compliance / audit artifact, not an analysis artifact.
5. **Skipping the sandbox for first-time users.** Offer to test against `sandbox.zenodo.org` first — it's the exact same API, creates disposable DOIs, saves the user from a "oh no I published something malformed" moment.
