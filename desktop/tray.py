"""
NEXUS Windows System Tray Integration
Keeps NEXUS accessible from the Windows notification area.
"""
from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from PySide6.QtCore import Signal, QObject
from interface.themes import get_skin

def create_default_tray_pixmap(skin_name="cyber_cyan") -> QPixmap:
    """Generates an in-memory high-DPI cyber orb tray icon."""
    pix = QPixmap(32, 32)
    pix.fill(QColor(0, 0, 0, 0))
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    
    skin = get_skin(skin_name)
    # Outer ring
    painter.setPen(skin.primary)
    painter.setBrush(skin.body_fill)
    painter.drawEllipse(2, 2, 28, 28)
    
    # Core glow
    painter.setPen(QColor(0, 0, 0, 0))
    painter.setBrush(skin.primary)
    painter.drawEllipse(9, 9, 14, 14)
    
    # Inner pupil
    painter.setBrush(QColor(255, 255, 255))
    painter.drawEllipse(12, 11, 4, 4)
    painter.end()
    return pix

class NexusTrayIcon(QSystemTrayIcon):
    """System Tray Icon for NEXUS."""

    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        
        # Set icon
        skin_name = self.controller.settings.get("character_skin", "cyber_cyan")
        self.setIcon(QIcon(create_default_tray_pixmap(skin_name)))
        self.setToolTip("NEXUS — AI Desktop Companion")
        
        # Build tray context menu
        self.menu = QMenu()
        self._build_menu()
        self.setContextMenu(self.menu)
        
        self.activated.connect(self._on_activated)

    def _build_menu(self):
        self.menu.clear()
        
        # 1. Primary ON / OFF Toggle
        is_active = getattr(self.controller, "is_active", True)
        label = "💤  Turn NEXUS OFF (Exit Desktop)" if is_active else "⚡  Turn NEXUS ON (Enter Desktop)"
        self.power_action = self.menu.addAction(label)
        self.power_action.triggered.connect(self.controller.toggle_power)

        self.menu.addSeparator()

        action_panel = self.menu.addAction("💻  Laptop Command Center")
        action_panel.triggered.connect(self.controller.open_control_panel)

        action_chat = self.menu.addAction("💬  Talk to NEXUS (Chat HUD)")
        action_chat.triggered.connect(self.controller.open_chat)

        action_show = self.menu.addAction("👁️  Show Desktop Pet")
        action_show.triggered.connect(self.controller.show_pet)

        action_sleep = self.menu.addAction("🌙  Toggle Sleep Mode")
        action_sleep.triggered.connect(self.controller.toggle_sleep)

        self.menu.addSeparator()

        action_settings = self.menu.addAction("⚙️  Settings & Free AI Keys")
        action_settings.triggered.connect(self.controller.open_settings)

        action_estop = self.menu.addAction("🚨  Emergency STOP")
        action_estop.triggered.connect(self.controller.trigger_emergency_stop)

        self.menu.addSeparator()

        action_quit = self.menu.addAction("❌  Exit NEXUS Completely")
        action_quit.triggered.connect(self.controller.quit_application)

    def update_power_state(self, is_active: bool):
        """Updates tray action text and tooltip reflecting ON/OFF state."""
        if hasattr(self, 'power_action'):
            label = "💤  Turn NEXUS OFF (Exit Desktop)" if is_active else "⚡  Turn NEXUS ON (Enter Desktop)"
            self.power_action.setText(label)
        status_text = "NEXUS — AI Desktop Companion (Active)" if is_active else "NEXUS — AI Desktop Companion (OFF / In Tray)"
        self.setToolTip(status_text)

    def _on_activated(self, reason):
        if reason in (QSystemTrayIcon.ActivationReason.Trigger, QSystemTrayIcon.ActivationReason.DoubleClick):
            if not getattr(self.controller, "is_active", True):
                self.controller.turn_on()
            else:
                self.controller.show_pet()
                self.controller.open_chat()

    def update_skin(self, skin_name: str):
        self.setIcon(QIcon(create_default_tray_pixmap(skin_name)))
