"""
NEXUS Desktop Pet Minimalist Context Menu
Clean, modern Windows 11 style popup menu (no clutter, no gaudy borders).
"""
from PySide6.QtWidgets import QMenu, QWidget, QInputDialog
from PySide6.QtGui import QAction, QActionGroup, QIcon
from PySide6.QtCore import Signal, QObject
from core.character_state import CharacterState
from interface.themes import get_menu_stylesheet, SKINS, CANONICAL_SKINS
from core.memory_manager import get_memory_manager

class PetContextMenu(QMenu):
    """Clean minimalist context menu for NEXUS desktop companion."""

    def __init__(self, parent: QWidget, controller):
        super().__init__(parent)
        self.controller = controller
        skin_name = controller.settings.get("character_skin", "neo_cyber")
        self.setStyleSheet(get_menu_stylesheet(skin_name))
        self._build_menu()

    def _build_menu(self):
        self.clear()
        mm = get_memory_manager()
        user_name = mm.get_user_name()
        bond = mm.get_bond_stats()

        # Primary Core Actions
        action_talk = self.addAction("💬  Talk to NEXUS")
        action_talk.triggered.connect(self.controller.open_chat)

        action_voice = self.addAction("🎙️  Voice Mode")
        action_voice.triggered.connect(self.controller.toggle_voice)

        action_vision = self.addAction("👁️  Screen Vision")
        action_vision.triggered.connect(lambda: self.controller.trigger_tool("analyze_screen", {"query": "Analyze active screen context"}))

        action_cp = self.addAction("💻  Command Center")
        action_cp.triggered.connect(self.controller.open_control_panel)

        self.addSeparator()

        # Affection & Interactions
        bond_menu = self.addMenu(f"💖  Affection ({bond['title']} • {bond['xp']} XP)")
        pet_action = bond_menu.addAction("💖  Pet NEXUS (+5 XP)")
        pet_action.triggered.connect(self._trigger_pet)

        five_action = bond_menu.addAction("✋  High-Five NEXUS (+10 XP)")
        five_action.triggered.connect(self._trigger_high_five)

        cheer_action = bond_menu.addAction("⭐  Sparkle Cheer (+5 XP)")
        cheer_action.triggered.connect(self._trigger_sparkle_cheer)

        # Identity & Profile
        name_display = f"👤  My Name ({user_name})" if user_name else "👤  Set My Name..."
        action_name = self.addAction(name_display)
        action_name.triggered.connect(self._change_name_dialog)

        # Settings
        action_settings = self.addAction("⚙️  Settings")
        action_settings.triggered.connect(self.controller.open_settings)

        # Appearance Submenu
        appearance_menu = self.addMenu("🎨  Appearance")
        
        # Skins Submenu (Only canonical unique archetypes)
        skin_menu = appearance_menu.addMenu("Character Skin")
        skin_group = QActionGroup(self)
        skin_group.setExclusive(True)
        current_skin = self.controller.settings.get("character_skin", "neo_cyber")

        for key in CANONICAL_SKINS:
            skin_data = SKINS.get(key)
            if not skin_data:
                continue
            s_action = skin_menu.addAction(skin_data.display_name)
            s_action.setCheckable(True)
            if key == current_skin:
                s_action.setChecked(True)
            skin_group.addAction(s_action)
            def make_skin_handler(k=key):
                return lambda *args, sk=k: self.controller.set_skin(sk, announce=False)
            s_action.triggered.connect(make_skin_handler())

        # Size Submenu
        size_menu = appearance_menu.addMenu("Size")
        sizes = [("Small (160px)", 160), ("Medium (200px)", 200), ("Large (260px)", 260)]
        curr_width = self.controller.settings.get("pet_width", 200)
        for label, sz in sizes:
            sz_action = size_menu.addAction(label)
            sz_action.setCheckable(True)
            if abs(curr_width - sz) < 15:
                sz_action.setChecked(True)
            def make_sz_handler(s=sz):
                return lambda *args, sz_val=s: self.controller.set_pet_size(sz_val)
            sz_action.triggered.connect(make_sz_handler())

        # Always On Top toggle
        top_action = appearance_menu.addAction("📌  Always on Top")
        top_action.setCheckable(True)
        top_action.setChecked(self.controller.settings.get("always_on_top", True))
        top_action.toggled.connect(self.controller.toggle_always_on_top)

        self.addSeparator()

        # Sleep & Power
        sleep_action = self.addAction("💤  Sleep Mode")
        sleep_action.triggered.connect(self.controller.toggle_sleep)

        off_action = self.addAction("⚡  Dismiss to Tray")
        off_action.triggered.connect(self.controller.turn_off)

        exit_action = self.addAction("✕  Exit NEXUS")
        exit_action.triggered.connect(self.controller.quit_application)

    def _change_name_dialog(self):
        mm = get_memory_manager()
        current = mm.get_user_name()
        new_name, ok = QInputDialog.getText(
            self.parent(), "Owner Name", "What should NEXUS call you?", text=current
        )
        if ok and new_name.strip():
            clean = new_name.strip()
            mm.set_user_name(clean)
            if hasattr(self.controller, "chat_window") and hasattr(self.controller.chat_window, "user_badge"):
                self.controller.chat_window.user_badge.setText(f"👤 {clean}")
            pet = self._get_pet_instance()
            if hasattr(pet, "say"):
                pet.say(f"I will remember you as {clean}! ✦", 3000)
            try:
                from core.voice_engine import get_voice_engine
                get_voice_engine().speak(f"Understood. I will remember you as {clean} forever.")
            except Exception:
                pass

    def _get_pet_instance(self):
        if hasattr(self.controller, "pet") and self.controller.pet:
            return self.controller.pet
        return self.controller

    def _trigger_pet(self):
        pet = self._get_pet_instance()
        if hasattr(pet, "pet_the_pet"):
            pet.pet_the_pet()

    def _trigger_high_five(self):
        pet = self._get_pet_instance()
        if hasattr(pet, "high_five"):
            pet.high_five()
        elif hasattr(pet, "pet_the_pet"):
            pet.pet_the_pet()

    def _trigger_sparkle_cheer(self):
        pet = self._get_pet_instance()
        if hasattr(pet, "sparkle_cheer"):
            pet.sparkle_cheer()
        elif hasattr(pet, "pet_the_pet"):
            pet.pet_the_pet()
