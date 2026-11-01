"""
NEXUS Floating Quick Speech & Thought Bubble
Displays speech and reaction text above the desktop pet with smooth fade-in/out.
"""
from PySide6.QtCore import Qt, QTimer, QRectF, QPointF
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import (
    QPainter, QColor, QPainterPath, QFont, QPen, QBrush, 
    QFontMetrics, QLinearGradient
)
from interface.themes import CharacterSkin

class QuickBubble(QWidget):
    """Floating transparent speech bubble widget above NEXUS."""

    def __init__(self, parent=None, skin: CharacterSkin = None):
        super().__init__(parent)
        self.skin = skin
        self.message = ""
        self.opacity = 0.0
        
        # Transparent frameless window setup
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        
        # Timer for auto-dismiss
        self.dismiss_timer = QTimer(self)
        self.dismiss_timer.setSingleShot(True)
        self.dismiss_timer.timeout.connect(self.hide_bubble)
        
        # Fade animation timer
        self.fade_timer = QTimer(self)
        self.fade_timer.setInterval(20)
        self.fade_timer.timeout.connect(self._step_fade)
        self.target_opacity = 0.0

    def set_skin(self, skin: CharacterSkin):
        self.skin = skin
        self.update()

    def show_message(self, text: str, duration_ms: int = 3500):
        """Displays text with automatic sizing and positioning."""
        if not text:
            self.hide_bubble()
            return
            
        self.message = text
        self.dismiss_timer.stop()
        
        # Measure text size
        font = QFont("Segoe UI", 10, QFont.Weight.Medium)
        metrics = QFontMetrics(font)
        text_rect = metrics.boundingRect(QRectF(0, 0, 240, 300).toRect(), Qt.TextFlag.TextWordWrap, text)
        
        w = max(110, text_rect.width() + 28)
        h = text_rect.height() + 24 + 8 # plus 8 for bottom tail
        self.resize(int(w), int(h))
        
        self.target_opacity = 1.0
        if not self.fade_timer.isActive():
            self.fade_timer.start()
            
        self.show()
        self.update()
        
        if duration_ms > 0:
            self.dismiss_timer.start(duration_ms)

    def hide_bubble(self):
        self.target_opacity = 0.0
        if not self.fade_timer.isActive():
            self.fade_timer.start()

    def _step_fade(self):
        diff = self.target_opacity - self.opacity
        if abs(diff) < 0.08:
            self.opacity = self.target_opacity
            self.fade_timer.stop()
            if self.opacity <= 0.0:
                self.hide()
        else:
            self.opacity += diff * 0.35
        self.update()

    def paintEvent(self, event):
        if self.opacity <= 0.01 or not self.message:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setOpacity(self.opacity)

        w = float(self.width())
        h = float(self.height()) - 8.0 # leave 8px for pointer tail

        # Create rounded bubble path with downward pointing pointer
        path = QPainterPath()
        radius = 12.0
        path.addRoundedRect(QRectF(2, 2, w - 4, h - 4), radius, radius)
        
        # Bottom pointer towards NEXUS
        tail_cx = w / 2.0
        path.moveTo(tail_cx - 8, h - 2)
        path.lineTo(tail_cx, h + 7)
        path.lineTo(tail_cx + 8, h - 2)

        # Bubble background gradient
        bg_col = QColor(13, 17, 23, 240)
        border_col = QColor(255, 255, 255, 45)
        
        grad = QLinearGradient(0, 0, 0, h)
        grad.setColorAt(0.0, bg_col.lighter(115))
        grad.setColorAt(1.0, bg_col)

        painter.setPen(QPen(border_col, 1.0))
        painter.setBrush(QBrush(grad))
        painter.drawPath(path)

        # Text
        painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        painter.setPen(QColor(240, 246, 255))
        painter.drawText(
            QRectF(12, 8, w - 24, h - 16),
            Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap,
            self.message
        )
