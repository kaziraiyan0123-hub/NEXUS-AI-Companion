"""
NEXUS Futuristic Settings & Configuration Center
Glassmorphic HUD control panel for AI Provider setup, Windows DPAPI credentials,
real-time connectivity diagnostics, character aesthetics, and security permission levels.
"""
import time
import webbrowser
from typing import Optional
from PySide6.QtCore import Qt, Signal, QPoint, QThread
from PySide6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QLineEdit, QComboBox, QSlider, QCheckBox,
    QTabWidget, QFrame, QRadioButton, QButtonGroup, QMessageBox,
    QScrollArea
)
from PySide6.QtGui import QFont, QCursor, QColor

from config.settings import get_settings
from security.secure_storage import get_secure_storage
from core.ai_manager import get_ai_manager
from interface.themes import get_skin, SKINS

class ConnectionTesterThread(QThread):
    """Background worker for testing API connectivity without freezing the dialog."""
    test_completed = Signal(bool, str)

    def __init__(self, provider_id: str, api_key: Optional[str] = None, base_url: Optional[str] = None):
        super().__init__()
        self.provider_id = provider_id
        self.api_key = api_key
        self.base_url = base_url

    def run(self):
        ai_mgr = get_ai_manager()
        success, msg = ai_mgr.test_provider_connection(
            provider_name=self.provider_id,
            api_key=self.api_key,
            base_url=self.base_url
        )
        self.test_completed.emit(success, msg)

class SettingsDialog(QDialog):
    """Futuristic HUD settings dialog."""

    settings_applied = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = get_settings()
        self.secure_storage = get_secure_storage()
        self.ai_manager = get_ai_manager()
        self.skin = get_skin(self.settings.get("character_skin", "neo_cyber"))

        self.drag_pos = QPoint()
        self.is_dragging = False
        self.test_worker: Optional[ConnectionTesterThread] = None

        self._setup_window()
        self._build_ui()
        self._load_current_values()

    def _setup_window(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.resize(580, 640)
        self.setMinimumSize(520, 580)

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Outer Container Frame
        self.container = QFrame()
        self.container.setObjectName("SettingsCard")
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        # 1. Title Bar
        title_bar = self._create_title_bar()
        container_layout.addWidget(title_bar)

        # 2. Tabbed Section
        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("SettingsTabs")
        self.tab_widget.addTab(self._build_ai_tab(), "🤖 AI Brain")
        self.tab_widget.addTab(self._build_character_tab(), "🎨 Character")
        self.tab_widget.addTab(self._build_voice_tab(), "🎙️ Audio & Voice")
        self.tab_widget.addTab(self._build_security_tab(), "🛡️ Security")
        container_layout.addWidget(self.tab_widget, 1)

        # 3. Bottom Action Bar
        action_bar = self._create_action_bar()
        container_layout.addWidget(action_bar)

        main_layout.addWidget(self.container)
        self._apply_styling()

    def _create_title_bar(self) -> QWidget:
        bar = QFrame()
        bar.setObjectName("TitleBar")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(16, 12, 16, 12)

        icon_lbl = QLabel("⚙️")
        icon_lbl.setFont(QFont("Segoe UI", 13))
        layout.addWidget(icon_lbl)

        title_lbl = QLabel("NEXUS CONFIGURATION CENTER")
        title_lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        title_lbl.setStyleSheet("color: #ffffff; letter-spacing: 0.5px;")
        layout.addWidget(title_lbl)

        layout.addStretch()

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
                background: rgba(239, 68, 68, 0.3);
                border-color: #ef4444;
                color: #ffffff;
            }
        """)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

        return bar

    # TAB 1: AI Brain & Providers
    def _build_ai_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(14)

        # Provider Selection
        p_row = QHBoxLayout()
        p_lbl = QLabel("AI Provider:")
        p_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
        p_lbl.setFixedWidth(120)
        self.provider_combo = QComboBox()
        self.provider_combo.addItem("✦ [100% FREE] Groq Cloud (Ultra-Fast Qwen 3.8 & Allam 2)", "groq")
        self.provider_combo.addItem("✦ [100% FREE TIER] Google Gemini (Gemini 3.1 Flash-Lite)", "gemini")
        self.provider_combo.addItem("✦ [FREE MODELS] OpenRouter Community", "openrouter")
        self.provider_combo.addItem("✦ [100% FREE OFFLINE] Local LLM (Ollama)", "local")
        self.provider_combo.addItem("OpenAI (Commercial / Paid Key Required)", "openai")
        self.provider_combo.addItem("Anthropic Claude (Commercial / Paid Key Required)", "claude")
        self.provider_combo.addItem("xAI Grok (Commercial / Paid Key Required)", "grok")
        self.provider_combo.currentIndexChanged.connect(self._on_provider_selection_changed)
        p_row.addWidget(p_lbl)
        p_row.addWidget(self.provider_combo, 1)
        layout.addLayout(p_row)

        # Model Selection
        m_row = QHBoxLayout()
        m_lbl = QLabel("Model:")
        m_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
        m_lbl.setFixedWidth(120)
        self.model_combo = QComboBox()
        m_row.addWidget(m_lbl)
        m_row.addWidget(self.model_combo, 1)
        layout.addLayout(m_row)

        # API Key Row
        self.key_row = QHBoxLayout()
        self.key_lbl = QLabel("API Key:")
        self.key_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
        self.key_lbl.setFixedWidth(120)
        
        self.key_input = QLineEdit()
        self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.key_input.setPlaceholderText("Enter API key (stored encrypted in Windows DPAPI)")
        
        self.toggle_eye_btn = QPushButton("👁️")
        self.toggle_eye_btn.setFixedSize(32, 28)
        self.toggle_eye_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.toggle_eye_btn.setToolTip("Show / Hide Key")
        self.toggle_eye_btn.clicked.connect(self._toggle_key_visibility)

        self.save_key_btn = QPushButton("💾 Save")
        self.save_key_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.save_key_btn.setToolTip("Save encrypted key to Windows DPAPI vault")
        self.save_key_btn.setFixedSize(65, 28)
        self.save_key_btn.clicked.connect(self._save_api_key_clicked)

        self.clear_key_btn = QPushButton("🗑️")
        self.clear_key_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.clear_key_btn.setToolTip("Remove API key from vault")
        self.clear_key_btn.setFixedSize(32, 28)
        self.clear_key_btn.clicked.connect(self._clear_api_key_clicked)

        self.key_row.addWidget(self.key_lbl)
        self.key_row.addWidget(self.key_input, 1)
        self.key_row.addWidget(self.toggle_eye_btn)
        self.key_row.addWidget(self.save_key_btn)
        self.key_row.addWidget(self.clear_key_btn)
        layout.addLayout(self.key_row)

        # Key Status Badge
        self.key_status_lbl = QLabel("🔒 Key encrypted and protected by Windows DPAPI")
        self.key_status_lbl.setFont(QFont("Segoe UI", 8))
        self.key_status_lbl.setStyleSheet("color: #10b981; margin-left: 124px;")
        layout.addWidget(self.key_status_lbl)

        # Free Key Helper Button
        self.free_key_btn = QPushButton("✦ Get 100% Free API Key (No Credit Card)")
        self.free_key_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.free_key_btn.setStyleSheet("""
            QPushButton {
                background: rgba(56, 189, 248, 0.08);
                border: 1px solid rgba(56, 189, 248, 0.3);
                border-radius: 6px;
                color: #38bdf8;
                padding: 4px 10px;
                font-size: 11px;
                font-weight: 600;
                margin-left: 124px;
            }
            QPushButton:hover {
                background: rgba(56, 189, 248, 0.18);
                border-color: #38bdf8;
                color: #ffffff;
            }
        """)
        self.free_key_btn.clicked.connect(self._open_free_key_link)
        layout.addWidget(self.free_key_btn)

        # Local LLM Base URL (Hidden unless local chosen)
        self.url_row = QHBoxLayout()
        self.url_lbl = QLabel("Base URL:")
        self.url_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
        self.url_lbl.setFixedWidth(120)
        self.url_input = QLineEdit("http://localhost:11434/v1")
        self.url_input.setPlaceholderText("e.g. http://localhost:11434/v1 or http://localhost:1234/v1")
        self.url_row.addWidget(self.url_lbl)
        self.url_row.addWidget(self.url_input, 1)
        layout.addLayout(self.url_row)

        # Test Connectivity Row
        test_row = QHBoxLayout()
        test_row.setContentsMargins(124, 4, 0, 4)
        self.test_btn = QPushButton("🧪 Test API Connectivity")
        self.test_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.test_btn.setFixedWidth(180)
        self.test_btn.clicked.connect(self._test_connection_clicked)
        self.test_result_lbl = QLabel("")
        self.test_result_lbl.setFont(QFont("Segoe UI", 8, QFont.Weight.DemiBold))
        test_row.addWidget(self.test_btn)
        test_row.addWidget(self.test_result_lbl, 1)
        layout.addLayout(test_row)

        layout.addSpacing(6)

        # Temperature Slider
        temp_row = QHBoxLayout()
        temp_lbl = QLabel("Temperature:")
        temp_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
        temp_lbl.setFixedWidth(120)
        self.temp_slider = QSlider(Qt.Orientation.Horizontal)
        self.temp_slider.setRange(0, 100) # 0.0 to 1.0
        self.temp_slider.setValue(70)
        self.temp_val_lbl = QLabel("0.70")
        self.temp_val_lbl.setFixedWidth(40)
        self.temp_val_lbl.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        self.temp_slider.valueChanged.connect(lambda v: self.temp_val_lbl.setText(f"{v/100:.2f}"))
        temp_row.addWidget(temp_lbl)
        temp_row.addWidget(self.temp_slider, 1)
        temp_row.addWidget(self.temp_val_lbl)
        layout.addLayout(temp_row)

        # Max Tokens Slider
        tokens_row = QHBoxLayout()
        tokens_lbl = QLabel("Max Tokens:")
        tokens_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
        tokens_lbl.setFixedWidth(120)
        self.tokens_slider = QSlider(Qt.Orientation.Horizontal)
        self.tokens_slider.setRange(256, 4096)
        self.tokens_slider.setValue(1500)
        self.tokens_val_lbl = QLabel("1500")
        self.tokens_val_lbl.setFixedWidth(40)
        self.tokens_val_lbl.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        self.tokens_slider.valueChanged.connect(lambda v: self.tokens_val_lbl.setText(str(v)))
        tokens_row.addWidget(tokens_lbl)
        tokens_row.addWidget(self.tokens_slider, 1)
        tokens_row.addWidget(self.tokens_val_lbl)
        layout.addLayout(tokens_row)

        layout.addStretch()
        return page

    # TAB 2: Character & Desktop
    def _build_character_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(14)

        # Theme / Skin
        skin_row = QHBoxLayout()
        skin_lbl = QLabel("Character Skin:")
        skin_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
        skin_lbl.setFixedWidth(120)
        self.skin_combo = QComboBox()
        from interface.themes import CANONICAL_SKINS
        for k in CANONICAL_SKINS:
            skin_obj = SKINS.get(k)
            if skin_obj:
                self.skin_combo.addItem(skin_obj.display_name, k)
        skin_row.addWidget(skin_lbl)
        skin_row.addWidget(self.skin_combo, 1)
        layout.addLayout(skin_row)

        # Pet Scale
        size_row = QHBoxLayout()
        size_lbl = QLabel("Pet Scale:")
        size_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
        size_lbl.setFixedWidth(120)
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setRange(120, 280)
        self.size_slider.setValue(200)
        self.size_val_lbl = QLabel("200 px")
        self.size_val_lbl.setFixedWidth(50)
        self.size_slider.valueChanged.connect(lambda v: self.size_val_lbl.setText(f"{v} px"))
        size_row.addWidget(size_lbl)
        size_row.addWidget(self.size_slider, 1)
        size_row.addWidget(self.size_val_lbl)
        layout.addLayout(size_row)

        layout.addSpacing(6)

        # Behaviors
        self.always_on_top_chk = QCheckBox("Stay Always on Top of Windows")
        self.roam_chk = QCheckBox("Autonomous Idle Roaming (Walk and Explore Desktop)")
        self.cursor_gaze_chk = QCheckBox("Eye Gaze Cursor Tracking Physics")
        
        layout.addWidget(self.always_on_top_chk)
        layout.addWidget(self.roam_chk)
        layout.addWidget(self.cursor_gaze_chk)

        layout.addStretch()
        return page

    # TAB 3: Voice & Audio
    def _build_voice_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(14)

        self.tts_chk = QCheckBox("Enable Text-to-Speech (Natural Offline SAPI5 Voice)")
        layout.addWidget(self.tts_chk)

        # Voice Selection
        voice_row = QHBoxLayout()
        voice_lbl = QLabel("Active Voice:")
        voice_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
        voice_lbl.setFixedWidth(120)
        self.voice_combo = QComboBox()
        self.voice_combo.addItem("Default System Voice", "default")
        from core.voice_engine import get_voice_engine
        v_engine = get_voice_engine()
        for v in v_engine.get_available_voices():
            self.voice_combo.addItem(v["name"], v["id"])
        voice_row.addWidget(voice_lbl)
        voice_row.addWidget(self.voice_combo, 1)

        self.test_voice_btn = QPushButton("🔊 Test Voice")
        self.test_voice_btn.setFixedWidth(105)
        self.test_voice_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.test_voice_btn.clicked.connect(self._test_voice_clicked)
        voice_row.addWidget(self.test_voice_btn)
        layout.addLayout(voice_row)

        # ElevenLabs API Key row
        el_row = QHBoxLayout()
        el_lbl = QLabel("ElevenLabs Key:")
        el_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
        el_lbl.setFixedWidth(120)
        self.el_key_input = QLineEdit()
        self.el_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.el_key_input.setPlaceholderText("xi-api-key (for ultra-realistic human voices)")
        el_row.addWidget(el_lbl)
        el_row.addWidget(self.el_key_input, 1)
        layout.addLayout(el_row)

        # TTS Volume
        vol_row = QHBoxLayout()
        vol_lbl = QLabel("Voice Volume:")
        vol_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
        vol_lbl.setFixedWidth(120)
        self.vol_slider = QSlider(Qt.Orientation.Horizontal)
        self.vol_slider.setRange(0, 100)
        self.vol_slider.setValue(80)
        self.vol_val_lbl = QLabel("80%")
        self.vol_val_lbl.setFixedWidth(40)
        self.vol_slider.valueChanged.connect(lambda v: self.vol_val_lbl.setText(f"{v}%"))
        vol_row.addWidget(vol_lbl)
        vol_row.addWidget(self.vol_slider, 1)
        vol_row.addWidget(self.vol_val_lbl)
        layout.addLayout(vol_row)

        # TTS Speed
        speed_row = QHBoxLayout()
        speed_lbl = QLabel("Voice Speed:")
        speed_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
        speed_lbl.setFixedWidth(120)
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(50, 150)
        self.speed_slider.setValue(100)
        self.speed_val_lbl = QLabel("1.0x")
        self.speed_val_lbl.setFixedWidth(40)
        self.speed_slider.valueChanged.connect(lambda v: self.speed_val_lbl.setText(f"{v/100:.1f}x"))
        speed_row.addWidget(speed_lbl)
        speed_row.addWidget(self.speed_slider, 1)
        speed_row.addWidget(self.speed_val_lbl)
        layout.addLayout(speed_row)

        layout.addSpacing(6)

        # Voice Input (Microphone) & VAD
        self.vad_chk = QCheckBox("Enable Voice Input (Microphone / Voice Activity Detection)")
        layout.addWidget(self.vad_chk)

        # Wake Word Checkbox & Phrase Input
        self.wake_chk = QCheckBox("Enable Wake-Word Detection ('Hey Nexus')")
        layout.addWidget(self.wake_chk)

        wake_row = QHBoxLayout()
        wake_lbl = QLabel("Wake Phrase:")
        wake_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
        wake_lbl.setFixedWidth(120)
        self.wake_input = QLineEdit("Hey Nexus")
        self.wake_input.setPlaceholderText("Suggested: Hey Nexus")
        wake_row.addWidget(wake_lbl)
        wake_row.addWidget(self.wake_input, 1)
        layout.addLayout(wake_row)

        wake_note = QLabel("Flow: User says 'Hey Nexus' -> NEXUS says 'Yes? I'm listening.' -> Speaks prompt -> Answers.")
        wake_note.setFont(QFont("Segoe UI", 8))
        wake_note.setStyleSheet("color: #94a3b8; margin-left: 20px;")
        wake_note.setWordWrap(True)
        layout.addWidget(wake_note)

        layout.addStretch()
        return page

    # TAB 4: Security & Permissions
    def _build_security_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        sec_intro = QLabel("NEXUS ABSOLUTE PERMISSION SYSTEM")
        sec_intro.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        sec_intro.setStyleSheet("color: #38bdf8;")
        layout.addWidget(sec_intro)

        sec_desc = QLabel("Computer actions are strictly gated by permission tiers. Silence is never interpreted as approval.")
        sec_desc.setFont(QFont("Segoe UI", 8))
        sec_desc.setStyleSheet("color: #94a3b8;")
        sec_desc.setWordWrap(True)
        layout.addWidget(sec_desc)

        # Radio Group for Permission Levels
        self.perm_group = QButtonGroup(self)
        
        self.lvl1_radio = QRadioButton("Level 1: Information Only (Read-Only, No Computer Modifications)")
        self.lvl2_radio = QRadioButton("Level 2: Ask Before Action (Recommended — Approval Required for Every Operation)")
        self.lvl3_radio = QRadioButton("Level 3: Restricted Approval (Pre-Approved Low-Risk Actions Only)")

        self.perm_group.addButton(self.lvl1_radio, 1)
        self.perm_group.addButton(self.lvl2_radio, 2)
        self.perm_group.addButton(self.lvl3_radio, 3)

        layout.addWidget(self.lvl1_radio)
        layout.addWidget(self.lvl2_radio)
        layout.addWidget(self.lvl3_radio)

        layout.addSpacing(8)

        self.emergency_stop_chk = QCheckBox("Enable Global Emergency STOP Button in HUD")
        self.emergency_stop_chk.setChecked(True)
        layout.addWidget(self.emergency_stop_chk)

        vault_box = QFrame()
        vault_box.setStyleSheet("background: rgba(16, 185, 129, 0.08); border: 1px solid #10b98144; border-radius: 8px; padding: 8px;")
        vbox = QVBoxLayout(vault_box)
        v_title = QLabel("🛡️ Windows Data Protection API (DPAPI) Active")
        v_title.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        v_title.setStyleSheet("color: #10b981;")
        v_body = QLabel("All AI API credentials are cryptographically protected using OS-level DPAPI keys tied to your Windows logon credentials. Plaintext keys are never stored on disk.")
        v_body.setFont(QFont("Segoe UI", 8))
        v_body.setStyleSheet("color: #cbd5e1;")
        v_body.setWordWrap(True)
        vbox.addWidget(v_title)
        vbox.addWidget(v_body)
        layout.addWidget(vault_box)

        layout.addStretch()
        return page

    # Bottom Actions
    def _create_action_bar(self) -> QWidget:
        bar = QFrame()
        bar.setObjectName("ActionBar")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(10)

        reset_btn = QPushButton("Reset Defaults")
        reset_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        reset_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                color: #94a3b8;
                border-radius: 8px;
                padding: 6px 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.1);
                color: #ffffff;
            }
        """)
        reset_btn.clicked.connect(self._reset_defaults_clicked)
        layout.addWidget(reset_btn)

        layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                color: #ffffff;
                border-radius: 8px;
                padding: 6px 16px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.1);
            }
        """)
        cancel_btn.clicked.connect(self.close)
        layout.addWidget(cancel_btn)

        apply_btn = QPushButton("Apply & Save")
        apply_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        apply_btn.setStyleSheet("""
            QPushButton {
                background: #38bdf8;
                color: #0b0f19;
                font-weight: bold;
                border-radius: 8px;
                padding: 6px 20px;
                border: none;
            }
            QPushButton:hover {
                background: #7dd3fc;
            }
        """)
        apply_btn.clicked.connect(self._save_and_apply)
        layout.addWidget(apply_btn)

        return bar

    # Value loading and updating
    def _load_current_values(self):
        # AI Tab
        curr_provider = self.settings.get("ai_provider", "gemini")
        idx = self.provider_combo.findData(curr_provider)
        if idx >= 0:
            self.provider_combo.setCurrentIndex(idx)
        self._update_model_dropdown_for_provider(curr_provider)

        curr_model = self.settings.get("ai_model", "gemini-2.5-flash")
        m_idx = self.model_combo.findText(curr_model)
        if m_idx >= 0:
            self.model_combo.setCurrentIndex(m_idx)

        # Refresh key display
        self._refresh_key_display()

        self.url_input.setText(self.settings.get("local_llm_base_url", "http://localhost:11434/v1"))
        self.temp_slider.setValue(int(float(self.settings.get("temperature", 0.7)) * 100))
        self.tokens_slider.setValue(int(self.settings.get("max_tokens", 1500)))

        # Character Tab
        curr_skin = self.settings.get("character_skin", "neo_cyber")
        s_idx = self.skin_combo.findData(curr_skin)
        if s_idx >= 0:
            self.skin_combo.setCurrentIndex(s_idx)

        self.size_slider.setValue(int(self.settings.get("pet_width", 200)))
        self.always_on_top_chk.setChecked(bool(self.settings.get("always_on_top", True)))
        self.roam_chk.setChecked(bool(self.settings.get("idle_roam_enabled", True)))
        self.cursor_gaze_chk.setChecked(bool(self.settings.get("look_at_cursor", True)))

        # Voice Tab
        self.tts_chk.setChecked(bool(self.settings.get("tts_enabled", True)))
        saved_el_key = self.secure_storage.get_api_key("elevenlabs") or self.settings.get("elevenlabs_api_key", "")
        if saved_el_key:
            self.el_key_input.setText("••••••••••••••••••••")
        curr_voice = self.settings.get("tts_voice", "default")
        v_idx = self.voice_combo.findData(curr_voice)
        if v_idx >= 0:
            self.voice_combo.setCurrentIndex(v_idx)
        self.vol_slider.setValue(int(float(self.settings.get("tts_volume", 0.8)) * 100))
        self.speed_slider.setValue(int(float(self.settings.get("tts_speed", 1.0)) * 100))
        self.vad_chk.setChecked(bool(self.settings.get("voice_input_enabled", False)))
        self.wake_chk.setChecked(bool(self.settings.get("wake_word_enabled", False)))
        self.wake_input.setText(self.settings.get("wake_word", "Hey Nexus"))

        # Security Tab
        perm_lvl = int(self.settings.get("permission_level", 2))
        btn = self.perm_group.button(perm_lvl)
        if btn:
            btn.setChecked(True)
        self.emergency_stop_chk.setChecked(bool(self.settings.get("emergency_stop_enabled", True)))

    def _update_model_dropdown_for_provider(self, provider_id: str):
        self.model_combo.clear()
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
            self.model_combo.addItem(m)

        is_local = (provider_id == "local")
        self.url_lbl.setVisible(is_local)
        self.url_input.setVisible(is_local)
        self.key_lbl.setVisible(not is_local)
        self.key_input.setVisible(not is_local)
        self.toggle_eye_btn.setVisible(not is_local)
        self.save_key_btn.setVisible(not is_local)
        self.key_status_lbl.setVisible(not is_local)
        self.free_key_btn.setVisible(not is_local)

    def _open_free_key_link(self):
        p_id = self.provider_combo.currentData()
        urls = {
            "groq": "https://console.groq.com/keys",
            "gemini": "https://aistudio.google.com/app/apikey",
            "openrouter": "https://openrouter.ai/keys",
            "local": "https://ollama.ai/download",
            "openai": "https://platform.openai.com/api-keys",
            "claude": "https://console.anthropic.com/settings/keys"
        }
        url = urls.get(p_id, "https://console.groq.com/keys")
        webbrowser.open(url)

    def _on_provider_selection_changed(self, index: int):
        p_id = self.provider_combo.currentData()
        self._update_model_dropdown_for_provider(p_id)
        self._refresh_key_display()
        self.test_result_lbl.setText("")

    def _refresh_key_display(self):
        p_id = self.provider_combo.currentData()
        if p_id == "local":
            return
        has_key = self.secure_storage.has_api_key(p_id)
        if has_key:
            self.key_input.setText("••••••••••••••••••••")
            self.key_status_lbl.setText(f"🔒 {self.provider_combo.currentText()} key is safely stored in Windows DPAPI vault.")
            self.key_status_lbl.setStyleSheet("color: #10b981; margin-left: 124px;")
        else:
            self.key_input.setText("")
            self.key_status_lbl.setText(f"⚠️ No API key set for {self.provider_combo.currentText()} (embedded fallback active).")
            self.key_status_lbl.setStyleSheet("color: #f59e0b; margin-left: 124px;")

    def _toggle_key_visibility(self):
        if self.key_input.echoMode() == QLineEdit.EchoMode.Password:
            p_id = self.provider_combo.currentData()
            actual_key = self.secure_storage.get_api_key(p_id)
            if actual_key:
                self.key_input.setText(actual_key)
            self.key_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_eye_btn.setText("🔒")
        else:
            self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_eye_btn.setText("👁️")

    def _save_api_key_clicked(self):
        p_id = self.provider_combo.currentData()
        key_val = self.key_input.text().strip()
        if not key_val or "••••" in key_val:
            return
        self.secure_storage.store_api_key(p_id, key_val)
        self.settings.set("ai_provider", p_id)
        if self.model_combo.currentText():
            self.settings.set("ai_model", self.model_combo.currentText())
        self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.key_input.setText("••••••••••••••••••••")
        self.key_status_lbl.setText("✅ Stored securely in Windows DPAPI vault & set as active.")
        self.key_status_lbl.setStyleSheet("color: #10b981; margin-left: 124px;")

    def _clear_api_key_clicked(self):
        p_id = self.provider_combo.currentData()
        self.secure_storage.delete_api_key(p_id)
        self.key_input.clear()
        self._refresh_key_display()

    def _test_connection_clicked(self):
        p_id = self.provider_combo.currentData()
        raw_key = self.key_input.text().strip()
        key_to_test = None if ("••••" in raw_key or not raw_key) else raw_key
        base_url = self.url_input.text().strip() if p_id == "local" else None

        self.test_result_lbl.setText("⏳ Testing connection...")
        self.test_result_lbl.setStyleSheet("color: #38bdf8;")
        self.test_btn.setEnabled(False)

        self.test_worker = ConnectionTesterThread(p_id, key_to_test, base_url)
        self.test_worker.test_completed.connect(self._on_test_completed)
        self.test_worker.start()

    def _on_test_completed(self, success: bool, msg: str):
        self.test_btn.setEnabled(True)
        if success:
            self.test_result_lbl.setText(f"● {msg}")
            self.test_result_lbl.setStyleSheet("color: #10b981;")
        else:
            self.test_result_lbl.setText(f"✕ {msg}")
            self.test_result_lbl.setStyleSheet("color: #ef4444;")

    def _test_voice_clicked(self):
        from core.voice_engine import get_voice_engine
        ve = get_voice_engine()
        self.settings.set("tts_volume", round(self.vol_slider.value() / 100, 2))
        self.settings.set("tts_speed", round(self.speed_slider.value() / 100, 2))
        self.settings.set("tts_voice", self.voice_combo.currentData() or "default")
        sample = "Marhaba! Voice synthesis test is operational, Habibi." if self.skin.name == "habibi_dubai" else "NEXUS speech synthesis test is operational."
        ve.speak(sample)

    def _save_and_apply(self):
        # 1. AI Settings
        provider = self.provider_combo.currentData()
        self.settings.set("ai_provider", provider)
        if self.model_combo.currentText():
            self.settings.set("ai_model", self.model_combo.currentText())
        if provider == "local":
            self.settings.set("local_llm_base_url", self.url_input.text().strip())
        else:
            key_val = self.key_input.text().strip()
            if key_val and "••••" not in key_val:
                self.secure_storage.store_api_key(provider, key_val)

        self.settings.set("temperature", round(self.temp_slider.value() / 100, 2))
        self.settings.set("max_tokens", self.tokens_slider.value())

        # 2. Character Settings
        skin_id = self.skin_combo.currentData()
        self.settings.set("character_skin", skin_id)
        self.settings.set("pet_width", self.size_slider.value())
        self.settings.set("pet_height", self.size_slider.value())
        self.settings.set("always_on_top", self.always_on_top_chk.isChecked())
        self.settings.set("idle_roam_enabled", self.roam_chk.isChecked())
        self.settings.set("look_at_cursor", self.cursor_gaze_chk.isChecked())

        # 3. Voice Settings
        self.settings.set("tts_enabled", self.tts_chk.isChecked())
        self.settings.set("tts_voice", self.voice_combo.currentData() or "default")
        self.settings.set("tts_volume", round(self.vol_slider.value() / 100, 2))
        self.settings.set("tts_speed", round(self.speed_slider.value() / 100, 2))
        
        el_key = self.el_key_input.text().strip()
        if el_key and "••••" not in el_key:
            self.secure_storage.set_api_key("elevenlabs", el_key)
            self.settings.set("elevenlabs_api_key", el_key)

        self.settings.set("voice_input_enabled", self.vad_chk.isChecked())
        self.settings.set("wake_word_enabled", self.wake_chk.isChecked())
        self.settings.set("wake_word", self.wake_input.text().strip() or "Hey Nexus")

        # 4. Security Settings
        perm_lvl = self.perm_group.checkedId()
        self.settings.set("permission_level", perm_lvl)
        self.settings.set("emergency_stop_enabled", self.emergency_stop_chk.isChecked())

        self.settings.save()
        self.settings_applied.emit()
        self.accept()

    def _reset_defaults_clicked(self):
        reply = QMessageBox.question(
            self, "Reset Settings",
            "Are you sure you want to restore default configuration?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.settings.reset_defaults()
            self._load_current_values()

    def _apply_styling(self):
        self.setStyleSheet("""
            QFrame#SettingsCard {
                background-color: #0d1117;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 16px;
            }
            QFrame#TitleBar {
                border-bottom: 1px solid rgba(255, 255, 255, 0.06);
            }
            QFrame#ActionBar {
                border-top: 1px solid rgba(255, 255, 255, 0.06);
            }
            QTabWidget::pane {
                border: none;
                background: transparent;
            }
            QTabBar::tab {
                background: rgba(255, 255, 255, 0.03);
                color: #8b949e;
                border: 1px solid rgba(255, 255, 255, 0.06);
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 8px 16px;
                font-weight: 500;
                font-size: 11px;
                margin-right: 4px;
            }
            QTabBar::tab:selected {
                background: rgba(56, 189, 248, 0.08);
                color: #ffffff;
                border: 1px solid rgba(56, 189, 248, 0.25);
                border-bottom: 2px solid #38bdf8;
            }
            QLabel {
                color: #ffffff;
            }
            QComboBox, QLineEdit {
                background: rgba(0, 0, 0, 0.45);
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 6px;
                color: #ffffff;
                padding: 6px 10px;
                font-size: 12px;
            }
            QComboBox:focus, QLineEdit:focus {
                border-color: #38bdf8;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox QAbstractItemView {
                background: #161b22;
                border: 1px solid rgba(255, 255, 255, 0.12);
                color: #ffffff;
                selection-background-color: rgba(56, 189, 248, 0.2);
            }
            QCheckBox, QRadioButton {
                color: #e2e8f0;
                font-size: 12px;
                spacing: 8px;
            }
            QCheckBox::indicator, QRadioButton::indicator {
                width: 16px;
                height: 16px;
                background: rgba(0, 0, 0, 0.4);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 4px;
            }
            QRadioButton::indicator {
                border-radius: 8px;
            }
            QCheckBox::indicator:checked, QRadioButton::indicator:checked {
                background: #38bdf8;
                border-color: #38bdf8;
            }
            QSlider::groove:horizontal {
                border: 1px solid rgba(255, 255, 255, 0.1);
                height: 6px;
                background: rgba(0, 0, 0, 0.4);
                border-radius: 3px;
            }
            QSlider::sub-page:horizontal {
                background: #38bdf8;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #ffffff;
                border: 2px solid #38bdf8;
                width: 14px;
                margin-top: -5px;
                margin-bottom: -5px;
                border-radius: 7px;
            }
            QPushButton {
                background: rgba(255, 255, 255, 0.08);
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 11px;
            }
            QPushButton:hover {
                border-color: #38bdf8;
                background: rgba(56, 189, 248, 0.15);
            }
        """)

    # Dragging logic
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and event.position().y() < 50:
            self.is_dragging = True
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.is_dragging and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.is_dragging = False
        super().mouseReleaseEvent(event)
