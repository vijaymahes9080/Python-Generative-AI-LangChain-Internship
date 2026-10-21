"""
Reusable prompt templates and few-shot examples for Task 1: Structured JSON Extractor.
Designed for high extraction fidelity across Google Gemini and OpenAI.
"""

INVOICE_FEW_SHOT_EXAMPLE = """
Unstructured Input:
Invoice from Acme Solutions Inc, 100 Innovation Way, Austin TX (Tax ID: US-992144).
Billed to Vertex Retail, 45 Market St, Seattle WA (billing@vertex.com).
Invoice #: INV-2026-8819 | Date: 2026-03-15 | Due: Net 30
Items:
1. Cloud Hosting Credits (Annual) - Qty 2 @ $450.00 each = $900.00
2. Enterprise Support Retainer - Qty 1 @ $1200.00 each = $1200.00
Subtotal: $2100.00
Tax (8.25%): $173.25
Total Due: $2273.25

Extracted Output:
{
  "invoice_number": "INV-2026-8819",
  "date": "2026-03-15",
  "due_date": "2026-04-14",
  "supplier": {
    "name": "Acme Solutions Inc",
    "address": "100 Innovation Way, Austin TX",
    "tax_id": "US-992144",
    "email": null
  },
  "customer": {
    "name": "Vertex Retail",
    "address": "45 Market St, Seattle WA",
    "email": "billing@vertex.com"
  },
  "line_items": [
    {
      "description": "Cloud Hosting Credits (Annual)",
      "quantity": 2.0,
      "unit_price": 450.0,
      "total_price": 900.0
    },
    {
      "description": "Enterprise Support Retainer",
      "quantity": 1.0,
      "unit_price": 1200.0,
      "total_price": 1200.0
    }
  ],
  "subtotal": 2100.0,
  "tax_rate": 0.0825,
  "tax_amount": 173.25,
  "total_amount": 2273.25,
  "currency": "USD",
  "payment_terms": "Net 30"
}
"""

RESUME_FEW_SHOT_EXAMPLE = """
Unstructured Input:
Alex Rivera
Email: alex.rivera@techmail.io | Phone: (555) 349-2041 | Austin, TX
LinkedIn: linkedin.com/in/alexrivera-ai | GitHub: github.com/arivera-code

Summary:
Senior Machine Learning Engineer with 6+ years deploying scalable LLM and computer vision pipelines in production.

Education:
University of Texas at Austin — B.S. in Computer Science (2016 - 2020), GPA: 3.85

Skills:
Languages: Python, Go, SQL, C++
Frameworks: PyTorch, LangChain, FastAPI, HuggingFace Transformers
Tools: Docker, Kubernetes, PostgreSQL, AWS SageMaker
Soft Skills: Technical Mentorship, Agile Leadership

Experience:
NeuraTech Labs (Senior ML Engineer) | Jan 2022 - Present
- Architected enterprise RAG retrieval pipeline reducing latency by 45%.
- Led a team of 4 engineers shipping fine-tuned LLM agents for customer analytics.
- Tech: Python, LangChain, ChromaDB, Kubernetes.

DataFlow Dynamics (ML Engineer) | Aug 2020 - Dec 2021
- Built automated document classification system processing 100k daily records.
- Tech: Python, PyTorch, Docker, AWS.

Projects:
- NeuralAgent Studio: Open-source agentic workflow builder with 1.2k GitHub stars. Tech: Python, LangGraph, FastAPI.

Certifications:
- AWS Certified Machine Learning - Specialty (Amazon Web Services, 2023)

Extracted Output:
{
  "contact": {
    "name": "Alex Rivera",
    "email": "alex.rivera@techmail.io",
    "phone": "(555) 349-2041",
    "location": "Austin, TX",
    "linkedin": "linkedin.com/in/alexrivera-ai",
    "github": "github.com/arivera-code"
  },
  "summary": "Senior Machine Learning Engineer with 6+ years deploying scalable LLM and computer vision pipelines in production.",
  "skills": {
    "technical": ["Python", "Go", "SQL", "C++"],
    "frameworks": ["PyTorch", "LangChain", "FastAPI", "HuggingFace Transformers"],
    "tools": ["Docker", "Kubernetes", "PostgreSQL", "AWS SageMaker"],
    "soft_skills": ["Technical Mentorship", "Agile Leadership"]
  },
  "experience": [
    {
      "company": "NeuraTech Labs",
      "role": "Senior ML Engineer",
      "start_date": "Jan 2022",
      "end_date": "Present",
      "responsibilities": [
        "Architected enterprise RAG retrieval pipeline reducing latency by 45%.",
        "Led a team of 4 engineers shipping fine-tuned LLM agents for customer analytics."
      ],
      "technologies": ["Python", "LangChain", "ChromaDB", "Kubernetes"]
    },
    {
      "company": "DataFlow Dynamics",
      "role": "ML Engineer",
      "start_date": "Aug 2020",
      "end_date": "Dec 2021",
      "responsibilities": [
        "Built automated document classification system processing 100k daily records."
      ],
      "technologies": ["Python", "PyTorch", "Docker", "AWS"]
    }
  ],
  "education": [
    {
      "institution": "University of Texas at Austin",
      "degree": "B.S.",
      "field": "Computer Science",
      "graduation_year": "2020",
      "gpa": "3.85"
    }
  ],
  "projects": [
    {
      "name": "NeuralAgent Studio",
      "description": "Open-source agentic workflow builder with 1.2k GitHub stars.",
      "tech_stack": ["Python", "LangGraph", "FastAPI"],
      "link": null
    }
  ],
  "certifications": [
    {
      "name": "AWS Certified Machine Learning - Specialty",
      "issuer": "Amazon Web Services",
      "issue_date": "2023"
    }
  ]
}
"""

def get_extraction_system_prompt(mode: str) -> str:
    """Return strict system instructions for JSON extraction."""
    return f"""You are a precise, production-grade JSON extraction engine specialized in extracting {mode} records.
Your task is to parse unstructured input text and extract clean, validated data matching the target schema.

CRITICAL RULES:
1. Output MUST be strictly valid, raw JSON only. Do NOT enclose in markdown code blocks like ```json ... ``` or add explanatory commentary.
2. Do NOT invent, assume, or hallucinate facts that are absent from the source document.
3. If an optional field is missing from the source text, set its value to null or an empty list as specified in the schema.
4. Ensure all numerical fields (quantities, prices, totals) are parsed as numbers (float/int), not strings with currency signs.
5. Adhere strictly to the field names and nested objects shown in the reference schema.
"""


def get_extraction_user_prompt(mode: str, raw_text: str) -> str:
    """Assemble parameterized prompt combining few-shot example and target document text."""
    few_shot = INVOICE_FEW_SHOT_EXAMPLE if mode == "invoice" else RESUME_FEW_SHOT_EXAMPLE
    return f"""### REFERENCE FEW-SHOT EXAMPLE:
{few_shot}

### DOCUMENT TO EXTRACT ({mode.upper()}):
{raw_text}

Extract the {mode} JSON following the reference schema precisely. Remember: output valid JSON only.
"""


def get_repair_prompt(mode: str, raw_text: str, bad_json: str, validation_errors: str) -> str:
    """Construct self-correction repair prompt containing specific validation error diagnostics."""
    return f"""The previous JSON extraction for {mode} failed validation with the following schema errors:
{validation_errors}

Original Document:
{raw_text}

Rejected JSON:
{bad_json}

Please fix the errors and output a corrected, strictly valid JSON object matching the schema. Output JSON only without commentary.
"""
