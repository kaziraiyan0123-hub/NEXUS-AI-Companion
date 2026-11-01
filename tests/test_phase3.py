"""
NEXUS Phase 3 Automated Verification Test Suite
Tests Modular AI Brain:
- SecureStorage (Windows DPAPI encryption)
- AI Provider interfaces (Gemini, OpenAI, Claude, Grok, Local LLM, Fallback)
- Persona system prompts & AIManager routing
- Real-time token streaming and fallback resilience
- SettingsDialog initialization and provider switching
"""
import sys
import os
import unittest
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from PySide6.QtWidgets import QApplication

from config.settings import SettingsManager
from security.secure_storage import SecureStorage
from core.providers.base_provider import BaseAIProvider
from core.providers.gemini_provider import GeminiProvider
from core.providers.openai_provider import OpenAIProvider
from core.providers.claude_provider import ClaudeProvider
from core.providers.grok_provider import GrokProvider
from core.providers.local_llm_provider import LocalLLMProvider
from core.providers.fallback_provider import FallbackProvider
from core.ai_manager import AIManager, PERSONA_SYSTEM_PROMPTS
from interface.settings_dialog import SettingsDialog

# Ensure single headless QApplication instance
app = QApplication.instance()
if not app:
    app = QApplication([])

class TestPhase3ModularAIBrain(unittest.TestCase):
    """Test suite for Phase 3 Modular AI Brain and Settings."""

    def setUp(self):
        self.tmp_dir = ROOT_DIR / "tests" / "tmp_test_phase3"
        self.tmp_dir.mkdir(parents=True, exist_ok=True)
        self.storage = SecureStorage(storage_dir=str(self.tmp_dir))
        self.settings = SettingsManager(config_dir=str(self.tmp_dir))
        self.ai_manager = AIManager()
        self.ai_manager.secure_storage = self.storage
        self.ai_manager.settings = self.settings

    def tearDown(self):
        # Cleanup vault and settings files
        try:
            for f in self.tmp_dir.glob("*"):
                if f.is_file():
                    f.unlink()
            self.tmp_dir.rmdir()
        except Exception:
            pass

    def test_01_secure_storage_dpapi(self):
        """Tests that API keys are stored encrypted via DPAPI and never plaintext on disk."""
        test_key = "AIzaSyTestKey_1234567890_Dubai"
        self.storage.store_api_key("gemini", test_key)

        # 1. Retrieve through decrypted accessor
        retrieved = self.storage.get_api_key("gemini")
        self.assertEqual(retrieved, test_key)
        self.assertTrue(self.storage.has_api_key("gemini"))

        # 2. Verify file on disk does NOT contain plaintext key
        vault_path = self.tmp_dir / "credentials.vault"
        self.assertTrue(vault_path.exists())
        with open(vault_path, "r", encoding="utf-8") as f:
            raw_content = f.read()
            self.assertNotIn(test_key, raw_content, "Plaintext API key leaked in credentials.vault!")

        # 3. Delete key
        self.storage.delete_api_key("gemini")
        self.assertFalse(self.storage.has_api_key("gemini"))
        self.assertIsNone(self.storage.get_api_key("gemini"))

    def test_02_provider_interface_contracts(self):
        """Tests that all providers adhere to BaseAIProvider contract."""
        providers = [
            GeminiProvider(),
            OpenAIProvider(),
            ClaudeProvider(),
            GrokProvider(),
            LocalLLMProvider(),
            FallbackProvider()
        ]
        for prov in providers:
            self.assertIsInstance(prov, BaseAIProvider)
            self.assertTrue(bool(prov.name))
            self.assertTrue(bool(prov.display_name))
            self.assertTrue(bool(prov.default_model))
            self.assertIsInstance(prov.available_models, list)
            self.assertGreater(len(prov.available_models), 0)

    def test_03_connection_diagnostics_without_keys(self):
        """Tests connection verification gracefully handles missing credentials."""
        gemini = GeminiProvider(api_key=None)
        ok, msg = gemini.test_connection()
        self.assertFalse(ok)
        self.assertIn("not configured", msg.lower())

        openai = OpenAIProvider(api_key=None)
        ok, msg = openai.test_connection()
        self.assertFalse(ok)
        self.assertIn("not configured", msg.lower())

        claude = ClaudeProvider(api_key=None)
        ok, msg = claude.test_connection()
        self.assertFalse(ok)
        self.assertIn("not configured", msg.lower())

    def test_04_persona_system_prompts(self):
        """Tests that all 5 personas have rich, distinct system prompts."""
        personas = ["habibi_dubai", "architect", "academic", "productivity", "security"]
        for p in personas:
            self.assertIn(p, PERSONA_SYSTEM_PROMPTS)
            prompt = self.ai_manager.get_system_prompt(p)
            self.assertGreater(len(prompt), 50)
            if p == "habibi_dubai":
                self.assertIn("Dubai", prompt)
            elif p == "architect":
                self.assertIn("Architect", prompt)

    def test_05_ai_manager_fallback_streaming(self):
        """Tests streaming token generation with fallback protection across capabilities."""
        # 1. Programming capability
        messages = [{"role": "user", "content": "Write a python function for data validation."}]
        tokens = list(self.ai_manager.stream_chat(messages, persona="habibi_dubai"))
        full_text = "".join(tokens)
        self.assertGreater(len(tokens), 5)
        self.assertIn("```python", full_text)

        # 2. Educational capability
        messages2 = [{"role": "user", "content": "Explain university calculus theorems."}]
        full_text2 = self.ai_manager.generate_chat(messages2, persona="academic")
        self.assertIn("Conceptual Overview", full_text2)

        # 3. Productivity capability
        messages3 = [{"role": "user", "content": "Draft an email regarding project timeline."}]
        full_text3 = self.ai_manager.generate_chat(messages3, persona="productivity")
        self.assertIn("Subject", full_text3)

    def test_06_settings_dialog_gui_lifecycle(self):
        """Tests SettingsDialog UI initialization, tab widgets, and value binding."""
        dialog = SettingsDialog()
        self.assertIsNotNone(dialog)
        self.assertEqual(dialog.tab_widget.count(), 4)

        # Provider switching updates model combo
        dialog.provider_combo.setCurrentIndex(dialog.provider_combo.findData("openai"))
        self.assertIn("gpt-4o", [dialog.model_combo.itemText(i) for i in range(dialog.model_combo.count())])

        dialog.provider_combo.setCurrentIndex(dialog.provider_combo.findData("claude"))
        self.assertIn("claude-3-7-sonnet-20250219", [dialog.model_combo.itemText(i) for i in range(dialog.model_combo.count())])

        dialog.provider_combo.setCurrentIndex(dialog.provider_combo.findData("local"))
        self.assertFalse(dialog.url_input.isHidden())

        # Test temperature and token sliders
        dialog.temp_slider.setValue(85)
        self.assertEqual(dialog.temp_val_lbl.text(), "0.85")

        dialog.tokens_slider.setValue(2048)
        self.assertEqual(dialog.tokens_val_lbl.text(), "2048")

        dialog.close()

if __name__ == "__main__":
    unittest.main()
