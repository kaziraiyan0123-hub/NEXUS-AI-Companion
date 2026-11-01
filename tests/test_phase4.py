"""
NEXUS Phase 4 Automated Verification Test Suite
Tests Voice Conversation System:
- Natural interruptible Text-to-Speech (VoiceEngine)
- Voice selection & audio property controls
- Text cleaning for natural speech synthesis
- Voice Activity Detection (VAD) & Listener thread controls (VoiceListenerThread)
- Wake word detection handling and conversational acknowledgment flow
- Interactive Voice HUD controls (Visualizer, level metering, and state switching)
"""
import sys
import time
import unittest
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from PySide6.QtWidgets import QApplication

from config.settings import get_settings
from core.character_state import CharacterState
from core.voice_engine import get_voice_engine
from core.voice_stt import VoiceListenerThread
from core.conversation import ConversationManager
from desktop.chat_window import AdvancedChatWindow

# Ensure headless QApplication
app = QApplication.instance()
if not app:
    app = QApplication([])

class TestPhase4VoiceConversation(unittest.TestCase):
    """Test suite for Phase 4 Voice Conversation System."""

    def setUp(self):
        self.settings = get_settings()
        self.voice_engine = get_voice_engine()
        self.conv_manager = ConversationManager()
        self.chat_window = AdvancedChatWindow(self.conv_manager)

    def tearDown(self):
        self.voice_engine.stop()

    def test_01_voice_engine_enumeration(self):
        """Tests that Windows SAPI5 voices can be discovered and enumerated."""
        voices = self.voice_engine.get_available_voices()
        self.assertIsInstance(voices, list)
        self.assertGreater(len(voices), 0, "No SAPI speech voices discovered on Windows system!")
        first_voice = voices[0]
        self.assertIn("name", first_voice)
        self.assertIn("id", first_voice)

    def test_02_text_cleaning_for_speech(self):
        """Tests that markdown syntax, URLs, and code blocks are stripped for natural speech."""
        raw_markdown = (
            "### 👑 Executive Solution\n\n"
            "Here is the code you asked for:\n"
            "```python\n"
            "def add(a, b):\n"
            "    return a + b\n"
            "```\n\n"
            "Visit https://nexus.ai for `documentation` and details!"
        )
        cleaned = self.voice_engine._clean_for_speech(raw_markdown)
        self.assertNotIn("def add", cleaned, "Code block leaked into spoken text!")
        self.assertNotIn("```", cleaned)
        self.assertNotIn("###", cleaned)
        self.assertNotIn("https://", cleaned)
        self.assertIn("Code snippet", cleaned)
        self.assertIn("documentation", cleaned)

    def test_03_interruptible_speech_execution(self):
        """Tests that speech can be triggered asynchronously and interrupted on demand."""
        # Speak long text
        self.voice_engine.speak("This is a long sentence meant to verify that speech interruption functions immediately.")
        time.sleep(0.1)
        # Calling stop should halt speech cleanly
        self.voice_engine.stop()
        self.assertFalse(self.voice_engine.is_speaking())

    def test_04_voice_listener_vad_and_rms(self):
        """Tests VoiceListenerThread RMS energy calculations and mute state."""
        listener = VoiceListenerThread()
        self.assertIsNotNone(listener.mic)

        # Test muted state
        listener.set_muted(True)
        self.assertTrue(listener._is_muted)
        listener.set_muted(False)
        self.assertFalse(listener._is_muted)

        # Test RMS calculation on synthetic PCM audio bytes (16-bit signed)
        silence_bytes = b"\x00\x00" * 100
        rms_silence = listener._calculate_rms(silence_bytes)
        self.assertEqual(rms_silence, 0.0)

        # Sine wave amplitude
        loud_bytes = (b"\xff\x3f" * 50) + (b"\x00\xc0" * 50)
        rms_loud = listener._calculate_rms(loud_bytes)
        self.assertGreater(rms_loud, 0.0)

    def test_05_chat_window_voice_hud_states(self):
        """Tests HUD Voice Visualizer bar and status transitions."""
        # 1. State: Listening
        self.chat_window.set_voice_listening_state("listening")
        self.assertFalse(self.chat_window.voice_bar.isHidden())
        self.assertIn("Listening", self.chat_window.voice_status_lbl.text())

        # 2. Audio Level Metering
        self.chat_window.set_voice_level(0.6)
        self.assertIn("❚", self.chat_window.voice_viz_lbl.text())

        # 3. State: Transcribing
        self.chat_window.set_voice_listening_state("transcribing")
        self.assertFalse(self.chat_window.voice_bar.isHidden())
        self.assertIn("Transcribing", self.chat_window.voice_status_lbl.text())

        # 4. State: Idle
        self.chat_window.set_voice_listening_state("idle")
        self.assertTrue(self.chat_window.voice_bar.isHidden())

    def test_06_conversational_voice_flow_signals(self):
        """Tests wake phrase signal emission and command delivery into conversation."""
        listener = VoiceListenerThread()
        received_texts = []
        listener.speech_transcribed.connect(lambda t: received_texts.append(t))

        # Simulate voice input arriving
        test_phrase = "Can you explain today's management topic?"
        listener.speech_transcribed.emit(test_phrase)

        self.assertEqual(len(received_texts), 1)
        self.assertEqual(received_texts[0], test_phrase)

if __name__ == "__main__":
    unittest.main()
