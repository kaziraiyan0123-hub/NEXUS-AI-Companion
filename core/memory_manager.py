"""
NEXUS Persistent Memory Manager
Stores user profile, user name, persistent facts, preferences, and long-term memory in SQLite.
"""
import os
import sqlite3
import time
import logging
from typing import Optional, List, Dict, Any
from pathlib import Path
from contextlib import contextmanager

from config.settings import get_settings

logger = logging.getLogger("NEXUS.Memory")

class MemoryManager:
    """Manages long-term SQLite persistent memory and user identity for NEXUS."""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(MemoryManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, db_path: Optional[str] = None):
        if getattr(self, "_initialized", False):
            return

        self.settings = get_settings()

        if not db_path:
            appdata = os.getenv("APPDATA") or str(Path.home() / ".nexus")
            nexus_dir = os.path.join(appdata, "NEXUS")
            os.makedirs(nexus_dir, exist_ok=True)
            db_path = os.path.join(nexus_dir, "nexus_memory.db")

        self.db_path = db_path
        self._init_db()
        self._sync_with_settings()
        self._initialized = True
        logger.info(f"NEXUS Memory Manager initialized at: {self.db_path}")

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # 1. User Profile table (Name, Nickname, Title)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_profile (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at REAL NOT NULL
                )
            """)
            # 2. Memories table (Facts, Preferences, Notes)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    timestamp REAL NOT NULL
                )
            """)
            conn.commit()

    def _sync_with_settings(self):
        """Syncs user_name between settings.json and SQLite database."""
        name_in_settings = self.settings.get("user_name", "").strip()
        name_in_db = self.get_user_name()

        if name_in_settings and not name_in_db:
            self.set_user_name(name_in_settings)
        elif name_in_db and not name_in_settings:
            self.settings.set("user_name", name_in_db)

    def get_bond_stats(self) -> Dict[str, Any]:
        """Returns the user's bond XP, level, and title with NEXUS."""
        xp = 0
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT value FROM user_profile WHERE key = 'bond_xp'")
                row = cursor.fetchone()
                if row:
                    xp = int(row["value"])
        except Exception:
            xp = 0

        # Calculate level and title
        if xp >= 1500:
            level = 5
            title = "Soulbound Companion"
            next_xp = 1500
        elif xp >= 700:
            level = 4
            title = "Desktop Co-Pilot"
            next_xp = 1500
        elif xp >= 300:
            level = 3
            title = "Trusted Ally"
            next_xp = 700
        elif xp >= 100:
            level = 2
            title = "Close Friend"
            next_xp = 300
        else:
            level = 1
            title = "New Companion"
            next_xp = 100

        return {
            "xp": xp,
            "level": level,
            "title": title,
            "next_level_xp": next_xp
        }

    def add_bond_xp(self, amount: int) -> Dict[str, Any]:
        """Awards affection/interaction bond XP and returns stats with level_up flag."""
        old_stats = self.get_bond_stats()
        new_xp = old_stats["xp"] + max(0, amount)
        now = time.time()

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO user_profile (key, value, updated_at)
                    VALUES ('bond_xp', ?, ?)
                    ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at
                """, (str(new_xp), now))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to save bond XP: {e}")

        new_stats = self.get_bond_stats()
        new_stats["leveled_up"] = (new_stats["level"] > old_stats["level"])
        return new_stats

    def has_user_name(self) -> bool:
        """Returns True if the companion already knows the owner's name."""
        name = self.get_user_name()
        return bool(name and len(name.strip()) > 0)

    def get_user_name(self) -> str:
        """Retrieves the user's saved name."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT value FROM user_profile WHERE key = 'user_name'")
                row = cursor.fetchone()
                if row:
                    return str(row["value"]).strip()
        except Exception as e:
            logger.error(f"Failed to read user_name from memory DB: {e}")

        # Fallback to settings
        return self.settings.get("user_name", "").strip()

    @staticmethod
    def extract_name(text: str) -> str:
        """Extracts a clean human name from common introductory phrases."""
        import re
        cleaned = text.strip().rstrip(".!?,")
        # Check patterns
        patterns = [
            r"^(?:my name is|i am|i'm|call me|you can call me|this is)\s+([A-Za-z0-9_'\- ]+)",
            r"^([A-Za-z0-9_'\-]+)$",
        ]
        for p in patterns:
            m = re.search(p, cleaned, re.IGNORECASE)
            if m:
                extracted = m.group(1).strip()
                extracted = re.sub(r"\b(please|thanks|thank you)\b", "", extracted, flags=re.IGNORECASE).strip()
                if 1 <= len(extracted) <= 30:
                    return extracted.title()
        words = cleaned.split()
        if 1 <= len(words) <= 3:
            return cleaned.title()
        return words[0].title() if words else "Friend"

    def set_user_name(self, name: str):
        """Permanently saves user's name in both SQLite memory and settings."""
        clean_name = name.strip()
        if not clean_name:
            return

        now = time.time()
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO user_profile (key, value, updated_at)
                    VALUES ('user_name', ?, ?)
                    ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at
                """, (clean_name, now))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to write user_name to memory DB: {e}")

        # Also persist to settings.json
        self.settings.set("user_name", clean_name)
        # Add memorable initial entry
        self.remember("identity", "owner_name", f"The owner's permanent name is {clean_name}")
        logger.info(f"User name permanently recorded: '{clean_name}'")

    def remember(self, category: str, key: str, value: str):
        """Stores a persistent memory item."""
        now = time.time()
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO memories (category, key, value, timestamp)
                    VALUES (?, ?, ?, ?)
                """, (category.strip(), key.strip(), value.strip(), now))
                conn.commit()
                logger.info(f"Remembered: [{category}] {key}: {value[:40]}")
        except Exception as e:
            logger.error(f"Failed to store memory: {e}")

    def recall(self, query: str = "") -> List[Dict[str, Any]]:
        """Searches or returns all stored memories."""
        results = []
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                if query:
                    cursor.execute("""
                        SELECT id, category, key, value, timestamp 
                        FROM memories 
                        WHERE key LIKE ? OR value LIKE ? OR category LIKE ?
                        ORDER BY timestamp DESC
                    """, (f"%{query}%", f"%{query}%", f"%{query}%"))
                else:
                    cursor.execute("""
                        SELECT id, category, key, value, timestamp 
                        FROM memories 
                        ORDER BY timestamp DESC
                    """)
                for row in cursor.fetchall():
                    results.append(dict(row))
        except Exception as e:
            logger.error(f"Failed to recall memories: {e}")
        return results

    def get_all_memories(self) -> List[Dict[str, Any]]:
        return self.recall()

    def forget(self, memory_id: int) -> bool:
        """Deletes a specific memory entry."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to delete memory {memory_id}: {e}")
            return False

    def clear_all(self):
        """Clears all memories and profile."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM memories")
                cursor.execute("DELETE FROM user_profile")
                conn.commit()
            self.settings.set("user_name", "")
        except Exception as e:
            logger.error(f"Failed to clear memory: {e}")


_memory_manager_instance = None

def get_memory_manager() -> MemoryManager:
    global _memory_manager_instance
    if _memory_manager_instance is None:
        _memory_manager_instance = MemoryManager()
    return _memory_manager_instance
