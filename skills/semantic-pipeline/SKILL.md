---
name: semantic-pipeline
description: Compute three measures of semantic diversity on a parquet of texts — word-level DSI (BERT layers 6+7, Beaty/Patterson 2022 recipe), sentence-level mean pairwise cosine distance (SBERT all-MiniLM-L6-v2), and document-level chamfer Distinctness (OpenAI text-embedding-3-large, min cosine distance to any other doc in the same cohort, per Moon et al.). Use when the user says "/semantic-pipeline", "compute semantic diversity", "do the three-level diversity analysis", or any request to replicate the Moon-Kibum / Beaty semantic homogenization pipeline.
---

# Semantic Pipeline — Three-Level Diversity (DSI / SBERT / Chamfer)

Replicates the Moon et al. "LLM-Era College Admissions Essays Exhibit Deep Homogenization Despite Lexical Diversity" pipeline, which itself uses Beaty/Patterson 2022 (BRM) for word-level DSI, Anderson et al. for sentence-level diversity, and Cox et al. for document-level chamfer Distinctness.

| level | measure | model | output per doc |
| --- | --- | --- | --- |
| word | DSI | `bert-large-uncased` layers 6+7 | `word_dsi` — mean cosine distance across all word-pair embeddings in the doc |
| sentence | mean pairwise distance | `sentence-transformers/all-MiniLM-L6-v2` | `sentence_dist`, `sentence_count` |
| document | chamfer Distinctness | OpenAI `text-embedding-3-large` (3072d) | `doc_dist_<cohort>` — min cosine distance to nearest other doc in same cohort |

All higher numbers = more diverse / more distinct / less homogeneous.

---

## When to invoke

When the user asks for any of:
- "Run /semantic-pipeline on [parquet path]"
- "Compute the three diversity measures on [data]"
- "Replicate the Moon et al pipeline"
- "Get DSI / sentence / chamfer scores on these texts"
- "Run the semantic homogenization analysis"

---

## Step 0 — Preconditions

### Inputs

A single parquet file with at minimum:
- An `id`-like column (default `id`; ask the user if non-obvious)
- A `text`-like column with the document text (default `text`; ask if non-obvious)
- (Optional) a grouping column for document-level cohort

If the user names a file without specifying columns, **read the parquet's schema first** to find the obvious id + text columns. Confirm guesses before running.

### Hardware

The scripts auto-detect `cuda` → `mps` (Apple Silicon Metal) → `cpu`. M-series Macs use MPS and run word-level DSI in ~30-60 min for ~1,000 docs of ~100 words each. CPU-only is 3-6× slower.

### API key

Document-level chamfer needs `OPENAI_API_KEY` in the environment. Check `~/.env` and the working-dir `.env`. If missing, ask the user.

### Dependencies

Stored in a dedicated venv at `~/.claude/skills/semantic-pipeline/.venv/`. Bootstrap on first run:

```bash
python3 -m venv ~/.claude/skills/semantic-pipeline/.venv
~/.claude/skills/semantic-pipeline/.venv/bin/python -m pip install -U pip
~/.claude/skills/semantic-pipeline/.venv/bin/python -m pip install -r ~/.claude/skills/semantic-pipeline/requirements.txt
```

`torch` needs Python 3.10–3.13 for stable wheels on Apple Silicon. **If the system `python3` is 3.14+, use `/usr/local/bin/python3.12` or `/opt/homebrew/bin/python3.12` explicitly to create the venv.** Check with `ls /usr/local/bin/python3.1?` and `ls /opt/homebrew/bin/python3.1?`.

---

## Step 1 — Ask about grouping

**This is the one question the user asks the skill to always check.** Use `AskUserQuestion`:

> *For the document-level Distinctness measure, each document's score is the minimum cosine distance to any OTHER document in the same cohort. What cohort should I use?*
>
> - **Free-for-all (one cohort = all docs).** Each doc's nearest neighbor can be any other doc in the dataset. Simplest.
> - **Grouped by a column.** Specify a column name; the metric is computed separately within each value of that column. (E.g., `cause` to compare within-cause near-neighbors.)
> - **Both.** Run both and add two output columns: `doc_dist_all` + `doc_dist_<col>`.

If the user picks "grouped" or "both", ask for the column name (and confirm it exists in the parquet).

---

## Step 2 — Run the pipeline

The orchestrator handles everything. Single call from the input parquet to the output parquet:

```bash
~/.claude/skills/semantic-pipeline/.venv/bin/python \
  ~/.claude/skills/semantic-pipeline/scripts/run_pipeline.py \
  --input <path/to/input.parquet> \
  --output <path/to/output.parquet> \
  --id_col <id_column> \
  --text_col <text_column> \
  [--group_col <column_name>] \
  [--cached_doc_embeddings <path>]  # optional, skips the OpenAI step
```

The orchestrator runs:
1. `01_word_level.py` — DSI with `bert-large-uncased`
2. `02_sentence_level.py` — mean pairwise dist with `all-MiniLM-L6-v2`
3. `03_doc_level.py` — OpenAI `text-embedding-3-large` + chamfer

If "both" was selected, run the doc-level step twice (once with `--group_col`, once with `--group_col=__all__`) and merge.

Use `--cached_doc_embeddings` whenever the input data already has `text-embedding-3-large` 3072-dim vectors on disk to avoid double-spending. Format: parquet with `id` + `embedding` columns (list[float] of length 3072).

---

## Step 3 — Save a reproducible run-script

Alongside the output parquet, always write a `.run.py` script that reproduces the run: it re-invokes the orchestrator with the exact same args and records the working directory and timestamp.

```python
# Auto-generated by /semantic-pipeline on YYYY-MM-DD HH:MM
# Reproduces: <output>
import subprocess, sys
subprocess.check_call([
    sys.executable.replace("python", "python"),
    "~/.claude/skills/semantic-pipeline/scripts/run_pipeline.py".replace("~", "<HOME>"),
    "--input", "<input>", "--output", "<output>",
    "--id_col", "<id>", "--text_col", "<text>",
    # ... any other args
])
```

---

## Output schema

A parquet with at minimum:
- `id` (string)
- `word_dsi` (float; NaN if doc too short or BERT failed)
- `sentence_dist` (float; NaN if < 2 sentences)
- `sentence_count` (int)
- `doc_dist_<cohort_label>` (float; one column per cohort definition)

If the user wants to compare across a condition variable (e.g., AI vs Google) **after** the pipeline runs, that's a separate analysis the orchestrator does NOT do. Suggest a follow-up: per-cohort t-tests + pooled Stouffer z + Cohen's d. Write it as a small companion script if needed.

---

## Important gotchas

- **bert-large-uncased is downloaded on first run** (~1.3GB to `~/.cache/huggingface/`). Don't surprise the user; mention it once.
- **NLTK punkt** is auto-downloaded into `~/nltk_data/`. The scripts handle this.
- **Long docs**: BERT scripts truncate sentences at 50 tokens (Beaty default). For very long docs, DSI saturates because token vocabulary repeats. Note in writeup if any doc has > 30 sentences.
- **MPS + bert-large**: confirmed working in this skill, but if you see `RuntimeError: MPS backend out of memory`, switch to CPU with `--device cpu`.
- **Costs**: OpenAI text-embedding-3-large is $0.13/M tokens. For 1,000 docs of 100 words = ~130k tokens ≈ $0.017. Negligible.

## Citation

If the user uses output in a paper, the cite chain is:
1. Word-level DSI: Johnson, D.R., Kaufman, J.C., Baker, B.S., Barbot, B., Green, A., van Hell, J., Patterson, J.D., Beaty, R.E. (2023). "Divergent semantic integration (DSI): Extracting creativity from narratives with distributional semantic modeling." *Behavior Research Methods.*
2. Sentence-level: Anderson, B. R., Shah, J. H., & Kreminski, M. (2024). "Homogenization Effects of Large Language Models on Human Creative Ideation."
3. Document-level: Cox et al. on chamfer Distinctness (referenced in Moon et al. methods).
4. Pipeline: Moon, K. (2025). "LLM-Era College Admissions Essays Exhibit Deep Homogenization Despite Lexical Diversity."
