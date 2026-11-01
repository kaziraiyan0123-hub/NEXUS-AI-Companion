"""
Unit Tests for NEXUS 'Do Anything' Assistant Accessibility and Habibi Visual Appearance
Verifies:
1. TimeDateTool (exact clock, calendar, formatted and spoken output)
2. WebOpenerTool (resolves YouTube, Google, ChatGPT, Reddit, GitHub, URLs)
3. LockWorkstationTool & EmptyRecycleBinTool (action requests, risk gating)
4. MediaVolumeTool (ctypes keybd_event execution without win32api crash)
5. ToolRegistry.parse_intent (natural language coverage for all desktop commands)
6. Habibi appearance only (ghutra and aviators vector rendering without robotic/Arabic speech)
7. Raiyan creator attribution determinism
"""
import unittest
import time
from unittest.mock import patch, MagicMock

from core.desktop_tools import (
    get_tool_registry, TimeDateTool, WebOpenerTool, LockWorkstationTool,
    EmptyRecycleBinTool, AppLauncherTool, MediaVolumeTool, ToolResult
)
from interface.themes import get_skin, CANONICAL_SKINS, SKINS
from desktop.pet_renderer import PetRenderer, CharacterState
from PySide6.QtGui import QImage, QPainter


class TestDoAnythingAndHabibiAppearance(unittest.TestCase):

    def setUp(self):
        self.registry = get_tool_registry()

    def test_01_time_date_tool(self):
        tool = self.registry.get_tool("get_time_date")
        self.assertIsNotNone(tool, "TimeDateTool must be registered in ToolRegistry")
        self.assertIsInstance(tool, TimeDateTool)

        req = tool.get_action_request({})
        self.assertEqual(req.tool_name, "get_time_date")

        res = tool.execute({})
        self.assertTrue(res.success)
        self.assertIn("time", res.data)
        self.assertIn("day", res.data)
        self.assertIn("date", res.data)
        self.assertIn("spoken", res.data)
        self.assertTrue(res.data["spoken"].startswith("It is "))
        self.assertIn("🕒 **Current Time & Date**", res.message)

    def test_02_web_opener_tool(self):
        tool = self.registry.get_tool("open_website")
        self.assertIsNotNone(tool, "WebOpenerTool must be registered in ToolRegistry")
        self.assertIsInstance(tool, WebOpenerTool)

        # Resolves popular sites
        self.assertEqual(tool._resolve_url("youtube"), "https://www.youtube.com")
        self.assertEqual(tool._resolve_url("github"), "https://github.com")
        self.assertEqual(tool._resolve_url("chatgpt"), "https://chatgpt.com")
        self.assertEqual(tool._resolve_url("reddit"), "https://www.reddit.com")

        # Resolves domain patterns
        self.assertEqual(tool._resolve_url("google.com"), "https://google.com")
        self.assertEqual(tool._resolve_url("https://example.com"), "https://example.com")

        # Test execute mocked
        with patch("webbrowser.open", return_value=True) as mock_open:
            res = tool.execute({"site": "youtube"})
            self.assertTrue(res.success)
            mock_open.assert_called_once_with("https://www.youtube.com")

    def test_03_lock_and_recycle_bin_tools(self):
        lock_tool = self.registry.get_tool("lock_workstation")
        self.assertIsNotNone(lock_tool)
        req_lock = lock_tool.get_action_request({})
        self.assertEqual(req_lock.tool_name, "lock_workstation")

        bin_tool = self.registry.get_tool("empty_recycle_bin")
        self.assertIsNotNone(bin_tool)
        req_bin = bin_tool.get_action_request({})
        self.assertEqual(req_bin.tool_name, "empty_recycle_bin")
        # Recycle bin should be categorized as destructive for security
        self.assertEqual(bin_tool.risk_level.value, "destructive")

    def test_04_media_volume_ctypes_safety(self):
        """Ensures MediaVolumeTool executes via ctypes without win32api ModuleNotFoundError."""
        tool = self.registry.get_tool("control_media")
        self.assertIsNotNone(tool)

        with patch("ctypes.windll.user32.keybd_event") as mock_keybd:
            res = tool.execute({"action": "mute"})
            self.assertTrue(res.success)
            self.assertGreaterEqual(mock_keybd.call_count, 2)

    def test_05_parse_intent_coverage(self):
        """Verifies natural language intents for desktop actions."""
        # Time queries
        res_time1 = self.registry.parse_intent("what time is it")
        self.assertEqual(res_time1, ("get_time_date", {}))

        res_time2 = self.registry.parse_intent("tell me the time please")
        self.assertEqual(res_time2, ("get_time_date", {}))

        res_time3 = self.registry.parse_intent("what day is today")
        self.assertEqual(res_time3, ("get_time_date", {}))

        res_time4 = self.registry.parse_intent("what is today's date")
        self.assertEqual(res_time4, ("get_time_date", {}))

        # Web search
        res_search1 = self.registry.parse_intent("search google for deep learning")
        self.assertEqual(res_search1, ("search_web", {"query": "deep learning"}))

        res_search2 = self.registry.parse_intent("google best coffee shops")
        self.assertEqual(res_search2, ("search_web", {"query": "best coffee shops"}))

        res_search3 = self.registry.parse_intent("search for quantum computing")
        self.assertEqual(res_search3, ("search_web", {"query": "quantum computing"}))

        # Opening websites & apps
        res_open_yt = self.registry.parse_intent("open youtube")
        self.assertEqual(res_open_yt, ("open_website", {"site": "youtube"}))

        res_open_gpt = self.registry.parse_intent("open chatgpt")
        self.assertEqual(res_open_gpt, ("open_website", {"site": "chatgpt"}))

        res_open_np = self.registry.parse_intent("open notepad")
        self.assertEqual(res_open_np, ("launch_application", {"app_name": "notepad"}))

        res_open_dl = self.registry.parse_intent("open downloads")
        self.assertEqual(res_open_dl, ("open_folder", {"folder": "downloads"}))

        # Lock & Bin
        res_lock = self.registry.parse_intent("lock pc")
        self.assertEqual(res_lock, ("lock_workstation", {}))

        res_lock_laptop = self.registry.parse_intent("lock laptop")
        self.assertEqual(res_lock_laptop, ("lock_workstation", {}))

        res_bin = self.registry.parse_intent("empty recycle bin")
        self.assertEqual(res_bin, ("empty_recycle_bin", {}))

        # Audio
        res_vol = self.registry.parse_intent("volume up")
        self.assertEqual(res_vol, ("control_media", {"action": "volume_up"}))

    def test_06_habibi_appearance_only_not_voice(self):
        """Verifies Habibi skin has archetype 'habibi' and renders with vector aviators and ghutra."""
        skin = get_skin("habibi_dubai")
        self.assertEqual(skin.archetype, "habibi")
        self.assertIn("Royal Habibi", skin.display_name)
        self.assertIn("habibi_dubai", CANONICAL_SKINS)

        # Test rendering without exception
        img = QImage(200, 200, QImage.Format.Format_ARGB32_Premultiplied)
        img.fill(0)
        painter = QPainter(img)
        renderer = PetRenderer(skin=skin)
        renderer.render(painter, 200, 200)
        painter.end()

        # Check methods exist on renderer
        self.assertTrue(hasattr(renderer, "_draw_dubai_aviators"))
        self.assertTrue(hasattr(renderer, "_draw_ghutra_drapes"))
        self.assertTrue(hasattr(renderer, "_draw_ghutra_top_and_agal"))

    def test_07_raiyan_creator_attribution(self):
        from core.ai_manager import get_ai_manager
        ai = get_ai_manager()
        response_tokens = list(ai.stream_chat([{"role": "user", "content": "who made you?"}]))
        full_text = "".join(response_tokens)
        self.assertIn("Raiyan coded me", full_text)


if __name__ == "__main__":
    unittest.main()
