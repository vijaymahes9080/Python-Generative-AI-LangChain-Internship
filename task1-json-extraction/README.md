# Task 1: Structured LLM Prompt Pipeline & JSON Extractor

## Overview
A production-grade information extraction service converting unstructured business documents (commercial invoices and job candidate resumes) into strictly typed, validated JSON records governed by **Pydantic v2** schemas.

## Features
- **Dual Extraction Modalities**: Separate, highly optimized pipelines for **Commercial Invoices** and **Candidate Resumes**.
- **Multi-Provider SDK Support**: Integrates directly with Google Gemini (`google-genai`) and OpenAI (`openai`), alongside an internal **Deterministic Offline Engine** that enables full offline evaluation and zero-token test runs.
- **Few-Shot In-Context Learning**: Embedded high-fidelity examples steer the model to adhere to schema field structures and avoid hallucination.
- **Strict Pydantic v2 Validation**: Comprehensive type checking, non-negative numerical constraints, date formatting, and line-item cross-validation.
- **Bounded Self-Correction Loop**: Catches schema validation failures and feeds specific diagnostics back to the LLM (up to 2 retries) to repair malformed outputs.
- **Interactive Streamlit Workspace**: Web interface with document uploader (PDF/TXT), sample document selector, live JSON viewer, confidence metrics, and download capabilities.

## Architecture

```
Unstructured Input (PDF / TXT / Raw String)
                   │
                   ▼
       Extraction Prompt Builder
    (System Rules + Few-Shot Exemplars)
                   │
                   ▼
     LLM Generation (Gemini / OpenAI / Offline)
                   │
                   ▼
         JSON Sanitizer & Parser
                   │
          ┌────────┴────────┐
   [Valid JSON]      [Syntax Error]
          │                 │
          ▼                 ▼
   Pydantic v2        Self-Correction
   Model Validate       Prompt Loop
          │            (Max 2 retries)
     ┌────┴────┐            ▲
  [Pass]    [Fail]──────────┘
     │
     ▼
 Validated JSON Result
```

## Directory Structure
```text
task1-json-extraction/
├── app.py                     # Streamlit interactive extraction workspace
├── schemas.py                 # Pydantic v2 Invoice and Resume models
├── prompts.py                 # Parameterized prompt templates & few-shot examples
├── extraction_service.py      # Core extraction engine with self-correction
├── requirements.txt           # Project dependencies
├── samples/                   # Realistic test invoices & resumes
│   ├── sample_invoice_techcorp.txt
│   ├── sample_invoice_logistics.txt
│   ├── sample_resume_senior_dev.txt
│   └── sample_resume_data_scientist.txt
├── tests/
│   ├── __init__.py
│   └── test_extraction.py     # Automated pytest suite (9 tests)
└── README.md
```

## Installation & Execution

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment (Optional)
Ensure your `.env` file at the root contains:
```env
GEMINI_API_KEY=your_gemini_api_key
# or
OPENAI_API_KEY=your_openai_api_key
```
*Note: If no API key is provided, the application automatically uses the Deterministic Offline Engine.*

### 3. Run the Streamlit Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

### 4. Run Automated Tests
```bash
pytest tests/test_extraction.py -v
```
