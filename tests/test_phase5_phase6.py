"""
Unit Tests for NEXUS Phase 5 (Windows Desktop Control) & Phase 6 (Absolute Permission System)
and Phase 4.5 (Neural Natural Voice & Free Models).
"""
import os
import sys
import tempfile
import unittest

# Ensure project root is on path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from PySide6.QtWidgets import QApplication
app = QApplication.instance() or QApplication([])

from security.permission_manager import (
    PermissionManager, get_permission_manager,
    PermissionLevel, ActionRisk, ActionRequest
)
from core.desktop_tools import (
    ToolRegistry, get_tool_registry,
    FolderOrganizerTool, SystemStatusTool, ClipboardTool
)
from core.providers.groq_provider import GroqProvider
from core.providers.openrouter_provider import OpenRouterProvider
from core.providers.fallback_provider import FallbackProvider
from core.voice_engine import get_voice_engine
from desktop.pet import DesktopPet


class TestPermissionSystem(unittest.TestCase):
    """Verifies strict safety rules of the NEXUS Absolute Permission System."""

    def setUp(self):
        self.pm = get_permission_manager()
        self.pm.reset_emergency_stop()

    def test_permission_levels(self):
        req_low = ActionRequest("t1", "tool", "Low Action", "desc", ActionRisk.LOW, [], {})
        req_mod = ActionRequest("t2", "tool", "Mod Action", "desc", ActionRisk.MODERATE, [], {})
        req_dest = ActionRequest("t3", "tool", "Dest Action", "desc", ActionRisk.DESTRUCTIVE, [], {})

        # Level 1: Info Only (Blocks all actions)
        self.pm.settings.set("permission_level", 1)
        self.assertFalse(self.pm.can_execute(req_low))
        self.assertFalse(self.pm.can_execute(req_dest))

        # Level 2: Ask Before Action (Default - every action needs approval)
        self.pm.settings.set("permission_level", 2)
        self.assertTrue(self.pm.can_execute(req_low))
        self.assertTrue(self.pm.should_request_approval(req_low))
        self.assertTrue(self.pm.should_request_approval(req_mod))
        self.assertTrue(self.pm.should_request_approval(req_dest))

        # Level 3: Restricted (Low risk pre-approved; Moderate & Destructive require approval)
        self.pm.settings.set("permission_level", 3)
        self.assertFalse(self.pm.should_request_approval(req_low))
        self.assertTrue(self.pm.should_request_approval(req_mod))
        self.assertTrue(self.pm.should_request_approval(req_dest))

        # Reset to safe default
        self.pm.settings.set("permission_level", 2)

    def test_emergency_stop(self):
        self.pm.reset_emergency_stop()
        self.assertFalse(self.pm.emergency_stop_active)

        self.pm.trigger_emergency_stop()
        self.assertTrue(self.pm.emergency_stop_active)

        req = ActionRequest("t4", "tool", "Action", "desc", ActionRisk.LOW, [], {})
        self.assertFalse(self.pm.can_execute(req))

        self.pm.reset_emergency_stop()
        self.assertFalse(self.pm.emergency_stop_active)

    def test_audit_logging(self):
        self.pm.log_audit("TEST_ACT_1", "test_tool", "Test Action", "low", "APPROVED", "Unit test audit write")
        entries = self.pm.get_recent_audit_entries(limit=10)
        self.assertTrue(len(entries) > 0)
        last = entries[-1]
        self.assertEqual(last["action_id"], "TEST_ACT_1")
        self.assertEqual(last["status"], "APPROVED")


class TestDesktopTools(unittest.TestCase):
    """Verifies tool parsing, safety validation, and execution."""

    def setUp(self):
        self.registry = get_tool_registry()

    def test_intent_parsing(self):
        # 1. Clean downloads
        t1 = self.registry.parse_intent("Nexus clean my downloads folder please")
        self.assertIsNotNone(t1)
        self.assertEqual(t1[0], "organize_folder")
        self.assertEqual(t1[1]["target_folder"], "Downloads")

        # 2. Open Notepad
        t2 = self.registry.parse_intent("open notepad")
        self.assertIsNotNone(t2)
        self.assertEqual(t2[0], "launch_application")
        self.assertEqual(t2[1]["app_name"], "notepad")

        # 3. Screenshot
        t3 = self.registry.parse_intent("take a screenshot")
        self.assertIsNotNone(t3)
        self.assertEqual(t3[0], "take_screenshot")

        # 4. System status
        t4 = self.registry.parse_intent("what is my system status and battery?")
        self.assertIsNotNone(t4)
        self.assertEqual(t4[0], "system_status")

        # 5. Mute
        t5 = self.registry.parse_intent("mute volume")
        self.assertIsNotNone(t5)
        self.assertEqual(t5[0], "control_media")
        self.assertEqual(t5[1]["action"], "mute")

    def test_folder_organizer_categorization(self):
        organizer = FolderOrganizerTool()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create sample files
            f_doc = os.path.join(tmpdir, "report.pdf")
            f_img = os.path.join(tmpdir, "photo.png")
            f_zip = os.path.join(tmpdir, "setup.zip")
            f_txt = os.path.join(tmpdir, "notes.txt")
            f_code = os.path.join(tmpdir, "main.py")

            for p in (f_doc, f_img, f_zip, f_txt, f_code):
                with open(p, "w") as f:
                    f.write("content")

            to_move, folders_needed, untouched = organizer._scan_folder(tmpdir)
            self.assertEqual(len(to_move), 5)
            self.assertIn("Documents", folders_needed)
            self.assertIn("Images", folders_needed)
            self.assertIn("Installers", folders_needed)
            self.assertIn("Code", folders_needed)

            # Test safe execution
            res = organizer.execute({"target_path": tmpdir})
            self.assertTrue(res.success)
            self.assertEqual(res.data["moved_count"], 5)
            self.assertTrue(os.path.exists(os.path.join(tmpdir, "Documents", "report.pdf")))
            self.assertTrue(os.path.exists(os.path.join(tmpdir, "Images", "photo.png")))
            self.assertTrue(os.path.exists(os.path.join(tmpdir, "Installers", "setup.zip")))

    def test_system_status_tool(self):
        tool = SystemStatusTool()
        res = tool.execute({})
        self.assertTrue(res.success)
        self.assertIn("CPU Load", res.message)
        self.assertIn("cpu", res.data)
        self.assertIn("memory_pct", res.data)

    def test_clipboard_tool(self):
        tool = ClipboardTool()
        res_w = tool.execute({"operation": "copy", "text": "NEXUS_TEST_TOKEN_12345"})
        self.assertTrue(res_w.success)

        res_r = tool.execute({"operation": "read"})
        self.assertTrue(res_r.success)
        self.assertEqual(res_r.data.get("text"), "NEXUS_TEST_TOKEN_12345")


class TestNeuralVoiceAndFreeModels(unittest.TestCase):
    """Verifies natural neural voices and free AI providers."""

    def test_neural_voices_available(self):
        ve = get_voice_engine()
        voices = ve.get_available_voices()
        voice_ids = [v["id"] for v in voices]
        # Verify Microsoft Neural Voices
        self.assertIn("en-US-AriaNeural", voice_ids)
        self.assertIn("en-US-ChristopherNeural", voice_ids)
        self.assertIn("en-US-GuyNeural", voice_ids)
        self.assertIn("ar-AE-HamdanNeural", voice_ids)

    def test_free_ai_providers(self):
        # Groq Cloud
        groq = GroqProvider()
        self.assertEqual(groq.name, "groq")
        self.assertIn("qwen/qwen3.8-27b", groq.available_models)
        self.assertIn("openai/gpt-oss-120b", groq.available_models)
        self.assertIn("allam-2-7b", groq.available_models)

        # OpenRouter Free
        openr = OpenRouterProvider()
        self.assertEqual(openr.name, "openrouter")
        self.assertIn("meta-llama/llama-3.3-70b-instruct:free", openr.available_models)
        self.assertIn("deepseek/deepseek-r1:free", openr.available_models)

    def test_fallback_free_models_advice(self):
        fallback = FallbackProvider()
        reply = fallback._craft_smart_reply("Can I use free API models?", "habibi_dubai")
        self.assertIn("Groq Cloud", reply)
        self.assertIn("Llama 3.3 70B", reply)
        self.assertIn("DeepSeek R1", reply)
        self.assertIn("Google Gemini", reply)

    def test_pet_skin_switching_no_restart(self):
        pet = DesktopPet()
        initial_pos = pet.pos()
        # Switch skin
        pet.set_skin("cyber_cyan")
        self.assertEqual(pet.skin.name, "cyber_cyan")
        # Ensure redundant switch does not reset or reload
        pet.set_skin("cyber_cyan")
        self.assertEqual(pet.skin.name, "cyber_cyan")
        # Switch back to habibi
        pet.set_skin("habibi_dubai")
        self.assertEqual(pet.skin.name, "habibi_dubai")
        # Ensure position did not reset to (0,0)
        self.assertEqual(pet.pos(), initial_pos)

    def test_laptop_control_panel(self):
        from interface.control_panel import LaptopControlPanel
        panel = LaptopControlPanel()
        self.assertEqual(panel.tabs.count(), 5)
        # Verify hardware diagnostics populated
        self.assertTrue(panel.cpu_bar.maximum() == 100)
        self.assertTrue(panel.ram_bar.maximum() == 100)
        self.assertTrue(panel.disk_bar.maximum() == 100)


if __name__ == "__main__":
    unittest.main()
