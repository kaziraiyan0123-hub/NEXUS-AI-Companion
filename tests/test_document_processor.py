"""
Unit Tests for NEXUS Document Processor and Multi-Format File Reading Engine
Tests PDF, source code, tabular data, text extraction, and prompt context enrichment.
"""
import os
import tempfile
import unittest
from core.document_processor import DocumentProcessor

class TestDocumentProcessor(unittest.TestCase):
    """Test suite for DocumentProcessor file extraction and LLM prompt enrichment."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_01_extract_plain_text(self):
        """Verify plain text file extraction and metadata calculation."""
        sample_path = os.path.join(self.temp_dir.name, "notes.txt")
        content = "Line 1: NEXUS AI Companion\nLine 2: High intelligence and document processing.\nLine 3: 100% natural human voice."
        with open(sample_path, "w", encoding="utf-8") as f:
            f.write(content)

        success, text, meta = DocumentProcessor.extract_file_content(sample_path)
        self.assertTrue(success)
        self.assertEqual(meta["file_type"], "Text Document")
        self.assertEqual(meta["line_count"], 3)
        self.assertGreater(meta["word_count"], 10)
        self.assertIn("NEXUS AI Companion", text)
        self.assertIn("100% natural human voice", text)

    def test_02_extract_source_code_with_fence(self):
        """Verify source code files are parsed and wrapped with appropriate markdown code fence."""
        py_path = os.path.join(self.temp_dir.name, "script.py")
        code = "def calculate_pi(n: int) -> float:\n    return 3.14159 * n\n"
        with open(py_path, "w", encoding="utf-8") as f:
            f.write(code)

        success, text, meta = DocumentProcessor.extract_file_content(py_path)
        self.assertTrue(success)
        self.assertEqual(meta["file_type"], "Source Code (PY)")
        self.assertIn("```py", text)
        self.assertIn("def calculate_pi", text)

    def test_03_extract_csv_tabular_data(self):
        """Verify CSV tabular files are parsed and labeled as tabular data."""
        csv_path = os.path.join(self.temp_dir.name, "data.csv")
        csv_content = "id,name,role\n1,Raiyan,Architect\n2,Nexus,Companion\n"
        with open(csv_path, "w", encoding="utf-8") as f:
            f.write(csv_content)

        success, text, meta = DocumentProcessor.extract_file_content(csv_path)
        self.assertTrue(success)
        self.assertEqual(meta["file_type"], "Tabular Data (CSV)")
        self.assertIn("```csv", text)
        self.assertIn("Raiyan,Architect", text)

    def test_04_extract_pdf_with_pypdf(self):
        """Verify PDF extraction using pypdf writer/reader."""
        import pypdf
        pdf_path = os.path.join(self.temp_dir.name, "test_doc.pdf")
        
        # Create a small valid PDF using pypdf
        writer = pypdf.PdfWriter()
        writer.add_blank_page(width=200, height=200)
        with open(pdf_path, "wb") as f:
            writer.write(f)

        success, text, meta = DocumentProcessor.extract_file_content(pdf_path)
        # Even if blank page, should succeed or report page count
        self.assertEqual(meta["file_type"], "PDF Document")
        self.assertIn("page_count", meta)
        self.assertEqual(meta["page_count"], 1)

    def test_05_missing_file_handling(self):
        """Verify graceful error handling when file does not exist."""
        ghost_path = os.path.join(self.temp_dir.name, "nonexistent.pdf")
        success, text, meta = DocumentProcessor.extract_file_content(ghost_path)
        self.assertFalse(success)
        self.assertIn("File not found", text)

    def test_06_build_prompt_with_attachments_user_question(self):
        """Verify prompt enrichment when user asks a specific question about an attachment."""
        doc_path = os.path.join(self.temp_dir.name, "readme.md")
        with open(doc_path, "w", encoding="utf-8") as f:
            f.write("# NEXUS Architecture\nAuthor: Raiyan\nVersion: 2.5\n")

        user_query = "Who is the author of this project?"
        full_prompt, meta_list = DocumentProcessor.build_prompt_with_attachments(user_query, [doc_path])
        
        self.assertEqual(len(meta_list), 1)
        self.assertIn(user_query, full_prompt)
        self.assertIn("ATTACHED DOCUMENT CONTENT: readme.md", full_prompt)
        self.assertIn("Author: Raiyan", full_prompt)
        self.assertIn("Instructions for AI", full_prompt)

    def test_07_build_prompt_empty_auto_summarize(self):
        """Verify that an empty prompt automatically prompts the AI to summarize the document."""
        doc_path = os.path.join(self.temp_dir.name, "report.txt")
        with open(doc_path, "w", encoding="utf-8") as f:
            f.write("Q3 Financial Analysis: Revenue grew by 42% year-over-year.")

        full_prompt, meta_list = DocumentProcessor.build_prompt_with_attachments("", [doc_path])
        self.assertIn("Please analyze, summarize, and explain", full_prompt)
        self.assertIn("Q3 Financial Analysis", full_prompt)

    def test_08_extract_docx(self):
        """Verify Word (.docx) document extraction."""
        import docx
        docx_path = os.path.join(self.temp_dir.name, "sample.docx")
        doc = docx.Document()
        doc.add_heading("NEXUS DOCX Heading", 0)
        doc.add_paragraph("Paragraph 1: Raiyan coded me!")
        doc.save(docx_path)

        success, text, meta = DocumentProcessor.extract_file_content(docx_path)
        self.assertTrue(success)
        self.assertEqual(meta["file_type"], "Word Document")
        self.assertIn("Raiyan coded me!", text)
        self.assertGreaterEqual(meta["paragraph_count"], 2)

    def test_09_extract_pptx(self):
        """Verify PowerPoint (.pptx) presentation extraction."""
        import pptx
        pptx_path = os.path.join(self.temp_dir.name, "sample.pptx")
        prs = pptx.Presentation()
        slide = prs.slides.add_slide(prs.slide_layouts[0])
        slide.shapes.title.text = "Presentation Title"
        slide.placeholders[1].text = "Slide bullet point details"
        prs.save(pptx_path)

        success, text, meta = DocumentProcessor.extract_file_content(pptx_path)
        self.assertTrue(success)
        self.assertEqual(meta["file_type"], "PowerPoint Presentation")
        self.assertIn("Presentation Title", text)
        self.assertIn("Slide bullet point details", text)
        self.assertEqual(meta["slide_count"], 1)

    def test_10_binary_probe_protection(self):
        """Verify binary file with null bytes is recognized safely without unicode corruption."""
        bin_path = os.path.join(self.temp_dir.name, "binary_blob.bin")
        with open(bin_path, "wb") as f:
            f.write(b"NEXUS_HEADER\x00\x01\x02\x03BINARY_PAYLOAD_DATA\x00\xff")

        success, text, meta = DocumentProcessor.extract_file_content(bin_path)
        self.assertTrue(success)
        self.assertEqual(meta["file_type"], "Binary File")
        self.assertIn("Binary File Attached", text)

    def test_11_image_multimodal_vision_extraction(self):
        """Verify image files are recognized as Vision documents without text crash."""
        img_path = os.path.join(self.temp_dir.name, "snapshot.png")
        # Write minimal 1x1 valid PNG
        from PIL import Image
        img = Image.new("RGB", (100, 100), color="blue")
        img.save(img_path)

        success, text, meta = DocumentProcessor.extract_file_content(img_path)
        self.assertTrue(success)
        self.assertEqual(meta["file_type"], "Image (Vision)")
        self.assertIn("dimensions 100x100", text)

    def test_12_fallback_provider_safe_document_notice(self):
        """Verify fallback provider does not echo raw multi-kilobyte documents into markdown."""
        from core.providers.fallback_provider import FallbackProvider
        prov = FallbackProvider()
        huge_doc_prompt = "Summarize this:\n[ATTACHED DOCUMENTS PROVIDED FOR YOU TO READ AND ANALYZE]:\n" + ("Sensitive Data Content " * 500)
        res = prov.generate_response([{"role": "user", "content": huge_doc_prompt}])
        # Must not contain the 500 repetitions of raw content
        self.assertNotIn("Sensitive Data Content " * 50, res)
        self.assertIn("Document Analysis", res)
        self.assertIn("Groq", res)

if __name__ == "__main__":
    unittest.main()
