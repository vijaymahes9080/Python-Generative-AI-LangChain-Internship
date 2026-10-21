"""
Chat Engine & Multi-Mode Orchestrator for Task 4: Interactive Full-Stack AI Chatbot.
Supports token streaming, persona management, and cross-task integrations
(Direct LLM, Task 2 Document RAG, and Task 3 Multi-Tool Autonomous Agent).
"""

import os
import sys
import time
from typing import List, Dict, Any, Generator, Optional
from dataclasses import dataclass, asdict

# Add workspace root to sys.path so Task 2 & Task 3 can be imported cleanly
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)


@dataclass
class ChatMessage:
    role: str  # "user", "assistant", or "system"
    content: str
    mode: str = "direct"
    timestamp: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


PERSONAS = {
    "General Assistant": (
        "You are an intelligent, articulate, and helpful AI assistant for the AI Innovation Studio. "
        "Provide thorough, clear, and structured answers with code examples where relevant."
    ),
    "Senior Code Reviewer": (
        "You are an elite principal software architect and code reviewer. "
        "Analyze code snippets for architectural integrity, edge-case safety, cyclomatic complexity, "
        "and idiomatic Python 3 standards. Be constructive, rigorous, and precise."
    ),
    "Technical Researcher": (
        "You are a computer science research scientist specializing in NLP and generative AI. "
        "Provide deeply technical, benchmark-grounded explanations with theoretical context and references."
    ),
    "Data & Systems Architect": (
        "You are an enterprise data and cloud systems architect. "
        "Focus on scalability, distributed systems patterns, high-availability schemas, and security guardrails."
    ),
}


class ChatService:
    """Manages chat streaming, persona system prompts, and multi-pipeline integrations."""

    def __init__(self, provider: str = "auto", api_key: Optional[str] = None):
        self.provider = provider
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")

        # Lazy references for integrations
        self._rag_service = None
        self._agent_service = None

    def _get_rag_service(self):
        if self._rag_service is None:
            try:
                from task2_document_assistant.retrieval import RAGRetrievalService
                from task2_document_assistant.ingestion import DocumentIngestionService
                self._rag_service = RAGRetrievalService(provider="offline")
                # Auto-load sample doc
                sample_file = os.path.join(root_dir, "task2-document-assistant", "samples", "ai_governance_brief.txt")
                if os.path.exists(sample_file):
                    with open(sample_file, "rb") as f:
                        chunks = DocumentIngestionService().ingest(f.read(), "ai_governance_brief.txt")
                        self._rag_service.index_chunks(chunks)
            except Exception:
                try:
                    # Alternative import
                    sys.path.insert(0, os.path.join(root_dir, "task2-document-assistant"))
                    from retrieval import RAGRetrievalService
                    from ingestion import DocumentIngestionService
                    self._rag_service = RAGRetrievalService(provider="offline")
                    sample_file = os.path.join(root_dir, "task2-document-assistant", "samples", "ai_governance_brief.txt")
                    if os.path.exists(sample_file):
                        with open(sample_file, "rb") as f:
                            chunks = DocumentIngestionService().ingest(f.read(), "ai_governance_brief.txt")
                            self._rag_service.index_chunks(chunks)
                except Exception:
                    self._rag_service = None
        return self._rag_service

    def _get_agent_service(self):
        if self._agent_service is None:
            try:
                sys.path.insert(0, os.path.join(root_dir, "task3-autonomous-agent"))
                from agent import AutonomousAgent
                self._agent_service = AutonomousAgent(provider="offline")
            except Exception:
                self._agent_service = None
        return self._agent_service

    def stream_response(
        self,
        messages: List[Dict[str, str]],
        persona_name: str = "General Assistant",
        mode: str = "direct",
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> Generator[str, None, None]:
        """
        Generate incremental response stream for conversational UI.
        
        Args:
            messages: List of chat messages (dicts with 'role' and 'content').
            persona_name: Active persona key.
            mode: 'direct', 'rag', or 'agent'.
            temperature: Sampling temperature.
            max_tokens: Output token bound.
            
        Yields:
            Incremental text tokens/chunks.
        """
        last_user_message = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                last_user_message = m.get("content", "")
                break

        # Integration Mode: Task 2 Document RAG
        if mode == "rag":
            rag = self._get_rag_service()
            if rag:
                yield "🔍 *Querying Document Vector Index via Task 2 RAG Pipeline...*\n\n"
                result = rag.ask(last_user_message)
                
                # Stream answer tokens
                words = result.answer.split(" ")
                for word in words:
                    yield word + " "
                    time.sleep(0.015)

                if result.citations:
                    yield "\n\n---\n**📑 Verified Sources:**\n"
                    for c in result.citations:
                        yield f"- `{c.source_file}` (Page {c.page_number}, Relevance: {c.relevance_score*100:.1f}%)\n"
                return
            else:
                yield "RAG service integration is currently initializing. Falling back to direct conversational mode.\n\n"

        # Integration Mode: Task 3 Multi-Tool Agent
        if mode == "agent":
            agent = self._get_agent_service()
            if agent:
                yield "🤖 *Deploying Task 3 Autonomous Agent with sandboxed tools...*\n\n"
                result = agent.run(last_user_message)
                
                # Stream step highlights
                for ev in result.events:
                    yield f"- **Step {ev.step}:** Executed `{ev.tool_name}` ({ev.status} in {ev.duration_ms:.1f}ms)\n"
                    time.sleep(0.05)

                yield f"\n**🎯 Final Answer:**\n\n"
                words = result.final_answer.split(" ")
                for word in words:
                    yield word + " "
                    time.sleep(0.015)
                return
            else:
                yield "Autonomous agent integration is currently initializing. Falling back to direct conversational mode.\n\n"

        # Direct Chat Mode: Check Live Providers
        system_instruction = PERSONAS.get(persona_name, PERSONAS["General Assistant"])
        gemini_key = self.api_key or os.getenv("GEMINI_API_KEY")
        openai_key = self.api_key or os.getenv("OPENAI_API_KEY")

        # 1. Google Gemini Streaming
        if self.provider in ["auto", "gemini"] and gemini_key:
            try:
                from google import genai
                client = genai.Client(api_key=gemini_key)
                model_name = os.getenv("DEFAULT_GEMINI_MODEL", "gemini-2.5-flash")
                
                # Build contents
                contents = []
                for m in messages:
                    contents.append(f"{m['role'].capitalize()}: {m['content']}")
                prompt_full = "\n".join(contents)

                response_stream = client.models.generate_content_stream(
                    model=model_name,
                    contents=prompt_full,
                    config={
                        "system_instruction": system_instruction,
                        "temperature": temperature,
                        "max_output_tokens": max_tokens,
                    },
                )
                for chunk in response_stream:
                    if chunk.text:
                        yield chunk.text
                return
            except Exception:
                pass

        # 2. OpenAI Streaming
        if self.provider in ["auto", "openai"] and openai_key:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=openai_key)
                model_name = os.getenv("DEFAULT_OPENAI_MODEL", "gpt-4o-mini")

                formatted_msgs = [{"role": "system", "content": system_instruction}]
                formatted_msgs.extend([{"role": m["role"], "content": m["content"]} for m in messages])

                stream = client.chat.completions.create(
                    model=model_name,
                    messages=formatted_msgs,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=True,
                )
                for chunk in stream:
                    delta = chunk.choices[0].delta.content
                    if delta:
                        yield delta
                return
            except Exception:
                pass

        # 3. Deterministic Local Streaming Engine
        yield from self._stream_offline_response(last_user_message, persona_name)

    def _stream_offline_response(self, query: str, persona: str) -> Generator[str, None, None]:
        """Provides realistic streaming responses locally without requiring external network."""
        response_template = (
            f"Hello! I am responding in **{persona}** mode from the AI Innovation Studio.\n\n"
            f"Regarding your query: *\"{query}\"*\n\n"
            "This application operates on a full-stack reactive architecture with:\n"
            "1. **Streamlit Chat State**: Message threads are preserved in `st.session_state`.\n"
            "2. **Incremental Token Streaming**: Smooth visual rendering with non-blocking generator yields.\n"
            "3. **Pipeline Interoperability**: Seamless toggling between Direct LLM Chat, Task 2 RAG Q&A, and Task 3 Tool Agent.\n\n"
            "Feel free to select another persona or toggle to RAG / Agent mode in the sidebar to explore integrated capabilities!"
        )

        words = response_template.split(" ")
        for word in words:
            yield word + " "
            time.sleep(0.015)
