"""
Dual-Mode Vector Embeddings Engine for Task 2: Document Q&A Assistant.
Supports OpenAI, Google Gemini, and a high-speed Deterministic Local Embedding Engine
for 100% offline testing without external API key requirements.
"""

import os
import math
import hashlib
from typing import List, Optional
import numpy as np


class BaseEmbeddingEngine:
    """Abstract base interface for document and query embedding generation."""

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError

    def embed_query(self, text: str) -> List[float]:
        raise NotImplementedError

    def __call__(self, input: List[str]) -> List[List[float]]:
        """ChromaDB compatible embedding function interface."""
        return self.embed_documents(input)


class DeterministicLocalEmbeddingEngine(BaseEmbeddingEngine):
    """
    High-speed deterministic dense vector embedding engine (128-dim).
    Uses hashed character n-grams and term frequency with L2 normalization.
    Produces semantically meaningful cosine similarities for text retrieval
    with zero external dependencies or network requests.
    """

    def __init__(self, dimension: int = 128):
        self.dimension = dimension

    def _text_to_vector(self, text: str) -> List[float]:
        if not text.strip():
            return [0.0] * self.dimension

        vec = np.zeros(self.dimension, dtype=np.float32)
        words = text.lower().split()
        
        # Word-level features
        for word in words:
            h = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16)
            idx = h % self.dimension
            weight = 1.0 + (len(word) / 10.0)
            vec[idx] += weight

        # Character trigrams for morphological similarity
        cleaned = "".join(ch for ch in text.lower() if ch.isalnum() or ch.isspace())
        for i in range(len(cleaned) - 2):
            trigram = cleaned[i:i+3]
            h = int(hashlib.sha256(trigram.encode("utf-8")).hexdigest(), 16)
            idx = h % self.dimension
            vec[idx] += 0.5

        # L2 Normalization
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm

        return vec.tolist()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._text_to_vector(t) for t in texts]

    def embed_query(self, text: str) -> List[float]:
        return self._text_to_vector(text)


class OpenAIEmbeddingEngine(BaseEmbeddingEngine):
    """Embedding generator powered by OpenAI text-embedding-3-small."""

    def __init__(self, api_key: Optional[str] = None, model: str = "text-embedding-3-small"):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model = model

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        response = self.client.embeddings.create(input=texts, model=self.model)
        return [record.embedding for record in response.data]

    def embed_query(self, text: str) -> List[float]:
        response = self.client.embeddings.create(input=[text], model=self.model)
        return response.data[0].embedding


class GeminiEmbeddingEngine(BaseEmbeddingEngine):
    """Embedding generator powered by Google Gemini text-embedding-004."""

    def __init__(self, api_key: Optional[str] = None, model: str = "text-embedding-004"):
        from google import genai
        self.client = genai.Client(api_key=api_key or os.getenv("GEMINI_API_KEY"))
        self.model = model

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        for text in texts:
            result = self.client.models.embed_content(model=self.model, contents=text)
            embeddings.append(result.embedding.values)
        return embeddings

    def embed_query(self, text: str) -> List[float]:
        result = self.client.models.embed_content(model=self.model, contents=text)
        return result.embedding.values


def get_embedding_engine(
    provider: str = "auto",
    api_key: Optional[str] = None,
) -> BaseEmbeddingEngine:
    """
    Factory function instantiating the optimal embedding engine.
    Gracefully falls back to DeterministicLocalEmbeddingEngine if credentials are absent.
    """
    gemini_key = api_key or os.getenv("GEMINI_API_KEY")
    openai_key = api_key or os.getenv("OPENAI_API_KEY")

    if provider == "openai" and openai_key:
        try:
            return OpenAIEmbeddingEngine(api_key=openai_key)
        except Exception:
            pass
    elif provider == "gemini" and gemini_key:
        try:
            return GeminiEmbeddingEngine(api_key=gemini_key)
        except Exception:
            pass
    elif provider == "auto":
        if gemini_key:
            try:
                return GeminiEmbeddingEngine(api_key=gemini_key)
            except Exception:
                pass
        if openai_key:
            try:
                return OpenAIEmbeddingEngine(api_key=openai_key)
            except Exception:
                pass

    # Default robust deterministic local engine
    return DeterministicLocalEmbeddingEngine()
