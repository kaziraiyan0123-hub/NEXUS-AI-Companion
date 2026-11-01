"""
NEXUS Laptop Control Panel & Command Center
Comprehensive hardware diagnostics, one-click system controls, AI brain selector,
voice studio, and security permission management for Windows 11.
"""
import os
import time
import ctypes
import webbrowser
import logging
from typing import Optional

from PySide6.QtCore import Qt, QTimer, QPoint, Signal, Slot
from PySide6.QtGui import QFont, QCursor, QColor, QIcon, QPainter, QPen, QBrush
from PySide6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QProgressBar, QSlider, QTabWidget, QFrame,
    QComboBox, QLineEdit, QScrollArea, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox
)

from config.settings import get_settings
from interface.themes import get_skin, CharacterSkin
from security.permission_manager import get_permission_manager, ActionRisk
from security.secure_storage import get_secure_storage
from core.ai_manager import get_ai_manager
from core.desktop_tools import get_tool_registry
from core.voice_engine import get_voice_engine

logger = logging.getLogger("NEXUS.ControlPanel")


class SolidControlCard(QFrame):
    """100% opaque solid background frame to completely prevent desktop bleed-through."""
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor(13, 17, 23, 255)))
        painter.setPen(QPen(QColor(255, 255, 255, 20), 1))
        painter.drawRoundedRect(self.rect().adjusted(0, 0, -1, -1), 16, 16)


class LaptopControlPanel(QDialog):
    """Full-featured Laptop Command Center for NEXUS."""

    def __init__(self, controller=None, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.settings = get_settings()
        self.skin: CharacterSkin = get_skin(self.settings.get("character_skin", "neo_cyber"))
        self.pm = get_permission_manager()
        self.tool_registry = get_tool_registry()
        self.ai_manager = get_ai_manager()
        self.secure_storage = get_secure_storage()
        self.voice_engine = get_voice_engine()

        self.drag_pos = QPoint()

        self._setup_window()
        self._build_ui()
        self._apply_styling()

        # Hardware metrics polling timer (every 1.5 seconds)
        self.metrics_timer = QTimer(self)
        self.metrics_timer.setInterval(1500)
        self.metrics_timer.timeout.connect(self._refresh_hardware_metrics)
        self.metrics_timer.start()

        # Initial refresh
        self._refresh_hardware_metrics()

    def _setup_window(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Window |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.resize(720, 600)
        self.setMinimumSize(600, 500)

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Outer Card (100% opaque solid background)
        self.card = SolidControlCard()
        self.card.setObjectName("ControlPanelCard")
        self.card.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        # 1. Custom Title Bar
        title_bar = self._create_title_bar()
        card_layout.addWidget(title_bar)

        # 2. Main Tabbed Control Center
        self.tabs = QTabWidget()
        self.tabs.setObjectName("ControlTabs")
        self.tabs.addTab(self._build_hardware_tab(), "💻 Laptop Hardware")
        self.tabs.addTab(self._build_quick_controls_tab(), "⚡ Laptop Controls")
        self.tabs.addTab(self._build_ai_models_tab(), "🤖 AI Models & Keys")
        self.tabs.addTab(self._build_voice_studio_tab(), "🎙️ Voice Studio")
        self.tabs.addTab(self._build_security_tab(), "🛡️ Security & Audit")
        card_layout.addWidget(self.tabs, 1)

        # 3. Emergency Status Bar at Bottom
        status_bar = self._create_status_bar()
        card_layout.addWidget(status_bar)

        main_layout.addWidget(self.card)

    def _create_title_bar(self) -> QWidget:
        bar = QFrame()
        bar.setObjectName("TitleBar")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(18, 12, 18, 12)

        icon_lbl = QLabel("💻")
        icon_lbl.setFont(QFont("Segoe UI Emoji", 14))
        layout.addWidget(icon_lbl)

        title_lbl = QLabel("NEXUS LAPTOP COMMAND CENTER")
        title_lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        title_lbl.setStyleSheet("color: #f0f6fc; font-weight: 700; letter-spacing: 0.5px;")
        layout.addWidget(title_lbl)

        layout.addStretch()

        # Desktop Companion Enter / Exit Power Toggle
        is_active = getattr(self.controller, "is_active", True) if self.controller else True
        btn_text = "⚡ COMPANION: ACTIVE (ON)" if is_active else "💤 COMPANION: OFF (DISMISSED)"
        btn_color = "#10b981" if is_active else "#ef4444"
        self.power_toggle_btn = QPushButton(btn_text)
        self.power_toggle_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.power_toggle_btn.setStyleSheet(f"""
            QPushButton {{
                background: {btn_color}22;
                border: 1px solid {btn_color};
                color: {btn_color};
                border-radius: 6px;
                padding: 4px 10px;
                font-size: 11px;
                font-weight: bold;
                margin-right: 8px;
            }}
            QPushButton:hover {{
                background: {btn_color}44;
            }}
        """)
        self.power_toggle_btn.clicked.connect(self._toggle_companion_power)
        layout.addWidget(self.power_toggle_btn)

        # Emergency stop indicator
        self.estop_status_lbl = QLabel("● SYSTEM SECURE")
        self.estop_status_lbl.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        self.estop_status_lbl.setStyleSheet("color: #10b981; margin-right: 12px;")
        layout.addWidget(self.estop_status_lbl)

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(26, 26)
        close_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        close_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                color: #94a3b8;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(239, 68, 68, 0.35);
                border-color: #ef4444;
                color: #ffffff;
            }
        """)
        close_btn.clicked.connect(self.hide)
        layout.addWidget(close_btn)

        return bar

    # TAB 1: Real-time Hardware Diagnostics
    def _build_hardware_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(22, 18, 22, 18)
        layout.setSpacing(16)

        header = QLabel("REAL-TIME LAPTOP HARDWARE MONITOR")
        header.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        header.setStyleSheet("color: #94a3b8; letter-spacing: 0.5px;")
        layout.addWidget(header)

        # Metrics Grid (CPU, RAM, Battery, Storage)
        grid_frame = QFrame()
        grid_frame.setObjectName("MetricsGrid")
        grid_layout = QVBoxLayout(grid_frame)
        grid_layout.setContentsMargins(16, 14, 16, 14)
        grid_layout.setSpacing(14)

        # 1. CPU Load
        cpu_row = QHBoxLayout()
        cpu_lbl = QLabel("CPU Load:")
        cpu_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
        cpu_lbl.setFixedWidth(100)
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setRange(0, 100)
        self.cpu_bar.setTextVisible(False)
        self.cpu_val = QLabel("0%")
        self.cpu_val.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.cpu_val.setFixedWidth(50)
        cpu_row.addWidget(cpu_lbl)
        cpu_row.addWidget(self.cpu_bar, 1)
        cpu_row.addWidget(self.cpu_val)
        grid_layout.addLayout(cpu_row)

        # 2. RAM Memory
        ram_row = QHBoxLayout()
        ram_lbl = QLabel("RAM Memory:")
        ram_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
        ram_lbl.setFixedWidth(100)
        self.ram_bar = QProgressBar()
        self.ram_bar.setRange(0, 100)
        self.ram_bar.setTextVisible(False)
        self.ram_val = QLabel("0 GB / 0 GB")
        self.ram_val.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.ram_val.setFixedWidth(110)
        ram_row.addWidget(ram_lbl)
        ram_row.addWidget(self.ram_bar, 1)
        ram_row.addWidget(self.ram_val)
        grid_layout.addLayout(ram_row)

        # 3. Battery / Power
        bat_row = QHBoxLayout()
        bat_lbl = QLabel("Battery / AC:")
        bat_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
        bat_lbl.setFixedWidth(100)
        self.bat_bar = QProgressBar()
        self.bat_bar.setRange(0, 100)
        self.bat_bar.setTextVisible(False)
        self.bat_val = QLabel("100% (AC)")
        self.bat_val.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.bat_val.setFixedWidth(110)
        bat_row.addWidget(bat_lbl)
        bat_row.addWidget(self.bat_bar, 1)
        bat_row.addWidget(self.bat_val)
        grid_layout.addLayout(bat_row)

        # 4. Storage Disk (C:)
        disk_row = QHBoxLayout()
        disk_lbl = QLabel("Storage (C:):")
        disk_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
        disk_lbl.setFixedWidth(100)
        self.disk_bar = QProgressBar()
        self.disk_bar.setRange(0, 100)
        self.disk_bar.setTextVisible(False)
        self.disk_val = QLabel("0 GB Free")
        self.disk_val.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.disk_val.setFixedWidth(110)
        disk_row.addWidget(disk_lbl)
        disk_row.addWidget(self.disk_bar, 1)
        disk_row.addWidget(self.disk_val)
        grid_layout.addLayout(disk_row)

        layout.addWidget(grid_frame)

        # Hardware Note
        note = QLabel("⚡ Hardware metrics are streamed directly from Windows kernel via psutil.")
        note.setFont(QFont("Segoe UI", 8))
        note.setStyleSheet("color: #64748b;")
        layout.addWidget(note)

        layout.addStretch()
        return page

    # TAB 2: Laptop Controls & Quick Launchers
    def _build_quick_controls_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(22, 18, 22, 18)
        layout.setSpacing(14)

        header = QLabel("ONE-CLICK LAPTOP OPERATIONS")
        header.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        header.setStyleSheet("color: #94a3b8;")
        layout.addWidget(header)

        # Audio Volume Bar
        vol_box = QFrame()
        vol_box.setObjectName("ControlBox")
        vb_layout = QHBoxLayout(vol_box)
        vb_layout.setContentsMargins(14, 10, 14, 10)

        vol_lbl = QLabel("🔊 System Volume:")
        vol_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
        self.vol_slider = QSlider(Qt.Orientation.Horizontal)
        self.vol_slider.setRange(0, 100)
        self.vol_slider.setValue(75)

        mute_btn = QPushButton("🔇 Mute / Unmute")
        mute_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        mute_btn.clicked.connect(lambda: self._exec_tool("control_media", {"action": "mute"}))

        vb_layout.addWidget(vol_lbl)
        vb_layout.addWidget(self.vol_slider, 1)
        vb_layout.addWidget(mute_btn)
        layout.addWidget(vol_box)

        # Quick System Action Buttons Grid
        btn_grid = QVBoxLayout()
        btn_grid.setSpacing(10)

        r1 = QHBoxLayout()
        lock_btn = QPushButton("🔒 Lock Laptop")
        lock_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        lock_btn.clicked.connect(self._lock_laptop)

        shot_btn = QPushButton("📸 Take Screenshot")
        shot_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        shot_btn.clicked.connect(lambda: self._exec_tool("take_screenshot", {}))

        clean_btn = QPushButton("📁 Organize Downloads")
        clean_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        clean_btn.clicked.connect(lambda: self._exec_tool("organize_folder", {"target_folder": "Downloads"}))

        r1.addWidget(lock_btn)
        r1.addWidget(shot_btn)
        r1.addWidget(clean_btn)
        btn_grid.addLayout(r1)

        r2 = QHBoxLayout()
        task_btn = QPushButton("📊 Task Manager")
        task_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        task_btn.clicked.connect(lambda: self._exec_tool("launch_application", {"app_name": "taskmgr"}))

        note_btn = QPushButton("📝 Notepad")
        note_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        note_btn.clicked.connect(lambda: self._exec_tool("launch_application", {"app_name": "notepad"}))

        term_btn = QPushButton("💻 Windows Terminal")
        term_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        term_btn.clicked.connect(lambda: self._exec_tool("launch_application", {"app_name": "terminal"}))

        r2.addWidget(task_btn)
        r2.addWidget(note_btn)
        r2.addWidget(term_btn)
        btn_grid.addLayout(r2)

        r3 = QHBoxLayout()
        recycle_btn = QPushButton("🗑️ Empty Recycle Bin")
        recycle_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        recycle_btn.clicked.connect(self._empty_recycle_bin)

        settings_btn = QPushButton("⚙️ Windows Settings")
        settings_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        settings_btn.clicked.connect(lambda: self._exec_tool("launch_application", {"app_name": "settings"}))

        exp_btn = QPushButton("📂 File Explorer")
        exp_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        exp_btn.clicked.connect(lambda: self._exec_tool("launch_application", {"app_name": "explorer"}))

        r3.addWidget(recycle_btn)
        r3.addWidget(settings_btn)
        r3.addWidget(exp_btn)
        btn_grid.addLayout(r3)

        layout.addLayout(btn_grid)

        # Companion Presence & VIP Card
        vip_box = QFrame()
        vip_box.setObjectName("ControlBox")
        vb_layout = QVBoxLayout(vip_box)
        vb_layout.setContentsMargins(14, 12, 14, 12)
        vb_layout.setSpacing(10)

        vip_title = QLabel("✦ DESKTOP COMPANION PRESENCE & AFFECTION")
        vip_title.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        vip_title.setStyleSheet("color: #e2e8f0;")
        vb_layout.addWidget(vip_title)

        vp_r1 = QHBoxLayout()
        enter_btn = QPushButton("⚡ Summon NEXUS (Turn ON)")
        enter_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        enter_btn.clicked.connect(self._turn_companion_on)

        exit_btn = QPushButton("💤 Dismiss NEXUS (Turn OFF)")
        exit_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        exit_btn.clicked.connect(self._turn_companion_off)

        shortcut_btn = QPushButton("📌 Refresh Desktop Icon")
        shortcut_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        shortcut_btn.clicked.connect(self._create_desktop_shortcut_clicked)

        vp_r1.addWidget(enter_btn)
        vp_r1.addWidget(exit_btn)
        vp_r1.addWidget(shortcut_btn)
        vb_layout.addLayout(vp_r1)

        vp_r2 = QHBoxLayout()
        pet_btn = QPushButton("💖 Pet NEXUS (+5 XP)")
        pet_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        pet_btn.clicked.connect(self._pet_clicked)

        five_btn = QPushButton("✋ High-Five (+10 XP)")
        five_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        five_btn.clicked.connect(self._five_clicked)

        cheer_btn = QPushButton("⭐ Sparkle Cheer")
        cheer_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        cheer_btn.clicked.connect(self._cheer_clicked)

        vp_r2.addWidget(pet_btn)
        vp_r2.addWidget(five_btn)
        vp_r2.addWidget(cheer_btn)
        vb_layout.addLayout(vp_r2)

        layout.addWidget(vip_box)
        layout.addStretch()
        return page

    # TAB 3: AI Models & Free Keys
    def _build_ai_models_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(22, 18, 22, 18)
        layout.setSpacing(14)

        header = QLabel("AI BRAIN & MODEL CONFIGURATION")
        header.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        header.setStyleSheet("color: #94a3b8;")
        layout.addWidget(header)

        # Provider Selector
        p_row = QHBoxLayout()
        p_lbl = QLabel("AI Provider:")
        p_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
        p_lbl.setFixedWidth(110)
        self.p_combo = QComboBox()
        self.p_combo.addItem("✦ [100% FREE] Groq Cloud (Ultra-Fast Qwen 3.8 & Allam 2)", "groq")
        self.p_combo.addItem("✦ [100% FREE TIER] Google Gemini (Gemini 3.1 Flash-Lite)", "gemini")
        self.p_combo.addItem("✦ [FREE MODELS] OpenRouter Community", "openrouter")
        self.p_combo.addItem("✦ [100% FREE OFFLINE] Local LLM (Ollama)", "local")
        self.p_combo.addItem("OpenAI (Commercial / Paid Key Required)", "openai")
        self.p_combo.addItem("Anthropic Claude (Commercial / Paid Key Required)", "claude")
        self.p_combo.addItem("xAI Grok (Commercial / Paid Key Required)", "grok")
        self.p_combo.currentIndexChanged.connect(self._on_provider_changed)
        p_row.addWidget(p_lbl)
        p_row.addWidget(self.p_combo, 1)
        layout.addLayout(p_row)

        # Model Selector
        m_row = QHBoxLayout()
        m_lbl = QLabel("AI Model:")
        m_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
        m_lbl.setFixedWidth(110)
        self.m_combo = QComboBox()
        m_row.addWidget(m_lbl)
        m_row.addWidget(self.m_combo, 1)
        layout.addLayout(m_row)

        # Key Input + DPAPI status
        k_row = QHBoxLayout()
        k_lbl = QLabel("API Key:")
        k_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
        k_lbl.setFixedWidth(110)
        self.k_input = QLineEdit()
        self.k_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.k_input.setPlaceholderText("Paste API key here (protected by Windows DPAPI)")
        
        save_k_btn = QPushButton("💾 Save")
        save_k_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        save_k_btn.setFixedWidth(70)
        save_k_btn.clicked.connect(self._save_key)

        k_row.addWidget(k_lbl)
        k_row.addWidget(self.k_input, 1)
        k_row.addWidget(save_k_btn)
        layout.addLayout(k_row)

        # Free Key Button
        free_btn = QPushButton("✦ Get 100% Free API Key (0$ - No Credit Card Needed)")
        free_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        free_btn.setStyleSheet("""
            QPushButton {
                background: rgba(56, 189, 248, 0.08);
                border: 1px solid rgba(56, 189, 248, 0.3);
                border-radius: 6px;
                color: #38bdf8;
                padding: 6px 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: rgba(56, 189, 248, 0.18);
                border-color: #38bdf8;
                color: #ffffff;
            }
        """)
        free_btn.clicked.connect(self._open_free_key_portal)
        layout.addWidget(free_btn)

        self.k_status_lbl = QLabel("🔒 Vault Status: Ready")
        self.k_status_lbl.setFont(QFont("Segoe UI", 8))
        self.k_status_lbl.setStyleSheet("color: #10b981; margin-left: 114px;")
        layout.addWidget(self.k_status_lbl)

        layout.addStretch()

        # Load initial values
        curr_p = self.settings.get("ai_provider", "groq")
        p_idx = self.p_combo.findData(curr_p)
        if p_idx >= 0:
            self.p_combo.setCurrentIndex(p_idx)
        self._update_models(curr_p)

        return page

    # TAB 4: Voice Studio
    def _build_voice_studio_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(22, 18, 22, 18)
        layout.setSpacing(14)

        header = QLabel("NEURAL VOICE & HANDS-FREE STUDIO")
        header.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        header.setStyleSheet("color: #94a3b8;")
        layout.addWidget(header)

        # Voice Selector
        v_row = QHBoxLayout()
        v_lbl = QLabel("Active Voice:")
        v_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
        v_lbl.setFixedWidth(110)
        self.v_combo = QComboBox()
        for v in self.voice_engine.get_available_voices():
            self.v_combo.addItem(v["name"], v["id"])
        
        # Select active voice from settings
        curr_voice = self.settings.get("tts_voice", "default")
        idx = self.v_combo.findData(curr_voice)
        if idx >= 0:
            self.v_combo.setCurrentIndex(idx)
        self.v_combo.currentIndexChanged.connect(self._on_voice_changed)
        v_row.addWidget(v_lbl)
        v_row.addWidget(self.v_combo, 1)
        layout.addLayout(v_row)

        # ElevenLabs Real Human Voice API Key Box
        el_box = QFrame()
        el_box.setObjectName("ControlBox")
        el_layout = QVBoxLayout(el_box)
        el_layout.setContentsMargins(12, 10, 12, 10)
        el_layout.setSpacing(6)

        el_lbl = QLabel("✨ ElevenLabs Realistic Voice Engine (Optional API Key):")
        el_lbl.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        el_lbl.setStyleSheet("color: #38bdf8;")
        el_layout.addWidget(el_lbl)

        el_row = QHBoxLayout()
        self.el_key_input = QLineEdit()
        self.el_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.el_key_input.setPlaceholderText("Paste ElevenLabs API key here (xi-api-key)")
        saved_el_key = self.secure_storage.get_api_key("elevenlabs") or self.settings.get("elevenlabs_api_key", "")
        if saved_el_key:
            self.el_key_input.setText("••••••••••••••••••••")

        save_el_btn = QPushButton("💾 Save Key")
        save_el_btn.setFixedWidth(85)
        save_el_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        save_el_btn.clicked.connect(self._save_elevenlabs_key)
        el_row.addWidget(self.el_key_input, 1)
        el_row.addWidget(save_el_btn)
        el_layout.addLayout(el_row)

        el_note = QLabel("Tip: Edge Neural Voices work 100% free with zero keys. Add ElevenLabs for studio-grade human realism.")
        el_note.setFont(QFont("Segoe UI", 8))
        el_note.setStyleSheet("color: #64748b;")
        el_layout.addWidget(el_note)
        layout.addWidget(el_box)

        # Speed and Volume
        s_row = QHBoxLayout()
        s_lbl = QLabel("Speed & Volume:")
        s_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
        s_lbl.setFixedWidth(110)
        self.v_vol_slider = QSlider(Qt.Orientation.Horizontal)
        self.v_vol_slider.setRange(20, 100)
        self.v_vol_slider.setValue(int(float(self.settings.get("tts_volume", 0.9)) * 100))
        s_row.addWidget(s_lbl)
        s_row.addWidget(self.v_vol_slider, 1)
        layout.addLayout(s_row)

        # Hands-free Wake Word toggle
        self.wake_chk = QPushButton("🎙️ Continuous Wake-Word: ACTIVE ('Hey Nexus')")
        self.wake_chk.setCheckable(True)
        self.wake_chk.setChecked(bool(self.settings.get("wake_word_enabled", True)))
        self.wake_chk.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.wake_chk.clicked.connect(self._toggle_wake_word)
        layout.addWidget(self.wake_chk)

        test_v_btn = QPushButton("🔊 Test Natural Voice")
        test_v_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        test_v_btn.clicked.connect(self._test_voice)
        layout.addWidget(test_v_btn)

        layout.addStretch()
        return page

    # TAB 5: Security & Audit Log
    def _build_security_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(22, 18, 22, 18)
        layout.setSpacing(14)

        header = QLabel("ABSOLUTE PERMISSION SYSTEM & AUDIT TRAIL")
        header.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        header.setStyleSheet("color: #94a3b8;")
        layout.addWidget(header)

        # Level indicator
        lvl_row = QHBoxLayout()
        lvl_lbl = QLabel("Permission Mode:")
        lvl_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
        self.lvl_combo = QComboBox()
        self.lvl_combo.addItem("Level 1: Information Only (No computer changes)", 1)
        self.lvl_combo.addItem("Level 2: Ask Before Action (Strict Consent - Default)", 2)
        self.lvl_combo.addItem("Level 3: Restricted (Low risk pre-approved)", 3)
        self.lvl_combo.setCurrentIndex(1)
        self.lvl_combo.currentIndexChanged.connect(self._on_permission_level_changed)
        lvl_row.addWidget(lvl_lbl)
        lvl_row.addWidget(self.lvl_combo, 1)
        layout.addLayout(lvl_row)

        # Emergency Stop Action
        estop_btn = QPushButton("🚨 TRIGGER GLOBAL EMERGENCY STOP")
        estop_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        estop_btn.setStyleSheet("""
            QPushButton {
                background: rgba(239, 68, 68, 0.2);
                border: 1.5px solid #ef4444;
                border-radius: 8px;
                color: #ffffff;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton:hover {
                background: #ef4444;
            }
        """)
        estop_btn.clicked.connect(self._trigger_estop)
        layout.addWidget(estop_btn)

        # Audit History Table
        audit_lbl = QLabel("Recent Security Audit Entries:")
        audit_lbl.setFont(QFont("Segoe UI", 8, QFont.Weight.DemiBold))
        audit_lbl.setStyleSheet("color: #94a3b8;")
        layout.addWidget(audit_lbl)

        self.audit_table = QTableWidget(0, 4)
        self.audit_table.setHorizontalHeaderLabels(["Time", "Tool", "Action", "Status"])
        self.audit_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.audit_table.setStyleSheet("""
            QTableWidget {
                background: rgba(15, 23, 42, 0.6);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 6px;
                color: #cbd5e1;
            }
        """)
        layout.addWidget(self.audit_table, 1)

        self._refresh_audit_table()
        return page

    def _create_status_bar(self) -> QWidget:
        bar = QFrame()
        bar.setStyleSheet("background: rgba(0, 0, 0, 0.25); border-top: 1px solid rgba(255, 255, 255, 0.06);")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(18, 8, 18, 8)

        lbl = QLabel("NEXUS v2.5 • Windows 11 Native Desktop Architecture")
        lbl.setFont(QFont("Segoe UI", 8))
        lbl.setStyleSheet("color: #64748b;")
        layout.addWidget(lbl)

        layout.addStretch()

        reset_estop_btn = QPushButton("Reset Emergency Stop")
        reset_estop_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        reset_estop_btn.setStyleSheet("color: #38bdf8; background: transparent; border: none; font-size: 11px;")
        reset_estop_btn.clicked.connect(self._reset_estop)
        layout.addWidget(reset_estop_btn)

        return bar

    # --- Live Hardware Metrics Refresh ---
    def _refresh_hardware_metrics(self):
        try:
            import psutil
            cpu_p = int(psutil.cpu_percent(interval=None))
            self.cpu_bar.setValue(cpu_p)
            self.cpu_val.setText(f"{cpu_p}%")

            mem = psutil.virtual_memory()
            used_gb = round(mem.used / (1024**3), 1)
            tot_gb = round(mem.total / (1024**3), 1)
            self.ram_bar.setValue(int(mem.percent))
            self.ram_val.setText(f"{used_gb} / {tot_gb} GB")

            bat = psutil.sensors_battery()
            if bat:
                b_pct = int(bat.percent)
                self.bat_bar.setValue(b_pct)
                status = "⚡ Charging" if bat.power_plugged else "Discharging"
                self.bat_val.setText(f"{b_pct}% ({status})")
            else:
                self.bat_bar.setValue(100)
                self.bat_val.setText("100% (AC Direct)")

            disk = psutil.disk_usage("C:\\")
            free_gb = round(disk.free / (1024**3), 1)
            self.disk_bar.setValue(int(disk.percent))
            self.disk_val.setText(f"{free_gb} GB Free")

        except Exception as e:
            logger.debug(f"Metrics update: {e}")

    # --- Quick Operations ---
    def _lock_laptop(self):
        try:
            ctypes.windll.user32.LockWorkStation()
        except Exception as e:
            logger.error(f"Failed to lock workstation: {e}")

    def _empty_recycle_bin(self):
        # Always confirm through permission architecture
        res = QMessageBox.question(
            self,
            "Confirm Empty Recycle Bin",
            "Are you sure you want to permanently delete all items in the Windows Recycle Bin?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if res == QMessageBox.StandardButton.Yes:
            try:
                ctypes.windll.shell32.SHEmptyRecycleBinW(0, None, 7)
                self.pm.log_audit("BIN_EMPTY", "SYSTEM", "Empty Recycle Bin", "destructive", "SUCCESS", "Recycle bin emptied.")
                QMessageBox.information(self, "Success", "Windows Recycle Bin has been emptied.")
            except Exception as e:
                logger.error(f"Error emptying bin: {e}")

    def _exec_tool(self, tool_name: str, params: dict):
        res = self.tool_registry.execute_with_permission(tool_name, params, parent_widget=self)
        if res.success:
            QMessageBox.information(self, "Operation Successful", res.message)
        else:
            QMessageBox.warning(self, "Operation Notice", res.message)
        self._refresh_audit_table()

    # --- AI Models & Key Helpers ---
    def _on_provider_changed(self, idx: int):
        p_id = self.p_combo.currentData()
        self._update_models(p_id)
        has_k = self.secure_storage.has_api_key(p_id)
        if has_k:
            self.k_input.setText("••••••••••••••••••••")
            self.k_status_lbl.setText(f"🔒 {p_id.upper()} key stored securely in Windows DPAPI vault.")
            self.k_status_lbl.setStyleSheet("color: #10b981; margin-left: 114px;")
        else:
            self.k_input.setText("")
            self.k_status_lbl.setText(f"⚠️ No key set for {p_id.upper()} (Free offline brain active).")
            self.k_status_lbl.setStyleSheet("color: #f59e0b; margin-left: 114px;")

    def _update_models(self, provider_id: str):
        self.m_combo.clear()
        models_map = {
            "groq": [
                "llama-3.3-70b-versatile",
                "deepseek-r1-distill-llama-70b",
                "qwen/qwen3.8-27b",
                "llama-3.1-8b-instant",
                "mixtral-8x7b-32768",
                "gemma2-9b-it"
            ],
            "gemini": [
                "gemini-2.5-flash",
                "gemini-2.5-pro",
                "gemini-2.5-flash-lite",
                "gemini-2.0-flash",
                "gemini-1.5-flash",
                "gemini-1.5-pro",
                "gemini-3.1-flash-lite",
                "gemini-3-flash-preview"
            ],
            "openrouter": [
                "meta-llama/llama-3.3-70b-instruct:free",
                "deepseek/deepseek-r1:free",
                "google/gemma-4-31b-it:free",
                "liquid/lfm-2.5-2.6b:free",
                "nvidia/nemotron-3.5-lightning:free",
                "cohere/north-mini-code:free"
            ],
            "local": ["llama3.2", "deepseek-r1:8b", "mistral", "qwen2.5", "phi3"],
            "openai": ["gpt-4o", "gpt-4o-mini", "o3-mini", "o1"],
            "claude": ["claude-3-7-sonnet-20250219", "claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022"],
            "grok": ["grok-2-1212", "grok-2-vision-1212", "grok-beta"]
        }
        for m in models_map.get(provider_id, []):
            self.m_combo.addItem(m)

    def _save_key(self):
        p_id = self.p_combo.currentData()
        key_val = self.k_input.text().strip()
        if key_val and not key_val.startswith("••"):
            self.secure_storage.set_api_key(p_id, key_val)
            self.settings.set("ai_provider", p_id)
            if self.m_combo.currentText():
                self.settings.set("ai_model", self.m_combo.currentText())
            self.settings.save()
            self._on_provider_changed(0)
            QMessageBox.information(self, "Key Stored", f"Your {p_id.upper()} key was encrypted into Windows DPAPI.")

    def _open_free_key_portal(self):
        p_id = self.p_combo.currentData()
        urls = {
            "groq": "https://console.groq.com/keys",
            "gemini": "https://aistudio.google.com/app/apikey",
            "openrouter": "https://openrouter.ai/keys",
            "local": "https://ollama.ai/download"
        }
        webbrowser.open(urls.get(p_id, "https://console.groq.com/keys"))

    # --- Voice & Audio Helpers ---
    def _test_voice(self):
        sample = "Hello! I am NEXUS, your personal autonomous AI desktop companion."
        v_id = self.v_combo.currentData() or "default"
        self.settings.set("tts_voice", v_id)
        self.voice_engine.speak(sample)

    def _on_voice_changed(self, idx: int):
        v_id = self.v_combo.currentData()
        if v_id:
            self.settings.set("tts_voice", v_id)

    def _save_elevenlabs_key(self):
        key = self.el_key_input.text().strip()
        if key and not key.startswith("••"):
            self.secure_storage.set_api_key("elevenlabs", key)
            self.settings.set("elevenlabs_api_key", key)
            self.settings.save()
            QMessageBox.information(self, "ElevenLabs Key Saved", "ElevenLabs API key successfully encrypted and stored.")

    def _toggle_wake_word(self):
        enabled = self.wake_chk.isChecked()
        self.settings.set("wake_word_enabled", enabled)
        self.wake_chk.setText("🎙️ Continuous Wake-Word: ACTIVE ('Hey Nexus')" if enabled else "🎙️ Continuous Wake-Word: DISABLED")

    # --- Security & Emergency Stop ---
    def _on_permission_level_changed(self, idx: int):
        lvl = self.lvl_combo.currentData()
        self.settings.set("permission_level", lvl)
        self.settings.save()

    def _trigger_estop(self):
        self.pm.trigger_emergency_stop()
        self.estop_status_lbl.setText("🚨 EMERGENCY STOP ACTIVE")
        self.estop_status_lbl.setStyleSheet("color: #ef4444; font-weight: bold;")
        self._refresh_audit_table()
        QMessageBox.warning(self, "Emergency Stop", "Global Emergency Stop has been activated. All desktop tools are locked.")

    def _reset_estop(self):
        self.pm.reset_emergency_stop()
        self.estop_status_lbl.setText("● SYSTEM SECURE")
        self.estop_status_lbl.setStyleSheet("color: #10b981; font-weight: bold;")
        self._refresh_audit_table()
        QMessageBox.information(self, "System Reset", "Emergency Stop reset. Operations returned to configured level.")

    def _refresh_audit_table(self):
        entries = self.pm.get_recent_audit_entries(limit=15)
        self.audit_table.setRowCount(len(entries))
        for r, entry in enumerate(reversed(entries)):
            t_str = time.strftime("%H:%M:%S", time.localtime(entry.get("timestamp", time.time())))
            self.audit_table.setItem(r, 0, QTableWidgetItem(t_str))
            self.audit_table.setItem(r, 1, QTableWidgetItem(entry.get("tool_name", "")))
            self.audit_table.setItem(r, 2, QTableWidgetItem(entry.get("title", "")[:25]))
            self.audit_table.setItem(r, 3, QTableWidgetItem(entry.get("status", "")))

    # --- Desktop Presence & VIP Actions ---
    def _toggle_companion_power(self):
        if self.controller:
            self.controller.toggle_power()

    def _turn_companion_on(self):
        if self.controller:
            self.controller.turn_on()

    def _turn_companion_off(self):
        if self.controller:
            self.controller.turn_off()

    def update_power_state(self, is_active: bool):
        """Updates the power button label and color in real time."""
        if hasattr(self, 'power_toggle_btn'):
            btn_text = "⚡ COMPANION: ACTIVE (ON)" if is_active else "💤 COMPANION: OFF (DISMISSED)"
            btn_color = "#10b981" if is_active else "#ef4444"
            self.power_toggle_btn.setText(btn_text)
            self.power_toggle_btn.setStyleSheet(f"""
                QPushButton {{
                    background: {btn_color}22;
                    border: 1px solid {btn_color};
                    color: {btn_color};
                    border-radius: 6px;
                    padding: 4px 10px;
                    font-size: 11px;
                    font-weight: bold;
                    margin-right: 8px;
                }}
                QPushButton:hover {{
                    background: {btn_color}44;
                }}
            """)

    def _create_desktop_shortcut_clicked(self):
        try:
            import subprocess
            cmd = r"""
            $WshShell = New-Object -comObject WScript.Shell
            $DesktopPath = [System.Environment]::GetFolderPath('Desktop')
            $Shortcut = $WshShell.CreateShortcut("$DesktopPath\NEXUS.lnk")
            $Shortcut.TargetPath = "E:\NEXUS\run_nexus.bat"
            $Shortcut.WorkingDirectory = "E:\NEXUS"
            $Shortcut.IconLocation = "E:\NEXUS\nexus_icon.ico,0"
            $Shortcut.Description = "NEXUS — Intelligent AI Desktop Companion & Command Center"
            $Shortcut.Save()
            """
            subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True)
            QMessageBox.information(self, "Desktop Icon Created", "✅ NEXUS shortcut with companion icon has been refreshed on your Windows Desktop!")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to create desktop shortcut: {e}")

    def _get_pet_instance(self):
        if self.controller and hasattr(self.controller, 'pet') and self.controller.pet:
            return self.controller.pet
        return self.controller

    def _pet_clicked(self):
        pet = self._get_pet_instance()
        if pet and hasattr(pet, 'pet_the_pet'):
            pet.pet_the_pet()

    def _five_clicked(self):
        pet = self._get_pet_instance()
        if pet and hasattr(pet, 'high_five'):
            pet.high_five()
        elif pet and hasattr(pet, 'pet_the_pet'):
            pet.pet_the_pet()

    def _cheer_clicked(self):
        pet = self._get_pet_instance()
        if pet and hasattr(pet, 'sparkle_cheer'):
            pet.sparkle_cheer()
        elif pet and hasattr(pet, 'pet_the_pet'):
            pet.pet_the_pet()

    def _apply_styling(self):
        self.setStyleSheet("""
            QFrame#ControlPanelCard {
                background-color: #0d1117;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 16px;
            }
            QFrame#MetricsGrid, QFrame#ControlBox {
                background: rgba(255, 255, 255, 0.02);
                border: 1px solid rgba(255, 255, 255, 0.06);
                border-radius: 10px;
            }
            QProgressBar {
                background: rgba(255, 255, 255, 0.05);
                border-radius: 4px;
                max-height: 8px;
                border: none;
            }
            QProgressBar::chunk {
                background: #38bdf8;
                border-radius: 4px;
            }
            QTabWidget::pane {
                border: none;
                background: transparent;
            }
            QTabBar::tab {
                background: transparent;
                border: none;
                color: #8b949e;
                padding: 8px 16px;
                font-family: 'Segoe UI', system-ui, sans-serif;
                font-size: 12px;
                font-weight: 500;
                margin-right: 4px;
            }
            QTabBar::tab:selected {
                background: rgba(255, 255, 255, 0.05);
                color: #f0f6fc;
                font-weight: 600;
                border-bottom: 2px solid #38bdf8;
                border-radius: 6px;
            }
            QTabBar::tab:hover {
                color: #f0f6fc;
            }
            QPushButton {
                background: rgba(255, 255, 255, 0.04);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 8px;
                color: #f0f6fc;
                padding: 7px 14px;
                font-family: 'Segoe UI', system-ui, sans-serif;
                font-size: 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.08);
                border-color: rgba(255, 255, 255, 0.16);
            }
            QComboBox, QLineEdit {
                background: rgba(255, 255, 255, 0.04);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 8px;
                color: #f0f6fc;
                padding: 6px 12px;
                font-size: 12px;
            }
            QComboBox:focus, QLineEdit:focus {
                border-color: rgba(56, 189, 248, 0.5);
                background: rgba(255, 255, 255, 0.06);
            }
        """)

    # Draggable title bar
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and not self.drag_pos.isNull():
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
        else:
            super().keyPressEvent(event)
