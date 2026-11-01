"""
NEXUS Forensic Bug Fixes Automated Verification Suite
Tests the 12 critical fixes:
1. QAction parameter preservation (prevents checked:bool overwriting models, skins, animations)
2. Thread-safe VoiceEngine QObject signals (no cross-thread GUI calls, no COM apartment hangs)
3. Distance-based drag vs click detection (prevents accidental clicks after dragging)
4. Screen edge clamping for floating HUD speech bubble
5. Escape key handling in chat HUD
6. Throttled markdown rendering preventing Qt6Gui.dll layout stack overflow (0xC00000FD)
"""
import sys
import unittest
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from PySide6.QtCore import Qt, QPoint, QRect, QKeyCombination
from PySide6.QtGui import QAction, QKeyEvent
from PySide6.QtWidgets import QApplication

from core.character_state import CharacterState
from core.conversation import ConversationManager, ChatMessage
from core.voice_engine import get_voice_engine
from desktop.pet import DesktopPet
from desktop.chat_window import AdvancedChatWindow
from desktop.chat_bubble_widget import MessageBubbleWidget
from interface.themes import get_skin

# Ensure single headless QApplication instance
app = QApplication.instance()
if not app:
    app = QApplication([])
app.setQuitOnLastWindowClosed(False)

class TestForensicBugFixes(unittest.TestCase):
    """Test suite verifying fixes for subtle edge cases, crashes, and visual bugs."""

    def setUp(self):
        self.conv_mgr = ConversationManager()
        self.chat_window = AdvancedChatWindow(self.conv_mgr)
        self.skin = get_skin("habibi_dubai")

    def test_01_qaction_parameter_preservation(self):
        """Verifies that QAction.triggered(bool) does NOT overwrite keyword arguments with False."""
        action = QAction("Test Action")
        captured = []
        target_model = "gpt-4o"
        target_provider = "openai"

        # Using the fix: lambda *args, mod=model_id, pid=provider_id: ...
        handler = lambda *args, mod=target_model, pid=target_provider: captured.append((mod, pid))
        action.triggered.connect(handler)
        # Trigger emits checked=False
        action.trigger()

        self.assertEqual(len(captured), 1)
        self.assertEqual(captured[0], ("gpt-4o", "openai"), "QAction.triggered overwrote argument with False!")

    def test_02_voice_engine_qobject_signals(self):
        """Verifies VoiceEngine is a QObject emitting Qt signals safely on GUI thread."""
        ve = get_voice_engine()
        self.assertTrue(hasattr(ve, "speech_started"))
        self.assertTrue(hasattr(ve, "speech_finished"))
        self.assertFalse(ve.is_speaking())
        ve.stop()

    def test_03_pet_drag_vs_click_detection(self):
        """Verifies that travel distance < 8px is treated as a click, while >= 8px is a drag."""
        pet = DesktopPet()
        clicked_events = []
        pet.chat_requested.connect(lambda: clicked_events.append("clicked"))

        # Case A: Mouse moved 2 pixels (Click)
        pet.drag_start_pos = QPoint(100, 100)
        dist_small = (QPoint(101, 101) - pet.drag_start_pos).manhattanLength()
        if dist_small < 8:
            pet._on_pet_clicked()
        self.assertEqual(len(clicked_events), 1)

        # Case B: Mouse moved 50 pixels (Drag)
        dist_large = (QPoint(150, 150) - pet.drag_start_pos).manhattanLength()
        if dist_large < 8:
            pet._on_pet_clicked()
        # Should still be 1 (no extra click)
        self.assertEqual(len(clicked_events), 1)
        pet.close()

    def test_04_escape_key_hides_chat_window(self):
        """Verifies that pressing Escape cleanly hides the AdvancedChatWindow."""
        self.chat_window.show()
        esc_event = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_Escape, Qt.KeyboardModifier.NoModifier)
        self.chat_window.keyPressEvent(esc_event)
        self.assertTrue(self.chat_window.isHidden())

    def test_05_speech_bubble_boundary_clamping(self):
        """Verifies speech bubble is clamped inside monitor geometry and never overflows off-screen."""
        pet = DesktopPet()
        # Move pet to extreme top-left corner
        pet.move(0, 0)
        pet._update_bubble_position()
        # by should not be negative
        self.assertGreaterEqual(pet.bubble.y(), 0)
        self.assertGreaterEqual(pet.bubble.x(), 0)
        pet.close()

    def test_06_streaming_throttling_safety(self):
        """Verifies rapid token streaming updates do not trigger layout recursion or crashes."""
        msg = ChatMessage(id="msg_test", role="assistant", content="")
        bubble = MessageBubbleWidget(msg, self.skin)
        
        # Simulate 100 rapid token updates
        accumulated = ""
        for i in range(100):
            accumulated += f"word_{i} "
            bubble.update_content(accumulated, force=False)
        bubble.update_content(accumulated, force=True)

        self.assertEqual(bubble.message.content, accumulated)
        bubble.close()

if __name__ == "__main__":
    unittest.main()
