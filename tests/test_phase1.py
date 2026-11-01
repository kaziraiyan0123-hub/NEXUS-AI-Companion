"""
NEXUS Phase 1 Comprehensive Verification Test Suite
Tests settings, states, rendering engine, all 17 animations, and window components.
"""
import sys
import os
import unittest
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PySide6.QtCore import Qt, QPoint, QRectF
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPixmap, QPainter, QColor

from config.settings import SettingsManager, DEFAULT_SETTINGS
from core.character_state import CharacterState, InteractionMode
from interface.themes import SKINS, get_skin, get_menu_stylesheet
from desktop.pet_renderer import PetRenderer, Particle
from desktop.pet import DesktopPet
from desktop.quick_bubble import QuickBubble

# Initialize QApplication once for headless/offscreen widget testing
app = QApplication.instance()
if not app:
    app = QApplication([])

class TestNexusPhase1(unittest.TestCase):

    def setUp(self):
        self.settings = SettingsManager()
        self.settings.set("pet_width", 200)
        self.settings.set("pet_height", 200)
        self.skin = get_skin("cyber_cyan")

    def test_01_all_17_character_states(self):
        """Verify that all 17 specified animations exist in CharacterState."""
        expected_states = [
            "idle", "walking", "running", "floating", "sitting", "sleeping",
            "waking", "listening", "thinking", "talking", "happy", "sad",
            "surprised", "confused", "working", "error", "celebrating"
        ]
        self.assertEqual(len(CharacterState), 17)
        for state_str in expected_states:
            state = CharacterState(state_str)
            self.assertIsNotNone(state)
            self.assertEqual(state.value, state_str)

    def test_02_skins_and_themes(self):
        """Verify skins exist with valid colors and CSS generators."""
        self.assertIn("cyber_cyan", SKINS)
        self.assertIn("neon_purple", SKINS)
        self.assertIn("matrix_green", SKINS)
        self.assertIn("sunset_amber", SKINS)
        self.assertIn("cosmic_white", SKINS)

        for skin_key, skin in SKINS.items():
            self.assertTrue(skin.primary.isValid())
            self.assertTrue(skin.secondary.isValid())
            self.assertTrue(skin.body_fill.isValid())
            self.assertTrue(skin.body_rim.isValid())
            self.assertTrue(skin.visor_bg.isValid())

        # Test stylesheet generator
        css = get_menu_stylesheet("cyber_cyan")
        self.assertIn("QMenu", css)
        self.assertIn("#00f0ff", css)

    def test_03_settings_manager(self):
        """Test settings get, set, persistence."""
        self.assertEqual(self.settings.get("pet_width"), 200)
        self.assertEqual(self.settings.get("always_on_top"), True)
        
        # Test modifying setting
        self.settings.set("pet_width", 220)
        self.assertEqual(self.settings.get("pet_width"), 220)
        
        # Restore
        self.settings.set("pet_width", 200)

    def test_04_renderer_physics_and_gaze(self):
        """Test procedural renderer state updates, gaze physics, and particles."""
        renderer = PetRenderer(self.skin)
        
        # Test gaze tracking interpolation
        renderer.update_physics(dt=0.025, cursor_rel_x=0.8, cursor_rel_y=-0.5)
        self.assertGreater(renderer.current_look_x, 0.0)
        self.assertLess(renderer.current_look_y, 0.0)

        # Test particle updates
        p = Particle(100, 100, "star", QColor(0, 240, 255))
        self.assertTrue(p.is_alive)
        p.update()
        self.assertNotEqual(p.y, 100)

    def test_05_renderer_all_17_animations_offscreen(self):
        """Render all 17 animations to offscreen QPixmaps to verify zero exceptions or draw faults."""
        renderer = PetRenderer(self.skin)
        pixmap = QPixmap(200, 200)

        for state in CharacterState:
            renderer.set_state(state)
            renderer.update_physics(dt=0.03, cursor_rel_x=0.0, cursor_rel_y=0.0)
            
            # Draw to offscreen buffer
            pixmap.fill(QColor(0, 0, 0, 0))
            painter = QPainter(pixmap)
            try:
                renderer.render(painter, 200, 200)
            finally:
                painter.end()

            self.assertEqual(renderer.state, state)

    def test_06_desktop_pet_window(self):
        """Test desktop pet window creation, flags, and size."""
        pet = DesktopPet()
        
        # Window attributes
        self.assertTrue(pet.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground))
        self.assertEqual(pet.width(), 200)
        self.assertEqual(pet.height(), 200)

        # Change size
        pet.set_pet_size(160)
        self.assertEqual(pet.width(), 160)
        pet.set_pet_size(200)

        # Change skin
        pet.set_skin("neon_purple")
        self.assertEqual(pet.skin.name, "neon_purple")
        pet.set_skin("cyber_cyan")

        # Clean up
        pet.bubble.close()
        pet.close()

    def test_07_quick_bubble(self):
        """Test speech bubble message and layout."""
        bubble = QuickBubble(skin=self.skin)
        bubble.show_message("Test message for NEXUS speech bubble", duration_ms=1000)
        self.assertEqual(bubble.message, "Test message for NEXUS speech bubble")
        self.assertGreater(bubble.width(), 100)
        bubble.close()

if __name__ == "__main__":
    unittest.main()
