# AI Innovation Studio — System Architecture Specification

## 1. Executive Architecture Summary
The **AI Innovation Studio** is an enterprise-grade software portfolio comprising four modular, independently executable artificial intelligence applications built in Python 3.12. The system adheres to strict separation of concerns, zero-trust security boundaries, and reproducible dual-mode execution (supporting both cloud LLM APIs and deterministic offline engines).

```
+---------------------------------------------------------------------------------------------------------+
|                                        AI INNOVATION STUDIO                                             |
|                                       (Central index.html)                                              |
+--------------------+---------------------+-------------------------------+------------------------------+
                     |                     |                               |
                     v                     v                               v
+--------------------+   +-----------------+   +---------------------------+   +--------------------------+
| Task 1: Extractor  |   | Task 2: RAG Q&A |   | Task 3: Autonomous Agent  |   | Task 4: Streamlit Chat   |
| - Invoices & Resume|   | - PyPDF & TXT   |   | - DuckDuckGo Search       |   | - Session State          |
| - Pydantic v2      |   | - Text Splitter |   | - AST Math Engine         |   | - Token Streaming        |
| - Self-Correction  |   | - ChromaDB Store|   | - Sandboxed File Reader   |   | - Integrates T2 & T3     |
| - Streamlit UI     |   | - Citations UI  |   | - ReAct Audit Trace       |   | - Mode Selector UI       |
+--------------------+   +-----------------+   +---------------------------+   +--------------------------+
```

---

## 2. Component Architecture & Data Flow

### Task 1 — Structured LLM Prompt Pipeline & JSON Extractor
- **Core Engine**: `task1-json-extraction/extraction_service.py`
- **Schemas**: Strict Pydantic v2 data models for Commercial Invoices (`InvoiceSchema`) and Candidate Resumes (`ResumeSchema`).
- **Data Validation & Math Reconciliation**:
  - Validates that each line item's `total_price` matches `quantity * unit_price`.
  - Reconciles subtotal against the sum of line items.
  - Reconciles final `total_amount` against `subtotal + tax_amount`.
- **Bounded Self-Correction Loop**:
  - When raw LLM output triggers a `ValidationError` or syntax error, the engine formats diagnostic error paths and submits a repair prompt to the model (up to 2 retry attempts).
- **Interface**: Interactive Streamlit workspace with document uploader (PDF/TXT), sample document selector, formatted JSON viewer, confidence score tracking, and JSON export.

### Task 2 — Document Q&A Assistant with RAG & Vector Embeddings
- **Core Engine**: `task2-document-assistant/retrieval.py`
- **Ingestion & Chunking**: `task2-document-assistant/ingestion.py`
  - Extracts text from `.pdf` (via `pypdf`) and `.txt` files while capturing page boundaries.
  - Implements `RecursiveCharacterTextSplitter` configured for 700-character chunks with 120-character semantic overlaps.
- **Dual Vector Embeddings**: `task2-document-assistant/embeddings.py`
  - Supports Google Gemini (`text-embedding-004`) and OpenAI (`text-embedding-3-small`).
  - Supports an internal **Deterministic Local Embedding Engine** (128-dimensional L2-normalized dense vector representations) allowing 100% offline indexing and search without API keys.
- **Vector Storage**: ChromaDB collection using cosine similarity metric.
- **Hallucination Prevention**:
  - Enforces strict similarity thresholds; if retrieved chunks lack necessary facts, outputs:
    `"I cannot find sufficient evidence in the uploaded documents to answer this question."`
  - Every grounded claim provides verifiable citations: source filename, page number, similarity score, and exact supporting excerpt.

### Task 3 — Multi-Tool Autonomous AI Agent
- **Core Engine**: `task3-autonomous-agent/agent.py`
- **Reasoning Loop**: ReAct (Reasoning + Action + Observation) state machine with a 6-step ceiling and execution timeout.
- **Tool Sandbox**:
  1. `restricted_calculator`: Pure AST mathematical evaluation; zero `eval()`, zero `exec()`, zero code injection vulnerabilities.
  2. `local_file_reader`: Strictly isolated to `./sandbox_data/`; canonical path traversal defense blocks any attempt to escape via `..`, absolute paths, or symlinks.
  3. `duckduckgo_search`: Live web search with query sanitization and offline cache fallback.
- **Auditable Trace**: Captures step numbers, selected tools, sanitized arguments, execution status (`SUCCESS` / `FAILURE`), latency in milliseconds, and observation excerpts.
- **Interface**: Interactive Rich console CLI (`main.py`) with colored tables and markdown response panels.

### Task 4 — Interactive Full-Stack AI Chatbot with Streamlit
- **Core Engine**: `task4-ai-chat/chat_service.py`
- **Streaming UI**: `task4-ai-chat/app.py`
- **Session State**: Manages complete conversation history across user interactions via `st.session_state`.
- **Incremental Streaming**: Asynchronous token yields via Python generators, rendering responses smoothly in the browser.
- **Dynamic Persona Steering**: Configurable system instructions:
  - *General AI Assistant*
  - *Senior Code Reviewer*
  - *Technical Researcher*
  - *Data & Systems Architect*
- **Cross-Pipeline Integrations**:
  - *Direct Mode*: Standard conversational AI.
  - *Document-Grounded RAG Mode*: Directly interfaces with Task 2 ChromaDB retrieval engine.
  - *Autonomous Agent Mode*: Directly interfaces with Task 3 ReAct agent for compound multi-step tools.

---

## 3. Security & Trust Architecture

1. **Credential Hygiene**:
   - Zero hardcoded credentials or API keys.
   - Environment variables loaded securely from `.env`.
   - `.env.example` committed exclusively with placeholder values.
   - `.gitignore` configured to block `.env`, secrets, `.sqlite3`, `.chromadb`, and cache stores.

2. **Zero-Trust Tool Execution**:
   - Restricted Calculator strictly checks AST nodes against an explicit whitelist of mathematical operators and math library functions.
   - File Reader validates canonical directory containment using `os.path.commonpath([sandbox_root, target_path]) == sandbox_root`.
   - Read size limit enforced at 100 KB.

3. **Deterministic Offline Parity**:
   - Every single task features an internal deterministic offline engine alongside live cloud APIs.
   - Reviewers, CI/CD runners, and automated test suites can execute the full portfolio without incurring API charges or requiring internet access.
