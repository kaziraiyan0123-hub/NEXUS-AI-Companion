"""
NEXUS Document & File Processing Engine
Extracts full text, structured data, and code from attached files:
- PDF documents (page-by-page extraction via pypdf / QtPdf fallback)
- Text & Markdown documents (.txt, .md, .rtf, .log)
- Code files (.py, .js, .ts, .html, .css, .json, .xml, .yaml, .sql, etc.)
- Spreadsheets (.csv, .xlsx)
Injects rich, contextualized document data into AI prompts so the companion
understands attached files completely and delivers 100% accurate answers.
"""
import os
import logging
from typing import Tuple, Dict, Any, List, Optional

logger = logging.getLogger("NEXUS.DocumentProcessor")


class DocumentProcessor:
    """Intelligent document content extractor for NEXUS."""

    MAX_CHARS_PER_FILE = 65000  # ~15,000 to 18,000 words per document

    @classmethod
    def extract_file_content(cls, filepath: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Reads and extracts the content of a file.
        Returns: (success: bool, text_content: str, metadata: dict)
        """
        if not os.path.exists(filepath):
            return False, f"File not found: {filepath}", {}

        filename = os.path.basename(filepath)
        size_bytes = os.path.getsize(filepath)
        size_kb = round(size_bytes / 1024, 1)
        ext = os.path.splitext(filename)[1].lower()

        meta = {
            "filename": filename,
            "filepath": filepath,
            "size_kb": size_kb,
            "extension": ext,
            "file_type": "Unknown"
        }

        # 1. PDF Documents
        if ext == ".pdf":
            meta["file_type"] = "PDF Document"
            return cls._extract_pdf(filepath, meta)

        # 2. Excel Spreadsheets
        elif ext in (".xlsx", ".xlsm"):
            meta["file_type"] = "Excel Spreadsheet"
            return cls._extract_excel(filepath, meta)

        # 3. CSV / TSV tabular data
        elif ext in (".csv", ".tsv"):
            meta["file_type"] = "Tabular Data (CSV)"
            return cls._extract_text_file(filepath, meta, code_fence="csv")

        # 4. Source Code and Structured Formats
        elif ext in (
            ".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".css", ".scss",
            ".json", ".xml", ".yaml", ".yml", ".sql", ".sh", ".bat", ".ps1",
            ".c", ".cpp", ".h", ".hpp", ".cs", ".java", ".rs", ".go", ".php"
        ):
            meta["file_type"] = f"Source Code ({ext[1:].upper()})"
            lang = ext[1:]
            if lang in ("yml",):
                lang = "yaml"
            elif lang in ("ps1", "bat"):
                lang = "powershell" if lang == "ps1" else "batch"
            return cls._extract_text_file(filepath, meta, code_fence=lang)

        # 5. Plain Text, Markdown, Logs
        elif ext in (".txt", ".md", ".markdown", ".rst", ".log", ".ini", ".cfg", ".env"):
            meta["file_type"] = "Text Document"
            return cls._extract_text_file(filepath, meta)

        # 6. Fallback generic text attempt
        else:
            meta["file_type"] = "Document"
            return cls._extract_text_file(filepath, meta)

    @classmethod
    def _extract_pdf(cls, filepath: str, meta: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """Extracts text from PDF files using pypdf or PySide6.QtPdf fallback."""
        text_pages = []
        total_pages = 0

        # Try pypdf first
        try:
            import pypdf
            reader = pypdf.PdfReader(filepath)
            total_pages = len(reader.pages)
            meta["page_count"] = total_pages

            for idx, page in enumerate(reader.pages):
                page_text = page.extract_text() or ""
                if page_text.strip():
                    text_pages.append(f"--- Page {idx + 1} ---\n{page_text.strip()}")

        except Exception as e:
            logger.debug(f"pypdf extraction error on {filepath}: {e}, trying QtPdf...")

        # Fallback to PySide6.QtPdf if pypdf didn't get pages
        if not text_pages:
            try:
                from PySide6.QtPdf import QPdfDocument
                doc = QPdfDocument()
                doc.load(filepath)
                total_pages = doc.pageCount()
                meta["page_count"] = total_pages

                for idx in range(total_pages):
                    selection = doc.getAllText(idx)
                    page_text = selection.text() if hasattr(selection, "text") else str(selection)
                    if page_text.strip():
                        text_pages.append(f"--- Page {idx + 1} ---\n{page_text.strip()}")
                doc.close()
            except Exception as e2:
                logger.debug(f"QtPdf extraction error on {filepath}: {e2}")

        if not text_pages:
            return False, f"Could not extract text from PDF '{meta['filename']}'. The PDF may be scanned as pure images or password protected.", meta

        full_text = "\n\n".join(text_pages)
        truncated = False
        if len(full_text) > cls.MAX_CHARS_PER_FILE:
            full_text = full_text[:cls.MAX_CHARS_PER_FILE] + f"\n\n[... Remaining content truncated for performance. Total pages: {total_pages} ...]"
            truncated = True

        words = len(full_text.split())
        meta["word_count"] = words
        meta["truncated"] = truncated

        header = f"📄 **PDF Document:** `{meta['filename']}` ({meta['size_kb']} KB, {total_pages} pages, ~{words} words)\n\n"
        return True, header + full_text, meta

    @classmethod
    def _extract_excel(cls, filepath: str, meta: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """Extracts sheets and tabular rows from Excel files."""
        try:
            import openpyxl
            wb = openpyxl.load_workbook(filepath, read_only=True, data_only=True)
            output_parts = [f"📊 **Excel Workbook:** `{meta['filename']}` ({meta['size_kb']} KB)"]
            meta["sheets"] = wb.sheetnames

            for sheet_name in wb.sheetnames[:5]:  # First 5 sheets
                sheet = wb[sheet_name]
                output_parts.append(f"\n### Sheet: {sheet_name}")
                rows_text = []
                for row_idx, row in enumerate(sheet.iter_rows(values_only=True)):
                    if row_idx >= 100:  # Cap at 100 rows per sheet
                        rows_text.append("... [additional rows truncated]")
                        break
                    row_vals = [str(cell) if cell is not None else "" for cell in row]
                    if any(row_vals):
                        rows_text.append(" | ".join(row_vals))
                output_parts.append("\n".join(rows_text))

            full_text = "\n".join(output_parts)
            return True, full_text, meta
        except Exception as e:
            logger.warning(f"Failed to read Excel file {filepath}: {e}")
            return False, f"Could not read Excel file '{meta['filename']}': {e}", meta

    @classmethod
    def _extract_text_file(
        cls,
        filepath: str,
        meta: Dict[str, Any],
        code_fence: Optional[str] = None
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """Extracts text or source code from files with encoding fallbacks."""
        content = None
        encodings = ["utf-8", "utf-8-sig", "latin1", "cp1252", "ascii"]

        for enc in encodings:
            try:
                with open(filepath, "r", encoding=enc) as f:
                    content = f.read()
                break
            except (UnicodeDecodeError, Exception):
                continue

        if content is None:
            return False, f"Could not decode text file '{meta['filename']}'. Binary or unsupported encoding.", meta

        truncated = False
        if len(content) > cls.MAX_CHARS_PER_FILE:
            content = content[:cls.MAX_CHARS_PER_FILE] + f"\n\n[... Truncated for performance. File size: {meta['size_kb']} KB ...]"
            truncated = True

        lines = len(content.splitlines())
        words = len(content.split())
        meta["line_count"] = lines
        meta["word_count"] = words
        meta["truncated"] = truncated

        header = f"📝 **File:** `{meta['filename']}` ({meta['file_type']}, {meta['size_kb']} KB, {lines} lines, ~{words} words)\n"

        if code_fence:
            formatted = f"{header}\n```{code_fence}\n{content}\n```"
        else:
            formatted = f"{header}\n\n{content}"

        return True, formatted, meta

    @classmethod
    def build_prompt_with_attachments(cls, user_prompt: str, attachment_paths: List[str]) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Parses all attached files and formats an authoritative context block
        for the LLM. If the user sent an empty or minimal prompt, automatically
        prompts the AI to analyze, explain, and summarize the attached document.
        """
        if not attachment_paths:
            return user_prompt, []

        attachment_blocks = []
        parsed_metadata = []

        for fpath in attachment_paths:
            success, extracted_text, meta = cls.extract_file_content(fpath)
            parsed_metadata.append(meta)
            if success:
                block = (
                    f"================================================================================\n"
                    f"ATTACHED DOCUMENT CONTENT: {meta['filename']}\n"
                    f"TYPE: {meta.get('file_type', 'Document')} | SIZE: {meta.get('size_kb', 0)} KB\n"
                    f"================================================================================\n"
                    f"{extracted_text}\n"
                    f"================================================================================\n"
                )
                attachment_blocks.append(block)
            else:
                attachment_blocks.append(f"\n[Attached file notice: {extracted_text}]\n")

        all_attachments_text = "\n\n".join(attachment_blocks)

        clean_user_prompt = user_prompt.strip()
        if not clean_user_prompt:
            clean_user_prompt = (
                "Please analyze, summarize, and explain the key findings, topics, "
                "and structure of the attached document in detail."
            )

        full_prompt = (
            f"{clean_user_prompt}\n\n"
            f"[ATTACHED DOCUMENTS PROVIDED FOR YOU TO READ AND ANALYZE]:\n\n"
            f"{all_attachments_text}\n\n"
            f"Instructions for AI: The user has provided the document content above. "
            f"Use this text to provide thorough, accurate, and comprehensive answers. "
            f"Cite sections, page numbers, or key quotes where appropriate."
        )

        return full_prompt, parsed_metadata
