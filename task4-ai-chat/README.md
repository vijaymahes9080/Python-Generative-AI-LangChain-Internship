# Task 4: Interactive Full-Stack AI Chatbot with Streamlit

## Overview
A responsive full-stack conversational AI web application built on **Streamlit**, featuring real-time token streaming, stateful conversation persistence via `st.session_state`, dynamic persona steering, and unified cross-pipeline integration with Task 2 (Document RAG) and Task 3 (Autonomous Multi-Tool Agent).

## Features
- **Conversational Chat UI**: Implements Streamlit's native `st.chat_message` and `st.chat_input` components with smooth auto-scroll.
- **Incremental Token Streaming**: Asynchronous token yields via Python generators, compatible with live LLM streaming APIs (`google-genai` and `openai`) and an internal local fallback engine.
- **Dynamic Persona Steering**: Pre-configured system instruction profiles:
  - *General AI Assistant*: Well-rounded engineering guidance.
  - *Senior Code Reviewer*: In-depth algorithmic, complexity, and safety analysis.
  - *Technical Researcher*: Academic, theoretical, and benchmark-focused insights.
  - *Data & Systems Architect*: Distributed systems, data modeling, and security.
- **Cross-Task Pipeline Integrations**:
  - **Direct Mode**: Pure conversational LLM synthesis.
  - **Document-Grounded RAG Mode**: Direct bridge to Task 2 ChromaDB retrieval engine for fact-checked, cited answers.
  - **Autonomous Agent Mode**: Direct bridge to Task 3 ReAct agent for compound calculations, file reading, and web search.
- **Session Control & Data Privacy**: Single-click conversation reset, session isolation, and masked credential management.

## Architecture

```
User Message Input (`st.chat_input`)
                   │
                   ▼
         Chat Mode Dispatcher
                   │
    ┌──────────────┼──────────────┐
    ▼              ▼              ▼
 Direct LLM     Task 2 RAG     Task 3 Agent
 Persona Chat   ChromaDB Q&A    Multi-Tool
    │              │              │
    └──────────────┼──────────────┘
                   │
                   ▼
       Token Streaming Generator
        (`st.write_stream`)
                   │
                   ▼
  Persistent Session State Memory
       (`st.session_state`)
```

## Directory Structure
```text
task4-ai-chat/
├── app.py                     # Streamlit conversational web interface
├── chat_service.py            # Chat engine, personas, and cross-task dispatchers
├── requirements.txt           # Project dependencies
├── tests/
│   ├── __init__.py
│   └── test_chat.py           # Automated pytest suite (6 tests)
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

### 3. Run the Streamlit Chatbot
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

### 4. Run Automated Tests
```bash
pytest tests/test_chat.py -v
```
