"""
NEXUS Minimalist Chat Bubble Widgets
High-tech message components supporting Markdown, code blocks, attachments, and actions.
Crafted with clean, minimalist aesthetics (no gaudy neon borders).
"""
import os
import html
import time
from PySide6.QtCore import Qt, Signal, QSize, QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTextBrowser, QPushButton, QFrame, QApplication, QFileDialog
)
from PySide6.QtGui import QColor, QFont, QCursor, QClipboard

from core.conversation import ChatMessage
from interface.themes import CharacterSkin
from desktop.markdown_formatter import markdown_to_html
from core.voice_engine import get_voice_engine

class MessageBubbleWidget(QWidget):
    """Clean, minimalist message bubble."""
    regenerate_requested = Signal(str)  # message id
    speak_requested = Signal(str)       # text

    def __init__(self, message: ChatMessage, skin: CharacterSkin = None, parent=None):
        super().__init__(parent)
        self.message = message
        self.skin = skin
        self.browser = None
        self._last_render_time = 0.0
        self._resize_scheduled = False
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(6, 4, 6, 4)
        self.layout.setSpacing(4)
        self._build_ui()

    def update_content(self, new_text: str, force: bool = False):
        """Allows streaming updates to assistant messages with throttling to prevent Qt layout overflow."""
        self.message.content = new_text
        now = time.time()
        if force or (now - self._last_render_time > 0.05):
            self._last_render_time = now
            if self.browser:
                formatted_html = markdown_to_html(new_text, self.skin)
                self.browser.setHtml(formatted_html)

    def _on_doc_size_changed(self, sz):
        """Asynchronously resizes browser to prevent Qt layout recursion (0xC00000FD)."""
        if not self._resize_scheduled:
            self._resize_scheduled = True
            QTimer.singleShot(0, self._apply_doc_size)

    def _apply_doc_size(self):
        self._resize_scheduled = False
        if self.browser:
            doc = self.browser.document()
            target_h = int(doc.size().height()) + 14
            if abs(self.browser.height() - target_h) > 2:
                self.browser.setFixedHeight(target_h)

    def _build_ui(self):
        if self.message.role == "user":
            self._build_user_ui()
        else:
            self._build_assistant_ui()

    def _build_user_ui(self):
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.addStretch()

        card = QFrame()
        card.setObjectName("UserCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(12, 8, 12, 8)
        card_layout.setSpacing(4)

        # Attachments preview
        if self.message.attachments:
            att_row = QHBoxLayout()
            for att in self.message.attachments:
                fname = os.path.basename(att)
                att_lbl = QLabel(f"📎 {fname}")
                att_lbl.setStyleSheet("""
                    background: rgba(255, 255, 255, 0.08);
                    color: #94a3b8;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 4px;
                    padding: 1px 6px;
                    font-size: 11px;
                """)
                att_row.addWidget(att_lbl)
            att_row.addStretch()
            card_layout.addLayout(att_row)

        text_label = QLabel(self.message.content)
        text_label.setWordWrap(True)
        text_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        text_label.setFont(QFont("Segoe UI", 10))
        text_label.setStyleSheet("color: #f8fafc; background: transparent; line-height: 1.4;")
        card_layout.addWidget(text_label)

        card.setStyleSheet("""
            #UserCard {
                background-color: #21262d;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 12px;
                border-bottom-right-radius: 3px;
            }
        """)
        row.addWidget(card)
        self.layout.addLayout(row)

    def _build_assistant_ui(self):
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setAlignment(Qt.AlignmentFlag.AlignTop)

        card = QFrame()
        card.setObjectName("AssistantCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(12, 8, 12, 6)
        card_layout.setSpacing(4)

        # Rich text browser for markdown
        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(True)
        self.browser.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.browser.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.browser.setFrameShape(QFrame.Shape.NoFrame)
        self.browser.setStyleSheet("background: transparent; border: none;")
        
        self.browser.document().documentLayout().documentSizeChanged.connect(self._on_doc_size_changed)
        formatted_html = markdown_to_html(self.message.content, self.skin)
        self.browser.setHtml(formatted_html)

        card_layout.addWidget(self.browser)

        # Minimal Action toolbar (Copy, Read Aloud, Regenerate)
        tool_row = QHBoxLayout()
        tool_row.setContentsMargins(0, 2, 0, 0)
        tool_row.setSpacing(4)

        copy_btn = QPushButton("📋 Copy")
        copy_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        copy_btn.setStyleSheet(self._btn_style())
        copy_btn.clicked.connect(self._copy_content)
        tool_row.addWidget(copy_btn)

        speak_btn = QPushButton("🔊 Listen")
        speak_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        speak_btn.setStyleSheet(self._btn_style())
        speak_btn.clicked.connect(self._speak_content)
        tool_row.addWidget(speak_btn)

        regen_btn = QPushButton("🔄 Retry")
        regen_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        regen_btn.setStyleSheet(self._btn_style())
        regen_btn.clicked.connect(lambda: self.regenerate_requested.emit(self.message.id))
        tool_row.addWidget(regen_btn)

        tool_row.addStretch()
        card_layout.addLayout(tool_row)

        card.setStyleSheet("""
            #AssistantCard {
                background-color: rgba(255, 255, 255, 0.02);
                border: 1px solid rgba(255, 255, 255, 0.06);
                border-radius: 12px;
                border-top-left-radius: 3px;
            }
        """)
        row.addWidget(card)
        row.addStretch()
        self.layout.addLayout(row)

    def _btn_style(self) -> str:
        return """
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 4px;
                color: #64748b;
                padding: 2px 7px;
                font-family: 'Segoe UI', system-ui, sans-serif;
                font-size: 11px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.06);
                color: #38bdf8;
            }
        """

    def _copy_content(self):
        cb = QApplication.clipboard()
        cb.setText(self.message.content)
        sender = self.sender()
        if sender and isinstance(sender, QPushButton):
            orig_text = sender.text()
            sender.setText("✓ Copied")
            QTimer.singleShot(1500, lambda: sender.setText(orig_text))

    def _speak_content(self):
        self.speak_requested.emit(self.message.content)

    def _save_code_snippet(self):
        import re
        match = re.search(r"```([a-zA-Z0-9_\-\+]*)\n(.*?)```", self.message.content, re.DOTALL)
        if match:
            lang = match.group(1).lower() or "txt"
            code = match.group(2)
            ext_map = {"python": ".py", "py": ".py", "javascript": ".js", "js": ".js", 
                       "html": ".html", "css": ".css", "json": ".json", "powershell": ".ps1"}
            ext = ext_map.get(lang, f".{lang}")
            
            save_path, _ = QFileDialog.getSaveFileName(
                self, "Save Code Snippet", f"nexus_snippet{ext}", f"Code File (*{ext});;All Files (*.*)"
            )
            if save_path:
                try:
                    with open(save_path, "w", encoding="utf-8") as f:
                        f.write(code)
                except Exception:
                    pass

class ThinkingBubbleWidget(QWidget):
    """Clean minimalist thinking indicator."""

    def __init__(self, skin: CharacterSkin = None, parent=None):
        super().__init__(parent)
        self.skin = skin
        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)

        self.label = QLabel("✦ NEXUS is thinking...")
        self.label.setStyleSheet("""
            color: #94a3b8;
            font-size: 11.5px;
            font-weight: 500;
            padding: 6px 12px;
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.07);
            border-radius: 10px;
        """)
        layout.addWidget(self.label)
        layout.addStretch()

        self.step = 0
        self.timer = QTimer(self)
        self.timer.setInterval(320)
        self.timer.timeout.connect(self._step_dots)
        self.timer.start()

    def _step_dots(self):
        self.step = (self.step + 1) % 4
        dots = "." * self.step
        self.label.setText(f"✦ NEXUS is thinking{dots}")
