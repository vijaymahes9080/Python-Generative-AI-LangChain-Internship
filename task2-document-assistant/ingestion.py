"""
Document Ingestion & Chunking Pipeline for Task 2: Document Q&A Assistant.
Extracts text from PDF/TXT documents, tracks page metadata, and applies
RecursiveCharacterTextSplitter for optimal embedding chunk distribution.
"""

import io
import os
from typing import List, Dict, Any, Union
from dataclasses import dataclass, asdict
from langchain_text_splitters import RecursiveCharacterTextSplitter


@dataclass
class DocumentChunk:
    chunk_id: str
    text: str
    source_file: str
    page_number: int
    chunk_index: int
    char_count: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class DocumentIngestionError(Exception):
    """Raised when document ingestion encounters empty, scanned, or invalid files."""
    pass


class DocumentIngestionService:
    """Service handling multi-format document parsing and recursive semantic chunking."""

    def __init__(self, chunk_size: int = 700, chunk_overlap: int = 120):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
            keep_separator=True,
        )

    def extract_text_from_txt(self, file_bytes: bytes, filename: str) -> List[Dict[str, Any]]:
        """Extract content from plain text file."""
        try:
            text = file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            try:
                text = file_bytes.decode("latin-1")
            except Exception as e:
                raise DocumentIngestionError(f"Failed to decode text file '{filename}': {str(e)}")

        if not text.strip():
            raise DocumentIngestionError(f"The document '{filename}' is empty.")

        return [{"text": text, "page_number": 1, "source_file": filename}]

    def extract_text_from_pdf(self, file_bytes: bytes, filename: str) -> List[Dict[str, Any]]:
        """Extract content and page boundaries from PDF file."""
        try:
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        except Exception as e:
            raise DocumentIngestionError(f"Corrupted or invalid PDF file '{filename}': {str(e)}")

        if len(reader.pages) == 0:
            raise DocumentIngestionError(f"PDF document '{filename}' has no pages.")

        pages_data = []
        total_extracted_chars = 0

        for idx, page in enumerate(reader.pages):
            try:
                page_text = page.extract_text() or ""
            except Exception:
                page_text = ""

            page_num = idx + 1
            if page_text.strip():
                pages_data.append({
                    "text": page_text.strip(),
                    "page_number": page_num,
                    "source_file": filename,
                })
                total_extracted_chars += len(page_text.strip())

        if total_extracted_chars == 0:
            raise DocumentIngestionError(
                f"Document '{filename}' appears to be a scanned or image-only PDF with no extractable text."
            )

        return pages_data

    def ingest(self, file_bytes: bytes, filename: str) -> List[DocumentChunk]:
        """
        Ingest raw document bytes, extract text with page metadata, and split into chunks.
        
        Args:
            file_bytes: Raw binary file content.
            filename: Name of the uploaded file.
            
        Returns:
            List of DocumentChunk instances with preserved metadata.
        """
        ext = os.path.splitext(filename)[1].lower()
        if ext == ".txt":
            pages = self.extract_text_from_txt(file_bytes, filename)
        elif ext == ".pdf":
            pages = self.extract_text_from_pdf(file_bytes, filename)
        else:
            raise DocumentIngestionError(
                f"Unsupported file format '{ext}'. Only .pdf and .txt are supported."
            )

        chunks: List[DocumentChunk] = []
        global_chunk_idx = 0

        for page in pages:
            raw_splits = self.text_splitter.split_text(page["text"])
            for split in raw_splits:
                if split.strip():
                    chunk_id = f"{filename}_p{page['page_number']}_c{global_chunk_idx}"
                    chunks.append(DocumentChunk(
                        chunk_id=chunk_id,
                        text=split.strip(),
                        source_file=page["source_file"],
                        page_number=page["page_number"],
                        chunk_index=global_chunk_idx,
                        char_count=len(split.strip()),
                    ))
                    global_chunk_idx += 1

        return chunks
