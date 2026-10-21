"""
Streamlit Web Application for Task 2: Document Q&A Assistant with RAG & Vector Embeddings.
Part of the AI Innovation Studio suite.
"""

import os
import sys
import streamlit as st

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from ingestion import DocumentIngestionService, DocumentIngestionError
from retrieval import RAGRetrievalService, FALLBACK_REFUSAL_MESSAGE

# Page configuration
st.set_page_config(
    page_title="Document RAG Assistant | AI Innovation Studio",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #38bdf8 0%, #a78bfa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        color: #94a3b8;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    .citation-card {
        padding: 0.9rem;
        border-radius: 0.5rem;
        background-color: #0f172a;
        border-left: 4px solid #38bdf8;
        margin-bottom: 0.8rem;
    }
    .citation-meta {
        font-size: 0.82rem;
        color: #94a3b8;
        font-weight: 600;
        margin-bottom: 0.3rem;
    }
    .citation-text {
        font-size: 0.9rem;
        color: #e2e8f0;
        font-style: italic;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "rag_service" not in st.session_state:
    st.session_state.rag_service = RAGRetrievalService()
if "ingestion_service" not in st.session_state:
    st.session_state.ingestion_service = DocumentIngestionService(chunk_size=700, chunk_overlap=120)
if "indexed_docs" not in st.session_state:
    st.session_state.indexed_docs = []

rag: RAGRetrievalService = st.session_state.rag_service
ingestion: DocumentIngestionService = st.session_state.ingestion_service

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ RAG Engine Configuration")

    provider = st.selectbox(
        "Provider",
        options=["auto", "gemini", "openai", "offline"],
        format_func=lambda x: {
            "auto": "Auto-Select (Environment)",
            "gemini": "Google Gemini + text-embedding-004",
            "openai": "OpenAI + text-embedding-3-small",
            "offline": "Deterministic Local Engine",
        }[x],
        index=0,
    )
    if provider != rag.provider:
        rag.provider = provider

    top_k = st.slider("Retrieved Context Chunks (Top-K)", min_value=1, max_value=5, value=3)

    st.markdown("---")
    st.markdown("### 📚 Load Sample Policies")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        if st.button("Load AI Governance", use_container_width=True):
            sample_path = os.path.join(current_dir, "samples", "ai_governance_brief.txt")
            if os.path.exists(sample_path):
                with open(sample_path, "rb") as f:
                    content = f.read()
                chunks = ingestion.ingest(content, "ai_governance_brief.txt")
                rag.index_chunks(chunks)
                if "ai_governance_brief.txt" not in st.session_state.indexed_docs:
                    st.session_state.indexed_docs.append("ai_governance_brief.txt")
                st.success("Loaded AI Governance Policy!")

    with col_s2:
        if st.button("Load Cloud Security", use_container_width=True):
            sample_path = os.path.join(current_dir, "samples", "cloud_security_standards.txt")
            if os.path.exists(sample_path):
                with open(sample_path, "rb") as f:
                    content = f.read()
                chunks = ingestion.ingest(content, "cloud_security_standards.txt")
                rag.index_chunks(chunks)
                if "cloud_security_standards.txt" not in st.session_state.indexed_docs:
                    st.session_state.indexed_docs.append("cloud_security_standards.txt")
                st.success("Loaded Cloud Security Standards!")

    st.markdown("---")
    st.markdown("### 📊 Index Status")
    st.metric("Total Indexed Chunks", rag.total_chunks)
    st.metric("Active Documents", len(st.session_state.indexed_docs))
    if st.session_state.indexed_docs:
        for doc in st.session_state.indexed_docs:
            st.caption(f"• {doc}")

    if st.button("🗑️ Reset Vector Index", type="secondary", use_container_width=True):
        rag._reset_or_get_collection()
        st.session_state.indexed_docs = []
        st.rerun()

# Main Header
st.markdown("<div class='main-header'>Document Q&A Assistant with RAG & Vector Embeddings</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='sub-header'>Semantic document search with ChromaDB, verified page-level citations, and strict anti-hallucination guardrails.</div>",
    unsafe_allow_html=True,
)

# Upload Area
with st.expander("📤 Upload New Documents (PDF or TXT)", expanded=(rag.total_chunks == 0)):
    uploaded_files = st.file_uploader(
        "Upload files to add to the ChromaDB vector store",
        type=["pdf", "txt"],
        accept_multiple_files=True,
    )
    if uploaded_files:
        for uf in uploaded_files:
            if uf.name not in st.session_state.indexed_docs:
                try:
                    file_bytes = uf.read()
                    chunks = ingestion.ingest(file_bytes, uf.name)
                    rag.index_chunks(chunks)
                    st.session_state.indexed_docs.append(uf.name)
                    st.success(f"Indexed '{uf.name}' ({len(chunks)} chunks)")
                except DocumentIngestionError as die:
                    st.error(f"Error indexing '{uf.name}': {str(die)}")
                except Exception as e:
                    st.error(f"Unexpected error with '{uf.name}': {str(e)}")

# Query Section
st.markdown("#### 💬 Ask a Document Question")

query_input = st.text_input(
    "Enter your question regarding the uploaded documents:",
    placeholder="e.g. What is the mandatory encryption standard for data at rest? Or: What is the fallback notice for ungrounded RAG?",
)

# Starter Query Buttons if samples are loaded
if st.session_state.indexed_docs:
    st.markdown("<span style='font-size:0.85rem; color:#94a3b8;'>Quick Starter Queries:</span>", unsafe_allow_html=True)
    q_col1, q_col2, q_col3 = st.columns(3)
    with q_col1:
        if st.button("What is the fallback notice for ungrounded RAG?", use_container_width=True):
            query_input = "What is the fallback notice for ungrounded RAG?"
    with q_col2:
        if st.button("What is the required token TTL for OIDC workloads?", use_container_width=True):
            query_input = "What is the required token TTL for OIDC workloads?"
    with q_col3:
        if st.button("What is the quarterly revenue of Tesla?", use_container_width=True):
            query_input = "What is the quarterly revenue of Tesla?"

if st.button("🔎 Search & Synthesize Answer", type="primary"):
    if not query_input.strip():
        st.warning("Please enter a question.")
    elif rag.total_chunks == 0:
        st.error("Vector index is currently empty. Please upload a document or load sample policies from the sidebar.")
    else:
        with st.spinner("Retrieving semantic chunks and synthesizing answer..."):
            result = rag.ask(query_input, top_k=top_k)

            # Answer Banner
            col_ans, col_stats = st.columns([3, 1])
            with col_ans:
                if result.is_grounded:
                    st.markdown("### 💡 Grounded Answer")
                    st.info(result.answer)
                else:
                    st.markdown("### ⚠️ Document Refusal (Anti-Hallucination Guard)")
                    st.warning(result.answer)

            with col_stats:
                st.markdown("### ⏱️ Diagnostics")
                st.metric("Execution Latency", f"{result.execution_time_ms:.1f} ms")
                st.metric("Provider", result.provider_used)
                st.metric("Retrieved Chunks", result.retrieved_chunks_count)

            # Citations Section
            st.markdown("---")
            st.markdown(f"#### 📑 Verifiable Citations ({len(result.citations)} references)")

            if result.citations:
                for idx, c in enumerate(result.citations):
                    with st.expander(f"Citation #{idx+1} — {c.source_file} (Page {c.page_number}) — Relevance: {c.relevance_score * 100:.1f}%", expanded=True):
                        st.markdown(f"**Source Document:** `{c.source_file}` | **Page:** `{c.page_number}` | **Similarity Score:** `{c.relevance_score:.4f}`")
                        st.markdown(f"> *\"{c.excerpt}\"*")
            else:
                st.caption("No citations available for this query.")
