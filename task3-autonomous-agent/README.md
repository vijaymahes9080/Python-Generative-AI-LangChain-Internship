# Task 3: Multi-Tool Autonomous AI Agent

## Overview
A console-based autonomous agent utilizing the **ReAct (Reasoning + Action + Observation)** paradigm to solve compound, multi-step engineering tasks. Orchestrates three strictly sandboxed tools under strict security parameters, producing an auditable execution trace without exposing private internal thoughts.

## Available Tools & Security Boundaries

### 1. DuckDuckGo Web Search (`duckduckgo_search`)
- Searches the live web for documentation, recent package releases, and technical references.
- Features query sanitization (stripping non-printable characters and control codes) and offline cache fallback.

### 2. Restricted Mathematical Calculator (`restricted_calculator`)
- Evaluates arithmetic and scientific mathematical expressions via Python's Abstract Syntax Tree (`ast`).
- Whitelisted operations: `+`, `-`, `*`, `/`, `//`, `%`, `**`, `sqrt`, `sin`, `cos`, `tan`, `log`, `abs`, `round`, `pow`.
- **Zero `eval()`, zero `exec()`, zero arbitrary code execution**: Any function call, attribute access, or unauthorized AST node raises an explicit security restriction error.

### 3. Sandboxed Local File Reader (`local_file_reader`)
- Reads file content strictly limited to the `./sandbox_data` directory.
- Enforces canonical path boundary checks: rejects `..` traversal sequences, absolute paths, and symlink escapes.
- Enforces a 100 KB maximum file read size limit to prevent buffer saturation.

## Architecture

```
User Query (Compound Multi-Step Prompt)
                   │
                   ▼
       Autonomous Agent ReAct Loop
                   │
    ┌──────────────┼──────────────┐
    ▼              ▼              ▼
DuckDuckGo    Restricted      Sandboxed
Web Search    Calculator     File Reader
    │              │              │
    └──────────────┼──────────────┘
                   ▼
     Auditable Observation Stream
                   │
                   ▼
       Final Synthesized Response
        (With Citations & Stats)
```

## Directory Structure
```text
task3-autonomous-agent/
├── main.py                    # Interactive Rich console CLI runner
├── agent.py                   # ReAct loop controller and tool dispatcher
├── tools/
│   ├── __init__.py
│   ├── calculator.py          # Safe AST-based math evaluator
│   ├── file_reader.py         # Sandboxed file reader with path traversal guard
│   └── web_search.py          # DuckDuckGo search with sanitization
├── sandbox_data/              # Isolated data repository
│   ├── quarterly_earnings.txt
│   └── system_specs.json
├── requirements.txt           # Project dependencies
├── tests/
│   ├── __init__.py
│   └── test_agent.py          # Automated pytest suite (8 tests)
└── README.md
```

## Installation & Execution

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Interactive Console
```bash
python main.py
```

### 3. Run a One-Shot Query via CLI
```bash
python main.py --query "Read system_specs.json and calculate the total cluster RAM across all 8 nodes."
```

### 4. Run Automated Tests
```bash
pytest tests/test_agent.py -v
```
