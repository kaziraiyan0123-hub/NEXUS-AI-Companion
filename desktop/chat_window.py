"""
NEXUS Advanced Floating Visual Chat Window
Ultra-advanced glassmorphism HUD interface with persona drawer, multi-thread history,
drag-and-drop file upload, streaming responses, offline voice reading, and model switching.
"""
import os
from typing import Optional, List, Dict, Any
from PySide6.QtCore import Qt, Signal, QPoint, QRect, QTimer, QSize
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTextEdit, QScrollArea, QFileDialog, 
    QFrame, QLineEdit, QComboBox, QApplication, QSplitter,
    QListWidget, QListWidgetItem, QMenu, QInputDialog
)
from PySide6.QtGui import (
    QColor, QFont, QCursor, QIcon, QPainter, 
    QPen, QBrush, QLinearGradient, QDragEnterEvent, QDropEvent
)

from config.settings import get_settings
from core.conversation import ConversationManager, ChatMessage
from interface.themes import get_skin, CharacterSkin
from desktop.chat_bubble_widget import MessageBubbleWidget, ThinkingBubbleWidget
from core.voice_engine import get_voice_engine
from core.memory_manager import get_memory_manager

class ChatInputEdit(QTextEdit):
    """TextEdit that sends on Enter and adds newline on Shift+Enter."""
    send_requested = Signal()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                super().keyPressEvent(event)
            else:
                self.send_requested.emit()
                event.accept()
        else:
            super().keyPressEvent(event)

class SolidHudCard(QFrame):
    """100% opaque solid background frame to completely prevent desktop bleed-through."""
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor(13, 17, 23, 255)))
        painter.setPen(QPen(QColor(255, 255, 255, 20), 1))
        painter.drawRoundedRect(self.rect().adjusted(0, 0, -1, -1), 16, 16)


class AdvancedChatWindow(QWidget):
    """Ultra-advanced futuristic HUD conversational interface for NEXUS."""

    # Signals
    message_sent = Signal(str, list)   # (prompt, attachments)
    voice_toggled = Signal()
    stop_generation_requested = Signal()
    persona_changed = Signal(str)
    speech_active = Signal(bool)
    settings_requested = Signal()
    control_panel_requested = Signal()

    PERSONAS = {
        "companion": ("✦ NEXUS Companion", "Natural, perceptive, witty, and intelligent companion."),
        "architect": ("💻 Senior Architect", "Deep software design, clean code architecture, and high-performance engineering."),
        "academic": ("🎓 Professor & Academic", "Detailed Socratic explanations, homework guidance, and university topic mastery."),
        "productivity": ("📝 Executive Writer", "High-impact emails, business proposals, schedules, and concise executive briefings."),
        "security": ("🛡️ Security Analyst", "Vulnerability auditing, safe permission architecture, and robust cyber defense.")
    }

    def __init__(self, conv_manager: ConversationManager, parent=None):
        super().__init__(parent)
        self.conv_manager = conv_manager
        self.settings = get_settings()
        self.skin = get_skin(self.settings.get("character_skin", "neo_cyber"))
        self.active_persona = "companion"
        
        self.is_generating = False
        self.attached_files = []
        self.thinking_widget = None
        self.streaming_target_widget = None
        self.streaming_full_text = ""
        self.streaming_index = 0
        self.stream_timer = QTimer(self)
        self.stream_timer.setInterval(20) # 50 words per sec fast streaming
        self.stream_timer.timeout.connect(self._step_stream)

        # Enable Drag and Drop
        self.setAcceptDrops(True)

        # Dragging state
        self.drag_pos = QPoint()
        self.is_dragging = False

        # Window styling
        self._setup_window()
        self._build_ui()

        # Load active conversation
        self._load_active_conversation()

    def _setup_window(self):
        flags = Qt.WindowType.FramelessWindowHint
        if self.settings.get("always_on_top", True):
            flags |= Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.resize(520, 680)
        self.setMinimumSize(420, 520)

    def set_skin(self, skin: CharacterSkin):
        self.skin = skin
        self._update_styles()
        self._reload_messages()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Outer HUD Card (100% opaque solid background)
        self.hud_card = SolidHudCard()
        self.hud_card.setObjectName("HudCard")
        self.hud_card.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        hud_layout = QVBoxLayout(self.hud_card)
        hud_layout.setContentsMargins(0, 0, 0, 0)
        hud_layout.setSpacing(0)

        # 1. Custom Title Bar
        title_bar = self._create_title_bar()
        hud_layout.addWidget(title_bar)

        # 2. Search Bar (hidden by default)
        self.search_container = self._create_search_bar()
        self.search_container.setVisible(False)
        hud_layout.addWidget(self.search_container)

        # 3. Center Area with Collapsible Sidebar Drawer
        center_splitter = QHBoxLayout()
        center_splitter.setContentsMargins(0, 0, 0, 0)
        center_splitter.setSpacing(0)

        # Drawer (Sidebar for history and personas)
        self.drawer = self._create_drawer()
        self.drawer.setVisible(False)
        center_splitter.addWidget(self.drawer)

        # Right Main Chat Area
        chat_pane = QWidget()
        chat_pane_layout = QVBoxLayout(chat_pane)
        chat_pane_layout.setContentsMargins(0, 0, 0, 0)
        chat_pane_layout.setSpacing(0)

        # Scroll Area for Messages
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setStyleSheet("background: transparent; border: none;")

        self.messages_container = QWidget()
        self.messages_container.setStyleSheet("background: transparent;")
        self.messages_layout = QVBoxLayout(self.messages_container)
        self.messages_layout.setContentsMargins(6, 8, 6, 8)
        self.messages_layout.setSpacing(10)
        self.messages_layout.addStretch()

        self.scroll_area.setWidget(self.messages_container)
        chat_pane_layout.addWidget(self.scroll_area, 1)

        # Quick Action Chips Row
        quick_chips = self._create_quick_chips()
        chat_pane_layout.addWidget(quick_chips)

        # Attachment Preview Bar
        self.att_container = QWidget()
        self.att_layout = QHBoxLayout(self.att_container)
        self.att_layout.setContentsMargins(12, 4, 12, 4)
        self.att_layout.setSpacing(6)
        self.att_container.setVisible(False)
        chat_pane_layout.addWidget(self.att_container)

        # Voice Visualizer & Status Bar
        self.voice_bar = self._create_voice_bar()
        chat_pane_layout.addWidget(self.voice_bar)

        # Bottom Input Bar
        input_bar = self._create_input_bar()
        chat_pane_layout.addWidget(input_bar)

        center_splitter.addWidget(chat_pane, 1)
        hud_layout.addLayout(center_splitter, 1)

        main_layout.addWidget(self.hud_card)
        self._update_styles()

    def _create_title_bar(self) -> QWidget:
        bar = QFrame()
        bar.setObjectName("TitleBar")
        bar_layout = QHBoxLayout(bar)
        bar_layout.setContentsMargins(14, 10, 14, 10)
        bar_layout.setSpacing(10)

        # 1. Left Brand & User Identity Badge
        left_layout = QHBoxLayout()
        left_layout.setSpacing(8)
        left_layout.setContentsMargins(0, 0, 0, 0)

        self.brand_lbl = QLabel("✦ NEXUS")
        self.brand_lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.brand_lbl.setStyleSheet("color: #ffffff; letter-spacing: 0.5px;")
        left_layout.addWidget(self.brand_lbl)

        self.status_dot = QLabel("●")
        self.status_dot.setStyleSheet("color: #10b981; font-size: 9px;")
        self.status_dot.setToolTip("NEXUS Online & Active")
        left_layout.addWidget(self.status_dot)

        # User Name Pill Badge (Permanent Memory)
        mm = get_memory_manager()
        current_user = mm.get_user_name()
        badge_text = f"👤 {current_user}" if current_user else "👤 Set Name"
        self.user_badge = QPushButton(badge_text)
        self.user_badge.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.user_badge.setToolTip("Click to set or change your name (Permanent Memory)")
        self.user_badge.setStyleSheet("""
            QPushButton {
                background: rgba(56, 189, 248, 0.08);
                color: #38bdf8;
                border: 1px solid rgba(56, 189, 248, 0.25);
                border-radius: 9px;
                padding: 3px 8px;
                font-size: 11px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: rgba(56, 189, 248, 0.18);
                border-color: #38bdf8;
                color: #ffffff;
            }
        """)
        self.user_badge.clicked.connect(self._prompt_change_name)
        left_layout.addWidget(self.user_badge)

        bar_layout.addLayout(left_layout)
        bar_layout.addStretch()

        # 2. Center: Model Selector Pill
        current_model = self.settings.get("ai_model", "gemini-2.5-flash")
        self.model_pill = QPushButton(f"✦ {current_model} ▾")
        self.model_pill.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.model_pill.setToolTip("Click to select AI provider / model")
        self.model_pill.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.04);
                color: #cbd5e1;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 4px 10px;
                font-size: 11px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.08);
                border-color: rgba(255, 255, 255, 0.2);
                color: #ffffff;
            }
        """)
        self.model_pill.clicked.connect(self._open_model_menu)
        bar_layout.addWidget(self.model_pill)

        bar_layout.addStretch()

        # 3. Right: Sleek Action Controls
        right_layout = QHBoxLayout()
        right_layout.setSpacing(6)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # Drawer Toggle Button
        self.drawer_btn = QPushButton("☰")
        self.drawer_btn.setFixedSize(28, 28)
        self.drawer_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.drawer_btn.setToolTip("Toggle Persona & Conversation Drawer")
        self.drawer_btn.setStyleSheet(self._icon_btn_style())
        self.drawer_btn.clicked.connect(self._toggle_drawer)
        right_layout.addWidget(self.drawer_btn)

        # New Chat Button
        new_chat_btn = QPushButton("＋")
        new_chat_btn.setFixedSize(28, 28)
        new_chat_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        new_chat_btn.setToolTip("New Conversation")
        new_chat_btn.setStyleSheet(self._icon_btn_style())
        new_chat_btn.clicked.connect(self._new_chat)
        right_layout.addWidget(new_chat_btn)

        # Laptop Control Panel Button
        cp_btn = QPushButton("⚙️")
        cp_btn.setFixedSize(28, 28)
        cp_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        cp_btn.setToolTip("Open Laptop Command Center & Hardware Diagnostics")
        cp_btn.setStyleSheet(self._icon_btn_style())
        cp_btn.clicked.connect(self.control_panel_requested.emit)
        right_layout.addWidget(cp_btn)

        # Close Button
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(28, 28)
        close_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        close_btn.setToolTip("Close Chat Window")
        close_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.04);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 8px;
                color: #94a3b8;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(239, 68, 68, 0.25);
                border-color: #ef4444;
                color: #ffffff;
            }
        """)
        close_btn.clicked.connect(self.hide)
        right_layout.addWidget(close_btn)

        bar_layout.addLayout(right_layout)
        return bar

    def _update_user_badge(self):
        mm = get_memory_manager()
        name = mm.get_user_name()
        if hasattr(self, 'user_badge'):
            if name:
                self.user_badge.setText(f"👤 {name}")
                self.user_badge.setToolTip(f"User: {name} (Click to change)")
            else:
                self.user_badge.setText("👤 Set Name")
                self.user_badge.setToolTip("Click to introduce yourself to NEXUS")

    def _prompt_change_name(self):
        mm = get_memory_manager()
        curr = mm.get_user_name()
        new_name, ok = QInputDialog.getText(
            self,
            "Your Identity",
            "What should NEXUS call you?",
            QLineEdit.EchoMode.Normal,
            curr
        )
        if ok and new_name.strip():
            clean = new_name.strip()
            mm.set_user_name(clean)
            self._update_user_badge()
            self.post_assistant_response(f"✨ **Pleasure to meet you, {clean}!** I have permanently remembered your name.", stream=True)
            self._speak_message(f"Pleasure to meet you, {clean}! I will remember your name.")

    def _create_drawer(self) -> QWidget:
        """Left collapsible drawer for persona selection and conversation thread history."""
        drawer = QFrame()
        drawer.setFixedWidth(200)
        drawer.setStyleSheet(f"""
            background: rgba(8, 12, 20, 0.95);
            border-right: 1px solid rgba(255, 255, 255, 0.1);
        """)
        layout = QVBoxLayout(drawer)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # Persona Header
        p_lbl = QLabel("AI PERSONA")
        p_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        p_lbl.setStyleSheet("color: #38bdf8;")
        layout.addWidget(p_lbl)

        # Persona Selector Box
        self.persona_combo = QComboBox()
        for p_key, (p_title, _) in self.PERSONAS.items():
            self.persona_combo.addItem(p_title, p_key)
        self.persona_combo.setStyleSheet("""
            QComboBox {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 6px;
                color: #ffffff;
                padding: 4px 8px;
                font-size: 11px;
                font-weight: 500;
            }
        """)
        self.persona_combo.currentIndexChanged.connect(self._on_persona_selected)
        layout.addWidget(self.persona_combo)

        # Divider
        div = QFrame()
        div.setFrameShape(QFrame.Shape.HLine)
        div.setStyleSheet("background: rgba(255, 255, 255, 0.06);")
        layout.addWidget(div)

        # Conversation History Header
        h_row = QHBoxLayout()
        h_lbl = QLabel("CONVERSATIONS")
        h_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        h_lbl.setStyleSheet("color: #38bdf8;")
        h_row.addWidget(h_lbl)
        h_row.addStretch()

        add_chat_btn = QPushButton("＋")
        add_chat_btn.setFixedSize(20, 20)
        add_chat_btn.setStyleSheet(self._icon_btn_style())
        add_chat_btn.clicked.connect(self._new_chat)
        h_row.addWidget(add_chat_btn)
        layout.addLayout(h_row)

        # List Widget for past chats
        self.conv_list_widget = QListWidget()
        self.conv_list_widget.setStyleSheet("""
            QListWidget {
                background: transparent;
                border: none;
                color: #cbd5e1;
                font-size: 11.5px;
            }
            QListWidget::item {
                padding: 6px 8px;
                border-radius: 6px;
                margin-bottom: 2px;
            }
            QListWidget::item:selected {
                background: rgba(56, 189, 248, 0.15);
                color: #ffffff;
                border: 1px solid rgba(56, 189, 248, 0.35);
            }
        """)
        self.conv_list_widget.itemClicked.connect(self._on_conv_item_clicked)
        layout.addWidget(self.conv_list_widget, 1)

        # Export Button at bottom of drawer
        export_btn = QPushButton("💾 Export Markdown")
        export_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        export_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.04);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 6px;
                color: #94a3b8;
                padding: 5px;
                font-size: 11px;
            }
            QPushButton:hover {
                background: rgba(56, 189, 248, 0.15);
                border-color: #38bdf8;
                color: #ffffff;
            }
        """)
        export_btn.clicked.connect(self._export_chat_markdown)
        layout.addWidget(export_btn)

        return drawer

    def _toggle_drawer(self):
        new_vis = self.drawer.isHidden()
        self.drawer.setVisible(new_vis)
        if new_vis:
            self._refresh_conv_list()

    def _refresh_conv_list(self):
        self.conv_list_widget.clear()
        for conv in self.conv_manager.list_conversations():
            item = QListWidgetItem(f"💬 {conv.title}")
            item.setData(Qt.ItemDataRole.UserRole, conv.id)
            if conv.id == self.conv_manager.active_id:
                item.setSelected(True)
            self.conv_list_widget.addItem(item)

    def _on_conv_item_clicked(self, item: QListWidgetItem):
        conv_id = item.data(Qt.ItemDataRole.UserRole)
        self.conv_manager.set_active(conv_id)
        self._load_active_conversation()

    def _on_persona_selected(self, index: int):
        p_key = self.persona_combo.currentData()
        self.active_persona = p_key
        p_title, p_desc = self.PERSONAS.get(p_key, ("Assistant", ""))
        self.persona_changed.emit(p_key)
        self.post_assistant_response(f"🎭 **Persona switched to {p_title}**.\n\n*{p_desc}*")

    def _export_chat_markdown(self):
        active_conv = self.conv_manager.get_active()
        lines = [f"# {active_conv.title}\n\n*Exported from NEXUS AI Companion*\n"]
        for msg in active_conv.messages:
            prefix = "### 👤 User" if msg.role == "user" else "### 💠 NEXUS"
            lines.append(f"{prefix}\n\n{msg.content}\n\n---\n")

        save_path, _ = QFileDialog.getSaveFileName(
            self, "Export Conversation", f"{active_conv.title[:20]}.md", "Markdown (*.md)"
        )
        if save_path:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))

    def _open_model_menu(self):
        from core.ai_manager import get_ai_manager
        ai_mgr = get_ai_manager()

        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background: #161b22;
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 10px;
                color: #ffffff;
                padding: 6px;
            }
            QMenu::item {
                padding: 6px 18px;
                border-radius: 6px;
                color: #e2e8f0;
            }
            QMenu::item:selected {
                background: rgba(56, 189, 248, 0.15);
                color: #38bdf8;
            }
            QMenu::separator {
                height: 1px;
                background: rgba(255, 255, 255, 0.08);
                margin: 4px 8px;
            }
        """)

        providers = ai_mgr.get_supported_providers()
        for prov in providers:
            p_menu = menu.addMenu(f"✦ {prov['name']}")
            p_menu.setStyleSheet(menu.styleSheet())
            for m in prov["models"]:
                action = p_menu.addAction(m)
                def make_handler(model_id=m, provider_id=prov["id"]):
                    return lambda *args, mod=model_id, pid=provider_id: self._set_model(mod, pid)
                action.triggered.connect(make_handler())

        menu.addSeparator()
        settings_action = menu.addAction("⚙️  Configure AI Providers & Keys...")
        settings_action.triggered.connect(self.settings_requested.emit)

        menu.exec(self.model_pill.mapToGlobal(QPoint(0, self.model_pill.height() + 4)))

    def _set_model(self, model_id: str, provider_id: Optional[str] = None):
        if provider_id:
            self.settings.set("ai_provider", provider_id)
        self.settings.set("ai_model", model_id)
        self.model_pill.setText(f"✦ {model_id}")
        self.post_assistant_response(f"⚡ **AI Model switched to `{model_id}`** ({provider_id.upper() if provider_id else 'Active Provider'}).")

    def _create_search_bar(self) -> QWidget:
        container = QFrame()
        container.setStyleSheet("background: rgba(15, 23, 42, 0.7); border-bottom: 1px solid rgba(255,255,255,0.08);")
        layout = QHBoxLayout(container)
        layout.setContentsMargins(14, 6, 14, 6)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search messages in this thread...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background: rgba(0, 0, 0, 0.4);
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 6px;
                color: #ffffff;
                padding: 4px 10px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #38bdf8;
            }
        """)
        self.search_input.textChanged.connect(self._on_search_query_changed)
        layout.addWidget(self.search_input)

        close_s_btn = QPushButton("✕")
        close_s_btn.setFixedSize(22, 22)
        close_s_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        close_s_btn.setStyleSheet("background: transparent; color: #94a3b8; border: none; font-size: 11px;")
        close_s_btn.clicked.connect(self._toggle_search)
        layout.addWidget(close_s_btn)

        return container

    def _create_quick_chips(self) -> QWidget:
        chips_bar = QFrame()
        chips_bar.setStyleSheet("background: transparent; border-top: 1px solid rgba(255,255,255,0.04);")
        layout = QHBoxLayout(chips_bar)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(6)

        chips = [
            ("👁️ Vision", "NEXUS, look at my screen and tell me what you see."),
            ("💻 Code", "Can you explain how this code works?\n```\n\n```"),
            ("⚡ Summarize", "Please summarize this topic: "),
            ("📝 Draft", "Draft a professional email regarding: "),
            ("✨ Ask", "What are your top recommendations for: ")
        ]

        for label, prompt in chips:
            btn = QPushButton(label)
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.setStyleSheet("""
                QPushButton {
                    background: rgba(255, 255, 255, 0.03);
                    border: 1px solid rgba(255, 255, 255, 0.08);
                    border-radius: 10px;
                    color: #8b949e;
                    padding: 3px 8px;
                    font-size: 11px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background: rgba(56, 189, 248, 0.1);
                    border-color: rgba(56, 189, 248, 0.3);
                    color: #ffffff;
                }
            """)
            def make_handler(p=prompt):
                return lambda: self._apply_chip_prompt(p)
            btn.clicked.connect(make_handler())
            layout.addWidget(btn)

        layout.addStretch()
        return chips_bar

    def _create_voice_bar(self) -> QWidget:
        container = QFrame()
        container.setStyleSheet("""
            background: rgba(13, 17, 23, 0.95);
            border-top: 1px solid rgba(56, 189, 248, 0.3);
            border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        """)
        layout = QHBoxLayout(container)
        layout.setContentsMargins(14, 6, 14, 6)
        layout.setSpacing(10)

        self.voice_status_lbl = QLabel("🎙️ Listening...")
        self.voice_status_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.voice_status_lbl.setStyleSheet("color: #38bdf8;")
        layout.addWidget(self.voice_status_lbl)

        self.voice_viz_lbl = QLabel("[                    ]")
        self.voice_viz_lbl.setFont(QFont("Consolas", 9, QFont.Weight.Bold))
        self.voice_viz_lbl.setStyleSheet("color: #10b981; letter-spacing: 1px;")
        layout.addWidget(self.voice_viz_lbl)

        layout.addStretch()

        mute_btn = QPushButton("✕ Mute")
        mute_btn.setFixedSize(56, 22)
        mute_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        mute_btn.setStyleSheet("""
            QPushButton {
                background: rgba(239, 68, 68, 0.2);
                color: #ef4444;
                border: 1px solid rgba(239, 68, 68, 0.4);
                border-radius: 4px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(239, 68, 68, 0.35);
                color: #ffffff;
            }
        """)
        mute_btn.clicked.connect(self.voice_toggled.emit)
        layout.addWidget(mute_btn)

        container.setVisible(False)
        return container

    def set_voice_listening_state(self, state: str):
        """Updates voice HUD controls to reflect listening state."""
        if state == "listening":
            self.voice_bar.setVisible(True)
            self.voice_status_lbl.setText("🎙️ Listening... Speak command (silence sends)")
            self.voice_status_lbl.setStyleSheet("color: #38bdf8; font-weight: bold;")
            self.voice_btn.setStyleSheet("""
                QPushButton {
                    background: rgba(239, 68, 68, 0.35);
                    border: 1.5px solid #ef4444;
                    border-radius: 8px;
                    color: #ffffff;
                }
            """)
        elif state == "transcribing":
            self.voice_bar.setVisible(True)
            self.voice_status_lbl.setText("⚡ Transcribing audio...")
            self.voice_status_lbl.setStyleSheet("color: #38bdf8; font-weight: bold;")
        else:
            self.voice_bar.setVisible(False)
            self.voice_btn.setStyleSheet(self._icon_btn_style())

    def set_voice_level(self, level: float):
        """Updates live audio level visualizer bar."""
        if not self.voice_bar.isHidden():
            bars_count = int(level * 20)
            viz = "❚" * bars_count + " " * (20 - bars_count)
            self.voice_viz_lbl.setText(f"[{viz}]")

    def _create_input_bar(self) -> QWidget:
        box = QFrame()
        box.setObjectName("InputBar")
        layout = QHBoxLayout(box)
        layout.setContentsMargins(12, 8, 12, 10)
        layout.setSpacing(8)

        # Attachment button
        att_btn = QPushButton("📎")
        att_btn.setFixedSize(34, 34)
        att_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        att_btn.setToolTip("Attach file (PDF, TXT, Code, CSV, Image)")
        att_btn.setStyleSheet(self._icon_btn_style())
        att_btn.clicked.connect(self._pick_attachment)
        layout.addWidget(att_btn)

        # Text Input
        self.input_edit = ChatInputEdit()
        self.input_edit.setPlaceholderText("Message NEXUS... (Enter to send, Shift+Enter for newline)")
        self.input_edit.setMaximumHeight(85)
        self.input_edit.setStyleSheet("""
            QTextEdit {
                background: rgba(22, 27, 34, 0.65);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                color: #ffffff;
                padding: 6px 10px;
                font-family: 'Segoe UI', system-ui;
                font-size: 13px;
            }
            QTextEdit:focus {
                border: 1px solid rgba(56, 189, 248, 0.6);
                background: rgba(22, 27, 34, 0.95);
            }
        """)
        self.input_edit.send_requested.connect(self._send_message)
        layout.addWidget(self.input_edit, 1)

        # Voice Toggle Button
        self.voice_btn = QPushButton("🎙️")
        self.voice_btn.setFixedSize(34, 34)
        self.voice_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.voice_btn.setToolTip("Voice Conversation Mode")
        self.voice_btn.setStyleSheet(self._icon_btn_style())
        self.voice_btn.clicked.connect(self.voice_toggled.emit)
        layout.addWidget(self.voice_btn)

        # Send / Stop Button
        self.send_btn = QPushButton("➤")
        self.send_btn.setFixedSize(36, 34)
        self.send_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.send_btn.setStyleSheet("""
            QPushButton {
                background: #38bdf8;
                border: none;
                border-radius: 10px;
                color: #0b0f19;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #7dd3fc;
            }
        """)
        self.send_btn.clicked.connect(self._handle_send_or_stop)
        layout.addWidget(self.send_btn)

        return box

    def _update_styles(self):
        self.hud_card.setStyleSheet("""
            #HudCard {
                background: #0d1117;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 16px;
            }
            #TitleBar {
                border-bottom: 1px solid rgba(255, 255, 255, 0.06);
                background: rgba(22, 27, 34, 0.4);
                border-top-left-radius: 16px;
                border-top-right-radius: 16px;
            }
            #InputBar {
                border-top: 1px solid rgba(255, 255, 255, 0.06);
                background: rgba(13, 17, 23, 0.85);
                border-bottom-left-radius: 16px;
                border-bottom-right-radius: 16px;
            }
        """)

    def _icon_btn_style(self) -> str:
        return """
            QPushButton {
                background: rgba(255, 255, 255, 0.04);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 8px;
                color: #94a3b8;
                font-size: 13px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.09);
                border-color: rgba(255, 255, 255, 0.18);
                color: #ffffff;
            }
        """

    # --- Drag & Drop Support ---
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            fpath = url.toLocalFile()
            if os.path.exists(fpath) and fpath not in self.attached_files:
                self.attached_files.append(fpath)
        self._render_attached_chips()
        event.acceptProposedAction()

    def _apply_chip_prompt(self, template: str):
        self.input_edit.setPlainText(template)
        self.input_edit.setFocus()
        cursor = self.input_edit.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.input_edit.setTextCursor(cursor)
        # If complete prompt without trailing colon/space, send immediately
        if not template.endswith(" ") and not template.endswith("```"):
            self._send_message()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
            event.accept()
        else:
            super().keyPressEvent(event)

    def _pick_attachment(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Attach Files to Conversation",
            "",
            "Documents & Files (*.pdf *.docx *.doc *.pptx *.ppt *.xlsx *.xls *.txt *.csv *.md *.rtf *.py *.js *.ts *.html *.css *.json *.xml *.yaml *.sql *.png *.jpg *.jpeg *.webp);;All Files (*.*)"
        )
        if files:
            for f in files:
                if f not in self.attached_files:
                    self.attached_files.append(f)
            self._render_attached_chips()

    def _render_attached_chips(self):
        while self.att_layout.count():
            item = self.att_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self.attached_files:
            self.att_container.setVisible(False)
            return

        self.att_container.setVisible(True)
        for filepath in self.attached_files:
            fname = os.path.basename(filepath)
            chip = QFrame()
            chip.setStyleSheet("""
                background: rgba(56, 189, 248, 0.1);
                border: 1px solid rgba(56, 189, 248, 0.3);
                border-radius: 6px;
                padding: 1px 6px;
            """)
            c_layout = QHBoxLayout(chip)
            c_layout.setContentsMargins(4, 2, 4, 2)
            c_layout.setSpacing(4)

            lbl = QLabel(f"📄 {fname}")
            lbl.setStyleSheet("color: #38bdf8; font-size: 11px;")
            c_layout.addWidget(lbl)

            rm_btn = QPushButton("✕")
            rm_btn.setFixedSize(16, 16)
            rm_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            rm_btn.setStyleSheet("background: transparent; color: #94a3b8; border: none; font-size: 9px;")
            def make_rm(fp=filepath):
                return lambda: self._remove_attachment(fp)
            rm_btn.clicked.connect(make_rm())
            c_layout.addWidget(rm_btn)

            self.att_layout.addWidget(chip)
        self.att_layout.addStretch()

    def _remove_attachment(self, filepath: str):
        if filepath in self.attached_files:
            self.attached_files.remove(filepath)
        self._render_attached_chips()

    def _handle_send_or_stop(self):
        if self.is_generating:
            self.stream_timer.stop()
            self.stop_generation_requested.emit()
            self.set_generating(False)
        else:
            self._send_message()

    def _send_message(self):
        text = self.input_edit.toPlainText().strip()
        if not text and not self.attached_files:
            return

        mm = get_memory_manager()

        # Check if first-run onboarding needs the user's name
        if not mm.has_user_name() and not self.attached_files:
            name = mm.extract_name(text)
            if name:
                mm.set_user_name(name)
                self.input_edit.clear()
                self._update_user_badge()

                active_conv = self.conv_manager.get_active()
                user_msg = active_conv.add_message("user", text, [])
                self._append_message_widget(user_msg)

                reply = (
                    f"Pleasure to meet you, **{name}**! 🤝\n\n"
                    f"I have permanently committed your name to my memory database. "
                    f"From now on, I will remember you across every session, voice interaction, and task.\n\n"
                    f"What would you like to work on today, {name}?"
                )
                self.post_assistant_response(reply, stream=True)
                self._speak_message(f"Pleasure to meet you, {name}! I will remember your name.")
                return

        if self.stream_timer.isActive():
            self.stream_timer.stop()
            if self.streaming_target_widget:
                self.streaming_target_widget.update_content(self.streaming_full_text)
                self.streaming_target_widget = None

        attachments = list(self.attached_files)
        self.input_edit.clear()
        self.attached_files.clear()
        self._render_attached_chips()

        active_conv = self.conv_manager.get_active()
        user_msg = active_conv.add_message("user", text, attachments)
        self._append_message_widget(user_msg)

        self.set_generating(True)
        self.message_sent.emit(text, attachments)

    def set_generating_state(self, generating: bool):
        self.set_generating(generating)

    def set_generating(self, generating: bool):
        self.is_generating = generating
        if generating:
            self.send_btn.setText("⏹")
            self.send_btn.setStyleSheet("""
                QPushButton {
                    background: #ef4444;
                    border: none;
                    border-radius: 10px;
                    color: #ffffff;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: #f87171;
                }
            """)
            if self.thinking_widget is not None:
                try:
                    self.thinking_widget.deleteLater()
                except Exception:
                    pass
                self.thinking_widget = None

            try:
                self.thinking_widget = ThinkingBubbleWidget(self.skin)
                cnt = self.messages_layout.count()
                self.messages_layout.insertWidget(cnt - 1, self.thinking_widget)
                self._scroll_to_bottom()
            except Exception:
                pass
        else:
            self.send_btn.setText("➤")
            self.send_btn.setStyleSheet("""
                QPushButton {
                    background: #38bdf8;
                    border: none;
                    border-radius: 10px;
                    color: #0b0f19;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: #7dd3fc;
                }
            """)
            if self.thinking_widget is not None:
                try:
                    self.thinking_widget.deleteLater()
                except Exception:
                    pass
                self.thinking_widget = None

    def post_assistant_response(self, text: str, stream: bool = True):
        """Streams assistant response smoothly into message bubble."""
        self.set_generating(False)
        if self.stream_timer.isActive():
            self.stream_timer.stop()
            if self.streaming_target_widget:
                self.streaming_target_widget.update_content(self.streaming_full_text)
                self.streaming_target_widget = None

        active_conv = self.conv_manager.get_active()
        
        if stream:
            # Create empty message and stream into it
            msg = active_conv.add_message("assistant", "")
            widget = MessageBubbleWidget(msg, self.skin)
            widget.regenerate_requested.connect(self._on_regenerate)
            widget.speak_requested.connect(self._speak_message)
            
            cnt = self.messages_layout.count()
            self.messages_layout.insertWidget(cnt - 1, widget)
            
            self.streaming_target_widget = widget
            self.streaming_full_text = text
            self.streaming_index = 0
            self.stream_timer.start()
        else:
            msg = active_conv.add_message("assistant", text)
            self._append_message_widget(msg)

    def _step_stream(self):
        """Typist streaming effect."""
        chunk_size = 6
        self.streaming_index = min(len(self.streaming_full_text), self.streaming_index + chunk_size)
        curr_text = self.streaming_full_text[:self.streaming_index]
        
        if self.streaming_target_widget:
            self.streaming_target_widget.update_content(curr_text)
            if self.streaming_index % 24 == 0 or self.streaming_index >= len(self.streaming_full_text):
                self._scroll_to_bottom()

        if self.streaming_index >= len(self.streaming_full_text):
            self.stream_timer.stop()
            self.streaming_target_widget = None

    def begin_stream_response(self):
        """Initializes empty bubble for real-time background thread token streaming."""
        self.set_generating(True)
        if self.stream_timer.isActive():
            self.stream_timer.stop()
        if self.streaming_target_widget:
            self.streaming_target_widget.update_content(self.streaming_full_text)
            self.streaming_target_widget = None

        if self.thinking_widget is not None:
            try:
                self.thinking_widget.deleteLater()
            except Exception:
                pass
            self.thinking_widget = None

        active_conv = self.conv_manager.get_active()
        msg = active_conv.add_message("assistant", "")
        widget = MessageBubbleWidget(msg, self.skin)
        widget.regenerate_requested.connect(self._on_regenerate)
        widget.speak_requested.connect(self._speak_message)

        cnt = self.messages_layout.count()
        self.messages_layout.insertWidget(cnt - 1, widget)

        self.streaming_target_widget = widget
        self.streaming_full_text = ""
        self._scroll_to_bottom()
        return widget

    def append_stream_token(self, token: str):
        """Appends real-time token from AIWorkerThread to the active stream bubble."""
        if not self.streaming_target_widget:
            self.begin_stream_response()

        self.streaming_full_text += token
        self.streaming_target_widget.update_content(self.streaming_full_text, force=False)
        if len(self.streaming_full_text) % 40 == 0:
            self._scroll_to_bottom()

    def finish_stream_response(self, full_text: str):
        """Finalizes real-time token streaming."""
        self.set_generating(False)
        if self.streaming_target_widget:
            self.streaming_target_widget.update_content(full_text, force=True)
            self.streaming_target_widget = None
        self.streaming_full_text = ""
        self._scroll_to_bottom()

    def _append_message_widget(self, msg: ChatMessage):
        widget = MessageBubbleWidget(msg, self.skin)
        widget.regenerate_requested.connect(self._on_regenerate)
        widget.speak_requested.connect(self._speak_message)
        cnt = self.messages_layout.count()
        self.messages_layout.insertWidget(cnt - 1, widget)
        self._scroll_to_bottom()

    def _scroll_to_bottom(self):
        QTimer.singleShot(40, lambda: self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        ))

    def _speak_message(self, text: str):
        voice = get_voice_engine()
        self.speech_active.emit(True)
        voice.speak(
            text, 
            on_start=lambda: self.speech_active.emit(True),
            on_finish=lambda: self.speech_active.emit(False)
        )

    def _load_active_conversation(self):
        active_conv = self.conv_manager.get_active()
        if not active_conv.messages:
            mm = get_memory_manager()
            if not mm.has_user_name():
                welcome_text = (
                    "✦ **Welcome to NEXUS**\n\n"
                    "I am your autonomous AI desktop companion, designed to work alongside you with speed, intelligence, and precision.\n\n"
                    "Before we begin, **what should I call you?**\n\n"
                    "*Type your name below (or say 'My name is ...') and I will permanently remember you.*"
                )
            else:
                user_name = mm.get_user_name()
                welcome_text = (
                    f"✦ **Welcome back, {user_name}!**\n\n"
                    "NEXUS is ready. How can I assist you right now?\n\n"
                    "• **AI Coding & Architecture**: Refactoring, debugging, and scripts\n"
                    "• **Vision & Screen**: Click '👁️ Vision' to analyze your screen\n"
                    "• **Laptop Control**: Open '⚙️ Control Center' for hardware diagnostics"
                )
            active_conv.add_message("assistant", welcome_text)

        self._reload_messages()

    def _reload_messages(self):
        while self.messages_layout.count() > 1:
            item = self.messages_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        active_conv = self.conv_manager.get_active()
        for msg in active_conv.messages:
            widget = MessageBubbleWidget(msg, self.skin)
            widget.regenerate_requested.connect(self._on_regenerate)
            widget.speak_requested.connect(self._speak_message)
            cnt = self.messages_layout.count()
            self.messages_layout.insertWidget(cnt - 1, widget)
        self._scroll_to_bottom()

    def _new_chat(self):
        conv = self.conv_manager.new_conversation()
        self._load_active_conversation()
        if self.drawer.isVisible():
            self._refresh_conv_list()

    def _toggle_search(self):
        vis = not self.search_container.isVisible()
        self.search_container.setVisible(vis)
        if vis:
            self.search_input.setFocus()
        else:
            self.search_input.clear()
            self._reload_messages()

    def _on_search_query_changed(self, text: str):
        query = text.strip()
        if not query:
            self._reload_messages()
            return
        for i in range(self.messages_layout.count() - 1):
            item = self.messages_layout.itemAt(i)
            if item and item.widget():
                w = item.widget()
                if isinstance(w, MessageBubbleWidget):
                    w.setVisible(query.lower() in w.message.content.lower())

    def _on_regenerate(self, msg_id: str):
        active_conv = self.conv_manager.get_active()
        for i, m in enumerate(active_conv.messages):
            if m.id == msg_id and i > 0:
                user_msg = active_conv.messages[i - 1]
                if user_msg.role == "user":
                    self.set_generating(True)
                    self.message_sent.emit(user_msg.content, user_msg.attachments)
                break

    # --- Window Dragging ---
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if event.position().y() < 60:
                self.is_dragging = True
                self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.is_dragging = False

    def dock_near_pet(self, pet_rect: QRect):
        """Smart docking: positions chat window adjacent to NEXUS without going off-screen."""
        screen = QApplication.primaryScreen()
        avail = screen.availableGeometry() if screen else QRect(0, 0, 1920, 1080)

        target_x = pet_rect.left() - self.width() - 15
        if target_x < avail.left():
            target_x = pet_rect.right() + 15

        target_y = pet_rect.bottom() - self.height()
        if target_y < avail.top():
            target_y = avail.top() + 20

        final_x = min(max(avail.left() + 10, target_x), avail.right() - self.width() - 10)
        final_y = min(max(avail.top() + 10, target_y), avail.bottom() - self.height() - 10)

        self.move(int(final_x), int(final_y))
