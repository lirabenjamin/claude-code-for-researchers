"""
02_sentence_level.py — Sentence-level semantic diversity.

For each document: NLTK Punkt sentence-segment, embed each sentence with
sentence-transformers/all-MiniLM-L6-v2 (or any SBERT model), compute the
mean pairwise cosine distance across sentence embeddings.

Per Anderson, Shah, Kreminski (2024) homogenization paper.

Changes from upstream:
  - parquet I/O
  - device auto-select: cuda > mps > cpu
"""

from __future__ import annotations

import argparse
import os
import string
import sys
import time
from pathlib import Path
from typing import List, Tuple

import numpy as np
import pandas as pd
import torch
from tqdm import tqdm

nltk = None
PunktSentenceTokenizer = None
SentenceTransformer = None


def _lazy_imports():
    global nltk, PunktSentenceTokenizer, SentenceTransformer
    import nltk as _nltk
    nltk = _nltk
    try:
        _nltk.data.find("tokenizers/punkt")
    except LookupError:
        _nltk.download("punkt", quiet=True)
        _nltk.download("punkt_tab", quiet=True)
    from nltk.tokenize.punkt import PunktSentenceTokenizer as _Punkt
    from sentence_transformers import SentenceTransformer as _ST
    PunktSentenceTokenizer = _Punkt
    SentenceTransformer = _ST


def pick_device(override: str | None = None) -> torch.device:
    if override:
        return torch.device(override)
    if torch.cuda.is_available():
        return torch.device("cuda")
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


class SentDivPipeline:
    def __init__(self, model_name: str, device: torch.device, min_len: int = 3, batch_size: int = 16):
        self.device = device
        self.segmenter = PunktSentenceTokenizer()
        self.model = SentenceTransformer(model_name, device=str(device))
        self.model.eval()
        self.min_len = min_len
        self.batch_size = batch_size
        self._punct = str.maketrans("", "", string.punctuation)
        torch.set_grad_enabled(False)

    def _segment(self, text: str) -> List[str]:
        self.segmenter.train(text)
        raw = self.segmenter.tokenize(text)
        return [s.translate(self._punct).strip() for s in raw if len(s.translate(self._punct).strip()) >= self.min_len]

    @torch.no_grad()
    def mean_pairwise_distance(self, text: str) -> Tuple[float, int]:
        if not isinstance(text, str) or len(text) < 10:
            return float("nan"), 0
        sents = self._segment(text)
        if len(sents) < 2:
            return float("nan"), len(sents)
        emb = self.model.encode(
            sents,
            batch_size=self.batch_size,
            convert_to_tensor=True,
            device=self.device,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        if emb.size(0) < 2:
            return float("nan"), emb.size(0)
        sim = emb @ emb.T
        dist = 1.0 - sim
        n = dist.size(0)
        iu = torch.triu_indices(n, n, offset=1, device=dist.device)
        return float(dist[iu[0], iu[1]].mean().item()), n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--id_col", default="id")
    ap.add_argument("--text_col", default="text")
    ap.add_argument("--model", default="sentence-transformers/all-MiniLM-L6-v2")
    ap.add_argument("--device", default=None)
    ap.add_argument("--batch_size", type=int, default=16)
    ap.add_argument("--min_sentence_len", type=int, default=3)
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()

    _lazy_imports()
    device = pick_device(args.device)
    print(f"[02_sentence_level] device={device}  model={args.model}", file=sys.stderr)

    df = pd.read_parquet(args.input)
    if args.id_col not in df.columns:
        raise SystemExit(f"id_col {args.id_col!r} not in input columns")
    if args.text_col not in df.columns:
        raise SystemExit(f"text_col {args.text_col!r} not in input columns")
    if args.limit:
        df = df.head(args.limit)

    pipe = SentDivPipeline(args.model, device, args.min_sentence_len, args.batch_size)
    rows = []
    t0 = time.time()
    for _, row in tqdm(df[[args.id_col, args.text_col]].iterrows(), total=len(df), desc="sent-div"):
        d, n = pipe.mean_pairwise_distance(row[args.text_col])
        rows.append({"id": str(row[args.id_col]), "sentence_dist": d, "sentence_count": n})

    out = pd.DataFrame(rows)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    out.to_parquet(args.output, index=False)
    elapsed = time.time() - t0
    print(f"[02_sentence_level] wrote {args.output}  rows={len(out)}  elapsed={elapsed:.1f}s", file=sys.stderr)


if __name__ == "__main__":
    main()
