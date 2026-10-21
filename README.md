# AI Innovation Studio — Enterprise AI Software Portfolio

An enterprise-grade artificial intelligence software suite featuring four production-ready, independently executable applications developed in Python 3.12. Designed for verifiable reliability, strict data validation, grounded vector retrieval, sandboxed autonomous execution, and responsive conversational UI.

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

## Portfolio Applications Overview

### [Task 1: Structured LLM Prompt Pipeline & JSON Extractor](task1-json-extraction/README.md)
- **Objective**: Convert unstructured commercial invoices and candidate resumes into strictly typed, validated JSON records.
- **Key Technologies**: Pydantic v2, Few-Shot Prompt Templates, Bounded Self-Correction Retry Loop, Streamlit.
- **Key Features**: Line item mathematical reconciliation (`quantity * price`), skills categorization, field diagnostic error recovery, and one-click JSON export.
- **Launch Command**: `streamlit run task1-json-extraction/app.py`
- **Unit Tests**: 9/9 Passed (`pytest task1-json-extraction/tests/test_extraction.py -v`)

### [Task 2: Document Q&A Assistant with RAG & Vector Embeddings](task2-document-assistant/README.md)
- **Objective**: Context-grounded question answering over PDF and TXT documents with verifiable page-level citations.
- **Key Technologies**: ChromaDB, `RecursiveCharacterTextSplitter`, Dense Vector Embeddings, PyPDF, Streamlit.
- **Key Features**: Top-k semantic similarity search, page and excerpt citation tracking, and strict anti-hallucination refusal:
  `"I cannot find sufficient evidence in the uploaded documents to answer this question."`
- **Launch Command**: `streamlit run task2-document-assistant/app.py`
- **Unit Tests**: 8/8 Passed (`pytest task2-document-assistant/tests/test_rag.py -v`)

### [Task 3: Multi-Tool Autonomous AI Agent](task3-autonomous-agent/README.md)
- **Objective**: Solve complex compound tasks through controlled sequential tool invocation under strict security boundaries.
- **Key Technologies**: ReAct Reasoning Loop, DuckDuckGo Search, Safe AST Math Engine, Sandboxed File IO, Rich CLI.
- **Key Features**: Pure AST arithmetic (zero `eval()`), canonical path containment (blocks `..` traversal), and auditable action-and-observation trace tables.
- **Launch Command**: `python task3-autonomous-agent/main.py`
- **Unit Tests**: 8/8 Passed (`pytest task3-autonomous-agent/tests/test_agent.py -v`)

### [Task 4: Interactive Full-Stack AI Chatbot with Streamlit](task4-ai-chat/README.md)
- **Objective**: Responsive conversational application with real-time streaming, persona steering, and unified project integrations.
- **Key Technologies**: Streamlit (`st.chat_message`, `st.chat_input`), `st.session_state`, Asynchronous Token Generators.
- **Key Features**: Dynamic persona steering (General Assistant, Senior Code Reviewer, Technical Researcher, Data Architect) and multi-mode dispatchers integrating Task 2 RAG and Task 3 Multi-Tool Agent.
- **Launch Command**: `streamlit run task4-ai-chat/app.py`
- **Unit Tests**: 6/6 Passed (`pytest task4-ai-chat/tests/test_chat.py -v`)

---

## Central Landing Portal

The suite includes a central landing portal styled in a dark graphite foundation with electric violet and cyan accents.

- Open directly: Double-click `index.html` in your browser.
- Open via CLI: `python launcher.py portal`

---

## Quickstart & Unified Launcher

The repository provides a single unified CLI utility (`launcher.py`):

```bash
# 1. Verify runtime environment and dependencies
python launcher.py check

# 2. Run all 31 unit tests across all 4 projects
python launcher.py test

# 3. Launch individual applications
python launcher.py run --task task1
python launcher.py run --task task2
python launcher.py run --task task3
python launcher.py run --task task4

# 4. Open the central landing portal
python launcher.py portal
```

---

## 28-Commit Git Delivery Ledger

This repository was constructed across 28 discrete, atomic Git commits:

1. `chore: initialize repository with environment configuration and gitignore`
2. `feat(task1): define pydantic v2 schemas for invoices and resumes`
3. `feat(task1): add parameterized prompt templates and few-shot examples`
4. `feat(task1): implement extraction service with bounded self-correction`
5. `feat(task1): add realistic invoice and resume sample documents`
6. `feat(task1): build streamlit extraction interface with json preview`
7. `test(task1): add automated pytest suite for schema validation and recovery`
8. `docs(task1): add project documentation and dependency specification`
9. `feat(task2): implement document ingestion and recursive text chunking`
10. `feat(task2): implement dual-mode vector embeddings engine`
11. `feat(task2): implement chromadb retrieval with citation grounding and hallucination guard`
12. `feat(task2): add sample governance and cloud security test documents`
13. `feat(task2): build streamlit document rag and citation explorer interface`
14. `test(task2): implement automated pytest suite for chunking, indexing and retrieval`
15. `docs(task2): add rag assistant documentation and dependencies`
16. `feat(task3): implement safe ast-based mathematical calculator tool`
17. `feat(task3): implement sandboxed file reader with path-traversal prevention`
18. `feat(task3): implement duckduckgo search tool with sanitization`
19. `feat(task3): implement react autonomous agent reasoning loop controller`
20. `feat(task3): add sandboxed dataset and interactive rich cli runner`
21. `test(task3): add comprehensive test suite for tools, security boundaries and react loop`
22. `docs(task3): add autonomous agent documentation and dependencies`
23. `feat(task4): implement conversation service with session state, personas, and integrations`
24. `feat(task4): build full-stack streamlit chat interface with streaming and mode toggles`
25. `test(task4): add unit tests for session state, streaming, and reset handling`
26. `feat(portal): create dark graphite central landing page and unified cli launcher`
27. `docs: add comprehensive system architecture, installation guide, and test report`
28. `chore(release): complete ai innovation studio suite with top-level documentation`

---

## Documentation Links
- [System Architecture Specification](docs/architecture.md)
- [Installation & Execution Guide](docs/installation.md)
- [Automated Test Verification Report](docs/test-report.md)
