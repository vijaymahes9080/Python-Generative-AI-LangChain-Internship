"""
Automated unit tests for Task 3: Multi-Tool Autonomous AI Agent.
Validates AST calculator safety, sandboxed file reader traversal defense,
DuckDuckGo search sanitization, and the ReAct multi-tool reasoning loop.
"""

import sys
import os
import pytest

# Ensure task directory is in sys.path
task_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if task_dir not in sys.path:
    sys.path.insert(0, task_dir)

from tools.calculator import SafeCalculator, run_calculator
from tools.file_reader import SandboxedFileReader, run_file_reader
from tools.web_search import DuckDuckGoSearchTool, run_web_search
from agent import AutonomousAgent, AgentRunResult


# ==============================================================================
# CALCULATOR TOOL TESTS
# ==============================================================================

def test_calculator_valid_arithmetic():
    """Verify that arithmetic and whitelisted math functions calculate accurately."""
    res = run_calculator("150 * 2 + 50")
    assert res == "350"

    res_sqrt = run_calculator("sqrt(144) + 10 * 2")
    assert res_sqrt == "32"

    res_float = run_calculator("24.5 + 28.2")
    assert res_float == "52.7"


def test_calculator_zero_division_guard():
    """Verify division by zero returns clean diagnostic error."""
    res = run_calculator("100 / 0")
    assert "error" in res.lower()
    assert "division by zero" in res.lower()


def test_calculator_security_sandbox_eval_rejection():
    """Verify dangerous code injection strings are strictly rejected by the AST parser."""
    dangerous_payloads = [
        "__import__('os').system('ls')",
        "eval('2 + 2')",
        "exec('print(1)')",
        "open('/etc/passwd').read()",
        "'hello'.upper()",
        "[x for x in (1, 2, 3)]",
        "lambda x: x + 1",
    ]

    for payload in dangerous_payloads:
        res = run_calculator(payload)
        assert "calculation error" in res.lower() or "security restriction" in res.lower() or "forbidden" in res.lower()


# ==============================================================================
# FILE READER TOOL TESTS
# ==============================================================================

def test_file_reader_valid_sandbox_read():
    """Verify reading authorized files inside the sandbox succeeds."""
    res = run_file_reader("system_specs.json")
    assert "alpha-compute-prod-01" in res
    assert "H100" in res


def test_file_reader_path_traversal_rejection():
    """Verify path traversal sequences are strictly blocked by boundary checks."""
    traversal_attempts = [
        "../README.md",
        "../../etc/passwd",
        "..\\..\\Windows\\System32\\calc.exe",
        "/etc/shadow",
        "C:\\autoexec.bat",
        "subdir/../../../secrets.env",
    ]

    for attempt in traversal_attempts:
        res = run_file_reader(attempt)
        assert "security restriction" in res.lower()
        assert "forbidden" in res.lower() or "traversal" in res.lower()


def test_file_reader_nonexistent_file():
    """Verify non-existent files return helpful diagnostic list of available sandbox files."""
    res = run_file_reader("non_existent_file_99.txt")
    assert "file reader error" in res.lower()
    assert "not found in sandbox" in res.lower()
    assert "available files" in res.lower()


# ==============================================================================
# WEB SEARCH TOOL TESTS
# ==============================================================================

def test_web_search_query_sanitization():
    """Verify search tool sanitizes raw queries and provides fallback info."""
    clean = DuckDuckGoSearchTool.sanitize_query("  Python 3.12   features! \x00\x1f  ")
    assert "\x00" not in clean
    assert clean == "Python 3.12 features!"

    # Test search with knowledge query
    res = run_web_search("Python latest version")
    assert len(res) > 20
    assert "Python" in res


# ==============================================================================
# REACT REASONING LOOP TESTS
# ==============================================================================

def test_agent_compound_workflow_execution():
    """Verify agent executes multiple tools sequentially and synthesizes an answer."""
    agent = AutonomousAgent(provider="offline", max_steps=4)
    query = "Read system_specs.json, calculate 64 * 8 for total memory, and search DuckDuckGo for Python."
    
    result: AgentRunResult = agent.run(query)

    assert result.success is True
    assert result.total_steps >= 2
    assert len(result.events) >= 2
    
    # Check that all executed events succeeded
    for ev in result.events:
        assert ev.status == "SUCCESS"
        assert ev.duration_ms >= 0

    # Verify final answer includes computed calculation and file data
    assert "512" in result.final_answer or "Calculation Result" in result.final_answer
    assert "File Data Retrieved" in result.final_answer
    assert result.total_duration_ms > 0
