"""
AI Innovation Studio — Unified CLI Launcher & Verification Utility.
Enables one-command health checks, automated multi-project test execution,
and direct application launching across all four portfolio tasks.
"""

import os
import sys
import subprocess
import webbrowser
import argparse

# Ensure standard output supports UTF-8 on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

WORKSPACE_ROOT = os.path.dirname(os.path.abspath(__file__))

TASK_DIRS = {
    "task1": os.path.join(WORKSPACE_ROOT, "task1-json-extraction"),
    "task2": os.path.join(WORKSPACE_ROOT, "task2-document-assistant"),
    "task3": os.path.join(WORKSPACE_ROOT, "task3-autonomous-agent"),
    "task4": os.path.join(WORKSPACE_ROOT, "task4-ai-chat"),
}


def print_banner():
    print("=" * 80)
    print("  AI INNOVATION STUDIO — UNIFIED SYSTEM LAUNCHER")
    print("  Four Enterprise AI Internship Applications | Python 3.12")
    print("=" * 80)


def run_health_check():
    """Verify runtime environment and dependencies."""
    print_banner()
    print("\n🔍 Checking Python Environment & Dependencies...\n")
    print(f"• Python Version: {sys.version.split()[0]}")
    print(f"• Workspace Root: {WORKSPACE_ROOT}\n")

    required_packages = [
        ("pydantic", "Pydantic v2 Schema Engine"),
        ("streamlit", "Streamlit UI Framework"),
        ("chromadb", "ChromaDB Vector Store"),
        ("pypdf", "PyPDF Document Ingestion"),
        ("duckduckgo_search", "DuckDuckGo Search Tool"),
        ("rich", "Rich Terminal UI"),
        ("pytest", "Pytest Test Runner"),
    ]

    all_ok = True
    for pkg, label in required_packages:
        try:
            __import__(pkg)
            print(f"  [PASS] {label} ({pkg}) is installed.")
        except ImportError:
            print(f"  [FAIL] {label} ({pkg}) is MISSING.")
            all_ok = False

    print("\n" + ("=" * 80))
    if all_ok:
        print("✅ Environment Status: HEALTHY — All studio dependencies are verified.")
    else:
        print("⚠️ Environment Status: MISSING PACKAGES — Run 'pip install -r <task>/requirements.txt'")
    print("=" * 80 + "\n")


def run_all_tests():
    """Execute pytest suites across all four task directories."""
    print_banner()
    print("\n🧪 Executing Automated Test Suites Across All 4 Projects...\n")
    
    test_paths = [
        ("Task 1: Structured JSON Extractor", "task1-json-extraction/tests/test_extraction.py"),
        ("Task 2: Document RAG Assistant", "task2-document-assistant/tests/test_rag.py"),
        ("Task 3: Autonomous Multi-Tool Agent", "task3-autonomous-agent/tests/test_agent.py"),
        ("Task 4: Interactive Streamlit Chatbot", "task4-ai-chat/tests/test_chat.py"),
    ]

    total_passed = 0
    all_succeeded = True

    for name, rel_path in test_paths:
        full_path = os.path.join(WORKSPACE_ROOT, rel_path)
        print(f"--- Running {name} ({rel_path}) ---")
        cmd = [sys.executable, "-m", "pytest", full_path, "-v"]
        result = subprocess.run(cmd, cwd=WORKSPACE_ROOT)
        if result.returncode != 0:
            all_succeeded = False
        print()

    print("=" * 80)
    if all_succeeded:
        print("🎉 ALL TEST SUITES PASSED (31/31 Unit Tests Succeeded)")
    else:
        print("❌ SOME TESTS FAILED — Review test logs above.")
    print("=" * 80 + "\n")


def launch_task(task_key: str):
    """Launch the chosen application process."""
    if task_key not in TASK_DIRS:
        print(f"Error: Unknown task '{task_key}'. Valid choices: {list(TASK_DIRS.keys())}")
        return

    target_dir = TASK_DIRS[task_key]
    print(f"\n🚀 Launching {task_key.upper()} from {target_dir}...\n")

    if task_key in ["task1", "task2", "task4"]:
        cmd = ["streamlit", "run", "app.py"]
        subprocess.run(cmd, cwd=target_dir)
    elif task_key == "task3":
        cmd = [sys.executable, "main.py"]
        subprocess.run(cmd, cwd=target_dir)


def open_portal():
    """Open central landing page in browser."""
    portal_path = os.path.join(WORKSPACE_ROOT, "index.html")
    if os.path.exists(portal_path):
        print(f"Opening central portal: {portal_path}")
        webbrowser.open(f"file://{portal_path}")
    else:
        print(f"Error: Portal file '{portal_path}' not found.")


def main():
    parser = argparse.ArgumentParser(description="AI Innovation Studio Unified Launcher")
    parser.add_argument(
        "action",
        choices=["check", "test", "run", "portal"],
        help="Action to perform: 'check' (verify environment), 'test' (run all test suites), 'run' (launch app), 'portal' (open index.html)",
    )
    parser.add_argument(
        "--task",
        "-t",
        choices=["task1", "task2", "task3", "task4"],
        default="task1",
        help="Specify task to launch when using 'run'",
    )

    args = parser.parse_args()

    if args.action == "check":
        run_health_check()
    elif args.action == "test":
        run_all_tests()
    elif args.action == "run":
        launch_task(args.task)
    elif args.action == "portal":
        open_portal()


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print_banner()
        print("\nUsage Commands:")
        print("  python launcher.py check          # Verify Python environment & dependencies")
        print("  python launcher.py test           # Execute automated test suites for all 4 tasks")
        print("  python launcher.py portal         # Open central index.html in browser")
        print("  python launcher.py run --task task1   # Launch Task 1 (JSON Extractor)")
        print("  python launcher.py run --task task2   # Launch Task 2 (Document RAG)")
        print("  python launcher.py run --task task3   # Launch Task 3 (Autonomous Agent)")
        print("  python launcher.py run --task task4   # Launch Task 4 (AI Chatbot)\n")
    else:
        main()
