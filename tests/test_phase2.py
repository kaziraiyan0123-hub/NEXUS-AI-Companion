"""
NEXUS Phase 2 Comprehensive Test Suite
Tests ConversationManager, Markdown/Pygments formatting, AdvancedChatWindow, and Habibi Dubai.
"""
import sys
import unittest
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PySide6.QtCore import Qt, QRect
from PySide6.QtWidgets import QApplication
from core.conversation import ConversationManager, ChatMessage, Conversation
from interface.themes import get_skin, SKINS
from desktop.markdown_formatter import markdown_to_html, format_code_block
from desktop.chat_window import AdvancedChatWindow

# Ensure QApplication exists
app = QApplication.instance()
if not app:
    app = QApplication([])

class TestNexusPhase2(unittest.TestCase):

    def setUp(self):
        self.conv_manager = ConversationManager()
        self.skin = get_skin("habibi_dubai")

    def test_01_conversation_manager(self):
        """Test creating, listing, searching conversations and messages."""
        conv = self.conv_manager.get_active()
        self.assertIsNotNone(conv)

        msg1 = conv.add_message("user", "Marhaba NEXUS, can you help with Python?")
        self.assertEqual(msg1.role, "user")
        self.assertIn("Python", msg1.content)

        msg2 = conv.add_message("assistant", "Yes Habibi, I can assist with Python programming.")
        self.assertEqual(len(conv.messages), 2)

        # Test search
        results = self.conv_manager.search_messages("python")
        self.assertGreaterEqual(len(results), 2)

        # Test new conversation
        conv2 = self.conv_manager.new_conversation("Dubai Architecture")
        self.assertEqual(self.conv_manager.active_id, conv2.id)
        self.assertEqual(len(self.conv_manager.list_conversations()), 2)

    def test_02_habibi_skin_attributes(self):
        """Verify the premier Habibi of Dubai skin attributes and colors."""
        self.assertIn("habibi_dubai", SKINS)
        h_skin = SKINS["habibi_dubai"]
        self.assertEqual(h_skin.name, "habibi_dubai")
        self.assertIn("Habibi", h_skin.display_name)
        # Gold colors
        self.assertEqual(h_skin.primary.red(), 255)
        self.assertEqual(h_skin.primary.green(), 215)
        self.assertEqual(h_skin.primary.blue(), 0)

    def test_03_markdown_and_syntax_highlighting(self):
        """Test Markdown conversion to styled HTML with Pygments code blocks."""
        sample_md = (
            "# Main Heading\n\n"
            "This is **bold** text and `inline_code`.\n\n"
            "* Item 1\n* Item 2\n\n"
            "```python\n"
            "def add(a: int, b: int) -> int:\n"
            "    return a + b\n"
            "```\n"
        )
        html_out = markdown_to_html(sample_md, self.skin)
        self.assertIn("<h1>Main Heading</h1>", html_out)
        self.assertIn("<strong>bold</strong>", html_out)
        self.assertIn("code-card", html_out)
        self.assertIn("PYTHON", html_out)
        self.assertIn("add", html_out)

    def test_04_advanced_chat_window_creation(self):
        """Test AdvancedChatWindow UI setup, drawer, personas, and docking."""
        chat_win = AdvancedChatWindow(self.conv_manager)
        self.assertTrue(chat_win.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground))
        self.assertGreaterEqual(chat_win.width(), 420)
        self.assertGreaterEqual(chat_win.height(), 520)

        # Verify components exist
        self.assertIsNotNone(chat_win.input_edit)
        self.assertIsNotNone(chat_win.send_btn)
        self.assertIsNotNone(chat_win.scroll_area)
        self.assertIsNotNone(chat_win.drawer)

        # Test drawer toggle
        self.assertTrue(chat_win.drawer.isHidden())
        chat_win._toggle_drawer()
        self.assertFalse(chat_win.drawer.isHidden())
        chat_win._toggle_drawer()
        self.assertTrue(chat_win.drawer.isHidden())

        # Test docking math
        pet_rect = QRect(1200, 600, 200, 200)
        chat_win.dock_near_pet(pet_rect)
        self.assertLess(chat_win.x(), pet_rect.left())
        self.assertGreater(chat_win.y(), 0)

        chat_win.close()

    def test_05_message_generation_lifecycle(self):
        """Test sending message, thinking indicator, and streaming response."""
        chat_win = AdvancedChatWindow(self.conv_manager)

        # Set generating state
        chat_win.set_generating(True)
        self.assertTrue(chat_win.is_generating)
        self.assertIsNotNone(chat_win.thinking_widget)
        self.assertEqual(chat_win.send_btn.text(), "⏹")

        # Post response without stream for instant verification
        chat_win.post_assistant_response("Here is the generated answer.", stream=False)
        self.assertFalse(chat_win.is_generating)
        self.assertIsNone(chat_win.thinking_widget)
        self.assertEqual(chat_win.send_btn.text(), "➤")

        # Active conversation should contain the assistant message
        active_conv = self.conv_manager.get_active()
        self.assertEqual(active_conv.messages[-1].content, "Here is the generated answer.")

        chat_win.close()

    def test_06_attachments_handling(self):
        """Test attaching and removing files."""
        chat_win = AdvancedChatWindow(self.conv_manager)

        chat_win.attached_files.append("C:/docs/dubai_brief.pdf")
        chat_win._render_attached_chips()
        self.assertFalse(chat_win.att_container.isHidden())
        self.assertIn("C:/docs/dubai_brief.pdf", chat_win.attached_files)

        chat_win._remove_attachment("C:/docs/dubai_brief.pdf")
        self.assertTrue(chat_win.att_container.isHidden())
        self.assertEqual(len(chat_win.attached_files), 0)

        chat_win.close()

if __name__ == "__main__":
    unittest.main()
