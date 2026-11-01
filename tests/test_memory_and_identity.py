"""
Unit tests for NEXUS Memory Manager, User Identity, and Permanent Name Onboarding.
"""
import unittest
import os
import tempfile
import shutil

import core.memory_manager as mm_module
from core.memory_manager import MemoryManager
from core.ai_manager import AIManager
from config.settings import get_settings

class TestMemoryAndIdentity(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_memory.db")
        
        self.settings = get_settings()
        self.orig_user_name = self.settings.get("user_name", "")
        self.settings.set("user_name", "")
        
        # Reset singleton instance for test isolation
        MemoryManager._instance = None
        self.memory = MemoryManager(db_path=self.db_path)
        mm_module._memory_manager_instance = self.memory

    def tearDown(self):
        self.settings.set("user_name", self.orig_user_name)
        MemoryManager._instance = None
        mm_module._memory_manager_instance = None
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_name_initialization_empty(self):
        self.assertFalse(self.memory.has_user_name())
        self.assertEqual(self.memory.get_user_name(), "")

    def test_set_and_get_user_name(self):
        self.memory.set_user_name("Rayan")
        self.assertTrue(self.memory.has_user_name())
        self.assertEqual(self.memory.get_user_name(), "Rayan")

    def test_extract_name_patterns(self):
        cases = [
            ("Rayan", "Rayan"),
            ("my name is Alice", "Alice"),
            ("I am Bob", "Bob"),
            ("I'm Charlie", "Charlie"),
            ("Call me Habibi", "Habibi"),
            ("Sarah Connor", "Sarah Connor"),
            ("my name is David, please", "David"),
        ]
        for input_text, expected_name in cases:
            extracted = self.memory.extract_name(input_text)
            self.assertEqual(extracted, expected_name)

    def test_persistent_memory_storage_and_recall(self):
        self.memory.remember("work", "project", "Building NEXUS AI desktop pet")
        self.memory.remember("preference", "theme", "Dark Glass Minimalist")

        all_memories = self.memory.get_all_memories()
        self.assertGreaterEqual(len(all_memories), 2)

        recalled = self.memory.recall("desktop")
        self.assertEqual(len(recalled), 1)
        self.assertEqual(recalled[0]["key"], "project")

    def test_system_prompt_includes_user_name(self):
        self.memory.set_user_name("Commander Shepard")
        ai_mgr = AIManager()
        prompt = ai_mgr.get_system_prompt()
        self.assertIn("Commander Shepard", prompt)

    def test_bond_xp_and_progression(self):
        stats0 = self.memory.get_bond_stats()
        self.assertEqual(stats0["level"], 1)
        self.assertEqual(stats0["xp"], 0)

        # Add XP to reach level 2 (100 XP)
        stats1 = self.memory.add_bond_xp(110)
        self.assertEqual(stats1["level"], 2)
        self.assertTrue(stats1["leveled_up"])
        self.assertEqual(stats1["title"], "Close Friend")

    def test_creator_identity_raiyan_coded_me(self):
        ai_mgr = AIManager()
        questions = [
            "who made you",
            "who coded you?",
            "Who created you?",
            "who built you"
        ]
        for q in questions:
            tokens = list(ai_mgr.stream_chat([{"role": "user", "content": q}]))
            full_reply = "".join(tokens)
            self.assertIn("Raiyan coded me", full_reply)

    def test_spoken_highlight_extraction(self):
        from core.voice_engine import extract_spoken_highlight
        long_text = "Here is the summary of your project. We completed everything on schedule. Extra details follow below in three long paragraphs..."
        spoken = extract_spoken_highlight(long_text)
        self.assertLessEqual(len(spoken), 180)
        self.assertIn("Here is the summary", spoken)

        code_text = "Here is the python function.\n```python\ndef test(): pass\n```"
        spoken_code = extract_spoken_highlight(code_text)
        self.assertIn("chat", spoken_code.lower())

if __name__ == "__main__":
    unittest.main()
