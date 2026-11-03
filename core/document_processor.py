"""
NEXUS Document & File Processing Engine v3.1
Extracts full text, structured data, and code from attached files:
- Word Documents (.docx, .doc) via python-docx with zipfile/XML fallback
- PowerPoint Presentations (.pptx, .ppt) via python-pptx with zipfile/XML fallback
- PDF documents (.pdf) via pypdf with QtPdf fallback
- Excel Spreadsheets (.xlsx, .xlsm, .csv, .tsv) via openpyxl with XML fallback
- Source Code (.py, .js, .ts, .html, .css, .json, .xml, .yaml, .sql, .java, .cpp, .c, etc.)
- Text & Markdown (.txt, .md, .rtf, .log, .ini, .cfg)
Injects rich, contextualized document data into AI prompts so the companion
understands attached files completely and delivers 100% accurate answers.
"""
import os
import re
import zipfile
import logging
import xml.etree.ElementTree as ET
from typing import Tuple, Dict, Any, List, Optional

logger = logging.getLogger("NEXUS.DocumentProcessor")


class DocumentProcessor:
    """Intelligent multi-format document content extractor for NEXUS."""

    MAX_CHARS_PER_FILE = 35000  # ~8,000 to 9,000 words per document (prevents buffer overrun)

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

        # 1. Word Documents (.docx, .doc)
        if ext in (".docx", ".doc"):
            meta["file_type"] = "Word Document"
            return cls._extract_docx(filepath, meta)

        # 2. PowerPoint Presentations (.pptx, .ppt)
        elif ext in (".pptx", ".ppt"):
            meta["file_type"] = "PowerPoint Presentation"
            return cls._extract_pptx(filepath, meta)

        # 3. PDF Documents (.pdf)
        elif ext == ".pdf":
            meta["file_type"] = "PDF Document"
            return cls._extract_pdf(filepath, meta)

        # 4. Excel Spreadsheets (.xlsx, .xlsm)
        elif ext in (".xlsx", ".xlsm"):
            meta["file_type"] = "Excel Spreadsheet"
            return cls._extract_excel(filepath, meta)

        # 5. CSV / TSV tabular data
        elif ext in (".csv", ".tsv"):
            meta["file_type"] = "Tabular Data (CSV)"
            return cls._extract_text_file(filepath, meta, code_fence="csv")

        # 6. Source Code and Structured Formats
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

        # 7. Plain Text, Markdown, Logs, Rich Text
        elif ext in (".txt", ".md", ".markdown", ".rst", ".log", ".ini", ".cfg", ".env", ".rtf"):
            meta["file_type"] = "Text Document"
            return cls._extract_text_file(filepath, meta)

        # 8. Images (Multimodal Vision)
        elif ext in (".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif", ".ico", ".tiff"):
            meta["file_type"] = "Image (Vision)"
            return cls._extract_image_file(filepath, meta)

        # 9. Fallback generic text attempt
        else:
            meta["file_type"] = "Document"
            return cls._extract_text_file(filepath, meta)

    @classmethod
    def _extract_image_file(cls, filepath: str, meta: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """Extracts image metadata and converts to base64 for Multimodal Vision analysis."""
        dim_str = ""
        b64_str = ""
        mime = "image/jpeg"
        try:
            from PIL import Image
            import io
            import base64
            with Image.open(filepath) as img:
                w, h = img.size
                fmt = (img.format or "JPEG").upper()
                meta["dimensions"] = f"{w}x{h}"
                meta["image_format"] = fmt
                dim_str = f", dimensions {w}x{h}, format {fmt}"

                # Downsample if exceedingly large to optimize inference speed and token payload
                copy_img = img.copy()
                copy_img.thumbnail((1280, 1280), Image.Resampling.LANCZOS)
                if copy_img.mode not in ("RGB", "L"):
                    copy_img = copy_img.convert("RGB")
                buf = io.BytesIO()
                copy_img.save(buf, format="JPEG", quality=85)
                b64_str = base64.b64encode(buf.getvalue()).decode("utf-8")
                mime = "image/jpeg"
        except Exception as e:
            logger.debug(f"Pillow image processing error for {filepath}: {e}")
            try:
                import base64
                with open(filepath, "rb") as f:
                    b64_str = base64.b64encode(f.read()).decode("utf-8")
                mime = "image/png" if filepath.lower().endswith(".png") else "image/jpeg"
            except Exception:
                pass

        if b64_str:
            meta["base64"] = b64_str
            meta["mime_type"] = mime
            meta["is_image"] = True

        header = f"🖼️ **Attached Image:** `{meta['filename']}` ({meta['size_kb']} KB{dim_str})\n[Image provided for multimodal visual inspection and analysis]"
        return True, header, meta

    @classmethod
    def _extract_docx(cls, filepath: str, meta: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """Extracts text from Word documents (.docx) using python-docx with zipfile/XML fallback."""
        paragraphs = []

        # Layer 1: python-docx library
        try:
            import docx
            doc = docx.Document(filepath)
            for p in doc.paragraphs:
                txt = p.text.strip()
                if txt:
                    paragraphs.append(txt)
            for table in doc.tables:
                for row in table.rows:
                    row_txt = [c.text.strip() for c in row.cells if c.text.strip()]
                    if row_txt:
                        paragraphs.append(" | ".join(row_txt))
        except Exception as e:
            logger.debug(f"python-docx read failed for {filepath}: {e}, trying zipfile XML fallback...")

        # Layer 2: Standard library zipfile + XML parser (100% dependency-free)
        if not paragraphs and filepath.lower().endswith(".docx"):
            try:
                with zipfile.ZipFile(filepath) as z:
                    if "word/document.xml" in z.namelist():
                        xml_bytes = z.read("word/document.xml")
                        tree = ET.fromstring(xml_bytes)
                        for p_elem in tree.iter():
                            if p_elem.tag.endswith("}p"):
                                texts = [node.text for node in p_elem.iter() if node.tag.endswith("}t") and node.text]
                                if texts:
                                    paragraphs.append("".join(texts).strip())
            except Exception as e2:
                logger.debug(f"zipfile XML extraction failed for {filepath}: {e2}")

        # Layer 3: Legacy .doc string extraction
        if not paragraphs:
            try:
                with open(filepath, "rb") as f:
                    raw_bytes = f.read()
                # Extract ASCII/UTF-8 words (sequences of printable chars >= 4)
                words = re.findall(b"[\x20-\x7E\t\r\n]{4,}", raw_bytes)
                extracted_str = "\n".join([w.decode("latin1", errors="ignore").strip() for w in words[:300]])
                if len(extracted_str.strip()) > 50:
                    paragraphs.append(extracted_str.strip())
            except Exception as e3:
                logger.debug(f"Legacy .doc extraction failed: {e3}")

        if not paragraphs:
            return False, f"Could not extract readable text from Word document '{meta['filename']}'.", meta

        full_text = "\n\n".join(paragraphs)
        truncated = False
        if len(full_text) > cls.MAX_CHARS_PER_FILE:
            full_text = full_text[:cls.MAX_CHARS_PER_FILE] + f"\n\n[... Truncated for performance. Document size: {meta['size_kb']} KB ...]"
            truncated = True

        words_count = len(full_text.split())
        meta["paragraph_count"] = len(paragraphs)
        meta["word_count"] = words_count
        meta["truncated"] = truncated

        header = f"📄 **Word Document:** `{meta['filename']}` ({meta['size_kb']} KB, {len(paragraphs)} paragraphs, ~{words_count} words)\n\n"
        return True, header + full_text, meta

    @classmethod
    def _extract_pptx(cls, filepath: str, meta: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """Extracts slides and notes from PowerPoint presentations (.pptx) with zipfile fallback."""
        slides_text = []

        # Layer 1: python-pptx library
        try:
            import pptx
            prs = pptx.Presentation(filepath)
            for idx, slide in enumerate(prs.slides):
                slide_parts = [f"--- Slide {idx + 1} ---"]
                for shape in slide.shapes:
                    if shape.has_text_frame:
                        for paragraph in shape.text_frame.paragraphs:
                            t = paragraph.text.strip()
                            if t:
                                slide_parts.append(t)
                if len(slide_parts) > 1:
                    slides_text.append("\n".join(slide_parts))
        except Exception as e:
            logger.debug(f"python-pptx read failed for {filepath}: {e}, trying zipfile XML fallback...")

        # Layer 2: Standard library zipfile + XML parser (100% dependency-free)
        if not slides_text and filepath.lower().endswith(".pptx"):
            try:
                with zipfile.ZipFile(filepath) as z:
                    slide_files = [f for f in z.namelist() if f.startswith("ppt/slides/slide") and f.endswith(".xml")]
                    slide_files.sort(key=lambda s: int("".join(filter(str.isdigit, s)) or 0))

                    for idx, sfile in enumerate(slide_files):
                        xml_bytes = z.read(sfile)
                        tree = ET.fromstring(xml_bytes)
                        texts = [node.text for node in tree.iter() if node.tag.endswith("}t") and node.text]
                        if texts:
                            slides_text.append(f"--- Slide {idx + 1} ---\n" + "\n".join(texts))
            except Exception as e2:
                logger.debug(f"zipfile PPTX extraction failed for {filepath}: {e2}")

        # Layer 3: Legacy .ppt string extraction
        if not slides_text:
            try:
                with open(filepath, "rb") as f:
                    raw_bytes = f.read()
                words = re.findall(b"[\x20-\x7E\t\r\n]{4,}", raw_bytes)
                extracted_str = "\n".join([w.decode("latin1", errors="ignore").strip() for w in words[:400]])
                if len(extracted_str.strip()) > 50:
                    slides_text.append(extracted_str.strip())
            except Exception as e3:
                logger.debug(f"Legacy .ppt extraction failed: {e3}")

        if not slides_text:
            return False, f"Could not extract readable text from PowerPoint presentation '{meta['filename']}'.", meta

        full_text = "\n\n".join(slides_text)
        truncated = False
        if len(full_text) > cls.MAX_CHARS_PER_FILE:
            full_text = full_text[:cls.MAX_CHARS_PER_FILE] + f"\n\n[... Truncated for performance. Presentation size: {meta['size_kb']} KB ...]"
            truncated = True

        words_count = len(full_text.split())
        meta["slide_count"] = len(slides_text)
        meta["word_count"] = words_count
        meta["truncated"] = truncated

        header = f"📊 **PowerPoint Presentation:** `{meta['filename']}` ({meta['size_kb']} KB, {len(slides_text)} slides, ~{words_count} words)\n\n"
        return True, header + full_text, meta

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

        header = f"📑 **PDF Document:** `{meta['filename']}` ({meta['size_kb']} KB, {total_pages} pages, ~{words} words)\n\n"
        return True, header + full_text, meta

    @classmethod
    def _extract_excel(cls, filepath: str, meta: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """Extracts sheets and tabular rows from Excel files with XML fallback."""
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
            logger.debug(f"openpyxl failed for {filepath}: {e}, trying zipfile XML fallback...")

        # Fallback to zipfile XML for .xlsx
        try:
            with zipfile.ZipFile(filepath) as z:
                shared_strings = []
                if "xl/sharedStrings.xml" in z.namelist():
                    tree = ET.fromstring(z.read("xl/sharedStrings.xml"))
                    for si in tree.iter():
                        if si.tag.endswith("}t") and si.text:
                            shared_strings.append(si.text.strip())

                output_parts = [f"📊 **Excel Workbook:** `{meta['filename']}` ({meta['size_kb']} KB)"]
                sheet_files = [f for f in z.namelist() if f.startswith("xl/worksheets/sheet") and f.endswith(".xml")]
                for idx, sfile in enumerate(sheet_files[:5]):
                    output_parts.append(f"\n### Sheet {idx + 1}")
                    s_tree = ET.fromstring(z.read(sfile))
                    row_texts = []
                    for row in s_tree.iter():
                        if row.tag.endswith("}row"):
                            cell_vals = []
                            for c in row.iter():
                                if c.tag.endswith("}v") and c.text:
                                    val = c.text
                                    if val.isdigit() and int(val) < len(shared_strings):
                                        cell_vals.append(shared_strings[int(val)])
                                    else:
                                        cell_vals.append(val)
                            if cell_vals:
                                row_texts.append(" | ".join(cell_vals))
                    output_parts.append("\n".join(row_texts[:80]))

                full_text = "\n".join(output_parts)
                return True, full_text, meta
        except Exception as e2:
            logger.warning(f"Failed to read Excel file {filepath}: {e2}")
            return False, f"Could not read Excel file '{meta['filename']}': {e2}", meta

    @classmethod
    def _extract_text_file(
        cls,
        filepath: str,
        meta: Dict[str, Any],
        code_fence: Optional[str] = None
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """Extracts text or source code from files with encoding fallbacks and binary protection."""
        # Pre-check for binary files using null-byte detection
        try:
            with open(filepath, "rb") as bf:
                chunk = bf.read(2048)
                if b"\x00" in chunk:
                    # File contains null bytes -> Binary file
                    meta["file_type"] = "Binary File"
                    printable = re.findall(rb"[a-zA-Z0-9_\-\.\:\/ ]{4,}", chunk)
                    strings_preview = " ".join(s.decode("ascii", errors="ignore") for s in printable[:25])
                    content = (
                        f"📦 **Binary File Attached:** `{meta['filename']}` ({meta['size_kb']} KB)\n"
                        f"[File contains non-text binary data. Extracted string identifiers: {strings_preview}...]"
                    )
                    return True, content, meta
        except Exception as e:
            logger.debug(f"Binary probe error on {filepath}: {e}")

        content = None
        encodings = ["utf-8", "utf-8-sig", "cp1252", "latin1"]

        for enc in encodings:
            try:
                with open(filepath, "r", encoding=enc, errors="replace" if enc == "latin1" else "strict") as f:
                    content = f.read()
                break
            except (UnicodeDecodeError, Exception):
                continue

        if content is None:
            try:
                with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
            except Exception:
                return False, f"Could not decode text file '{meta['filename']}'. Unsupported format.", meta

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
