"""
High-level retriever wrapper for TechnicalAgent.
Loads FAISS artifacts, performs MMR-style retrieval with dedup & light reranking,
then applies a NO_CONTEXT threshold. Returns LangChain Documents + scores
and a compact sources view for citation.

Usage:
  uv run python -m retriever.retriever --query "My fiber internet drops; PON LED is blinking" \
      --artifacts_dir artifacts --top_k 8 --threshold 0.25

Integration (example):
  from retriever.retriever import load_retriever
  r = load_retriever()
  result = r.retrieve("How to enable bridge mode on ONT?")
  if result["no_context"]:
      # ask for clarification or say docs don't cover it
  else:
      docs = result["docs"]            # list[Document]
      sources = result["sources"]       # list[dict]
      # pass to LLM as context
"""
from __future__ import annotations

import argparse
import json
import math
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings


# -----------------------------
# Config
# -----------------------------

@dataclass
class RetrieverConfig:
    artifacts_dir: Path = Path("artifacts")
    index_name: str = "index"
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    top_k: int = 8 # final number of docs to return
    fetch_k: int = 24  # for MMR-style diversification - collect this many, then dedup & rerank
    threshold: float = 0.5  # cosine/IP with normalized embeddings; adjust by stats if present - threshold to decide NO_CONTEXT
    min_hits: int = 3  # require at least this many docs after filtering
    #freshness_boost: float = 0.10  # +10% to result score for newer docs (if last_updated present)
    #step_section_boost: float = 0.08  # +8% if section mentions step/verification (to favor procedural content)
    freshness_boost: float = 0.0  # DISABLED: boosts were inflating scores above 1.0, breaking threshold logic
    step_section_boost: float = 0.0  # DISABLED: section boost also prevented proper NO_CONTEXT detection

# -----------------------------
# Utilities
# -----------------------------

def _parse_date(iso: str | None) -> float:
    if not iso:
        return 0.0
    try:
        return datetime.fromisoformat(iso).timestamp()
    except Exception:
        return 0.0


def _softmax(x: List[float]) -> List[float]:
    m = max(x) if x else 0.0
    ex = [math.exp(v - m) for v in x]
    s = sum(ex) or 1.0
    return [v / s for v in ex]


# -----------------------------
# Core class
# -----------------------------
# Import OpenAIEmbeddings here so the top-level imports remain unchanged


class KBRetriever:
    def __init__(self, cfg: RetrieverConfig):
        self.cfg = cfg
        self.embedder = OpenAIEmbeddings(model=self.cfg.embedding_model)
        self.vs = FAISS.load_local(
            folder_path=str(cfg.artifacts_dir),
            index_name=cfg.index_name,
            embeddings=self.embedder,
        )
        self._stats = self._load_stats()
        self._apply_stats_threshold()

    # ---- meta ----
    def _load_stats(self) -> Dict[str, Any]:
        stats_path = self.cfg.artifacts_dir / "stats.json"
        if stats_path.exists():
            try:
                return json.loads(stats_path.read_text())
            except Exception:
                return {}
        return {}

    def _apply_stats_threshold(self) -> None:
        # If stats include p10 or similar, we could lift the threshold to avoid over-retrieving
        # This is a simple heuristic; keep user's configured threshold as a floor.
        # Currently stats.json from builder doesn't include p10; keep placeholder for future.
        pass

    # ---- retrieval ----
    def _mmr_fetch(self, query: str, fetch_k: int) -> List[Tuple[Document, float]]:
        # LangChain FAISS supports similarity_search_with_score; we implement a simple diversity pass.
        # 1) fetch many by similarity; 2) greedily add diverse docs by penalizing same section/doc.
        candidates = self.vs.similarity_search_with_score(query, k=fetch_k)
        picked: List[Tuple[Document, float]] = []
        seen_keys: set[str] = set()
        for doc, score in candidates:
            key = f"{doc.metadata.get('doc_id')}|{'/'.join(doc.metadata.get('section_path', []))}"
            if key in seen_keys:
                # keep only the first (best) per section
                continue
            seen_keys.add(key)
            picked.append((doc, float(score)))
        return picked

    def _apply_boosts(self, query: str, items: List[Tuple[Document, float]]) -> List[Tuple[Document, float]]:
        # Normalize scores to [0,1] (they may already be cosines); then apply light boosts
        # Note: FAISS with normalized embeddings returns inner product ~ cosine in [-1,1].
        # Clamp to [0,1].
        boosted: List[Tuple[Document, float]] = []
        for doc, s in items:
            score = max(0.0, min(1.0, float(s)))
            meta = doc.metadata or {}
            # freshness
            if self.cfg.freshness_boost > 0:
                ts = _parse_date(meta.get("last_updated"))
                if ts > 0:
                    # Relative boost versus oldest in this batch is complex; here add fixed % if date exists
                    score *= (1.0 + self.cfg.freshness_boost)
            # section boost
            section = " ".join(meta.get("section_path", [])).lower()
            if any(tag in section for tag in ["step", "verification"]):
                score *= (1.0 + self.cfg.step_section_boost)
            boosted.append((doc, score))
        # Re-rank by boosted score
        boosted.sort(key=lambda t: t[1], reverse=True)
        return boosted

    def retrieve(self, query: str, top_k: int | None = None) -> Dict[str, Any]:
        top_k = top_k or self.cfg.top_k
        # Step 1: fetch with diversity
        items = self._mmr_fetch(query, fetch_k=self.cfg.fetch_k)
        # Step 2: boosts & rerank
        items = self._apply_boosts(query, items)
        # Step 3: take top_k
        items = items[:top_k]
        # Step 4: NO_CONTEXT decision
        scores = [s for _, s in items]
        no_context = (len(items) < self.cfg.min_hits) or (sum(scores) / max(1, len(scores)) < self.cfg.threshold)
        # Compose sources view
        sources = [self._to_source_dict(doc, score) for doc, score in items]
        return {
            "docs": [doc for doc, _ in items],
            "scores": scores,
            "sources": sources,
            "no_context": no_context,
            "applied_threshold": self.cfg.threshold,
        }

    @staticmethod
    def _to_source_dict(doc: Document, score: float) -> Dict[str, Any]:
        m = doc.metadata or {}
        return {
            "title": m.get("title"),
            "section": " / ".join(m.get("section_path", [])) or None,
            "file": Path(m.get("path", "")).name or None,
            "version": m.get("version"),
            "score": round(float(score), 4),
        }
