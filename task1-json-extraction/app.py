"""
Streamlit Web Application for Task 1: Structured LLM Prompt Pipeline & JSON Extractor.
Part of the AI Innovation Studio suite.
"""

import os
import sys
import json
import streamlit as st

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from extraction_service import ExtractionService

# Page configuration
st.set_page_config(
    page_title="JSON Extractor | AI Innovation Studio",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #a78bfa 0%, #38bdf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        color: #94a3b8;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    .badge-pill {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        font-size: 0.8rem;
        font-weight: 600;
        border-radius: 9999px;
        background-color: #1e293b;
        color: #38bdf8;
        border: 1px solid #334155;
        margin-right: 0.5rem;
    }
    .status-card {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #0f172a;
        border: 1px solid #1e293b;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.markdown("### ⚙️ Engine Settings")
    
    provider_choice = st.selectbox(
        "LLM Provider",
        options=["auto", "gemini", "openai", "offline"],
        format_func=lambda x: {
            "auto": "Auto-Select (Environment)",
            "gemini": "Google Gemini (Official SDK)",
            "openai": "OpenAI (Official SDK)",
            "offline": "Deterministic Offline Engine",
        }[x],
        index=0,
    )

    api_key_input = st.text_input(
        "API Key (Optional override)",
        type="password",
        help="Leave blank to use environment variables (GEMINI_API_KEY / OPENAI_API_KEY) or offline mode.",
    )

    extraction_mode = st.radio(
        "Target Schema",
        options=["invoice", "resume"],
        format_func=lambda x: "📄 Commercial Invoice" if x == "invoice" else "👤 Candidate Resume",
    )

    st.markdown("---")
    st.markdown("### 📚 Load Sample Document")
    sample_options = ["None (Upload or Paste)"]
    if extraction_mode == "invoice":
        sample_options.extend(["TechCorp Cloud (H100 Invoice)", "SwiftLogistics (Freight Invoice)"])
    else:
        sample_options.extend(["Senior Backend & AI Engineer", "Lead NLP Data Scientist"])

    selected_sample = st.selectbox("Choose Sample", options=sample_options)

    st.markdown("---")
    st.markdown(
        "<div style='font-size: 0.8rem; color: #64748b;'>AI Innovation Studio • Task 1<br>Pydantic v2 Validated</div>",
        unsafe_allow_html=True,
    )

# Header Section
st.markdown("<div class='main-header'>Structured LLM Prompt Pipeline & JSON Extractor</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='sub-header'>Transform unstructured invoices and resumes into schema-validated, strongly typed JSON records with bounded self-correction.</div>",
    unsafe_allow_html=True,
)

# Determine Initial Content based on sample selection
sample_map = {
    "TechCorp Cloud (H100 Invoice)": "sample_invoice_techcorp.txt",
    "SwiftLogistics (Freight Invoice)": "sample_invoice_logistics.txt",
    "Senior Backend & AI Engineer": "sample_resume_senior_dev.txt",
    "Lead NLP Data Scientist": "sample_resume_data_scientist.txt",
}

initial_text = ""
if selected_sample in sample_map:
    sample_path = os.path.join(current_dir, "samples", sample_map[selected_sample])
    if os.path.exists(sample_path):
        with open(sample_path, "r", encoding="utf-8") as f:
            initial_text = f.read()

# Layout Columns
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.markdown("#### 📥 Input Document")
    
    uploaded_file = st.file_uploader(
        "Upload Document (TXT or PDF)",
        type=["txt", "pdf"],
        help="Upload an invoice or resume to extract structured data.",
    )

    if uploaded_file is not None:
        if uploaded_file.name.endswith(".txt"):
            initial_text = uploaded_file.read().decode("utf-8")
        elif uploaded_file.name.endswith(".pdf"):
            try:
                import pypdf
                reader = pypdf.PdfReader(uploaded_file)
                pages_text = [page.extract_text() or "" for page in reader.pages]
                initial_text = "\n".join(pages_text)
            except Exception as e:
                st.error(f"Error parsing PDF file: {str(e)}")

    document_text = st.text_area(
        "Document Text (Paste or Edit)",
        value=initial_text,
        height=380,
        placeholder="Paste invoice text, job candidate resume, or load a sample document from the sidebar...",
    )

    extract_btn = st.button("🚀 Run Extraction Pipeline", type="primary", use_container_width=True)

with col_right:
    st.markdown("#### 📤 Validated JSON Output")

    if extract_btn:
        if not document_text.strip():
            st.warning("Please provide or paste document text before running extraction.")
        else:
            with st.spinner("Executing extraction prompt with schema validation..."):
                service = ExtractionService(provider=provider_choice, api_key=api_key_input if api_key_input else None)
                result = service.extract(document_text, mode=extraction_mode, max_retries=2)

                if result.success and result.validated_data:
                    st.success("✅ Schema Validation Succeeded!")
                    
                    # Metrics Banner
                    m1, m2, m3 = st.columns(3)
                    with m1:
                        st.metric("Status", "Validated")
                    with m2:
                        st.metric("Confidence", f"{result.confidence_score * 100:.0f}%")
                    with m3:
                        st.metric("Self-Correction Retries", result.retry_count)

                    # Formatted Tabs
                    tab_json, tab_preview, tab_raw = st.tabs(["📄 Formatted JSON", "🔍 Field Inspector", "📝 Raw Response"])

                    with tab_json:
                        json_str = json.dumps(result.validated_data, indent=2)
                        st.code(json_str, language="json")
                        st.download_button(
                            label="⬇️ Download Validated JSON",
                            data=json_str,
                            file_name=f"extracted_{extraction_mode}.json",
                            mime="application/json",
                            use_container_width=True,
                        )

                    with tab_preview:
                        st.json(result.validated_data)

                    with tab_raw:
                        st.text_area("LLM Raw String", value=result.raw_response, height=250, disabled=True)
                else:
                    st.error("❌ Extraction Validation Failed")
                    if result.errors:
                        st.markdown("**Validation Diagnostics:**")
                        for err in result.errors:
                            st.error(err)
                    if result.raw_response:
                        with st.expander("Inspect Unvalidated Model Response"):
                            st.code(result.raw_response, language="json")
    else:
        st.info("👈 Load a sample document or paste text on the left, then click 'Run Extraction Pipeline'.")
