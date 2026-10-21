# Task 2: Document Q&A Assistant with RAG & Vector Embeddings

## Overview
A high-accuracy Retrieval-Augmented Generation (RAG) assistant designed for enterprise document question answering. Employs semantic vector search via **ChromaDB**, recursive character chunking with preserved metadata, strict anti-hallucination guardrails, and verifiable page-level citation attribution.

## Features
- **Multi-Format Ingestion**: Supports `.pdf` (via `pypdf`) and `.txt` files with automated page-boundary detection and encoding recovery.
- **Recursive Text Segmentation**: Implements `RecursiveCharacterTextSplitter` configured for optimal chunk distribution (700-character chunks with 120-character semantic overlaps).
- **Dual Vector Embedding Architecture**:
  - Cloud Providers: Google Gemini (`text-embedding-004`) and OpenAI (`text-embedding-3-small`).
  - Offline Provider: High-speed **Deterministic Local Embedding Engine** (128-dimensional L2-normalized dense representations) allowing 100% offline testing without API credentials.
- **Vector Storage with ChromaDB**: In-memory and persistent vector collections with cosine distance metric.
- **Strict Anti-Hallucination Guardrails**: Checks cosine similarity thresholds; if retrieved context is insufficient or out-of-domain, the assistant returns an explicit refusal message:
  `"I cannot find sufficient evidence in the uploaded documents to answer this question."`
- **Verifiable Citation Attribution**: Every grounded claim links back to the source filename, page number, similarity score, and verbatim excerpt snippet.
- **Interactive Streamlit Interface**: Real-time document manager, index statistics dashboard, sample policy loaders, and citation inspection cards.

## Architecture

```
Document Upload (PDF / TXT)
            │
            ▼
 Document Ingestion Service
  (Page & Text Extraction)
            │
            ▼
 RecursiveCharacterTextSplitter
  (Chunk Size: 700, Overlap: 120)
            │
            ▼
   Dense Vector Embedding
 (Gemini / OpenAI / Local Hash)
            │
            ▼
     ChromaDB Collection
 (Cosine Distance Vector Store)
            │
       User Query
            │
            ▼
  Semantic Top-K Retrieval
            │
     ┌──────┴──────┐
 [Sufficient]   [Insufficient / Irrelevant]
     │                 │
     ▼                 ▼
 Context-Grounded   Explicit Refusal
 LLM Synthesis      Fallback Message
     │
     ▼
 Grounded Answer + Verifiable Citations
```

## Directory Structure
```text
task2-document-assistant/
├── app.py                     # Streamlit interactive RAG workspace
├── ingestion.py               # Document parsing and recursive chunking
├── embeddings.py              # Cloud & local dense vector embeddings
├── retrieval.py               # ChromaDB retrieval and grounded QA engine
├── requirements.txt           # Project dependencies
├── samples/                   # Enterprise test policy documents
│   ├── ai_governance_brief.txt
│   └── cloud_security_standards.txt
├── tests/
│   ├── __init__.py
│   └── test_rag.py            # Automated pytest suite (8 tests)
└── README.md
```

## Installation & Execution

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment (Optional)
Add API keys to your `.env` file at the root:
```env
GEMINI_API_KEY=your_gemini_api_key
# or
OPENAI_API_KEY=your_openai_api_key
```
*Note: If no API keys are provided, the system defaults automatically to the Deterministic Local Engine.*

### 3. Run the Streamlit Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

### 4. Run Automated Tests
```bash
pytest tests/test_rag.py -v
```
