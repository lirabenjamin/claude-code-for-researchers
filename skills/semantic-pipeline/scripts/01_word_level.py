"""
01_word_level.py — Word-level Divergent Semantic Integration (DSI).

Adapted from Patterson/Beaty/Johnson 2022 (osf.io/ath2s) and Kibum Moon's
GPU-optimized variant. Same recipe:
  - bert-large-uncased
  - sentence-segment with NLTK Punkt (retrained per doc)
  - per sentence: strip punctuation, tokenize max_length=50, padded
  - filter out [CLS]/[SEP]/[PAD] + basic punctuation
  - extract layers 6 and 7 hidden states for each non-special token
  - mean cosine distance across all token-embedding pairs (both layers
    pooled, so each token contributes 2 vectors)

Changes:
  - parquet I/O (not CSV)
  - device auto-select: cuda > mps > cpu
  - batching across sentences (one forward pass per doc, not one per sentence)
"""

from __future__ import annotations

import argparse
import os
import string
import sys
import time
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd
import torch
from tqdm import tqdm

# Lazy heavy imports
nltk = None
PunktSentenceTokenizer = None
BertTokenizer = None
BertModel = None


def _lazy_imports():
    global nltk, PunktSentenceTokenizer, BertTokenizer, BertModel
    import nltk as _nltk
    nltk = _nltk
    try:
        _nltk.data.find("tokenizers/punkt")
    except LookupError:
        print("downloading nltk punkt...", file=sys.stderr)
        _nltk.download("punkt", quiet=True)
        _nltk.download("punkt_tab", quiet=True)
    from nltk.tokenize.punkt import PunktSentenceTokenizer as _Punkt
    from transformers import BertTokenizer as _BT, BertModel as _BM
    PunktSentenceTokenizer = _Punkt
    BertTokenizer = _BT
    BertModel = _BM


MODEL_NAME = "bert-large-uncased"
MAX_TOKENS = 50
LAYERS_TO_USE = [6, 7]
FILTER_TOKENS = {"[CLS]", "[SEP]", "[PAD]", ".", ",", "!", "?"}


def pick_device(override: str | None = None) -> torch.device:
    if override:
        return torch.device(override)
    if torch.cuda.is_available():
        return torch.device("cuda")
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


class DSIPipeline:
    def __init__(self, device: torch.device):
        self.device = device
        self.tokenizer = BertTokenizer.from_pretrained(MODEL_NAME)
        self.model = BertModel.from_pretrained(MODEL_NAME, output_hidden_states=True).to(device).eval()
        self.segmenter = PunktSentenceTokenizer()
        self._punct = str.maketrans("", "", string.punctuation)
        torch.set_grad_enabled(False)

    def _clean_sentences(self, text: str) -> List[str]:
        self.segmenter.train(text)
        sents = self.segmenter.tokenize(text)
        return [s.translate(self._punct).strip() for s in sents if len(s.strip()) > 3]

    @torch.no_grad()
    def compute_dsi(self, text: str) -> float:
        if not isinstance(text, str) or len(text) < 10:
            return float("nan")
        sentences = self._clean_sentences(text)
        if not sentences:
            return float("nan")

        toks = self.tokenizer(
            sentences,
            padding=True,
            truncation=True,
            max_length=MAX_TOKENS,
            return_tensors="pt",
        )
        toks = {k: v.to(self.device) for k, v in toks.items()}
        out = self.model(**toks)
        hidden = out.hidden_states  # tuple of (B, T, D)

        input_ids = toks["input_ids"]
        attn = toks["attention_mask"]
        B, T = input_ids.shape

        # Build per-token mask once, reusable across layers
        ids_flat = input_ids.cpu().numpy()
        attn_flat = attn.cpu().numpy().astype(bool)
        # Decode each token id once
        keep = np.zeros((B, T), dtype=bool)
        for i in range(B):
            for j in range(T):
                if not attn_flat[i, j]:
                    continue
                tok = self.tokenizer.convert_ids_to_tokens(int(ids_flat[i, j]))
                if tok in FILTER_TOKENS:
                    continue
                keep[i, j] = True

        if keep.sum() < 2:
            return float("nan")

        keep_t = torch.from_numpy(keep).to(self.device)

        # Stack embeddings from layers 6 and 7 -> (sum(keep) * len(LAYERS), D)
        emb_chunks = []
        for layer in LAYERS_TO_USE:
            h = hidden[layer]
            emb_chunks.append(h[keep_t])
        emb = torch.cat(emb_chunks, dim=0)  # (N, D)
        if emb.size(0) < 2:
            return float("nan")

        emb = emb / emb.norm(dim=1, keepdim=True).clamp(min=1e-12)
        sim = emb @ emb.T
        dist = 1.0 - sim
        n = dist.size(0)
        iu = torch.triu_indices(n, n, offset=1, device=dist.device)
        return float(dist[iu[0], iu[1]].mean().item())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="input parquet")
    ap.add_argument("--output", required=True, help="output parquet with id + word_dsi")
    ap.add_argument("--id_col", default="id")
    ap.add_argument("--text_col", default="text")
    ap.add_argument("--device", default=None, help="override device: cuda/mps/cpu")
    ap.add_argument("--limit", type=int, default=None, help="debug: process first N rows only")
    args = ap.parse_args()

    _lazy_imports()
    device = pick_device(args.device)
    print(f"[01_word_level] device={device}", file=sys.stderr)

    df = pd.read_parquet(args.input)
    if args.id_col not in df.columns:
        raise SystemExit(f"id_col {args.id_col!r} not in input columns {list(df.columns)}")
    if args.text_col not in df.columns:
        raise SystemExit(f"text_col {args.text_col!r} not in input columns {list(df.columns)}")
    if args.limit:
        df = df.head(args.limit)

    pipe = DSIPipeline(device)
    rows = []
    t0 = time.time()
    for _, row in tqdm(df[[args.id_col, args.text_col]].iterrows(), total=len(df), desc="DSI"):
        dsi = pipe.compute_dsi(row[args.text_col])
        rows.append({"id": str(row[args.id_col]), "word_dsi": dsi})

    out = pd.DataFrame(rows)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    out.to_parquet(args.output, index=False)
    elapsed = time.time() - t0
    print(f"[01_word_level] wrote {args.output}  rows={len(out)}  elapsed={elapsed:.1f}s", file=sys.stderr)


if __name__ == "__main__":
    main()
