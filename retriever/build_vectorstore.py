"""
Builds a FAISS vector index from local Markdown docs in data/docs/.

Run:
  uv run python retriever/build_vectorstore.py \
    --docs_dir data/docs \
    --artifacts_dir artifacts \
    --chunk_size 600 \
    --chunk_overlap 120
"""


from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import yaml

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

from dotenv import load_dotenv
load_dotenv()

# -----------------------------
# Helpers: file loading & FM
# -----------------------------

FRONT_MATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def read_markdown(path: Path) -> Tuple[Dict, str]:
    """Return (front_matter_dict, content_wo_fm) for a markdown file.
    If no FM, returns ({}, full_text)
    """
    text = path.read_text(encoding="utf-8")
    m = FRONT_MATTER_RE.match(text)
    if m:
        fm_raw = m.group(1)
        try:
            fm = yaml.safe_load(fm_raw) or {}
        except Exception:
            fm = {}
        content = text[m.end():]
    else:
        fm = {}
        content = text
    return fm, normalize_markdown(content)


def normalize_markdown(text: str) -> str:
    """Light normalization: strip trailing spaces, collapse >2 empty lines, convert tables to plain text.
    We keep lists/headers intact so the splitter can use boundaries.
    """
    # crude table strip: remove table pipes but keep content
    text = re.sub(r"^\|.*\|$", lambda m: m.group(0).replace("|", "\t"), text, flags=re.MULTILINE)
    # remove HTML comments
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    # collapse empty lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


# -----------------------------
# Chunking
# -----------------------------

@dataclass
class Chunk:
    doc_id: str
    title: str
    section_path: List[str]
    path: str
    version: Optional[str]
    last_updated: Optional[str]
    audience: Optional[str]
    keywords: List[str]
    language: str
    text: str
    sha1: str


HEADER_RE = re.compile(r"^(#{1,6})\s+(.*)$", re.MULTILINE)


def section_paths(md_text: str) -> List[Tuple[int, str]]:
    """Return list of (level, title) headers order from markdown.
    level = number of #
    """
    return [(len(m.group(1)), m.group(2).strip()) for m in HEADER_RE.finditer(md_text)]


def split_into_chunks(md_text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n## ", "\n### ", "\n- ", "\n1) ", "\n", " "],
    )
    return [c for c in splitter.split_text(md_text) if len(c.strip()) > 0]


def infer_section_path(full_text: str, chunk_text: str) -> List[str]:
    # heuristic: last 2 headers preceding first char of chunk in full text
    # fallback to []
    try:
        start_idx = full_text.find(chunk_text[:50])
        if start_idx == -1:
            return []
        headers = []
        for m in HEADER_RE.finditer(full_text[:start_idx]):
            headers.append((len(m.group(1)), m.group(2).strip()))
        titles = [t for _, t in headers[-3:]]  # last up to 3 headers
        return titles
    except Exception:
        return []


# -----------------------------
# Embeddings
# -----------------------------

def build_embedder():
    """
    Build an OpenAI embeddings client via the regular OpenAI API.
    Requires OPENAI_API_KEY in the environment. Optionally set:
      EMBEDDING_MODEL (default: text-embedding-3-small)
    """
    model_name = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY environment variable is required for OpenAI embeddings")
    return OpenAIEmbeddings(model=model_name)


# -----------------------------
# Build pipeline
# -----------------------------

def hash_text(t: str) -> str:
    return hashlib.sha1(t.encode("utf-8")).hexdigest()


def build_index(docs_dir: Path, artifacts_dir: Path, chunk_size: int, chunk_overlap: int) -> None:
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    chunks: List[Chunk] = []
    meta_records: List[Dict] = []

    for md_path in sorted(docs_dir.glob("*.md")):
        fm, content = read_markdown(md_path) # load front matter + content
        doc_id = md_path.stem
        title = fm.get("title", doc_id)
        version = fm.get("version")
        last_updated = fm.get("last_updated")
        audience = fm.get("audience")
        language = fm.get("language", "en")  # user said docs translated to EN

        # keywords: from summary + headers
        summary = fm.get("summary", "")
        header_titles = [t for _, t in section_paths(content)]
        kw_pool = (summary + " " + " ".join(header_titles)).lower()
        keywords = sorted(list({w.strip(".,:;()[]") for w in kw_pool.split() if 2 < len(w) < 24}))[:12]

        raw_chunks = split_into_chunks(content, chunk_size, chunk_overlap)
        for ch in raw_chunks:
            if len(ch) < 200 and not any(k in ch.lower() for k in keywords):
                continue
            section = infer_section_path(content, ch)
            c = Chunk(
                doc_id=doc_id,
                title=title,
                section_path=section,
                path=str(md_path),
                version=version,
                last_updated=last_updated,
                audience=audience,
                keywords=keywords,
                language=language,
                text=ch.strip(),
                sha1=hash_text(ch),
            )
            chunks.append(c)

        meta_records.append({
            "doc_id": doc_id,
            "path": str(md_path),
            "title": title,
            "version": version,
            "last_updated": last_updated,
            "num_chunks": len(raw_chunks),
            "language": language,
        })

    if not chunks:
        raise RuntimeError("No chunks produced. Check docs_dir and content.")

    # Prepare LC documents
    from langchain_core.documents import Document

    lc_docs = []
    for c in chunks:
        metadata = {
            "doc_id": c.doc_id,
            "title": c.title,
            "section_path": c.section_path,
            "path": c.path,
            "version": c.version,
            "last_updated": c.last_updated,
            "audience": c.audience,
            "keywords": c.keywords,
            "language": c.language,
            "sha1": c.sha1,
        }
        lc_docs.append(Document(page_content=c.text, metadata=metadata))

    embedder = build_embedder()

    # Build FAISS
    vs = FAISS.from_documents(lc_docs, embedder)

    # Persist artifacts
    index_path = artifacts_dir / "index.faiss"
    store_path = artifacts_dir / "index.pkl"
    vs.save_local(folder_path=str(artifacts_dir), index_name="index")

    # Write meta
    (artifacts_dir / "index_meta.json").write_text(json.dumps(meta_records, ensure_ascii=False, indent=2), encoding="utf-8")
    # Embedder info (OpenAI embeddings)
    embedder_info = {
        "provider": "openai",
        "model": os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
        "normalize": True,
        "dim_hint": getattr(getattr(embedder, "client", None), "get_sentence_embedding_dimension", lambda: None)(),
        "built_at": int(time.time()),
    }
    (artifacts_dir / "embedder_info.json").write_text(json.dumps(embedder_info, indent=2), encoding="utf-8")

    # Stats (simple)
    stats = {
        "num_docs": len(meta_records),
        "num_chunks": len(chunks),
        "avg_chunk_chars": int(sum(len(c.text) for c in chunks) / len(chunks)),
        "p_sample": 16,
    }
    (artifacts_dir / "stats.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")

    print(f"✅ Built FAISS index: {index_path} (+ meta). Chunks: {len(chunks)}")


# -----------------------------
# CLI
# -----------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--docs_dir", type=Path, default=Path("data/docs"))
    parser.add_argument("--artifacts_dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--chunk_size", type=int, default=600)
    parser.add_argument("--chunk_overlap", type=int, default=120)
    args = parser.parse_args()

    build_index(args.docs_dir, args.artifacts_dir, args.chunk_size, args.chunk_overlap)