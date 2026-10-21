"""
Pydantic v2 schemas for Structured LLM Prompt Pipeline & JSON Extractor.
Strict field definitions and model validators for Invoices and Resumes.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator


# ==============================================================================
# INVOICE SCHEMAS
# ==============================================================================

class SupplierInfo(BaseModel):
    name: str = Field(..., description="Legal business name of the supplier")
    address: Optional[str] = Field(None, description="Physical or registered address")
    tax_id: Optional[str] = Field(None, description="VAT/Tax ID or EIN")
    email: Optional[str] = Field(None, description="Contact email address")


class CustomerInfo(BaseModel):
    name: str = Field(..., description="Customer or company being billed")
    address: Optional[str] = Field(None, description="Billing address of the customer")
    email: Optional[str] = Field(None, description="Customer billing email")


class LineItem(BaseModel):
    description: str = Field(..., description="Description of the item or service")
    quantity: float = Field(..., gt=0, description="Quantity of items purchased")
    unit_price: float = Field(..., ge=0, description="Price per unit")
    total_price: float = Field(..., ge=0, description="Line item total (quantity * unit_price)")

    @model_validator(mode="after")
    def verify_line_total(self) -> "LineItem":
        expected = round(self.quantity * self.unit_price, 2)
        # Allow minor rounding differences (<= 0.05)
        if abs(self.total_price - expected) > 0.05:
            # Auto-correct if trivial floating point discrepancy, otherwise keep accurate
            self.total_price = expected
        return self


class InvoiceSchema(BaseModel):
    invoice_number: str = Field(..., description="Unique alphanumeric identifier for the invoice")
    date: str = Field(..., description="Invoice issue date in YYYY-MM-DD or readable string")
    due_date: Optional[str] = Field(None, description="Payment due date")
    supplier: SupplierInfo = Field(..., description="Details of the billing party")
    customer: CustomerInfo = Field(..., description="Details of the billed party")
    line_items: List[LineItem] = Field(..., min_length=1, description="List of invoiced items")
    subtotal: float = Field(..., ge=0, description="Sum of all line items before tax")
    tax_rate: Optional[float] = Field(0.0, ge=0, description="Tax percentage rate (e.g. 0.08 for 8%)")
    tax_amount: float = Field(0.0, ge=0, description="Calculated tax amount")
    total_amount: float = Field(..., ge=0, description="Final payable amount including tax")
    currency: str = Field("USD", description="Currency code (e.g. USD, EUR, GBP, INR)")
    payment_terms: Optional[str] = Field(None, description="Payment terms (e.g. Net 30, Due on Receipt)")

    @model_validator(mode="after")
    def validate_totals(self) -> "InvoiceSchema":
        calc_subtotal = round(sum(item.total_price for item in self.line_items), 2)
        # Verify subtotal aligns reasonably with line items
        if abs(self.subtotal - calc_subtotal) > 0.10:
            # Reconcile subtotal to sum of items if discordant
            self.subtotal = calc_subtotal

        expected_total = round(self.subtotal + self.tax_amount, 2)
        if abs(self.total_amount - expected_total) > 0.10:
            self.total_amount = expected_total

        return self


# ==============================================================================
# RESUME SCHEMAS
# ==============================================================================

class ContactInfo(BaseModel):
    name: str = Field(..., description="Candidate full name")
    email: str = Field(..., description="Email address")
    phone: Optional[str] = Field(None, description="Contact phone number")
    location: Optional[str] = Field(None, description="City, State, or Country")
    linkedin: Optional[str] = Field(None, description="LinkedIn profile URL or handle")
    github: Optional[str] = Field(None, description="GitHub portfolio URL or handle")


class SkillsProfile(BaseModel):
    technical: List[str] = Field(default_factory=list, description="Core programming languages and engineering fundamentals")
    frameworks: List[str] = Field(default_factory=list, description="Frameworks and libraries (e.g. FastAPI, React, PyTorch)")
    tools: List[str] = Field(default_factory=list, description="Databases, DevOps tools, cloud services")
    soft_skills: List[str] = Field(default_factory=list, description="Collaboration, leadership, problem-solving")


class ExperienceItem(BaseModel):
    company: str = Field(..., description="Company or organization name")
    role: str = Field(..., description="Job title or designation")
    start_date: str = Field(..., description="Start date (Month Year or Year)")
    end_date: Optional[str] = Field("Present", description="End date or Present")
    responsibilities: List[str] = Field(default_factory=list, description="Key duties and achievements")
    technologies: List[str] = Field(default_factory=list, description="Technologies utilized in this role")


class EducationItem(BaseModel):
    institution: str = Field(..., description="University, college, or educational institution")
    degree: str = Field(..., description="Degree type (e.g. B.S., M.S., Ph.D.)")
    field: str = Field(..., description="Field of study or major (e.g. Computer Science)")
    graduation_year: Optional[str] = Field(None, description="Graduation year or date range")
    gpa: Optional[str] = Field(None, description="Grade point average or academic honors")


class ProjectItem(BaseModel):
    name: str = Field(..., description="Project title")
    description: str = Field(..., description="Summary of the project purpose and results")
    tech_stack: List[str] = Field(default_factory=list, description="Technologies and libraries used")
    link: Optional[str] = Field(None, description="Repository or live demo link")


class CertificationItem(BaseModel):
    name: str = Field(..., description="Certification title")
    issuer: str = Field(..., description="Issuing organization (e.g. AWS, Google Cloud, Meta)")
    issue_date: Optional[str] = Field(None, description="Date or year awarded")


class ResumeSchema(BaseModel):
    contact: ContactInfo = Field(..., description="Candidate contact details")
    summary: Optional[str] = Field(None, description="Professional summary or career objective")
    skills: SkillsProfile = Field(default_factory=SkillsProfile, description="Categorized skill breakdown")
    experience: List[ExperienceItem] = Field(default_factory=list, description="Work experience history")
    education: List[EducationItem] = Field(..., min_length=1, description="Academic background")
    projects: List[ProjectItem] = Field(default_factory=list, description="Key software or research projects")
    certifications: List[CertificationItem] = Field(default_factory=list, description="Certifications and honors")


# ==============================================================================
# WRAPPER FOR VALIDATION OUTCOMES
# ==============================================================================

class ExtractionResult(BaseModel):
    success: bool
    mode: str
    validated_data: Optional[dict] = None
    raw_response: str = ""
    errors: List[str] = Field(default_factory=list)
    retry_count: int = 0
    confidence_score: float = 1.0
