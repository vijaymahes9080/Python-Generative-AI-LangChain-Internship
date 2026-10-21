"""
Streamlit Web Application for Task 4: Interactive Full-Stack AI Chatbot.
Part of the AI Innovation Studio suite.
Features real-time token streaming, persona steering, and pipeline integrations.
"""

import os
import sys
import streamlit as st

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from chat_service import ChatService, PERSONAS

# Page configuration
st.set_page_config(
    page_title="AI Chatbot Studio | AI Innovation Studio",
    page_icon="💬",
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
    .mode-pill {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        font-size: 0.78rem;
        font-weight: 600;
        border-radius: 9999px;
        background-color: #1e1b4b;
        color: #c084fc;
        border: 1px solid #4338ca;
        margin-left: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_service" not in st.session_state:
    st.session_state.chat_service = ChatService()

chat_svc: ChatService = st.session_state.chat_service

# Sidebar Controls
with st.sidebar:
    st.markdown("### 🎛️ Assistant Controls")

    # Mode Selector
    active_mode = st.radio(
        "Execution Mode",
        options=["direct", "rag", "agent"],
        format_func=lambda x: {
            "direct": "💬 Direct Conversational LLM",
            "rag": "📑 Document-Grounded RAG (Task 2)",
            "agent": "🤖 Multi-Tool Autonomous Agent (Task 3)",
        }[x],
        index=0,
    )

    # Persona Selector
    active_persona = st.selectbox(
        "System Persona",
        options=list(PERSONAS.keys()),
        index=0,
    )
    st.caption(f"_{PERSONAS[active_persona][:120]}..._")

    st.markdown("---")
    st.markdown("### ⚙️ Model Parameters")

    provider = st.selectbox(
        "Provider",
        options=["auto", "gemini", "openai", "offline"],
        format_func=lambda x: {
            "auto": "Auto-Select (Environment)",
            "gemini": "Google Gemini (Official SDK)",
            "openai": "OpenAI (Official SDK)",
            "offline": "Deterministic Local Engine",
        }[x],
        index=0,
    )
    if provider != chat_svc.provider:
        chat_svc.provider = provider

    temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.05)
    max_tokens = st.slider("Max Output Tokens", min_value=256, max_value=2048, value=1024, step=128)

    st.markdown("---")
    if st.button("🗑️ Clear Conversation History", type="secondary", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown(
        "<div style='font-size: 0.8rem; color: #64748b; margin-top: 1rem;'>AI Innovation Studio • Task 4<br>Streaming Chat Application</div>",
        unsafe_allow_html=True,
    )

# Main Header
st.markdown("<div class='main-header'>Interactive Full-Stack AI Chatbot</div>", unsafe_allow_html=True)
mode_labels = {
    "direct": "Direct Conversational Mode",
    "rag": "Grounded Document RAG Mode (Task 2 Integrated)",
    "agent": "Autonomous Multi-Tool Agent Mode (Task 3 Integrated)",
}
st.markdown(
    f"<div class='sub-header'>Responsive chat interface with streaming tokens, persona steering, and unified project integrations. <span class='mode-pill'>{mode_labels[active_mode]}</span></div>",
    unsafe_allow_html=True,
)

# Render Message History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Empty State Starter Suggestions
if not st.session_state.messages:
    st.markdown("### 💡 Starter Prompts")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Explain the architecture of Pydantic v2 validation.", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "Explain the architecture of Pydantic v2 validation."})
            st.rerun()
        if st.button("What is the difference between dense vectors and BM25 search?", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "What is the difference between dense vectors and BM25 search?"})
            st.rerun()
    with col2:
        if st.button("Read system_specs.json and calculate total cluster memory.", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "Read system_specs.json and calculate total cluster memory."})
            st.rerun()
        if st.button("How does the ReAct loop prevent infinite tool execution?", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "How does the ReAct loop prevent infinite tool execution?"})
            st.rerun()

# Chat Input & Streaming Execution
if prompt := st.chat_input("Type your message..."):
    # Append user prompt
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate streaming assistant response
    with st.chat_message("assistant"):
        stream_gen = chat_svc.stream_response(
            messages=st.session_state.messages,
            persona_name=active_persona,
            mode=active_mode,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        response_text = st.write_stream(stream_gen)

    # Persist assistant response
    st.session_state.messages.append({"role": "assistant", "content": response_text})
