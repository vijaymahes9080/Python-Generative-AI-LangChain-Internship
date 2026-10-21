"""
ChromaDB Vector Retrieval & Grounded Q&A Engine for Task 2: Document Q&A Assistant.
Enforces strict hallucination guardrails, citation verification (filename, page, excerpt),
and explicit refusal fallback when query is unsupported by document context.
"""

import os
import re
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict

import chromadb
from chromadb.config import Settings

from ingestion import DocumentChunk
from embeddings import get_embedding_engine, BaseEmbeddingEngine


FALLBACK_REFUSAL_MESSAGE = "I cannot find sufficient evidence in the uploaded documents to answer this question."


@dataclass
class Citation:
    source_file: str
    page_number: int
    excerpt: str
    relevance_score: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class QAResult:
    query: str
    answer: str
    is_grounded: bool
    citations: List[Citation]
    retrieved_chunks_count: int
    execution_time_ms: float
    provider_used: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "answer": self.answer,
            "is_grounded": self.is_grounded,
            "citations": [c.to_dict() for c in self.citations],
            "retrieved_chunks_count": self.retrieved_chunks_count,
            "execution_time_ms": self.execution_time_ms,
            "provider_used": self.provider_used,
        }


class RAGRetrievalService:
    """Manages ChromaDB indexing, semantic similarity retrieval, and grounded response synthesis."""

    def __init__(
        self,
        collection_name: str = "document_qa_collection",
        provider: str = "auto",
        api_key: Optional[str] = None,
        persist_directory: Optional[str] = None,
    ):
        self.collection_name = collection_name
        self.provider = provider
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.embedding_engine: BaseEmbeddingEngine = get_embedding_engine(provider, self.api_key)

        # Initialize ChromaDB Client
        if persist_directory:
            os.makedirs(persist_directory, exist_ok=True)
            self.chroma_client = chromadb.PersistentClient(path=persist_directory)
        else:
            self.chroma_client = chromadb.Client(Settings(anonymized_telemetry=False, is_persistent=False))

        self._reset_or_get_collection()

    def _reset_or_get_collection(self):
        """Create or recreate fresh Chroma collection."""
        try:
            self.chroma_client.delete_collection(self.collection_name)
        except Exception:
            pass
        self.collection = self.chroma_client.create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        self.indexed_files = set()
        self.total_chunks = 0

    def index_chunks(self, chunks: List[DocumentChunk]):
        """Embed and upsert document chunks into ChromaDB."""
        if not chunks:
            return

        ids = [c.chunk_id for c in chunks]
        texts = [c.text for c in chunks]
        metadatas = [
            {
                "source_file": c.source_file,
                "page_number": c.page_number,
                "chunk_index": c.chunk_index,
                "char_count": c.char_count,
            }
            for c in chunks
        ]

        embeddings = self.embedding_engine.embed_documents(texts)

        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
        )

        for c in chunks:
            self.indexed_files.add(c.source_file)
        self.total_chunks += len(chunks)

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Retrieve most similar chunks from vector store."""
        if self.total_chunks == 0:
            return []

        query_vector = self.embedding_engine.embed_query(query)
        results = self.collection.query(
            query_embeddings=[query_vector],
            n_results=min(top_k, self.total_chunks),
            include=["documents", "metadatas", "distances"],
        )

        retrieved = []
        if results and results["documents"] and results["documents"][0]:
            docs = results["documents"][0]
            metas = results["metadatas"][0]
            distances = results["distances"][0]

            for doc, meta, dist in zip(docs, metas, distances):
                # Cosine distance to similarity: similarity = 1 - distance
                similarity = round(max(0.0, 1.0 - float(dist)), 4)
                retrieved.append({
                    "text": doc,
                    "metadata": meta,
                    "similarity": similarity,
                })

        return retrieved

    def _synthesize_deterministic(self, query: str, retrieved: List[Dict[str, Any]]) -> str:
        """Offline deterministic QA engine that synthesizes answers strictly grounded in context."""
        query_words = set(re.findall(r"\w+", query.lower())) - {"what", "when", "where", "who", "which", "how", "is", "are", "the", "a", "an", "in", "on", "of", "for", "to"}
        
        best_sentence = None
        max_overlap = 0

        for item in retrieved:
            text = item["text"]
            sentences = re.split(r"(?<=[.!?])\s+", text)
            for s in sentences:
                s_words = set(re.findall(r"\w+", s.lower()))
                overlap = len(query_words.intersection(s_words))
                if overlap > max_overlap:
                    max_overlap = overlap
                    best_sentence = s.strip()

        # If query terms are absent or overlap is trivial, refuse cleanly
        if max_overlap < 1 or not best_sentence:
            return FALLBACK_REFUSAL_MESSAGE

        return f"Based on the documents: {best_sentence}"

    def ask(self, query: str, top_k: int = 3) -> QAResult:
        """
        Execute full RAG question answering pipeline:
        1. Retrieve top-k context chunks.
        2. Verify relevance threshold.
        3. Synthesize grounded answer.
        4. Assemble verifiable citations.
        """
        start_time = time.perf_counter()

        if self.total_chunks == 0:
            return QAResult(
                query=query,
                answer="No documents have been indexed yet. Please upload documents first.",
                is_grounded=False,
                citations=[],
                retrieved_chunks_count=0,
                execution_time_ms=0.0,
                provider_used="None",
            )

        retrieved = self.retrieve(query, top_k=top_k)

        # Build citations
        citations: List[Citation] = []
        for item in retrieved:
            excerpt_snippet = item["text"][:240] + "..." if len(item["text"]) > 240 else item["text"]
            citations.append(Citation(
                source_file=item["metadata"]["source_file"],
                page_number=item["metadata"]["page_number"],
                excerpt=excerpt_snippet,
                relevance_score=item["similarity"],
            ))

        # Check for context relevance
        if not retrieved or (retrieved and retrieved[0]["similarity"] < 0.20):
            elapsed = (time.perf_counter() - start_time) * 1000
            return QAResult(
                query=query,
                answer=FALLBACK_REFUSAL_MESSAGE,
                is_grounded=False,
                citations=citations,
                retrieved_chunks_count=len(retrieved),
                execution_time_ms=round(elapsed, 2),
                provider_used="Deterministic Guard",
            )

        # Context assembly
        context_blocks = []
        for idx, item in enumerate(retrieved):
            meta = item["metadata"]
            context_blocks.append(
                f"[Source {idx+1}: {meta['source_file']}, Page {meta['page_number']}]\n{item['text']}"
            )
        combined_context = "\n\n".join(context_blocks)

        system_prompt = (
            "You are a factual, context-grounded Document Q&A assistant. "
            "Answer the user's question ONLY using the factual context provided below. "
            "If the context does not explicitly contain the answer, reply exactly with: "
            f"'{FALLBACK_REFUSAL_MESSAGE}'\n"
            "Do NOT extrapolate, fabricate, or cite external knowledge not present in the context."
        )
        user_prompt = f"CONTEXT:\n{combined_context}\n\nQUESTION: {query}\n\nANSWER:"

        # Try live generation via Gemini or OpenAI if configured
        answer_text = None
        provider_used = "Deterministic Offline Engine"

        gemini_key = self.api_key or os.getenv("GEMINI_API_KEY")
        openai_key = self.api_key or os.getenv("OPENAI_API_KEY")

        if self.provider in ["auto", "gemini"] and gemini_key:
            try:
                from google import genai
                client = genai.Client(api_key=gemini_key)
                resp = client.models.generate_content(
                    model=os.getenv("DEFAULT_GEMINI_MODEL", "gemini-2.5-flash"),
                    contents=user_prompt,
                    config={"system_instruction": system_prompt, "temperature": 0.0},
                )
                if resp and resp.text:
                    answer_text = resp.text.strip()
                    provider_used = "Google Gemini"
            except Exception:
                pass

        if not answer_text and self.provider in ["auto", "openai"] and openai_key:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=openai_key)
                resp = client.chat.completions.create(
                    model=os.getenv("DEFAULT_OPENAI_MODEL", "gpt-4o-mini"),
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.0,
                )
                if resp.choices and resp.choices[0].message.content:
                    answer_text = resp.choices[0].message.content.strip()
                    provider_used = "OpenAI"
            except Exception:
                pass

        # Offline fallback synthesis
        if not answer_text:
            answer_text = self._synthesize_deterministic(query, retrieved)

        is_grounded = FALLBACK_REFUSAL_MESSAGE.lower() not in answer_text.lower()
        elapsed = (time.perf_counter() - start_time) * 1000

        return QAResult(
            query=query,
            answer=answer_text,
            is_grounded=is_grounded,
            citations=citations if is_grounded else citations[:1],
            retrieved_chunks_count=len(retrieved),
            execution_time_ms=round(elapsed, 2),
            provider_used=provider_used,
        )
