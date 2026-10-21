"""
Unit tests for Task 1: Structured LLM Prompt Pipeline & JSON Extractor.
Validates Pydantic v2 schemas, extraction service, edge-case rejection, and recovery.
"""

import sys
import os
import pytest
from pydantic import ValidationError

# Ensure task directory is in sys.path
task_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if task_dir not in sys.path:
    sys.path.insert(0, task_dir)

from schemas import (
    InvoiceSchema,
    SupplierInfo,
    CustomerInfo,
    LineItem,
    ResumeSchema,
    ContactInfo,
    EducationItem,
)
from extraction_service import clean_json_string, ExtractionService


# ==============================================================================
# INVOICE SCHEMA TESTS
# ==============================================================================

def test_valid_invoice_schema_validation():
    """Verify that a valid invoice dictionary successfully parses into InvoiceSchema."""
    data = {
        "invoice_number": "INV-2026-101",
        "date": "2026-03-01",
        "due_date": "2026-03-31",
        "supplier": {
            "name": "Cloud Matrix Systems",
            "address": "120 Silicon Blvd, Austin TX",
            "tax_id": "TAX-12345",
            "email": "invoices@cloudmatrix.io",
        },
        "customer": {
            "name": "Acme Ventures",
            "address": "400 Market St, San Francisco CA",
            "email": "ap@acme.com",
        },
        "line_items": [
            {
                "description": "Virtual GPU Node (Dedicated)",
                "quantity": 2.0,
                "unit_price": 500.00,
                "total_price": 1000.00,
            },
            {
                "description": "Managed Database Cluster",
                "quantity": 1.0,
                "unit_price": 250.00,
                "total_price": 250.00,
            },
        ],
        "subtotal": 1250.00,
        "tax_rate": 0.08,
        "tax_amount": 100.00,
        "total_amount": 1350.00,
        "currency": "USD",
        "payment_terms": "Net 30",
    }

    invoice = InvoiceSchema.model_validate(data)
    assert invoice.invoice_number == "INV-2026-101"
    assert invoice.total_amount == 1350.00
    assert len(invoice.line_items) == 2
    assert invoice.line_items[0].total_price == 1000.00


def test_invoice_missing_required_fields_fails():
    """Verify that omitting required fields raises Pydantic ValidationError."""
    incomplete_data = {
        # Missing invoice_number and supplier
        "date": "2026-03-01",
        "customer": {"name": "Acme Corp"},
        "line_items": [],
        "subtotal": 0.0,
        "total_amount": 0.0,
    }
    with pytest.raises(ValidationError):
        InvoiceSchema.model_validate(incomplete_data)


def test_invoice_line_item_math_reconciliation():
    """Ensure line item validator reconciles minor discrepancies and rejects non-positive quantities."""
    # Valid line item
    item = LineItem(
        description="Consulting",
        quantity=5.0,
        unit_price=100.0,
        total_price=500.0,
    )
    assert item.total_price == 500.0

    # Negative quantity must fail
    with pytest.raises(ValidationError):
        LineItem(
            description="Consulting",
            quantity=-1.0,
            unit_price=100.0,
            total_price=-100.0,
        )


# ==============================================================================
# RESUME SCHEMA TESTS
# ==============================================================================

def test_valid_resume_schema_validation():
    """Verify that a candidate profile correctly parses into ResumeSchema."""
    data = {
        "contact": {
            "name": "Jordan Lee",
            "email": "jordan.lee@example.com",
            "phone": "(555) 234-5678",
            "location": "New York, NY",
            "linkedin": "linkedin.com/in/jordanlee",
            "github": "github.com/jordanlee",
        },
        "summary": "Full Stack & Machine Learning Engineer with 5 years experience.",
        "skills": {
            "technical": ["Python", "TypeScript", "SQL"],
            "frameworks": ["FastAPI", "React", "Next.js"],
            "tools": ["Docker", "PostgreSQL", "Git"],
            "soft_skills": ["Team Mentorship"],
        },
        "experience": [
            {
                "company": "Horizon Cloud",
                "role": "AI Engineer",
                "start_date": "2022",
                "end_date": "Present",
                "responsibilities": ["Developed RAG pipeline"],
                "technologies": ["Python", "ChromaDB"],
            }
        ],
        "education": [
            {
                "institution": "Columbia University",
                "degree": "B.S.",
                "field": "Computer Science",
                "graduation_year": "2020",
                "gpa": "3.9",
            }
        ],
        "projects": [
            {
                "name": "VectorSearch-Kit",
                "description": "Lightweight embedding indexer.",
                "tech_stack": ["Python", "FastAPI"],
                "link": "https://github.com/example/kit",
            }
        ],
        "certifications": [],
    }

    resume = ResumeSchema.model_validate(data)
    assert resume.contact.name == "Jordan Lee"
    assert resume.contact.email == "jordan.lee@example.com"
    assert len(resume.education) == 1
    assert resume.skills.technical == ["Python", "TypeScript", "SQL"]


def test_resume_missing_education_fails():
    """Verify that a resume with empty education raises ValidationError."""
    data = {
        "contact": {
            "name": "Jordan Lee",
            "email": "jordan.lee@example.com",
        },
        "education": [],  # Requires min_length=1
    }
    with pytest.raises(ValidationError):
        ResumeSchema.model_validate(data)


# ==============================================================================
# UTILITY & EXTRACTION SERVICE TESTS
# ==============================================================================

def test_clean_json_string_markdown_stripping():
    """Ensure clean_json_string removes markdown fences and extra commentary."""
    dirty_json = """
    Here is the extracted JSON:
    ```json
    {
      "invoice_number": "INV-001",
      "total_amount": 500.00
    }
    ```
    Hope this helps!
    """
    cleaned = clean_json_string(dirty_json)
    assert cleaned.startswith("{")
    assert cleaned.endswith("}")
    assert '"invoice_number": "INV-001"' in cleaned


def test_extraction_service_offline_invoice():
    """Test deterministic offline extraction for invoices."""
    service = ExtractionService(provider="offline")
    sample_text = """
    Invoice # INV-2026-999
    Date: 2026-03-10
    From: Nexus Cloud LLC
    Billed to: Global Alpha Corp
    Amount: $1,500.00
    """
    result = service.extract(sample_text, mode="invoice")
    assert result.success is True
    assert result.validated_data is not None
    assert "invoice_number" in result.validated_data
    assert result.validated_data["total_amount"] > 0


def test_extraction_service_offline_resume():
    """Test deterministic offline extraction for resumes."""
    service = ExtractionService(provider="offline")
    sample_text = """
    Samantha Reed
    Email: samantha.reed@example.com
    Phone: (555) 778-9900
    Senior Data Engineer specializing in PySpark, SQL, and Kafka pipelines.
    Education: Stanford University, B.S. in Symbolic Systems (2019)
    """
    result = service.extract(sample_text, mode="resume")
    assert result.success is True
    assert result.validated_data is not None
    assert result.validated_data["contact"]["email"] == "samantha.reed@example.com"


def test_extraction_service_empty_text_handling():
    """Verify that empty text input returns graceful error without crashing."""
    service = ExtractionService(provider="offline")
    result = service.extract("   ", mode="invoice")
    assert result.success is False
    assert len(result.errors) > 0
    assert "empty" in result.errors[0].lower()
