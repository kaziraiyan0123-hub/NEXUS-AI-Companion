"""
Unit Tests for NEXUS Phase 7: Polish, Live AI Routing, Companion Power Toggle & VIP Interactions
"""
import os
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).parent.parent))

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from config.settings import get_settings
from security.secure_storage import get_secure_storage
from core.ai_manager import get_ai_manager
from core.providers.groq_provider import GroqProvider
from core.providers.gemini_provider import GeminiProvider
from core.assistant import NexusAssistant
from core.character_state import CharacterState

# Ensure QApplication singleton for headless test
app = QApplication.instance()
if app is None:
    app = QApplication([])

class TestPhase7PolishAndVIP(unittest.TestCase):

    def setUp(self):
        self.settings = get_settings()
        self.ai_manager = get_ai_manager()
        self.secure_storage = get_secure_storage()

    def test_groq_provider_routing_and_models(self):
        """Verifies Groq connects to api.groq.com and has active free models."""
        prov = GroqProvider()
        self.assertEqual(prov.name, "groq")
        self.assertEqual(prov.base_url, "https://api.groq.com/openai/v1")
        self.assertIn("qwen/qwen3.8-27b", prov.available_models)
        self.assertIn("allam-2-7b", prov.available_models)

    def test_gemini_active_models(self):
        """Verifies Gemini provider has active frontier 4-argon and 3.8-flash models."""
        prov = GeminiProvider()
        self.assertEqual(prov.name, "gemini")
        self.assertIn("gemini-4-argon", prov.available_models)
        self.assertIn("gemini-3.8-flash", prov.available_models)

    def test_ai_manager_smart_routing_with_keys(self):
        """Verifies AI manager auto-selects working provider if selected has no key."""
        # User has Groq and Gemini keys in vault
        prov = self.ai_manager.get_provider("claude")
        # Since claude has no key, smart routing must auto-select groq or gemini!
        self.assertIn(prov.name, ("groq", "gemini", "openrouter"))

    def test_desktop_shortcut_exists(self):
        """Verifies NEXUS.lnk desktop shortcut exists on Windows Desktop."""
        desktop = os.path.expanduser(r"~\Desktop")
        shortcut = os.path.join(desktop, "NEXUS.lnk")
        self.assertTrue(os.path.exists(shortcut), f"Desktop shortcut missing at {shortcut}")

    def test_companion_power_toggle(self):
        """Verifies Enter / Remove desktop companion toggle."""
        assistant = NexusAssistant(app)
        assistant.start()
        self.assertTrue(assistant.is_active)
        self.assertTrue(assistant.pet.isVisible())

        # Turn OFF (Exit desktop)
        assistant.turn_off()
        self.assertFalse(assistant.is_active)
        self.assertFalse(assistant.pet.isVisible())

        # Turn ON (Enter desktop)
        assistant.turn_on()
        self.assertTrue(assistant.is_active)
        self.assertTrue(assistant.pet.isVisible())

        # Toggle power
        assistant.toggle_power()
        self.assertFalse(assistant.is_active)
        assistant.toggle_power()
        self.assertTrue(assistant.is_active)
        assistant.quit_application()

    def test_vip_interactions(self):
        """Verifies pet affection, Karak Chai, and Gold Coin interactions."""
        assistant = NexusAssistant(app)
        # Petting
        assistant.pet_the_pet()
        self.assertEqual(assistant.pet.state, CharacterState.HAPPY)

        # Karak Chai
        assistant.feed_karak_chai()
        self.assertEqual(assistant.pet.state, CharacterState.CELEBRATING)

        # Gold Coin
        assistant.toss_gold_coin()
        self.assertEqual(assistant.pet.state, CharacterState.CELEBRATING)
        assistant.quit_application()

    def test_dock_widget_and_vision_tool(self):
        """Verifies Floating Dock Capsule, Vision Screen Intelligence, and Intent Routing."""
        assistant = NexusAssistant(app)
        self.assertIsNotNone(assistant.dock)
        self.assertTrue(assistant.dock.pill.isVisible() or assistant.dock.isVisible() or assistant.dock.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground))

        # Check screen vision tool registered
        tool = assistant.tool_registry.get("analyze_screen")
        self.assertIsNotNone(tool)
        self.assertEqual(tool.name, "analyze_screen")

        # Intent parsing
        intent = assistant.tool_registry.parse_intent("can you look at my screen and help me?")
        self.assertIsNotNone(intent)
        self.assertEqual(intent[0], "analyze_screen")

        # Proactive companion timer check
        self.assertIsNotNone(assistant.proactive_timer)
        self.assertTrue(assistant.proactive_timer.isActive())
        # Simulate proactive nudge tick
        assistant._on_proactive_companion_tick()
        self.assertEqual(assistant.pet.state, CharacterState.HAPPY)

        assistant.quit_application()

    def test_human_natural_speech_engine(self):
        """Verifies natural spoken dialogue conversion and Neural TTS configuration."""
        from core.voice_engine import get_voice_engine
        engine = get_voice_engine()
        
        # Test clean spoken conversion
        messy_input = "### 👑 Dubai Tip\nEarn $500 & make +100% ROI! Visit https://nexus.ai\n```python\nprint(1)\n```"
        cleaned = engine._clean_for_speech(messy_input)
        self.assertNotIn("###", cleaned)
        self.assertNotIn("https://", cleaned)
        self.assertNotIn("print(1)", cleaned)
        self.assertIn("dollars", cleaned)
        self.assertIn("and", cleaned)
        self.assertIn("plus", cleaned)
        self.assertIn("percent", cleaned)

if __name__ == "__main__":
    unittest.main()
