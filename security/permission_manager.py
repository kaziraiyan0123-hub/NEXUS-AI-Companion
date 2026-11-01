"""
NEXUS Absolute Permission System
Enforces strict user consent prior to executing any computer operation.
Never approves actions automatically; provides emergency stop and persistent audit logging.
"""
import os
import time
import json
import logging
from enum import Enum
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict

from config.settings import get_settings

logger = logging.getLogger("NEXUS.PermissionSystem")

class PermissionLevel(Enum):
    LEVEL_1_INFO_ONLY = 1        # NEXUS answers questions and analyzes data; NO computer changes allowed
    LEVEL_2_ASK_BEFORE_ACTION = 2 # DEFAULT: Requests explicit user approval for EVERY computer operation
    LEVEL_3_RESTRICTED = 3       # Low-risk read-only actions pre-approved; all writes/moves/kills require approval

class ActionRisk(Enum):
    LOW = "low"                 # Read-only or cosmetic (e.g. read clipboard, get battery, search files)
    MODERATE = "moderate"       # Creates folders, launches approved apps, organizes files into subfolders
    DESTRUCTIVE = "destructive" # Closes running apps, overwrites files, kills processes, deletes data

@dataclass
class ActionRequest:
    action_id: str
    tool_name: str
    title: str
    description: str
    risk: ActionRisk
    details: List[str]
    parameters: Dict[str, Any]
    timestamp: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["risk"] = self.risk.value
        return d

@dataclass
class AuditEntry:
    timestamp: float
    action_id: str
    tool_name: str
    title: str
    risk: str
    status: str  # "APPROVED", "DENIED", "BLOCKED_BY_LEVEL_1", "CANCELLED_EMERGENCY_STOP", "SUCCESS", "FAILED"
    details: str

class PermissionManager:
    """Core enforcement engine for the NEXUS Absolute Permission System."""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(PermissionManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.settings = get_settings()
        self.emergency_stop_active = False
        self.audit_log_path = os.path.join(self.settings.config_dir, "audit_log.jsonl")
        self._init_audit_log()
        self._initialized = True

    def _init_audit_log(self):
        try:
            os.makedirs(self.settings.config_dir, exist_ok=True)
            if not os.path.exists(self.audit_log_path):
                with open(self.audit_log_path, "w", encoding="utf-8") as f:
                    init_entry = {
                        "timestamp": time.time(),
                        "action_id": "INIT",
                        "tool_name": "SYSTEM",
                        "title": "NEXUS Absolute Permission System Initialized",
                        "risk": "low",
                        "status": "ACTIVE",
                        "details": "Level 2: Ask Before Action active by default."
                    }
                    f.write(json.dumps(init_entry) + "\n")
        except Exception as e:
            logger.warning(f"Failed to initialize audit log: {e}")

    @property
    def current_level(self) -> PermissionLevel:
        lvl_int = int(self.settings.get("permission_level", 2))
        try:
            return PermissionLevel(lvl_int)
        except ValueError:
            return PermissionLevel.LEVEL_2_ASK_BEFORE_ACTION

    def trigger_emergency_stop(self):
        """Global Emergency Stop: Halts all running tools and blocks any pending operations."""
        self.emergency_stop_active = True
        logger.warning("🚨 EMERGENCY STOP ACTIVATED. All desktop operations locked.")
        self.log_audit("EMERGENCY_STOP", "SYSTEM", "Global Emergency Stop Triggered", "destructive", "ACTIVATED", "All pending actions cancelled.")

    def reset_emergency_stop(self):
        """Resets the emergency stop state upon user confirmation."""
        self.emergency_stop_active = False
        logger.info("Emergency Stop reset. Operations returned to configured level.")

    def should_request_approval(self, request: ActionRequest) -> bool:
        """
        Determines whether user approval is mandatory according to NEXUS safety rules.
        Rule: Level 2 ALWAYS requires approval.
        Level 1 NEVER executes actions (blocked).
        Level 3 requires approval for Moderate and Destructive actions.
        """
        if self.emergency_stop_active:
            return True

        level = self.current_level
        if level == PermissionLevel.LEVEL_1_INFO_ONLY:
            return False  # Handled as auto-blocked

        if level == PermissionLevel.LEVEL_2_ASK_BEFORE_ACTION:
            # Rule: Ask before every computer operation
            return True

        if level == PermissionLevel.LEVEL_3_RESTRICTED:
            # Even in Level 3, destructive or moderate actions MUST require explicit approval
            if request.risk in (ActionRisk.MODERATE, ActionRisk.DESTRUCTIVE):
                return True
            return False

        return True

    def can_execute(self, request: ActionRequest) -> bool:
        """Returns True if Level 1 does not forbid computer interaction."""
        if self.emergency_stop_active:
            return False
        if self.current_level == PermissionLevel.LEVEL_1_INFO_ONLY:
            return False
        return True

    def log_audit(self, action_id: str, tool_name: str, title: str, risk: str, status: str, details: str):
        """Persists audit record to disk."""
        entry = AuditEntry(
            timestamp=time.time(),
            action_id=action_id,
            tool_name=tool_name,
            title=title,
            risk=risk,
            status=status,
            details=details
        )
        try:
            with open(self.audit_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(asdict(entry)) + "\n")
        except Exception as e:
            logger.error(f"Failed to append audit log: {e}")

    def get_recent_audit_entries(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Reads recent audit history."""
        if not os.path.exists(self.audit_log_path):
            return []
        entries = []
        try:
            with open(self.audit_log_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        entries.append(json.loads(line))
        except Exception as e:
            logger.error(f"Error reading audit log: {e}")
        return entries[-limit:]


_permission_manager_instance = None
def get_permission_manager() -> PermissionManager:
    global _permission_manager_instance
    if _permission_manager_instance is None:
        _permission_manager_instance = PermissionManager()
    return _permission_manager_instance
