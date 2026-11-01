"""
NEXUS Configuration and Settings Manager
Handles persistent configuration (window position, scale, theme, permissions, etc.)
"""
import os
import json
import logging
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger("NEXUS.Settings")

DEFAULT_SETTINGS = {
    # User Profile & Permanent Identity
    "user_name": "",

    # Character & Window
    "pet_scale": 1.0,
    "pet_width": 200,
    "pet_height": 200,
    "always_on_top": True,
    "position_x": -1,  # -1 means auto-place near bottom right
    "position_y": -1,
    "character_skin": "neo_cyber",
    "animation_speed": 1.0,
    "idle_roam_enabled": True,
    "look_at_cursor": True,
    "interaction_mode": "normal",
    
    # Sound & Voice
    "sound_enabled": True,
    "voice_input_enabled": True,
    "tts_enabled": True,
    "tts_voice": "default",
    "tts_speed": 1.0,
    "tts_volume": 0.9,
    "elevenlabs_api_key": "",
    "elevenlabs_voice_id": "21m00Tcm4TlvDq8ikWAM",
    "wake_word_enabled": True,
    "wake_word": "Hey Nexus",
    
    # AI Brain
    "ai_provider": "groq",
    "ai_model": "qwen/qwen3.8-27b",
    "temperature": 0.7,
    "max_tokens": 1500,
    
    # Security & Permissions
    "permission_level": 2,  # Level 1: Info Only, Level 2: Ask Before Action (Default), Level 3: Restricted
    "emergency_stop_enabled": True,
    
    # Background
    "run_in_tray": True,
    "start_with_windows": False,
    "auto_sleep_idle_minutes": 15,
}

class SettingsManager:
    """Singleton-style settings manager for NEXUS."""
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SettingsManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, config_dir: str = None):
        if self._initialized:
            return
        
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            appdata = os.environ.get("APPDATA")
            if appdata:
                self.config_dir = Path(appdata) / "NEXUS"
            else:
                self.config_dir = Path(__file__).parent.parent / "data"
        
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / "settings.json"
        self._settings: Dict[str, Any] = DEFAULT_SETTINGS.copy()
        self.load()
        self._initialized = True

    def load(self) -> None:
        """Load settings from JSON file with fallback to defaults."""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Merge loaded data over defaults so new keys are preserved
                    for k, v in data.items():
                        self._settings[k] = v
                logger.info(f"Loaded settings from {self.config_file}")
            except Exception as e:
                logger.error(f"Failed to load settings file: {e}. Using defaults.")
        else:
            self.save()

    def save(self) -> None:
        """Persist current settings to JSON file."""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self._settings, f, indent=4)
            logger.debug("Saved settings.")
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        return self._settings.get(key, default if default is not None else DEFAULT_SETTINGS.get(key))

    def set(self, key: str, value: Any, auto_save: bool = True) -> None:
        self._settings[key] = value
        if auto_save:
            self.save()

    def reset_defaults(self) -> None:
        self._settings = DEFAULT_SETTINGS.copy()
        self.save()

# Global accessor
def get_settings() -> SettingsManager:
    return SettingsManager()
