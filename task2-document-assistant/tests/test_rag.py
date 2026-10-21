"""
Automated unit tests for Task 2: Document Q&A Assistant with RAG & Vector Embeddings.
Validates chunking, metadata preservation, vector indexing, retrieval, citations, and refusal fallbacks.
"""

import sys
import os
import pytest
import numpy as np

# Ensure task directory is in sys.path
task_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if task_dir not in sys.path:
    sys.path.insert(0, task_dir)

from ingestion import DocumentIngestionService, DocumentIngestionError
from embeddings import DeterministicLocalEmbeddingEngine
from retrieval import RAGRetrievalService, FALLBACK_REFUSAL_MESSAGE


# ==============================================================================
# INGESTION TESTS
# ==============================================================================

def test_ingestion_txt_chunking_and_metadata():
    """Verify recursive text splitter preserves metadata and enforces chunk boundaries."""
    service = DocumentIngestionService(chunk_size=200, chunk_overlap=40)
    sample_text = (
        "Artificial intelligence systems are transforming enterprise operations.\n\n"
        "Retrieval-Augmented Generation couples large language models with vector retrieval.\n\n"
        "Security guardrails ensure that models only generate factual statements verified by source citations."
    )
    chunks = service.ingest(sample_text.encode("utf-8"), "test_policy.txt")

    assert len(chunks) >= 1
    for idx, c in enumerate(chunks):
        assert c.source_file == "test_policy.txt"
        assert c.page_number == 1
        assert c.chunk_index == idx
        assert len(c.text) > 0
        assert c.char_count == len(c.text)


def test_ingestion_empty_document_rejection():
    """Verify that empty documents raise DocumentIngestionError."""
    service = DocumentIngestionService()
    with pytest.raises(DocumentIngestionError):
        service.ingest(b"   \n  \t ", "empty.txt")


def test_ingestion_unsupported_extension_rejection():
    """Verify that unsupported extensions are rejected gracefully."""
    service = DocumentIngestionService()
    with pytest.raises(DocumentIngestionError):
        service.ingest(b"some content", "data.docx")


# ==============================================================================
# EMBEDDING ENGINE TESTS
# ==============================================================================

def test_embedding_deterministic_normalization():
    """Ensure the local embedding engine produces unit-norm dense vectors."""
    engine = DeterministicLocalEmbeddingEngine(dimension=128)
    vector = engine.embed_query("Principle of least privilege and cryptographic security")

    assert len(vector) == 128
    norm = np.linalg.norm(vector)
    # Unit vector check
    assert abs(norm - 1.0) < 1e-4


# ==============================================================================
# RETRIEVAL & GROUNDING TESTS
# ==============================================================================

def test_chromadb_indexing_and_similarity_retrieval():
    """Verify ChromaDB stores chunks and retrieves top hits with positive similarity scores."""
    rag = RAGRetrievalService(collection_name="test_retrieval_col", provider="offline")
    
    text_content = (
        "Standard SEC-902 mandates that all data at rest must be encrypted using AES-256-GCM. "
        "Customer-managed encryption keys must rotate automatically every 90 days. "
        "Network isolation requires that vector databases operate inside private subnets."
    )
    ingestion = DocumentIngestionService(chunk_size=300, chunk_overlap=50)
    chunks = ingestion.ingest(text_content.encode("utf-8"), "sec_902.txt")
    rag.index_chunks(chunks)

    assert rag.total_chunks == len(chunks)
    assert "sec_902.txt" in rag.indexed_files

    retrieved = rag.retrieve("What encryption algorithm is required for data at rest?", top_k=2)
    assert len(retrieved) > 0
    assert "AES-256-GCM" in retrieved[0]["text"]
    assert retrieved[0]["similarity"] > 0.0


def test_citation_generation_accuracy():
    """Verify citations include filename, page number, and literal excerpt."""
    rag = RAGRetrievalService(collection_name="test_citation_col", provider="offline")
    text = "Audit logging protocol requires quarterly automated bias testing for demographic parity."
    ingestion = DocumentIngestionService()
    chunks = ingestion.ingest(text.encode("utf-8"), "ethics_protocol.txt")
    rag.index_chunks(chunks)

    result = rag.ask("What is the frequency of automated bias testing?", top_k=1)
    assert result.is_grounded is True
    assert len(result.citations) > 0
    assert result.citations[0].source_file == "ethics_protocol.txt"
    assert result.citations[0].page_number == 1
    assert "bias testing" in result.citations[0].excerpt.lower()


def test_out_of_domain_refusal_fallback():
    """Verify that ungrounded queries trigger the canonical refusal message."""
    rag = RAGRetrievalService(collection_name="test_fallback_col", provider="offline")
    text = "The enterprise cloud infrastructure enforces mTLS on port 8443."
    ingestion = DocumentIngestionService()
    chunks = ingestion.ingest(text.encode("utf-8"), "infra.txt")
    rag.index_chunks(chunks)

    # Ask completely unrelated question
    result = rag.ask("What is the average surface temperature of Jupiter?", top_k=1)
    assert FALLBACK_REFUSAL_MESSAGE.lower() in result.answer.lower()
    assert result.is_grounded is False


def test_rag_with_empty_index():
    """Verify query on empty index returns graceful warning without error."""
    rag = RAGRetrievalService(collection_name="test_empty_col", provider="offline")
    result = rag.ask("Any question")
    assert result.is_grounded is False
    assert result.retrieved_chunks_count == 0
    assert "No documents have been indexed" in result.answer
