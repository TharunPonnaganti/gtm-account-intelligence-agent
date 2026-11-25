"""Retrieval-augmented generation (RAG) retriever.

Loads source documents from a directory, splits them into chunks, and returns
the chunks most relevant to a query. This uses a lightweight term-frequency
overlap score so it runs with no extra dependencies and no network. For
production you would swap `_score` for embedding-based similarity (e.g. Voyage
or another embedding model) behind the same interface.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from pathlib import Path

from .schemas import RetrievedChunk

_WORD = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> list[str]:
    return _WORD.findall(text.lower())


def _chunk(text: str, max_chars: int = 800) -> list[str]:
    """Split on blank lines, then pack paragraphs up to ~max_chars per chunk."""
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks: list[str] = []
    buf = ""
    for para in paras:
        if len(buf) + len(para) + 2 <= max_chars:
            buf = f"{buf}\n\n{para}" if buf else para
        else:
            if buf:
                chunks.append(buf)
            buf = para
    if buf:
        chunks.append(buf)
    return chunks


class Retriever:
    """Indexes text/markdown files in a folder and retrieves relevant chunks."""

    def __init__(self, sources_dir: str | Path) -> None:
        self.sources_dir = Path(sources_dir)
        self._chunks: list[tuple[str, str]] = []   # (source, text)
        self._doc_freq: Counter[str] = Counter()
        self._load()

    def _load(self) -> None:
        if not self.sources_dir.exists():
            return
        for path in sorted(self.sources_dir.rglob("*")):
            if path.suffix.lower() not in {".txt", ".md"}:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for chunk in _chunk(text):
                self._chunks.append((path.name, chunk))
                for term in set(_tokenize(chunk)):
                    self._doc_freq[term] += 1

    def _score(self, query_terms: list[str], chunk_text: str) -> float:
        """TF-IDF-style overlap: reward query terms that are rare across the corpus."""
        tf = Counter(_tokenize(chunk_text))
        n_docs = max(len(self._chunks), 1)
        score = 0.0
        for term in query_terms:
            if term in tf:
                idf = math.log((n_docs + 1) / (self._doc_freq.get(term, 0) + 1)) + 1.0
                score += tf[term] * idf
        # length-normalize so long chunks don't dominate
        return score / math.sqrt(sum(tf.values()) or 1)

    def retrieve(self, query: str, k: int = 4) -> list[RetrievedChunk]:
        query_terms = _tokenize(query)
        scored = [
            RetrievedChunk(source=src, text=txt, score=self._score(query_terms, txt))
            for src, txt in self._chunks
        ]
        scored = [c for c in scored if c.score > 0]
        scored.sort(key=lambda c: c.score, reverse=True)
        return scored[:k]
