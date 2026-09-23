"""
03_doc_level.py — Document-level chamfer Distinctness.

Embeds each document with OpenAI text-embedding-3-large (3072-dim), then
for each doc computes its minimum cosine distance to any OTHER doc in the
same cohort. Higher score = more thematically distinct relative to the
cohort.

Per Cox et al. (referenced in Moon et al. 2025).

Changes from upstream:
  - parquet I/O throughout
  - cohort column is generic (--group_col); if omitted, the whole dataset
    is one cohort ("free for all"); pass --group_col __all__ explicitly to
    request the same.
  - --cached_embeddings: skip the OpenAI step by passing an existing parquet
    with id + embedding (list[float], 3072-dim) columns.
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ALL_LABEL = "__all__"


def _get_api_key() -> str:
    # Try working-dir .env first, then $OPENAI_API_KEY, then a couple
    # of common dotfile locations.
    try:
        from dotenv import load_dotenv
        for p in [Path.cwd() / ".env", Path.home() / ".env"]:
            if p.exists():
                load_dotenv(p)
    except Exception:
        pass
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise SystemExit("OPENAI_API_KEY not set in env or .env files")
    return key


def embed_openai(texts: list[str], model: str = "text-embedding-3-large", batch_size: int = 128) -> np.ndarray:
    from openai import OpenAI
    client = OpenAI(api_key=_get_api_key())
    out: list[list[float]] = []
    for i in range(0, len(texts), batch_size):
        chunk = texts[i:i + batch_size]
        for attempt in range(5):
            try:
                resp = client.embeddings.create(model=model, input=chunk)
                out.extend([d.embedding for d in resp.data])
                break
            except Exception as e:
                wait = 2 ** attempt
                print(f"  retry {attempt + 1} after {wait}s: {e}", file=sys.stderr)
                time.sleep(wait)
        else:
            raise RuntimeError("embedding failed after 5 retries")
        print(f"  embedded {min(i + batch_size, len(texts))}/{len(texts)}", file=sys.stderr)
    return np.asarray(out, dtype=np.float32)


def chamfer_min_distance(X: np.ndarray) -> np.ndarray:
    """For each row of L2-normalized X, return min cosine distance to any
    other row. NaN if X has fewer than 2 rows.
    """
    if len(X) < 2:
        return np.full(len(X), np.nan)
    # X is float32; gram = X @ X.T, cosine dist = 1 - gram
    gram = X @ X.T
    np.fill_diagonal(gram, -np.inf)  # exclude self
    nearest_sim = gram.max(axis=1)
    return (1.0 - nearest_sim).astype(np.float64)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="input parquet")
    ap.add_argument("--output", required=True, help="output parquet w/ id + doc_dist_<cohort>")
    ap.add_argument("--id_col", default="id")
    ap.add_argument("--text_col", default="text")
    ap.add_argument("--group_col", default=None,
                    help="column for cohort; if None or __all__, whole dataset is one cohort")
    ap.add_argument("--cached_embeddings", default=None,
                    help="parquet with id + embedding columns to skip OpenAI step")
    ap.add_argument("--model", default="text-embedding-3-large")
    ap.add_argument("--save_embeddings", default=None,
                    help="optional path to cache the embeddings parquet for reuse")
    args = ap.parse_args()

    df = pd.read_parquet(args.input)
    if args.id_col not in df.columns:
        raise SystemExit(f"id_col {args.id_col!r} not in input columns")
    if args.text_col not in df.columns:
        raise SystemExit(f"text_col {args.text_col!r} not in input columns")

    ids = df[args.id_col].astype(str).to_numpy()
    texts = df[args.text_col].astype(str).fillna("").to_list()
    group_col = args.group_col
    label = ALL_LABEL if (group_col is None or group_col == ALL_LABEL) else group_col

    # --- embeddings ---
    if args.cached_embeddings and Path(args.cached_embeddings).exists():
        print(f"[03_doc_level] using cached embeddings from {args.cached_embeddings}", file=sys.stderr)
        cache = pd.read_parquet(args.cached_embeddings)
        if "id" not in cache.columns or "embedding" not in cache.columns:
            raise SystemExit("cached embeddings parquet must have id + embedding columns")
        cache["id"] = cache["id"].astype(str)
        emb_map = dict(zip(cache["id"], cache["embedding"]))
        missing = [i for i in ids if i not in emb_map]
        if missing:
            print(f"  {len(missing)} ids missing from cache — embedding those", file=sys.stderr)
            new_texts = [texts[k] for k, i in enumerate(ids) if i not in emb_map]
            new_ids = [i for i in ids if i not in emb_map]
            new_emb = embed_openai(new_texts, model=args.model)
            for i, e in zip(new_ids, new_emb):
                emb_map[i] = e.tolist()
        X = np.asarray([emb_map[i] for i in ids], dtype=np.float32)
    else:
        print(f"[03_doc_level] embedding {len(texts)} docs with {args.model}", file=sys.stderr)
        X = embed_openai(texts, model=args.model)

    if args.save_embeddings:
        Path(args.save_embeddings).parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame({"id": ids, "embedding": [list(map(float, v)) for v in X]}).to_parquet(
            args.save_embeddings, index=False)
        print(f"  saved embeddings -> {args.save_embeddings}", file=sys.stderr)

    # L2-normalize for cosine
    norms = np.linalg.norm(X, axis=1, keepdims=True)
    Xn = X / np.clip(norms, 1e-12, None)

    # --- chamfer per cohort ---
    if group_col is None or group_col == ALL_LABEL:
        groups = np.full(len(ids), "__all__", dtype=object)
    else:
        if group_col not in df.columns:
            raise SystemExit(f"group_col {group_col!r} not in input columns")
        groups = df[group_col].astype(str).to_numpy()

    out_dist = np.full(len(ids), np.nan)
    for g in np.unique(groups):
        mask = groups == g
        if mask.sum() < 2:
            print(f"  skip cohort {g!r}: only {int(mask.sum())} docs", file=sys.stderr)
            continue
        out_dist[mask] = chamfer_min_distance(Xn[mask])

    col_name = f"doc_dist_{label}"
    out = pd.DataFrame({"id": ids, col_name: out_dist, "cohort_" + label: groups})
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    out.to_parquet(args.output, index=False)
    print(f"[03_doc_level] wrote {args.output}  rows={len(out)}", file=sys.stderr)
    print(f"  {col_name}: mean={np.nanmean(out_dist):.4f}  median={np.nanmedian(out_dist):.4f}", file=sys.stderr)


if __name__ == "__main__":
    main()
