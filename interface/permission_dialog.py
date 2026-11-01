"""
NEXUS Absolute Permission Modal Dialog
Glassmorphic confirmation window for reviewing and approving/denying system operations.
Strictly blocks execution until explicit user consent is provided.
"""
from typing import Optional
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QFont, QColor, QCursor
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QTextEdit, QScrollArea, QWidget
)

from security.permission_manager import ActionRequest, ActionRisk
from interface.themes import get_skin, CharacterSkin
from config.settings import get_settings

class PermissionDialog(QDialog):
    """Futuristic modal approval dialog for NEXUS desktop actions."""

    def __init__(self, request: ActionRequest, parent=None):
        super().__init__(parent)
        self.request = request
        self.settings = get_settings()
        self.skin: CharacterSkin = get_skin(self.settings.get("character_skin", "habibi_dubai"))
        self.drag_pos = QPoint()

        self._setup_window()
        self._build_ui()
        self._apply_styling()

    def _setup_window(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Dialog |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setModal(True)
        self.resize(520, 480)

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)

        # Outer Card
        self.card = QFrame()
        self.card.setObjectName("PermissionCard")
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(22, 20, 22, 20)
        card_layout.setSpacing(14)

        # 1. Header Row (Shield icon + Title + Risk Badge)
        header_row = QHBoxLayout()
        icon_lbl = QLabel("🛡️")
        icon_lbl.setFont(QFont("Segoe UI Emoji", 22))
        header_row.addWidget(icon_lbl)

        title_col = QVBoxLayout()
        title_col.setSpacing(2)

        sys_lbl = QLabel("NEXUS PERMISSION SYSTEM")
        sys_lbl.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        sys_lbl.setStyleSheet(f"color: {self.skin.primary.name()}; letter-spacing: 1px;")
        title_col.addWidget(sys_lbl)

        action_title = QLabel("ACTION REQUESTED")
        action_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        action_title.setStyleSheet("color: #ffffff;")
        title_col.addWidget(action_title)

        header_row.addLayout(title_col, 1)

        # Risk badge
        risk_badge = QLabel()
        risk_badge.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        risk_badge.setContentsMargins(8, 4, 8, 4)
        if self.request.risk == ActionRisk.LOW:
            risk_badge.setText("● LOW RISK")
            risk_badge.setStyleSheet("color: #10b981; background: rgba(16, 185, 129, 0.15); border-radius: 4px;")
        elif self.request.risk == ActionRisk.MODERATE:
            risk_badge.setText("▲ MODERATE RISK")
            risk_badge.setStyleSheet("color: #f59e0b; background: rgba(245, 158, 11, 0.15); border-radius: 4px;")
        else:
            risk_badge.setText("⚠️ DESTRUCTIVE")
            risk_badge.setStyleSheet("color: #ef4444; background: rgba(239, 68, 68, 0.15); border-radius: 4px;")
        header_row.addWidget(risk_badge)

        card_layout.addLayout(header_row)

        # Separator line
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background: rgba(255, 255, 255, 0.08); max-height: 1px;")
        card_layout.addWidget(sep)

        # 2. Action Summary
        self.desc_lbl = QLabel(f"<b>{self.request.title}</b><br>{self.request.description}")
        self.desc_lbl.setFont(QFont("Segoe UI", 9))
        self.desc_lbl.setStyleSheet("color: #e2e8f0; line-height: 1.4;")
        self.desc_lbl.setWordWrap(True)
        card_layout.addWidget(self.desc_lbl)

        # Proposed Actions Overview List
        prop_lbl = QLabel("Proposed Actions:")
        prop_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
        prop_lbl.setStyleSheet("color: #94a3b8;")
        card_layout.addWidget(prop_lbl)

        self.summary_box = QFrame()
        self.summary_box.setObjectName("SummaryBox")
        sum_layout = QVBoxLayout(self.summary_box)
        sum_layout.setContentsMargins(14, 10, 14, 10)
        sum_layout.setSpacing(6)

        for detail in self.request.details[:5]:
            d_lbl = QLabel(f"•  {detail}")
            d_lbl.setFont(QFont("Segoe UI", 9))
            d_lbl.setStyleSheet("color: #cbd5e1;")
            d_lbl.setWordWrap(True)
            sum_layout.addWidget(d_lbl)

        card_layout.addWidget(self.summary_box)

        # 3. Expandable Details Box (Initially Hidden)
        self.details_box = QTextEdit()
        self.details_box.setReadOnly(True)
        self.details_box.setVisible(False)
        self.details_box.setFont(QFont("Consolas", 8))
        self.details_box.setStyleSheet("""
            QTextEdit {
                background: rgba(10, 15, 25, 0.85);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                color: #94a3b8;
                padding: 8px;
            }
        """)
        # Fill details
        details_text = "\n".join(f"[{i+1}] {d}" for i, d in enumerate(self.request.details))
        if self.request.parameters:
            details_text += f"\n\nParameters:\n{self.request.parameters}"
        self.details_box.setPlainText(details_text)
        card_layout.addWidget(self.details_box, 1)

        card_layout.addStretch()

        # 4. Action Buttons: [ REVIEW DETAILS ] [ DENY ] [ APPROVE ]
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.toggle_details_btn = QPushButton("🔍 Review Details")
        self.toggle_details_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.toggle_details_btn.setObjectName("SecondaryBtn")
        self.toggle_details_btn.clicked.connect(self._toggle_details)
        btn_row.addWidget(self.toggle_details_btn)

        btn_row.addStretch()

        self.deny_btn = QPushButton("✕  DENY")
        self.deny_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.deny_btn.setObjectName("DenyBtn")
        self.deny_btn.setFixedWidth(110)
        self.deny_btn.clicked.connect(self.reject)
        btn_row.addWidget(self.deny_btn)

        self.approve_btn = QPushButton("✓  APPROVE")
        self.approve_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.approve_btn.setObjectName("ApproveBtn")
        self.approve_btn.setFixedWidth(130)
        self.approve_btn.clicked.connect(self.accept)
        btn_row.addWidget(self.approve_btn)

        card_layout.addLayout(btn_row)

        main_layout.addWidget(self.card)

    def _toggle_details(self):
        is_visible = self.details_box.isVisible()
        self.details_box.setVisible(not is_visible)
        if not is_visible:
            self.toggle_details_btn.setText("Hide Details ▲")
            self.resize(520, 620)
        else:
            self.toggle_details_btn.setText("🔍 Review Details")
            self.resize(520, 480)

    def _apply_styling(self):
        gold = self.skin.primary.name()
        bg = self.skin.hud_bg
        self.setStyleSheet(f"""
            QFrame#PermissionCard {{
                background: {bg};
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 14px;
            }}
            QFrame#SummaryBox {{
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255, 255, 255, 0.06);
                border-radius: 8px;
            }}
            QPushButton#SecondaryBtn {{
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 7px;
                color: #94a3b8;
                padding: 8px 14px;
                font-weight: 600;
            }}
            QPushButton#SecondaryBtn:hover {{
                background: rgba(255, 255, 255, 0.1);
                color: #ffffff;
            }}
            QPushButton#DenyBtn {{
                background: rgba(239, 68, 68, 0.12);
                border: 1px solid rgba(239, 68, 68, 0.35);
                border-radius: 7px;
                color: #f87171;
                padding: 8px 14px;
                font-weight: 700;
            }}
            QPushButton#DenyBtn:hover {{
                background: rgba(239, 68, 68, 0.28);
                color: #ffffff;
            }}
            QPushButton#ApproveBtn {{
                background: {gold};
                border: none;
                border-radius: 7px;
                color: #000000;
                padding: 8px 16px;
                font-weight: 700;
            }}
            QPushButton#ApproveBtn:hover {{
                background: {self.skin.secondary.name()};
            }}
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
            self.reject()
        else:
            super().keyPressEvent(event)
