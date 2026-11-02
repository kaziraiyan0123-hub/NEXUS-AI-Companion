"""
NEXUS Minimalist Quick-Action Command Capsule
A sleek, modern glassmorphic desktop pill toolbar providing one-click access
to voice interaction, desktop vision, chat HUD, laptop command center, and power.
Crafted with clean, minimalist aesthetics (no gaudy neon borders).
"""
from PySide6.QtCore import Qt, QPoint, Signal, Slot
from PySide6.QtGui import QFont, QCursor, QColor
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton, QFrame, QGraphicsDropShadowEffect
)

from config.settings import get_settings
from interface.themes import get_skin, CharacterSkin

class NexusDockWidget(QWidget):
    """Ultra-modern minimalist floating pill toolbar for NEXUS."""

    voice_requested = Signal()
    chat_requested = Signal()
    vision_requested = Signal()
    control_panel_requested = Signal()
    games_requested = Signal()
    power_toggled = Signal()
    pet_summon_requested = Signal()

    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.settings = get_settings()
        self.skin: CharacterSkin = get_skin(self.settings.get("character_skin", "neo_cyber"))
        self.drag_pos = QPoint()

        self._setup_window()
        self._build_ui()
        self._restore_position()

    def _setup_window(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedHeight(48)
        self.setMinimumWidth(500)

    def _build_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(6, 3, 6, 5)

        self.pill = QFrame()
        self.pill.setObjectName("DockPill")
        pill_layout = QHBoxLayout(self.pill)
        pill_layout.setContentsMargins(12, 4, 12, 4)
        pill_layout.setSpacing(6)

        # 1. Companion Summon / Identity Badge
        self.brand_btn = QPushButton("✦ NEXUS")
        self.brand_btn.setObjectName("BrandBtn")
        self.brand_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.brand_btn.setToolTip("Click to focus NEXUS or interact with affection")
        self.brand_btn.clicked.connect(self._on_brand_clicked)
        pill_layout.addWidget(self.brand_btn)

        # 2. Voice Button
        self.voice_btn = QPushButton("🎙️ Voice")
        self.voice_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.voice_btn.setToolTip("Toggle Hands-Free Voice Conversation ('Hey Nexus')")
        self.voice_btn.clicked.connect(self.voice_requested.emit)
        pill_layout.addWidget(self.voice_btn)

        # 3. Screen Vision Button
        self.vision_btn = QPushButton("👁️ Vision")
        self.vision_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.vision_btn.setToolTip("Analyze active screen with AI Vision")
        self.vision_btn.clicked.connect(self.vision_requested.emit)
        pill_layout.addWidget(self.vision_btn)

        # 4. Chat HUD Button
        self.chat_btn = QPushButton("💬 Chat")
        self.chat_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.chat_btn.setToolTip("Toggle Clean Chat HUD")
        self.chat_btn.clicked.connect(self.chat_requested.emit)
        pill_layout.addWidget(self.chat_btn)

        # 4b. Brain Games & Arcade Button
        self.games_btn = QPushButton("🎮 Games")
        self.games_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.games_btn.setToolTip("Play Brain Games & Arcade (Tic-Tac-Toe, Memory, Trivia)")
        self.games_btn.clicked.connect(self.games_requested.emit)
        pill_layout.addWidget(self.games_btn)

        # 5. Laptop Command Center Button
        self.cp_btn = QPushButton("💻 Center")
        self.cp_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.cp_btn.setToolTip("Open Laptop Command Center & Hardware Monitor")
        self.cp_btn.clicked.connect(self.control_panel_requested.emit)
        pill_layout.addWidget(self.cp_btn)

        # 6. Power ON/OFF Toggle
        self.power_btn = QPushButton("● ON")
        self.power_btn.setObjectName("PowerBtnOn")
        self.power_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.power_btn.setToolTip("Turn NEXUS ON / OFF (Enter or Dismiss to Tray)")
        self.power_btn.clicked.connect(self.power_toggled.emit)
        pill_layout.addWidget(self.power_btn)

        main_layout.addWidget(self.pill)
        self._apply_styling()

    def _apply_styling(self):
        self.setStyleSheet("""
            QFrame#DockPill {
                background-color: rgba(13, 17, 23, 0.94);
                border: 1px solid rgba(255, 255, 255, 0.09);
                border-radius: 19px;
            }
            QPushButton {
                background: transparent;
                border: 1px solid transparent;
                border-radius: 12px;
                color: #94a3b8;
                font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
                font-size: 11.5px;
                font-weight: 500;
                padding: 4px 10px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.07);
                border: 1px solid rgba(255, 255, 255, 0.1);
                color: #f0f6fc;
            }
            QPushButton#BrandBtn {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 12px;
                color: #f0f6fc;
                font-size: 11.5px;
                font-weight: 600;
                padding: 4px 11px;
                letter-spacing: 0.3px;
            }
            QPushButton#BrandBtn:hover {
                background: rgba(56, 189, 248, 0.12);
                border-color: rgba(56, 189, 248, 0.35);
                color: #38bdf8;
            }
            QPushButton#PowerBtnOn {
                background: rgba(52, 211, 153, 0.12);
                border: 1px solid rgba(52, 211, 153, 0.3);
                color: #34d399;
                border-radius: 12px;
                font-size: 10.5px;
                font-weight: 600;
                padding: 4px 9px;
            }
            QPushButton#PowerBtnOn:hover {
                background: rgba(52, 211, 153, 0.22);
            }
            QPushButton#PowerBtnOff {
                background: rgba(248, 113, 113, 0.12);
                border: 1px solid rgba(248, 113, 113, 0.3);
                color: #f87171;
                border-radius: 12px;
                font-size: 10.5px;
                font-weight: 600;
                padding: 4px 9px;
            }
            QPushButton#PowerBtnOff:hover {
                background: rgba(248, 113, 113, 0.22);
            }
        """)

        # Soft drop shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(16)
        shadow.setColor(QColor(0, 0, 0, 160))
        shadow.setOffset(0, 3)
        self.pill.setGraphicsEffect(shadow)

    def update_power_state(self, is_active: bool):
        """Updates power pill indicator cleanly."""
        if is_active:
            self.power_btn.setText("● ON")
            self.power_btn.setObjectName("PowerBtnOn")
        else:
            self.power_btn.setText("○ OFF")
            self.power_btn.setObjectName("PowerBtnOff")
        self.power_btn.style().unpolish(self.power_btn)
        self.power_btn.style().polish(self.power_btn)

    def _on_brand_clicked(self):
        if self.controller:
            if not getattr(self.controller, "is_active", True):
                self.controller.turn_on()
            else:
                self.controller.show_pet()
                self.controller.pet_the_pet()

    def _restore_position(self):
        from PySide6.QtGui import QGuiApplication
        screen = QGuiApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            # Default: Bottom center above taskbar
            x = geo.center().x() - self.width() // 2
            y = geo.bottom() - self.height() - 15
            self.move(int(x), int(y))

    # Draggable dock
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and not self.drag_pos.isNull():
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()
