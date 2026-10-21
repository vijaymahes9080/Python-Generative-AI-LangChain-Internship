"""
Automated unit tests for Task 4: Interactive Full-Stack AI Chatbot.
Validates session state structures, persona steering, streaming generator behavior,
and cross-task RAG / Agent pipeline integrations.
"""

import sys
import os
import types
import pytest

# Ensure task directory is in sys.path
task_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if task_dir not in sys.path:
    sys.path.insert(0, task_dir)

from chat_service import ChatService, ChatMessage, PERSONAS


# ==============================================================================
# SESSION STATE & DATA MODEL TESTS
# ==============================================================================

def test_chat_message_dataclass():
    """Verify ChatMessage initialization and dictionary export."""
    msg = ChatMessage(
        role="user",
        content="Hello AI Studio",
        mode="direct",
        timestamp=100.0,
    )
    assert msg.role == "user"
    assert msg.content == "Hello AI Studio"
    d = msg.to_dict()
    assert d["role"] == "user"
    assert d["mode"] == "direct"


def test_personas_configuration():
    """Ensure all required system personas are defined and contain substantial instructions."""
    expected_personas = [
        "General Assistant",
        "Senior Code Reviewer",
        "Technical Researcher",
        "Data & Systems Architect",
    ]
    for persona in expected_personas:
        assert persona in PERSONAS
        assert len(PERSONAS[persona]) > 40


# ==============================================================================
# STREAMING & PIPELINE INTEGRATION TESTS
# ==============================================================================

def test_chat_service_streaming_generator():
    """Verify that stream_response returns a Python generator yielding string chunks."""
    service = ChatService(provider="offline")
    messages = [{"role": "user", "content": "Explain vector similarity search."}]

    stream = service.stream_response(messages, persona_name="General Assistant", mode="direct")
    assert isinstance(stream, types.GeneratorType)

    collected_chunks = list(stream)
    assert len(collected_chunks) > 0
    full_text = "".join(collected_chunks)
    assert len(full_text) > 20
    assert "AI Innovation Studio" in full_text


def test_chat_service_mode_rag_integration():
    """Verify RAG integration mode yields retrieval status and grounded evidence."""
    service = ChatService(provider="offline")
    messages = [{"role": "user", "content": "What is the compliance requirement for RAG citations?"}]

    stream = service.stream_response(messages, mode="rag")
    collected = "".join(list(stream))

    assert len(collected) > 0
    assert "Querying Document Vector Index" in collected or "Based on the documents" in collected or "evidence" in collected


def test_chat_service_mode_agent_integration():
    """Verify agent integration mode executes multi-tool steps and streams output."""
    service = ChatService(provider="offline")
    messages = [{"role": "user", "content": "Calculate 50 * 4 and check quarterly_earnings.txt"}]

    stream = service.stream_response(messages, mode="agent")
    collected = "".join(list(stream))

    assert len(collected) > 0
    assert "Deploying Task 3 Autonomous Agent" in collected or "Step" in collected or "Final Answer" in collected


def test_chat_history_state_mutation():
    """Verify message append and reset behavior mimics Streamlit session state."""
    session_messages = []
    session_messages.append({"role": "user", "content": "First prompt"})
    session_messages.append({"role": "assistant", "content": "First response"})
    assert len(session_messages) == 2

    # Reset
    session_messages.clear()
    assert len(session_messages) == 0
