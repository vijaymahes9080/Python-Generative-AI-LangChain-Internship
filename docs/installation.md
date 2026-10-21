# AI Innovation Studio — Installation & Execution Guide

## 1. Prerequisites
- **Python**: Version 3.10, 3.11, or 3.12 (Tested on Python 3.12.10).
- **Package Manager**: `pip` (Python package manager).
- **Operating System**: Windows, macOS, or Linux.
- **Web Browser**: Any modern browser (Chrome, Firefox, Edge, Safari).

---

## 2. Environment Setup

### Step A: Clone or Navigate to the Project Root
```bash
cd "D:/intership/Python + Generative AI & LangChain Internship/vj"
```

### Step B: Configure Environment Variables (Optional)
Copy the provided `.env.example` template to `.env`:
```bash
cp .env.example .env
```
Edit `.env` to include your provider credentials if you wish to run with live cloud LLMs:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
OPENAI_API_KEY=your_actual_openai_api_key_here
```
> [!NOTE]
> All applications are engineered with automatic offline fallback engines. If no API keys are provided, each application will automatically operate in Deterministic Mode with zero configuration!

---

## 3. Unified Management Commands

The root directory provides a unified CLI utility (`launcher.py`) to manage dependencies, run test suites, and launch applications.

### Verify Environment & Dependencies
```bash
python launcher.py check
```

### Run All 31 Automated Unit Tests
```bash
python launcher.py test
```

### Open the Central Landing Portal in Browser
```bash
python launcher.py portal
```
Or simply double-click `index.html` in your file explorer.

---

## 4. Launching Individual Applications

Each project can be executed independently from its respective directory or via the unified launcher.

### Task 1 — Structured LLM Prompt Pipeline & JSON Extractor
```bash
# Via launcher:
python launcher.py run --task task1

# Or directly:
streamlit run task1-json-extraction/app.py
```
*Access in browser at: `http://localhost:8501`*

### Task 2 — Document Q&A Assistant with RAG & Vector Embeddings
```bash
# Via launcher:
python launcher.py run --task task2

# Or directly:
streamlit run task2-document-assistant/app.py
```
*Access in browser at: `http://localhost:8501`*

### Task 3 — Multi-Tool Autonomous AI Agent
```bash
# Interactive Console Mode:
python launcher.py run --task task3

# Or directly with one-shot query:
python task3-autonomous-agent/main.py --query "Read system_specs.json and calculate the total cluster RAM across all 8 nodes."
```

### Task 4 — Interactive Full-Stack AI Chatbot with Streamlit
```bash
# Via launcher:
python launcher.py run --task task4

# Or directly:
streamlit run task4-ai-chat/app.py
```
*Access in browser at: `http://localhost:8501`*

---

## 5. Running Automated Unit Tests by Task

```bash
# Run Task 1 tests (9 tests)
pytest task1-json-extraction/tests/test_extraction.py -v

# Run Task 2 tests (8 tests)
pytest task2-document-assistant/tests/test_rag.py -v

# Run Task 3 tests (8 tests)
pytest task3-autonomous-agent/tests/test_agent.py -v

# Run Task 4 tests (6 tests)
pytest task4-ai-chat/tests/test_chat.py -v

# Run the complete test suite at once (31 tests)
pytest task1-json-extraction/tests task2-document-assistant/tests task3-autonomous-agent/tests task4-ai-chat/tests -v
```
