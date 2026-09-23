"""
run_pipeline.py — orchestrate the 3-level semantic diversity pipeline.

Reads an input parquet with `id` and `text` columns, runs:
  1. word-level DSI (BERT)
  2. sentence-level mean pairwise distance (SBERT)
  3. document-level chamfer Distinctness (OpenAI) — once per requested cohort

Writes one merged output parquet with all three measures, plus the
original columns preserved.

Also writes a sibling .run.py snapshot script for reproducibility (records
the exact invocation + timestamp + working directory).

Example:
  python run_pipeline.py \
    --input data/appeals.parquet --output data/appeals_diversity.parquet \
    --id_col session_id --text_col text \
    --group_col cause          # primary cohort
    --also_free_for_all        # add a __all__ cohort column too
"""

from __future__ import annotations

import argparse
import os
import shlex
import subprocess
import sys
import time
from pathlib import Path

import pandas as pd

SCRIPTS = Path(__file__).resolve().parent
ALL_LABEL = "__all__"


def run(cmd: list[str]) -> None:
    print("\n$ " + " ".join(shlex.quote(c) for c in cmd), file=sys.stderr)
    res = subprocess.run(cmd, check=False)
    if res.returncode != 0:
        raise SystemExit(f"step failed (rc={res.returncode}): {cmd[0]} {cmd[1] if len(cmd)>1 else ''}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--id_col", default="id")
    ap.add_argument("--text_col", default="text")
    ap.add_argument("--group_col", default=None,
                    help="cohort column for chamfer; if absent and --also_free_for_all not set, free-for-all is the only cohort")
    ap.add_argument("--also_free_for_all", action="store_true",
                    help="if --group_col is set, also compute a __all__ cohort column")
    ap.add_argument("--device", default=None)
    ap.add_argument("--cached_doc_embeddings", default=None)
    ap.add_argument("--save_doc_embeddings", default=None,
                    help="optional path to cache the OpenAI embeddings parquet for reuse")
    ap.add_argument("--openai_model", default="text-embedding-3-large")
    ap.add_argument("--sbert_model", default="sentence-transformers/all-MiniLM-L6-v2")
    ap.add_argument("--skip_word", action="store_true")
    ap.add_argument("--skip_sent", action="store_true")
    ap.add_argument("--skip_doc", action="store_true")
    args = ap.parse_args()

    input_p = Path(args.input).resolve()
    output_p = Path(args.output).resolve()
    output_p.parent.mkdir(parents=True, exist_ok=True)
    workdir = output_p.parent / (output_p.stem + "_workdir")
    workdir.mkdir(parents=True, exist_ok=True)

    py = sys.executable  # use the interpreter that called us (the skill venv)

    # ---- Step 1: word-level DSI ----
    word_out = workdir / "word_dsi.parquet"
    if args.skip_word and word_out.exists():
        print(f"[run] skipping word-level (cache exists)", file=sys.stderr)
    elif not args.skip_word:
        cmd = [py, str(SCRIPTS / "01_word_level.py"),
               "--input", str(input_p), "--output", str(word_out),
               "--id_col", args.id_col, "--text_col", args.text_col]
        if args.device:
            cmd += ["--device", args.device]
        run(cmd)

    # ---- Step 2: sentence-level ----
    sent_out = workdir / "sentence_dist.parquet"
    if args.skip_sent and sent_out.exists():
        print(f"[run] skipping sentence-level (cache exists)", file=sys.stderr)
    elif not args.skip_sent:
        cmd = [py, str(SCRIPTS / "02_sentence_level.py"),
               "--input", str(input_p), "--output", str(sent_out),
               "--id_col", args.id_col, "--text_col", args.text_col,
               "--model", args.sbert_model]
        if args.device:
            cmd += ["--device", args.device]
        run(cmd)

    # ---- Step 3: doc-level (per requested cohort) ----
    cohort_outs: list[tuple[str, Path]] = []
    cohorts: list[str | None] = []
    if not args.skip_doc:
        if args.group_col:
            cohorts.append(args.group_col)
            if args.also_free_for_all:
                cohorts.append(ALL_LABEL)
        else:
            cohorts.append(ALL_LABEL)

        for cohort in cohorts:
            label = ALL_LABEL if cohort == ALL_LABEL else cohort
            out_path = workdir / f"doc_dist_{label}.parquet"
            cmd = [py, str(SCRIPTS / "03_doc_level.py"),
                   "--input", str(input_p), "--output", str(out_path),
                   "--id_col", args.id_col, "--text_col", args.text_col,
                   "--model", args.openai_model]
            if cohort != ALL_LABEL:
                cmd += ["--group_col", cohort]
            if args.cached_doc_embeddings:
                cmd += ["--cached_embeddings", args.cached_doc_embeddings]
            if args.save_doc_embeddings:
                cmd += ["--save_embeddings", args.save_doc_embeddings]
            run(cmd)
            cohort_outs.append((label, out_path))

    # ---- Merge ----
    print("[run] merging outputs", file=sys.stderr)
    base = pd.read_parquet(input_p)
    base[args.id_col] = base[args.id_col].astype(str)
    merged = base.rename(columns={args.id_col: "id"})  # canonicalize for merges; restore at end

    if not args.skip_word and word_out.exists():
        wdf = pd.read_parquet(word_out)
        merged = merged.merge(wdf, on="id", how="left")
    if not args.skip_sent and sent_out.exists():
        sdf = pd.read_parquet(sent_out)
        merged = merged.merge(sdf, on="id", how="left")
    for label, p in cohort_outs:
        ddf = pd.read_parquet(p)
        merged = merged.merge(ddf, on="id", how="left")

    # restore the original id column name
    merged = merged.rename(columns={"id": args.id_col})
    merged.to_parquet(output_p, index=False)
    print(f"[run] wrote {output_p}  rows={len(merged)}  cols={list(merged.columns)}", file=sys.stderr)

    # ---- Reproducible run-script snapshot ----
    run_script = output_p.with_suffix(".run.py")
    invocation = sys.argv[:]  # the actual call this process received
    invocation[0] = str(SCRIPTS / "run_pipeline.py")  # canonicalize first arg
    ts = time.strftime("%Y-%m-%d %H:%M:%S %z")
    script_body = f'''#!/usr/bin/env python
# Auto-generated by /semantic-pipeline on {ts}
# CWD at runtime: {os.getcwd()}
# Reproduces: {output_p}

import subprocess, sys

subprocess.check_call([sys.executable] + {invocation!r})
'''
    run_script.write_text(script_body)
    run_script.chmod(0o755)
    print(f"[run] reproducible script -> {run_script}", file=sys.stderr)


if __name__ == "__main__":
    main()
