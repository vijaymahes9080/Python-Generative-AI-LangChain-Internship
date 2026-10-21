"""
Sandboxed Local File Reader Tool for Task 3: Autonomous Agent.
Strict path-traversal prevention, canonical boundary validation, and read size limits.
Ensures the agent cannot inspect files outside the explicitly designated sandbox folder.
"""

import os
from typing import Optional
from pydantic import BaseModel, Field


class FileReaderInput(BaseModel):
    filename: str = Field(
        ...,
        description="Relative filename or subpath inside the sandbox directory (e.g. 'quarterly_earnings.txt' or 'system_specs.json')",
    )


class SandboxedFileReader:
    """Safely reads files strictly within an isolated sandbox directory."""

    MAX_FILE_BYTES = 100 * 1024  # 100 KB limit to prevent buffer blowups

    def __init__(self, sandbox_dir: Optional[str] = None):
        if sandbox_dir:
            self.sandbox_dir = os.path.abspath(sandbox_dir)
        else:
            default_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "sandbox_data",
            )
            self.sandbox_dir = os.path.abspath(default_dir)

        os.makedirs(self.sandbox_dir, exist_ok=True)

    def read_file(self, filename: str) -> str:
        """
        Safely resolve path and read file content within sandbox.
        
        Args:
            filename: Relative file path.
            
        Returns:
            File content string or security error notification.
        """
        if not filename or not filename.strip():
            return "File Reader Error: Filename parameter cannot be empty."

        clean_name = filename.strip()

        # Reject obvious traversal patterns upfront
        if ".." in clean_name or clean_name.startswith("/") or clean_name.startswith("\\"):
            return f"Security Restriction: Path traversal detected. Access outside sandbox '{clean_name}' is forbidden."

        # Reject Windows drive letters (e.g. C:)
        if len(clean_name) > 1 and clean_name[1] == ":":
            return f"Security Restriction: Absolute drive paths '{clean_name}' are strictly forbidden."

        # Compute canonical paths
        target_path = os.path.abspath(os.path.join(self.sandbox_dir, clean_name))

        # Boundary check: target path must start with sandbox root
        try:
            common = os.path.commonpath([self.sandbox_dir, target_path])
            if common != self.sandbox_dir:
                return f"Security Restriction: Resolved path '{target_path}' escapes sandbox directory."
        except ValueError:
            return "Security Restriction: Cross-drive path access is forbidden."

        # File presence & type check
        if not os.path.exists(target_path):
            available = os.listdir(self.sandbox_dir)
            return (
                f"File Reader Error: File '{clean_name}' not found in sandbox. "
                f"Available files: {available if available else 'None'}"
            )

        if not os.path.isfile(target_path):
            return f"File Reader Error: Target '{clean_name}' is a directory, not a readable file."

        # Check file size limit
        file_size = os.path.getsize(target_path)
        if file_size > self.MAX_FILE_BYTES:
            return f"File Reader Error: File size ({file_size} bytes) exceeds sandbox maximum limit ({self.MAX_FILE_BYTES} bytes)."

        # Read content safely
        try:
            with open(target_path, "r", encoding="utf-8") as f:
                content = f.read()
            return content
        except UnicodeDecodeError:
            try:
                with open(target_path, "r", encoding="latin-1") as f:
                    return f.read()
            except Exception as e:
                return f"File Reader Error: Unable to decode file '{clean_name}': {str(e)}"
        except Exception as e:
            return f"File Reader Error: {str(e)}"


# Singleton default reader
_default_reader = SandboxedFileReader()


def run_file_reader(filename: str, sandbox_dir: Optional[str] = None) -> str:
    """Wrapper function conforming to agent tool signature."""
    if sandbox_dir:
        reader = SandboxedFileReader(sandbox_dir=sandbox_dir)
        return reader.read_file(filename)
    return _default_reader.read_file(filename)
