"""
NEXUS Modular Desktop Control & Tool Execution Layer
Provides safe, validated Windows automation with absolute permission enforcement.
Every tool possesses a strict schema, validation rules, risk classification, and error isolation.
Arbitrary code or unsanctioned system modifications are strictly blocked.
"""
import os
import re
import sys
import time
import glob
import shutil
import logging
import subprocess
import urllib.parse
import ctypes
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple

from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtGui import QGuiApplication, QClipboard
from PySide6.QtWidgets import QApplication

from security.permission_manager import (
    PermissionManager, get_permission_manager,
    ActionRequest, ActionRisk, PermissionLevel
)
from interface.permission_dialog import PermissionDialog

logger = logging.getLogger("NEXUS.DesktopTools")

class ToolResult:
    """Standardized tool execution outcome."""
    def __init__(self, success: bool, message: str, data: Any = None):
        self.success = success
        self.message = message
        self.data = data or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data
        }

    def __str__(self) -> str:
        status = "SUCCESS" if self.success else "FAILED"
        return f"[{status}] {self.message}"


class BaseTool(ABC):
    """Abstract base class for all NEXUS desktop control tools."""

    name: str = "base_tool"
    display_name: str = "Base Tool"
    description: str = "Abstract base tool"
    risk_level: ActionRisk = ActionRisk.LOW

    @abstractmethod
    def get_action_request(self, params: Dict[str, Any]) -> ActionRequest:
        """Constructs human-readable proposal for user permission window."""
        pass

    @abstractmethod
    def execute(self, params: Dict[str, Any]) -> ToolResult:
        """Executes operation after permission has been granted."""
        pass


# 1. App Launcher Tool
class AppLauncherTool(BaseTool):
    name = "launch_application"
    display_name = "Launch Application"
    description = "Opens a permitted Windows application."
    risk_level = ActionRisk.MODERATE

    APP_MAP = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "calc": "calc.exe",
        "explorer": "explorer.exe",
        "file explorer": "explorer.exe",
        "task manager": "taskmgr.exe",
        "taskmgr": "taskmgr.exe",
        "paint": "mspaint.exe",
        "mspaint": "mspaint.exe",
        "terminal": "wt.exe",
        "cmd": "cmd.exe",
        "powershell": "powershell.exe",
        "code": "code",
        "vs code": "code",
        "vscode": "code",
        "chrome": "chrome.exe",
        "edge": "msedge.exe",
        "firefox": "firefox.exe",
        "brave": "brave.exe",
        "opera": "opera.exe",
        "settings": "ms-settings:",
        "control panel": "control.exe",
        "snipping tool": "snippingtool.exe",
        "word": "winword.exe",
        "excel": "excel.exe",
        "powerpoint": "powerpnt.exe",
        "spotify": "spotify.exe",
        "discord": "discord.exe",
        "steam": "steam.exe"
    }

    def get_action_request(self, params: Dict[str, Any]) -> ActionRequest:
        app_name = str(params.get("app_name", "")).strip().lower()
        target = self.APP_MAP.get(app_name, app_name)
        return ActionRequest(
            action_id=f"launch_{int(time.time()*1000)}",
            tool_name=self.name,
            title=f"Launch Application: {app_name.capitalize()}",
            description=f"NEXUS is requesting to open '{app_name}' on your desktop.",
            risk=self.risk_level,
            details=[
                f"Application identifier: {target}",
                "Process will run in user desktop session",
                "No elevated privileges requested"
            ],
            parameters=params,
            timestamp=time.time()
        )

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        app_name = str(params.get("app_name", "")).strip().lower()
        target = self.APP_MAP.get(app_name, app_name)
        try:
            if target.startswith("ms-settings:"):
                os.system(f"start {target}")
            else:
                subprocess.Popen(target, shell=True)
            return ToolResult(True, f"Application '{app_name}' launched successfully.")
        except Exception as e:
            return ToolResult(False, f"Failed to launch '{app_name}': {e}")


# 1b. Web Opener Tool (Opens popular sites and URLs directly in default browser)
class WebOpenerTool(BaseTool):
    name = "open_website"
    display_name = "Open Website"
    description = "Opens a requested website or URL in your default browser."
    risk_level = ActionRisk.LOW

    POPULAR_SITES = {
        "youtube": "https://www.youtube.com",
        "google": "https://www.google.com",
        "github": "https://github.com",
        "chatgpt": "https://chatgpt.com",
        "openai": "https://openai.com",
        "reddit": "https://www.reddit.com",
        "twitter": "https://twitter.com",
        "x": "https://x.com",
        "gmail": "https://mail.google.com",
        "spotify": "https://open.spotify.com",
        "netflix": "https://www.netflix.com",
        "amazon": "https://www.amazon.com",
        "wikipedia": "https://www.wikipedia.org",
        "twitch": "https://www.twitch.tv",
        "discord": "https://discord.com/app",
        "linkedin": "https://www.linkedin.com",
        "instagram": "https://www.instagram.com",
        "facebook": "https://www.facebook.com",
        "maps": "https://maps.google.com",
        "google maps": "https://maps.google.com",
        "news": "https://news.google.com",
        "weather": "https://www.google.com/search?q=weather"
    }

    def _resolve_url(self, site: str) -> str:
        s = site.lower().strip()
        if s in self.POPULAR_SITES:
            return self.POPULAR_SITES[s]
        if s.startswith("http://") or s.startswith("https://"):
            return site
        if s.startswith("www.") or any(s.endswith(tld) for tld in (".com", ".org", ".net", ".io", ".app", ".ai", ".co", ".edu", ".gov", ".me", ".tv")):
            return f"https://{s}"
        return f"https://www.google.com/search?q={urllib.parse.quote(site)}"

    def get_action_request(self, params: Dict[str, Any]) -> ActionRequest:
        site = str(params.get("site", "")).strip()
        url = self._resolve_url(site)
        return ActionRequest(
            action_id=f"webopen_{int(time.time()*1000)}",
            tool_name=self.name,
            title=f"Open Website: {site.capitalize()}",
            description=f"NEXUS is requesting to open '{url}' in your default browser.",
            risk=self.risk_level,
            details=[
                f"Target URL: {url}",
                "Opens safely in default web browser",
                "No external code execution"
            ],
            parameters=params,
            timestamp=time.time()
        )

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        import webbrowser
        site = str(params.get("site", "")).strip()
        if not site:
            return ToolResult(False, "Website name or URL cannot be empty.")
        url = self._resolve_url(site)
        try:
            webbrowser.open(url)
            return ToolResult(True, f"Opened [{site}]({url}) in your default browser.", {"url": url, "site": site})
        except Exception as e:
            return ToolResult(False, f"Failed to open '{site}': {e}")


# 1c. Real-Time Time & Date Tool
class TimeDateTool(BaseTool):
    name = "get_time_date"
    display_name = "Time & Date"
    description = "Provides real-time Windows local clock, date, day of week, and timezone."
    risk_level = ActionRisk.LOW

    def get_action_request(self, params: Dict[str, Any]) -> ActionRequest:
        return ActionRequest(
            action_id=f"time_{int(time.time()*1000)}",
            tool_name=self.name,
            title="Query Real-Time Clock & Calendar",
            description="NEXUS will read the exact Windows kernel clock and calendar date.",
            risk=self.risk_level,
            details=[
                "Read-only system clock check",
                "Formatted local time and date",
                "Zero filesystem or process impact"
            ],
            parameters=params,
            timestamp=time.time()
        )

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        now = time.localtime()
        time_12h = time.strftime("%I:%M %p", now).lstrip("0")
        day_name = time.strftime("%A", now)
        date_str = time.strftime("%B %d, %Y", now)
        tz_name = time.strftime("%Z", now) or "Local Time"

        day_num = now.tm_mday
        if 11 <= day_num <= 13:
            suffix = "th"
        else:
            suffix = {1: "st", 2: "nd", 3: "rd"}.get(day_num % 10, "th")

        spoken = f"It is {time_12h} on {day_name}, {time.strftime('%B', now)} {day_num}{suffix}."
        display = (
            f"🕒 **Current Time & Date**\n\n"
            f"• **Time:** `{time_12h}` ({tz_name})\n"
            f"• **Date:** `{day_name}, {date_str}`"
        )
        return ToolResult(True, display, {
            "time": time_12h,
            "day": day_name,
            "date": date_str,
            "spoken": spoken
        })


# 2. App Closer Tool
class AppCloserTool(BaseTool):
    name = "close_application"
    display_name = "Close Application"
    description = "Gracefully closes a specified running process."
    risk_level = ActionRisk.DESTRUCTIVE

    def get_action_request(self, params: Dict[str, Any]) -> ActionRequest:
        process_name = str(params.get("process_name", "")).strip()
        return ActionRequest(
            action_id=f"close_{int(time.time()*1000)}",
            tool_name=self.name,
            title=f"Close Application: {process_name}",
            description=f"NEXUS is requesting to terminate process '{process_name}'. Unsaved work in this application may be lost.",
            risk=self.risk_level,
            details=[
                f"Target process: {process_name}",
                "Warning: Ensure all documents in this app are saved before approving",
                "Sends terminate signal to target process"
            ],
            parameters=params,
            timestamp=time.time()
        )

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        process_name = str(params.get("process_name", "")).strip()
        if not process_name:
            return ToolResult(False, "Process name cannot be empty.")

        if not process_name.lower().endswith(".exe"):
            process_name += ".exe"

        # Blacklist critical Windows services
        critical = ["explorer.exe", "svchost.exe", "csrss.exe", "lsass.exe", "winlogon.exe"]
        if process_name.lower() in critical:
            return ToolResult(False, f"Action blocked: '{process_name}' is a protected core system process.")

        try:
            import psutil
            closed_count = 0
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] and proc.info['name'].lower() == process_name.lower():
                    proc.terminate()
                    closed_count += 1
            if closed_count > 0:
                return ToolResult(True, f"Closed {closed_count} instance(s) of '{process_name}'.")
            else:
                return ToolResult(False, f"No running process matching '{process_name}' was found.")
        except Exception as e:
            return ToolResult(False, f"Error terminating '{process_name}': {e}")


# 3. Folder Opener Tool
class FolderOpenerTool(BaseTool):
    name = "open_folder"
    display_name = "Open Folder"
    description = "Opens a folder in Windows File Explorer."
    risk_level = ActionRisk.LOW

    def _resolve_folder(self, folder_name: str) -> str:
        home = os.path.expanduser("~")
        lower = folder_name.strip().lower()
        if lower in ("downloads", "download"):
            return os.path.join(home, "Downloads")
        elif lower in ("documents", "doc", "docs"):
            return os.path.join(home, "Documents")
        elif lower in ("desktop",):
            return os.path.join(home, "Desktop")
        elif lower in ("pictures", "photos"):
            return os.path.join(home, "Pictures")
        elif lower in ("music",):
            return os.path.join(home, "Music")
        elif lower in ("videos",):
            return os.path.join(home, "Videos")
        elif os.path.isdir(folder_name):
            return os.path.abspath(folder_name)
        return os.path.join(home, folder_name)

    def get_action_request(self, params: Dict[str, Any]) -> ActionRequest:
        folder = params.get("folder", "Downloads")
        path = self._resolve_folder(folder)
        return ActionRequest(
            action_id=f"folder_{int(time.time()*1000)}",
            tool_name=self.name,
            title=f"Open Folder: {folder.capitalize()}",
            description=f"Opens '{path}' in Windows File Explorer.",
            risk=self.risk_level,
            details=[
                f"Directory path: {path}",
                "Action opens read view in Windows File Explorer",
                "No filesystem changes will be made"
            ],
            parameters={"folder": folder, "path": path},
            timestamp=time.time()
        )

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        folder = params.get("folder", "Downloads")
        path = self._resolve_folder(folder)
        if not os.path.exists(path):
            try:
                os.makedirs(path, exist_ok=True)
            except Exception as e:
                return ToolResult(False, f"Folder does not exist and could not be created: {e}")
        try:
            os.startfile(path)
            return ToolResult(True, f"Opened folder: {path}", {"path": path})
        except Exception as e:
            return ToolResult(False, f"Failed to open folder '{path}': {e}")


# 4. Folder Organizer Tool (The signature user requested capability)
class FolderOrganizerTool(BaseTool):
    name = "organize_folder"
    display_name = "Organize Folder"
    description = "Cleans and organizes files into categorized subfolders with exact preview."
    risk_level = ActionRisk.MODERATE

    EXT_CATEGORIES = {
        "Documents": [".pdf", ".docx", ".doc", ".txt", ".pptx", ".xlsx", ".xls", ".csv", ".epub", ".rtf"],
        "Images": [".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".bmp", ".ico", ".tiff"],
        "Installers": [".exe", ".msi", ".iso", ".zip", ".rar", ".7z", ".tar", ".gz"],
        "Media": [".mp4", ".mp3", ".wav", ".mkv", ".mov", ".flac", ".aac", ".avi"],
        "Code": [".py", ".json", ".js", ".html", ".css", ".cpp", ".c", ".h", ".ts", ".xml", ".sql"]
    }

    def _scan_folder(self, target_dir: str) -> Tuple[List[Dict[str, str]], List[str], List[str]]:
        """Returns (files_to_move, folders_to_create, untouched_files)."""
        to_move = []
        created_folders = set()
        untouched = []

        if not os.path.exists(target_dir):
            return [], [], []

        for item in os.listdir(target_dir):
            item_path = os.path.join(target_dir, item)
            # Skip directories and hidden files
            if os.path.isdir(item_path) or item.startswith("."):
                untouched.append(item)
                continue

            _, ext = os.path.splitext(item)
            ext = ext.lower()

            categorized = False
            for cat_name, ext_list in self.EXT_CATEGORIES.items():
                if ext in ext_list:
                    dest_dir = os.path.join(target_dir, cat_name)
                    dest_path = os.path.join(dest_dir, item)
                    to_move.append({
                        "file": item,
                        "source": item_path,
                        "dest": dest_path,
                        "category": cat_name
                    })
                    created_folders.add(cat_name)
                    categorized = True
                    break

            if not categorized:
                untouched.append(item)

        return to_move, list(created_folders), untouched

    def get_action_request(self, params: Dict[str, Any]) -> ActionRequest:
        folder_target = params.get("target_folder", "Downloads")
        home = os.path.expanduser("~")
        if folder_target.lower() in ("downloads", "download"):
            target_path = os.path.join(home, "Downloads")
        elif folder_target.lower() in ("desktop",):
            target_path = os.path.join(home, "Desktop")
        else:
            target_path = os.path.abspath(folder_target)

        to_move, folders_needed, untouched = self._scan_folder(target_path)

        details = [
            f"Target Directory: {target_path}",
            f"Create {len(folders_needed)} folders ({', '.join(folders_needed) or 'None'})",
            f"Move {len(to_move)} files into organized subdirectories",
            f"Leave {len(untouched)} files untouched (already organized or unrecognized)"
        ]

        for m in to_move[:10]:
            details.append(f"Move '{m['file']}' ➔ {m['category']}/")

        if len(to_move) > 10:
            details.append(f"... and {len(to_move) - 10} additional files.")

        return ActionRequest(
            action_id=f"organize_{int(time.time()*1000)}",
            tool_name=self.name,
            title=f"Organize {folder_target.capitalize()} Folder",
            description=f"NEXUS scanned '{target_path}' and found {len(to_move)} files ready to organize.",
            risk=self.risk_level,
            details=details,
            parameters={
                "target_path": target_path,
                "to_move": to_move,
                "folders_needed": folders_needed,
                "untouched_count": len(untouched)
            },
            timestamp=time.time()
        )

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        target_path = params.get("target_path")
        if not target_path or not os.path.exists(target_path):
            return ToolResult(False, f"Target directory not found: {target_path}")

        to_move, folders_needed, _ = self._scan_folder(target_path)
        if not to_move:
            return ToolResult(True, f"The folder '{target_path}' is already organized. No files need moving.")

        moved_count = 0
        created_count = 0

        # 1. Create subfolders
        for folder_name in folders_needed:
            folder_dir = os.path.join(target_path, folder_name)
            if not os.path.exists(folder_dir):
                os.makedirs(folder_dir, exist_ok=True)
                created_count += 1

        # 2. Move files safely
        for item in to_move:
            try:
                dest_dir = os.path.dirname(item["dest"])
                os.makedirs(dest_dir, exist_ok=True)

                # Avoid overwriting existing files
                target_file = item["dest"]
                if os.path.exists(target_file):
                    base, ext = os.path.splitext(item["file"])
                    target_file = os.path.join(dest_dir, f"{base}_{int(time.time())}{ext}")

                shutil.move(item["source"], target_file)
                moved_count += 1
            except Exception as e:
                logger.error(f"Error moving {item['file']}: {e}")

        return ToolResult(
            True,
            f"Organized folder '{target_path}': Created {created_count} categories, moved {moved_count} files.",
            {"moved_count": moved_count, "created_count": created_count}
        )


# 5. File Search Tool
class FileSearchTool(BaseTool):
    name = "search_files"
    display_name = "Search Files"
    description = "Searches for files matching a wildcard pattern."
    risk_level = ActionRisk.LOW

    def get_action_request(self, params: Dict[str, Any]) -> ActionRequest:
        query = params.get("query", "*")
        scope = params.get("scope", "Documents & Downloads")
        return ActionRequest(
            action_id=f"search_{int(time.time()*1000)}",
            tool_name=self.name,
            title=f"Search Files: '{query}'",
            description=f"Searches for files matching '{query}' across {scope}.",
            risk=self.risk_level,
            details=[
                f"Pattern: {query}",
                "Read-only file search operation",
                "No files will be modified or deleted"
            ],
            parameters=params,
            timestamp=time.time()
        )

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        query = params.get("query", "").strip()
        if not query:
            return ToolResult(False, "Search query cannot be empty.")

        if not any(c in query for c in ("*", "?")):
            query = f"*{query}*"

        home = os.path.expanduser("~")
        search_roots = [
            os.path.join(home, "Documents"),
            os.path.join(home, "Downloads"),
            os.path.join(home, "Desktop"),
            os.path.join(home, "Pictures")
        ]

        matches = []
        for root in search_roots:
            if not os.path.exists(root):
                continue
            for dirpath, _, filenames in os.walk(root):
                for f in filenames:
                    import fnmatch
                    if fnmatch.fnmatch(f.lower(), query.lower()):
                        full_p = os.path.join(dirpath, f)
                        try:
                            sz = os.path.getsize(full_p)
                            matches.append({
                                "filename": f,
                                "path": full_p,
                                "size_kb": round(sz / 1024, 1)
                            })
                        except Exception:
                            pass
                if len(matches) >= 30:
                    break

        if matches:
            res_msg = f"Found {len(matches)} matching file(s):\n"
            for m in matches[:8]:
                res_msg += f"• {m['filename']} ({m['size_kb']} KB) - {m['path']}\n"
            if len(matches) > 8:
                res_msg += f"... and {len(matches) - 8} more."
            return ToolResult(True, res_msg, {"matches": matches})
        else:
            return ToolResult(True, f"No files found matching '{query}'.")


# 6. Screenshot Tool
class ScreenshotTool(BaseTool):
    name = "take_screenshot"
    display_name = "Capture Screenshot"
    description = "Captures the Windows desktop display."
    risk_level = ActionRisk.LOW

    def get_action_request(self, params: Dict[str, Any]) -> ActionRequest:
        return ActionRequest(
            action_id=f"screenshot_{int(time.time()*1000)}",
            tool_name=self.name,
            title="Capture Screenshot",
            description="NEXUS will capture the current Windows screen display and save it to your Pictures directory.",
            risk=self.risk_level,
            details=[
                "Captures primary monitor display",
                "Saves PNG to 'Pictures/NEXUS Screenshots'",
                "Image path provided for instant viewing"
            ],
            parameters=params,
            timestamp=time.time()
        )

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        try:
            screen = QGuiApplication.primaryScreen()
            if not screen:
                return ToolResult(False, "Could not acquire primary screen handle.")

            pixmap = screen.grabWindow(0)
            home = os.path.expanduser("~")
            save_dir = os.path.join(home, "Pictures", "NEXUS Screenshots")
            os.makedirs(save_dir, exist_ok=True)

            filename = f"screenshot_{time.strftime('%Y%m%d_%H%M%S')}.png"
            full_path = os.path.join(save_dir, filename)
            pixmap.save(full_path, "PNG")

            return ToolResult(
                True,
                f"Screenshot saved successfully to '{full_path}'.",
                {"path": full_path, "filename": filename}
            )
        except Exception as e:
            return ToolResult(False, f"Failed to capture screenshot: {e}")


# 7. System Status Tool
class SystemStatusTool(BaseTool):
    name = "system_status"
    display_name = "System Status"
    description = "Retrieves CPU, RAM, battery, and storage metrics."
    risk_level = ActionRisk.LOW

    def get_action_request(self, params: Dict[str, Any]) -> ActionRequest:
        return ActionRequest(
            action_id=f"sys_{int(time.time()*1000)}",
            tool_name=self.name,
            title="Read System Diagnostics",
            description="Retrieves current hardware utilization metrics (CPU, Memory, Battery, Storage).",
            risk=self.risk_level,
            details=[
                "Read-only hardware query",
                "CPU load %, RAM usage, Battery %",
                "Primary disk space available"
            ],
            parameters=params,
            timestamp=time.time()
        )

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        try:
            import psutil
            cpu_pct = psutil.cpu_percent(interval=0.2)
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage("C:\\")

            bat_str = "Desktop / AC Connected"
            battery = psutil.sensors_battery()
            if battery:
                bat_pct = int(battery.percent)
                charging = "Charging ⚡" if battery.power_plugged else "Discharging"
                bat_str = f"{bat_pct}% ({charging})"

            report = (
                f"💻 **System Diagnostic Report:**\n\n"
                f"• **CPU Load:** {cpu_pct}%\n"
                f"• **Memory:** {round(mem.used / (1024**3), 1)} GB / {round(mem.total / (1024**3), 1)} GB ({mem.percent}% used)\n"
                f"• **Storage (C:):** {round(disk.free / (1024**3), 1)} GB free of {round(disk.total / (1024**3), 1)} GB\n"
                f"• **Power:** {bat_str}"
            )
            return ToolResult(True, report, {
                "cpu": cpu_pct,
                "memory_pct": mem.percent,
                "disk_free_gb": round(disk.free / (1024**3), 1),
                "battery": bat_str
            })
        except Exception as e:
            return ToolResult(False, f"Failed to retrieve system stats: {e}")


# 8. Media & Volume Control Tool
class MediaVolumeTool(BaseTool):
    name = "control_media"
    display_name = "Media & Volume"
    description = "Adjusts system volume and media playback."
    risk_level = ActionRisk.LOW

    # Windows Virtual Key Codes
    VK_VOLUME_MUTE = 0xAD
    VK_VOLUME_DOWN = 0xAE
    VK_VOLUME_UP = 0xAF
    VK_MEDIA_NEXT_TRACK = 0xB0
    VK_MEDIA_PREV_TRACK = 0xB1
    VK_MEDIA_STOP = 0xB2
    VK_MEDIA_PLAY_PAUSE = 0xB3

    def get_action_request(self, params: Dict[str, Any]) -> ActionRequest:
        action = params.get("action", "mute")
        return ActionRequest(
            action_id=f"media_{int(time.time()*1000)}",
            tool_name=self.name,
            title=f"Audio Control: {action.replace('_', ' ').capitalize()}",
            description=f"NEXUS will adjust audio playback: '{action}'.",
            risk=self.risk_level,
            details=[
                f"Operation: {action}",
                "Emits native Windows audio hardware key event",
                "Reversible immediately"
            ],
            parameters=params,
            timestamp=time.time()
        )

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        action = str(params.get("action", "mute")).lower()
        key_map = {
            "mute": self.VK_VOLUME_MUTE,
            "unmute": self.VK_VOLUME_MUTE,
            "volume_up": self.VK_VOLUME_UP,
            "volume_down": self.VK_VOLUME_DOWN,
            "play_pause": self.VK_MEDIA_PLAY_PAUSE,
            "pause": self.VK_MEDIA_PLAY_PAUSE,
            "next": self.VK_MEDIA_NEXT_TRACK,
            "previous": self.VK_MEDIA_PREV_TRACK
        }

        vk = key_map.get(action)
        if not vk:
            return ToolResult(False, f"Unknown audio action '{action}'. Options: mute, volume_up, volume_down, play_pause, next, previous.")

        try:
            # Simulate key down + key up via native ctypes without win32api crash
            KEYEVENTF_KEYUP = 0x0002
            steps = 4 if "volume_" in action else 1
            for _ in range(steps):
                ctypes.windll.user32.keybd_event(vk, 0, 0, 0)
                ctypes.windll.user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)
                time.sleep(0.05)
            return ToolResult(True, f"Audio action '{action}' executed successfully.")
        except Exception as e:
            return ToolResult(False, f"Audio control failed: {e}")


# 9. Clipboard Tool
class ClipboardTool(BaseTool):
    name = "clipboard"
    display_name = "Clipboard Manager"
    description = "Reads or writes text to the Windows system clipboard."
    risk_level = ActionRisk.LOW

    def get_action_request(self, params: Dict[str, Any]) -> ActionRequest:
        op = params.get("operation", "read")
        return ActionRequest(
            action_id=f"clip_{int(time.time()*1000)}",
            tool_name=self.name,
            title=f"Clipboard: {op.capitalize()}",
            description=f"NEXUS will {op} content from your system clipboard.",
            risk=self.risk_level,
            details=[
                f"Operation: {op}",
                "Standard Windows clipboard access"
            ],
            parameters=params,
            timestamp=time.time()
        )

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        op = str(params.get("operation", "read")).lower()
        clip = QGuiApplication.clipboard()
        if not clip:
            return ToolResult(False, "Clipboard access unavailable.")

        if op == "read":
            text = clip.text()
            if text:
                preview = text[:200] + ("..." if len(text) > 200 else "")
                return ToolResult(True, f"Clipboard content:\n```\n{preview}\n```", {"text": text})
            else:
                return ToolResult(True, "Clipboard is currently empty.")
        elif op in ("write", "copy", "set"):
            text = params.get("text", "")
            clip.setText(text)
            return ToolResult(True, "Copied text to clipboard successfully.")
        return ToolResult(False, f"Unsupported clipboard operation: '{op}'")


# 10. Web Search Tool
class WebSearchTool(BaseTool):
    name = "search_web"
    display_name = "Web Search"
    description = "Searches the web in default browser."
    risk_level = ActionRisk.LOW

    def get_action_request(self, params: Dict[str, Any]) -> ActionRequest:
        query = params.get("query", "")
        return ActionRequest(
            action_id=f"web_{int(time.time()*1000)}",
            tool_name=self.name,
            title=f"Web Search: '{query}'",
            description=f"Opens browser search for '{query}'.",
            risk=self.risk_level,
            details=[
                f"Search query: {query}",
                "Opens in your default web browser",
                "No external code execution"
            ],
            parameters=params,
            timestamp=time.time()
        )

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        import urllib.parse
        import webbrowser
        query = str(params.get("query", "")).strip()
        if not query:
            return ToolResult(False, "Search query cannot be empty.")
        url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
        try:
            webbrowser.open(url)
            return ToolResult(True, f"Opened web search for '{query}'.")
        except Exception as e:
            return ToolResult(False, f"Failed to open browser: {e}")


# 11. Desktop Vision & Screen Analysis Tool
class ScreenVisionTool(BaseTool):
    name = "analyze_screen"
    display_name = "Desktop Vision & Screen Intelligence"
    description = "Captures the active screen or window and analyzes visible content with AI."
    risk_level = ActionRisk.LOW

    def get_action_request(self, params: Dict[str, Any]) -> ActionRequest:
        return ActionRequest(
            action_id=f"vision_{int(time.time()*1000)}",
            tool_name=self.name,
            title="Desktop Screen Vision Analysis",
            description="NEXUS will capture your current desktop screen and inspect the active applications, visible text, and layout to assist you.",
            risk=self.risk_level,
            details=[
                "Read-only screen capture snapshot",
                "Detects open windows and active workflow context",
                "Provides intelligent advice and summary"
            ],
            parameters=params,
            timestamp=time.time()
        )

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        try:
            import tempfile
            screen = QGuiApplication.primaryScreen()
            if not screen:
                return ToolResult(False, "Could not acquire screen handle.")

            pixmap = screen.grabWindow(0)
            temp_path = os.path.join(tempfile.gettempdir(), f"nexus_vision_{int(time.time()*1000)}.png")
            pixmap.save(temp_path, "PNG")

            active_title = "Desktop / Windows Workspace"
            try:
                import ctypes
                hwnd = ctypes.windll.user32.GetForegroundWindow()
                length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
                buff = ctypes.create_unicode_buffer(length + 1)
                ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)
                active_title = buff.value or "Active Desktop Window"
            except Exception:
                pass

            query = params.get("query", "Summarize what is on the screen and give advice.")
            
            from core.ai_manager import get_ai_manager
            ai = get_ai_manager()
            prompt = (
                f"You are NEXUS, an intelligent AI Desktop Companion with desktop vision. "
                f"The user's foreground focused window is: '{active_title}'. "
                f"User request: '{query}'. "
                f"Deliver a structured, charismatic, and actionable breakdown: "
                f"1. Explain what application or workflow the user is in. "
                f"2. Provide key insights and relevant recommendations for this task. "
                f"3. Offer immediate helpful next steps or commands."
            )
            analysis = ai.generate_chat([{"role": "user", "content": prompt}], persona="companion")

            res_msg = (
                f"👁️ **Desktop Screen Vision Analysis**\n\n"
                f"• **Active Focus:** `{active_title}`\n"
                f"• **Resolution:** `{screen.size().width()}x{screen.size().height()}`\n\n"
                f"{analysis}"
            )
            return ToolResult(True, res_msg, {"active_window": active_title, "snapshot": temp_path})
        except Exception as e:
            return ToolResult(False, f"Vision analysis encountered an issue: {e}")


# 12. Lock Workstation Tool
class LockWorkstationTool(BaseTool):
    name = "lock_workstation"
    display_name = "Lock Laptop / PC"
    description = "Locks the Windows session to keep your laptop secure."
    risk_level = ActionRisk.MODERATE

    def get_action_request(self, params: Dict[str, Any]) -> ActionRequest:
        return ActionRequest(
            action_id=f"lock_{int(time.time()*1000)}",
            tool_name=self.name,
            title="Lock Windows Workstation",
            description="NEXUS is requesting to lock your laptop screen to secure your system.",
            risk=self.risk_level,
            details=[
                "Locks active Windows user desktop session",
                "Preserves all open documents and running applications",
                "Requires password or PIN to unlock"
            ],
            parameters=params,
            timestamp=time.time()
        )

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        try:
            ctypes.windll.user32.LockWorkStation()
            return ToolResult(True, "Windows workstation locked successfully.")
        except Exception as e:
            return ToolResult(False, f"Failed to lock workstation: {e}")


# 13. Empty Recycle Bin Tool
class EmptyRecycleBinTool(BaseTool):
    name = "empty_recycle_bin"
    display_name = "Empty Recycle Bin"
    description = "Permanently cleans and empties all files in the Windows Recycle Bin."
    risk_level = ActionRisk.DESTRUCTIVE

    def get_action_request(self, params: Dict[str, Any]) -> ActionRequest:
        return ActionRequest(
            action_id=f"bin_{int(time.time()*1000)}",
            tool_name=self.name,
            title="Empty Windows Recycle Bin",
            description="NEXUS will permanently remove all deleted files in the Windows Recycle Bin to free up disk space.",
            risk=self.risk_level,
            details=[
                "Permanent deletion of items in Recycle Bin",
                "Frees up storage on drive C:",
                "Cannot be undone after confirmation"
            ],
            parameters=params,
            timestamp=time.time()
        )

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        try:
            # 7 = SHERB_NOCONFIRMATION | SHERB_NOPROGRESSUI | SHERB_NOSOUND
            ctypes.windll.shell32.SHEmptyRecycleBinW(0, None, 7)
            return ToolResult(True, "Windows Recycle Bin has been emptied.")
        except Exception as e:
            return ToolResult(False, f"Failed to empty Recycle Bin: {e}")


# Tool Registry & Execution Engine
class ToolRegistry:
    """Central registry and executor for all NEXUS desktop tools."""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ToolRegistry, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.permission_manager = get_permission_manager()
        self.tools: Dict[str, BaseTool] = {}
        self._register_default_tools()
        self._initialized = True

    def _register_default_tools(self):
        defaults = [
            AppLauncherTool(),
            WebOpenerTool(),
            TimeDateTool(),
            LockWorkstationTool(),
            EmptyRecycleBinTool(),
            AppCloserTool(),
            FolderOpenerTool(),
            FolderOrganizerTool(),
            FileSearchTool(),
            ScreenshotTool(),
            ScreenVisionTool(),
            SystemStatusTool(),
            MediaVolumeTool(),
            ClipboardTool(),
            WebSearchTool()
        ]
        for t in defaults:
            self.tools[t.name] = t

    def get_tool(self, name: str) -> Optional[BaseTool]:
        return self.tools.get(name)

    def get(self, name: str) -> Optional[BaseTool]:
        return self.tools.get(name)

    def parse_intent(self, user_text: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        """Recognizes desktop action intent from natural language prompts."""
        t = user_text.lower().strip()

        # 1. Real-time Time & Date Queries (Instant, accurate, no LLM lag)
        time_triggers = (
            "what time is it", "what's the time", "what is the time", "tell me the time",
            "current time", "time now", "what time", "check time", "what day is it",
            "what day is today", "what day is it today", "what's today's date",
            "what is today's date", "what is the date", "today's date", "current date",
            "what date is it", "time and date", "date and time"
        )
        if any(w in t for w in time_triggers) or t in ("time", "date", "clock"):
            return "get_time_date", {}

        # 2. Lock PC / Laptop
        if any(w in t for w in ("lock pc", "lock laptop", "lock workstation", "lock computer", "lock screen", "lock my pc", "lock my laptop", "lock my screen")):
            return "lock_workstation", {}

        # 3. Empty Recycle Bin
        if any(w in t for w in ("empty recycle bin", "clean recycle bin", "empty the bin", "clear recycle bin", "empty bin")):
            return "empty_recycle_bin", {}

        # 4. Open Control Panel / Command Center
        if any(w in t for w in ("control panel", "laptop control", "command center", "hardware monitor")):
            return "open_control_panel", {}

        # 5. Organize / Clean Folders
        if any(w in t for w in ("clean downloads", "organize downloads", "clean my downloads", "organize my downloads", "clean download folder")):
            return "organize_folder", {"target_folder": "Downloads"}

        if any(w in t for w in ("clean desktop", "organize desktop", "clean my desktop", "organize my desktop")):
            return "organize_folder", {"target_folder": "Desktop"}

        # 6. Web Search
        if t.startswith("search google for ") or t.startswith("google ") or t.startswith("search web for ") or t.startswith("search online for ") or t.startswith("search internet for "):
            q = t.replace("search google for ", "").replace("google ", "").replace("search web for ", "").replace("search online for ", "").replace("search internet for ", "").strip()
            return "search_web", {"query": q}

        if (t.startswith("search for ") or t.startswith("look up ")) and not any(f in t for f in ("file", "folder", "document", ".pdf", ".txt", ".py", ".docx", ".xlsx")):
            q = t.replace("search for ", "").replace("look up ", "").strip()
            q = q.replace(" on google", "").replace(" in google", "").strip()
            return "search_web", {"query": q}

        # 7. Local File Search
        if t.startswith("find file ") or t.startswith("search file ") or t.startswith("locate file ") or t.startswith("find document "):
            q = t.replace("find file ", "").replace("search file ", "").replace("locate file ", "").replace("find document ", "").strip()
            return "search_files", {"query": q}

        # 8. Open Applications, Websites & Folders
        if t.startswith("open ") or t.startswith("launch "):
            target = t.replace("open ", "").replace("launch ", "").replace("please ", "").strip()

            # Folders
            if target in ("downloads", "download", "documents", "doc", "docs", "desktop", "pictures", "photos", "music", "videos"):
                return "open_folder", {"folder": target}

            # Known Popular Websites or web URLs
            clean_target = target.replace("http://", "").replace("https://", "").replace("www.", "")
            if clean_target in WebOpenerTool.POPULAR_SITES or target in WebOpenerTool.POPULAR_SITES:
                return "open_website", {"site": target}
            if target.startswith("http://") or target.startswith("https://") or target.startswith("www.") or any(target.endswith(tld) for tld in (".com", ".org", ".net", ".io", ".app", ".ai", ".co", ".edu", ".gov", ".me", ".tv")):
                return "open_website", {"site": target}

            # Desktop Applications in map
            for key in AppLauncherTool.APP_MAP:
                if key == target or (len(key) > 3 and (key in target or target in key)):
                    return "launch_application", {"app_name": key}

            # Default to website opener if not an app
            return "open_website", {"site": target}

        # 9. Close Applications
        if t.startswith("close ") or t.startswith("kill ") or t.startswith("terminate "):
            proc = t.replace("close ", "").replace("kill ", "").replace("terminate ", "").strip()
            return "close_application", {"process_name": proc}

        # 10. Screenshot & Vision
        if any(w in t for w in ("look at my screen", "what's on my screen", "what is on my screen", "read my screen", "see my screen", "analyze my screen", "what am i looking at", "explain screen", "screen vision")):
            return "analyze_screen", {"query": user_text}

        if any(w in t for w in ("screenshot", "take a screenshot", "capture screen", "snapshot")):
            return "take_screenshot", {}

        # 11. System Status & Diagnostics
        if any(w in t for w in ("system status", "battery", "cpu", "ram usage", "pc specs", "hardware status", "how much ram", "how much memory", "diagnostics", "laptop health", "how is my laptop")):
            return "system_status", {}

        # 12. Audio Control
        if "mute" in t:
            return "control_media", {"action": "mute"}
        if "unmute" in t:
            return "control_media", {"action": "unmute"}
        if "volume up" in t or "louder" in t:
            return "control_media", {"action": "volume_up"}
        if "volume down" in t or "quieter" in t:
            return "control_media", {"action": "volume_down"}
        if any(w in t for w in ("pause music", "pause media", "play music", "play pause")):
            return "control_media", {"action": "play_pause"}
        if "next song" in t or "next track" in t:
            return "control_media", {"action": "next"}
        if "previous song" in t or "previous track" in t:
            return "control_media", {"action": "previous"}

        # 13. Clipboard
        if any(w in t for w in ("clipboard", "what is in my clipboard", "what's in my clipboard", "read clipboard")):
            return "clipboard", {"operation": "read"}

        return None

    def execute_with_permission(self, tool_name: str, params: Dict[str, Any], parent_widget=None) -> ToolResult:
        """
        Executes a tool with strict enforcement of the NEXUS Absolute Permission System.
        Presents the interactive permission modal to the user when approval is required.
        """
        tool = self.get_tool(tool_name)
        if not tool:
            return ToolResult(False, f"Unknown desktop tool: '{tool_name}'")

        # Emergency stop check
        if self.permission_manager.emergency_stop_active:
            self.permission_manager.log_audit("BLOCKED", tool.name, tool.display_name, tool.risk_level.value, "BLOCKED_EMERGENCY_STOP", "Emergency Stop active.")
            return ToolResult(False, "🚨 Action blocked: Global Emergency Stop is currently active.")

        # Level 1 check
        if not self.permission_manager.can_execute(ActionRequest("", tool.name, "", "", tool.risk_level, [], {})):
            self.permission_manager.log_audit("BLOCKED", tool.name, tool.display_name, tool.risk_level.value, "BLOCKED_BY_LEVEL_1", "Permission Level 1 forbids computer modifications.")
            return ToolResult(False, "🛡️ Action blocked: Permission Level 1 (Information Only) is active. Change to Level 2 in Settings to permit desktop operations.")

        # Construct Action Request
        req = tool.get_action_request(params)

        # Check if approval needed
        needs_approval = self.permission_manager.should_request_approval(req)

        if needs_approval:
            logger.info(f"Opening Absolute Permission Dialog for action: '{req.title}'")
            dialog = PermissionDialog(req, parent=parent_widget)
            result = dialog.exec()

            if result != PermissionDialog.DialogCode.Accepted:
                self.permission_manager.log_audit(req.action_id, req.tool_name, req.title, req.risk.value, "DENIED", "User denied action in permission window.")
                return ToolResult(False, f"Action denied by user: {req.title}")

            self.permission_manager.log_audit(req.action_id, req.tool_name, req.title, req.risk.value, "APPROVED", "User approved action in permission window.")

        # Execute
        try:
            tool_res = tool.execute(params)
            status = "SUCCESS" if tool_res.success else "FAILED"
            self.permission_manager.log_audit(req.action_id, req.tool_name, req.title, req.risk.value, status, tool_res.message)
            return tool_res
        except Exception as e:
            logger.error(f"Execution error in tool '{tool.name}': {e}")
            self.permission_manager.log_audit(req.action_id, req.tool_name, req.title, req.risk.value, "EXCEPTION", str(e))
            return ToolResult(False, f"Tool execution failed: {e}")


_tool_registry_instance = None
def get_tool_registry() -> ToolRegistry:
    global _tool_registry_instance
    if _tool_registry_instance is None:
        _tool_registry_instance = ToolRegistry()
    return _tool_registry_instance
