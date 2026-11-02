"""
NEXUS Transparent Desktop Pet Window
A transparent, frameless, draggable, animated desktop companion.
"""
import math
import random
import time
from PySide6.QtCore import (
    Qt, QTimer, QPoint, QRect, QPropertyAnimation, 
    QEasingCurve, Signal, Slot
)
from PySide6.QtWidgets import QWidget, QApplication, QMenu
from PySide6.QtGui import QPainter, QCursor, QGuiApplication, QScreen

from core.character_state import CharacterState
from config.settings import get_settings
from interface.themes import get_skin, CharacterSkin
from desktop.pet_renderer import PetRenderer
from desktop.context_menu import PetContextMenu
from desktop.quick_bubble import QuickBubble

class DesktopPet(QWidget):
    """The living desktop companion window for NEXUS."""

    # Signals
    chat_requested = Signal()
    quick_ask_requested = Signal()
    voice_toggle_requested = Signal()
    settings_requested = Signal()
    memory_requested = Signal()
    skin_changed = Signal(str)
    tool_requested = Signal(str, dict)
    emergency_stop_requested = Signal()
    control_panel_requested = Signal()
    games_requested = Signal()
    power_toggle_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = get_settings()
        
        # Load appearance settings
        skin_name = self.settings.get("character_skin", "cyber_cyan")
        self.skin = get_skin(skin_name)
        self.pet_size = int(self.settings.get("pet_width", 200))
        
        # Initialize rendering engine
        self.renderer = PetRenderer(self.skin)
        
        # Window setup: frameless, transparent, stays on top
        self._setup_window()
        
        # Speech bubble
        self.bubble = QuickBubble(skin=self.skin)
        
        # Mouse interaction states
        self.drag_position = QPoint()
        self.is_dragging = False
        self.drag_start_time = 0.0
        
        # Roaming & Idle AI timer
        self.roam_animation = None
        self.temp_state_timer = QTimer(self)
        self.temp_state_timer.setSingleShot(True)
        self.temp_state_timer.timeout.connect(self._on_temp_state_timeout)
        
        # Idle behavior timer (blinks, looks, short stretches)
        self.idle_behavior_timer = QTimer(self)
        self.idle_behavior_timer.setInterval(8000)  # check every 8s
        self.idle_behavior_timer.timeout.connect(self._perform_idle_behavior)
        self.idle_behavior_timer.start()
        
        # Main Animation Loop (40 FPS = 25ms, optimized for Ryzen 3 / Win 11)
        self.last_frame_time = time.time()
        self.anim_timer = QTimer(self)
        self.anim_timer.setInterval(25)
        self.anim_timer.timeout.connect(self._animation_tick)
        self.anim_timer.start()

        # Set initial position
        self._restore_or_default_position()
        
        # Welcome greeting after a brief delay
        def _initial_greeting():
            from core.memory_manager import get_memory_manager
            mm = get_memory_manager()
            name = mm.get_user_name()
            greeting = f"✦ Online and ready, {name}!" if name else "✦ Systems online. Hello! What shall we build?"
            self.say(greeting, 3500)
        QTimer.singleShot(800, _initial_greeting)

    def _setup_window(self):
        flags = Qt.WindowType.FramelessWindowHint
        if self.settings.get("always_on_top", True):
            flags |= Qt.WindowType.WindowStaysOnTopHint
            
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setMouseTracking(True)
        self.resize(self.pet_size, self.pet_size)

    def _restore_or_default_position(self):
        pos_x = self.settings.get("position_x", -1)
        pos_y = self.settings.get("position_y", -1)

        screen = QGuiApplication.primaryScreen()
        avail_geo = screen.availableGeometry() if screen else QRect(0, 0, 1920, 1080)

        if pos_x >= 0 and pos_y >= 0:
            # Check within visible screen
            x = min(max(avail_geo.left(), pos_x), avail_geo.right() - self.width())
            y = min(max(avail_geo.top(), pos_y), avail_geo.bottom() - self.height())
            self.move(int(x), int(y))
        else:
            # Default: lower right resting comfortably above taskbar
            x = avail_geo.right() - self.width() - 40
            y = avail_geo.bottom() - self.height() - 25
            self.move(int(x), int(y))
            self.settings.set("position_x", int(x), auto_save=False)
            self.settings.set("position_y", int(y), auto_save=True)

        self._update_bubble_position()

    def _update_bubble_position(self):
        """Places speech bubble cleanly right above NEXUS's head, clamping within screen bounds."""
        if not self.bubble.isVisible() and self.bubble.opacity <= 0.0:
            return

        screen = QGuiApplication.primaryScreen()
        avail = screen.availableGeometry() if screen else QRect(0, 0, 1920, 1080)

        bx = self.x() + (self.width() - self.bubble.width()) // 2
        # Clamp horizontal position
        bx = max(avail.left() + 10, min(bx, avail.right() - self.bubble.width() - 10))

        by = self.y() - self.bubble.height() + 8
        # If too close to top edge, flip below pet
        if by < avail.top() + 10:
            by = self.y() + self.height() + 4

        self.bubble.move(int(bx), int(by))

    def moveEvent(self, event):
        super().moveEvent(event)
        self._update_bubble_position()

    @property
    def state(self) -> CharacterState:
        return self.renderer.state

    def set_pet_size(self, size: int):
        """Resize pet dynamically."""
        if self.pet_size == size:
            return
        self.pet_size = size
        self.resize(size, size)
        self.settings.set("pet_width", size)
        self.settings.set("pet_height", size)
        self._update_bubble_position()
        self.update()

    def set_skin(self, skin_name: str, announce: bool = False):
        """Change visual skin smoothly without resetting position or restarting."""
        if hasattr(self, "skin") and self.skin and self.skin.name == skin_name:
            return
        self.skin = get_skin(skin_name)
        self.renderer.set_skin(self.skin)
        self.bubble.set_skin(self.skin)
        self.settings.set("character_skin", skin_name)
        if announce:
            self.say(f"Skin: {self.skin.display_name}", 2000)
        self.skin_changed.emit(skin_name)
        self.update()

    def play_animation(self, state: CharacterState, duration_sec: float = None):
        """Play one of the 17 animations."""
        self.temp_state_timer.stop()
        self.renderer.set_state(state)
        self.update()

        # Voice/Action reaction speech
        if state == CharacterState.HAPPY:
            self.say("✨ Feeling energized and happy!", 2500)
        elif state == CharacterState.SURPRISED:
            self.say("⚡ Oh! New signal detected!", 2500)
        elif state == CharacterState.CONFUSED:
            self.say("🤔 Analyzing context...", 2500)
        elif state == CharacterState.ERROR:
            self.say("⚠️ An anomaly occurred.", 2500)
        elif state == CharacterState.CELEBRATING:
            self.say("🎉 Mission accomplished! Great work!", 3000)
        elif state == CharacterState.SLEEPING:
            self.say("💤 Entering rest mode...", 2000)
        elif state == CharacterState.WAKING:
            self.say("👁️ Booting systems... Ready!", 2500)
        elif state == CharacterState.WORKING:
            self.say("⚙️ Processing tasks with precision...", 2500)

        # Temporary duration fallback to IDLE
        if duration_sec is None:
            if state in (CharacterState.SURPRISED, CharacterState.CONFUSED, 
                         CharacterState.HAPPY, CharacterState.ERROR, 
                         CharacterState.CELEBRATING, CharacterState.WAKING):
                duration_sec = 3.5

        if duration_sec and duration_sec > 0:
            self.temp_state_timer.start(int(duration_sec * 1000))

    def _on_temp_state_timeout(self):
        if self.renderer.state != CharacterState.SLEEPING:
            self.renderer.set_state(CharacterState.IDLE)
            self.update()

    def say(self, text: str, duration_ms: int = 3500):
        """Displays speech bubble above the pet."""
        self.bubble.show_message(text, duration_ms)
        self._update_bubble_position()

    def is_sleeping(self) -> bool:
        return self.renderer.state == CharacterState.SLEEPING

    def toggle_sleep(self):
        """Toggle between active and sleeping states."""
        if self.is_sleeping():
            self.play_animation(CharacterState.WAKING, duration_sec=2.5)
            self.settings.set("interaction_mode", "normal")
        else:
            self.play_animation(CharacterState.SLEEPING)
            self.settings.set("interaction_mode", "sleep")

    def toggle_always_on_top(self, enabled: bool):
        """Toggle always-on-top window hint safely without destroying position or restarting."""
        current_ontop = bool(self.windowFlags() & Qt.WindowType.WindowStaysOnTopHint)
        if current_ontop == enabled:
            return  # Prevent redundant window reconstruction and flashing

        cur_pos = self.pos()
        self.settings.set("always_on_top", enabled)
        was_visible = self.isVisible()
        flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool
        if enabled:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.move(cur_pos)
        self._update_bubble_position()
        if was_visible:
            self.show()

    def toggle_roaming(self, enabled: bool):
        self.settings.set("idle_roam_enabled", enabled)
        if enabled:
            self.say("Autonomous wandering enabled.", 2000)
        else:
            self.say("Staying in position.", 2000)

    def reset_position(self):
        """Moves NEXUS smoothly back to primary desktop corner."""
        screen = QGuiApplication.primaryScreen()
        avail = screen.availableGeometry() if screen else QRect(0, 0, 1920, 1080)
        target_x = avail.right() - self.width() - 40
        target_y = avail.bottom() - self.height() - 25
        self._animate_move_to(QPoint(target_x, target_y), CharacterState.FLOATING)

    def _perform_idle_behavior(self):
        """Autonomous idle expressions and occasional subtle wandering."""
        if self.is_sleeping() or self.is_dragging:
            return
        if self.renderer.state != CharacterState.IDLE:
            return

        chance = random.random()
        # 1. Subtle stretch / sit / float
        if chance < 0.25:
            action = random.choice([CharacterState.FLOATING, CharacterState.SITTING, CharacterState.THINKING])
            self.play_animation(action, duration_sec=4.0)
        # 2. Occasional wandering if roaming enabled
        elif chance < 0.45 and self.settings.get("idle_roam_enabled", True):
            self._roam_short_distance()

    def _roam_short_distance(self):
        """Walks a short distance across the bottom of the screen."""
        screen = QGuiApplication.primaryScreen()
        avail = screen.availableGeometry() if screen else QRect(0, 0, 1920, 1080)
        
        # Pick a target X within 180px
        delta_x = random.choice([-150, -100, 100, 150])
        new_x = min(max(avail.left() + 20, self.x() + delta_x), avail.right() - self.width() - 20)
        
        if abs(new_x - self.x()) > 30:
            target_pos = QPoint(new_x, self.y())
            self._animate_move_to(target_pos, CharacterState.WALKING)

    def _animate_move_to(self, target_pos: QPoint, move_state: CharacterState):
        """Animates window movement with QPropertyAnimation."""
        self.renderer.set_state(move_state)
        
        self.roam_animation = QPropertyAnimation(self, b"pos")
        dist = math.hypot(target_pos.x() - self.x(), target_pos.y() - self.y())
        duration = max(800, int(dist * 6.0)) # smooth walk speed
        
        self.roam_animation.setDuration(duration)
        self.roam_animation.setStartValue(self.pos())
        self.roam_animation.setEndValue(target_pos)
        self.roam_animation.setEasingCurve(QEasingCurve.Type.InOutSine)
        
        def on_finished():
            if self.settings.get("position_x") != self.x() or self.settings.get("position_y") != self.y():
                self.settings.set("position_x", self.x(), auto_save=False)
                self.settings.set("position_y", self.y(), auto_save=True)
            if self.renderer.state == move_state:
                self.renderer.set_state(CharacterState.IDLE)
            self.update()

        self.roam_animation.finished.connect(on_finished)
        self.roam_animation.start()

    # --- Mouse Events & Dragging ---

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Cancel ongoing roam animation so mouse dragging takes immediate precedence
            if hasattr(self, "roam_animation") and self.roam_animation and self.roam_animation.state() == QPropertyAnimation.State.Running:
                self.roam_animation.stop()

            self.is_dragging = True
            self.drag_start_pos = event.globalPosition().toPoint()
            self.drag_start_time = time.time()
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.renderer.is_dragged = True
            # Squish down slightly when grabbed
            self.renderer.squish_x = 1.15
            self.renderer.squish_y = 0.85
            event.accept()
        elif event.button() == Qt.MouseButton.RightButton:
            # Open Context Menu
            menu = PetContextMenu(self, self)
            menu.exec(event.globalPosition().toPoint())
            event.accept()

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            new_pos = event.globalPosition().toPoint() - self.drag_position
            # Prevent going completely off screen
            screen = QGuiApplication.primaryScreen()
            if screen:
                geo = screen.availableGeometry()
                new_pos.setX(min(max(geo.left() - 40, new_pos.x()), geo.right() - self.width() + 40))
                new_pos.setY(min(max(geo.top(), new_pos.y()), geo.bottom() - self.height() + 20))
            self.move(new_pos)
            event.accept()
        else:
            # Interactive petting detection (rubbing mouse back and forth)
            now = time.time()
            if not hasattr(self, '_petting_strokes'):
                self._petting_strokes = 0
                self._last_stroke_time = 0.0

            if now - self._last_stroke_time < 0.35:
                self._petting_strokes += 1
                if self._petting_strokes >= 8:
                    self._petting_strokes = 0
                    self.play_animation(CharacterState.HAPPY, duration_sec=2.5)
                    self.renderer.squish_x = 1.15
                    self.renderer.squish_y = 0.85
                    self.say("Purr... That feels wonderful! 💖", 2500)
            else:
                self._petting_strokes = 1
            self._last_stroke_time = now
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.is_dragging:
            self.is_dragging = False
            self.renderer.is_dragged = False
            # Bounce back squish
            self.renderer.squish_x = 0.9
            self.renderer.squish_y = 1.15
            # Save new position if changed
            if self.settings.get("position_x") != self.x() or self.settings.get("position_y") != self.y():
                self.settings.set("position_x", self.x(), auto_save=False)
                self.settings.set("position_y", self.y(), auto_save=True)
            
            # Precise drag vs click detection based on distance moved
            dist_moved = (event.globalPosition().toPoint() - self.drag_start_pos).manhattanLength()
            time_dragged = max(0.01, time.time() - self.drag_start_time)
            if dist_moved < 8:
                self._on_pet_clicked()
            elif dist_moved >= 8 and time_dragged < 0.35:
                # Gentle toss physics if dragged quickly
                delta = event.globalPosition().toPoint() - self.drag_start_pos
                vx = int(delta.x() / time_dragged * 0.12)
                vy = int(delta.y() / time_dragged * 0.12)
                screen = QGuiApplication.primaryScreen()
                if screen:
                    geo = screen.availableGeometry()
                    target_x = min(max(geo.left(), self.x() + vx), geo.right() - self.width())
                    target_y = min(max(geo.top(), self.y() + vy), geo.bottom() - self.height())
                    self._animate_move_to(QPoint(int(target_x), int(target_y)), CharacterState.FLOATING)
            event.accept()

    def enterEvent(self, event):
        self.renderer.is_hovered = True
        if self.renderer.state == CharacterState.IDLE:
            self.renderer.squish_x = 1.05
            self.renderer.squish_y = 0.95
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.renderer.is_hovered = False
        super().leaveEvent(event)

    def mouseDoubleClickEvent(self, event):
        """Double-click reaction: High-Five / celebratory interaction!"""
        if event.button() == Qt.MouseButton.LeftButton:
            from core.memory_manager import get_memory_manager
            user_name = get_memory_manager().get_user_name() or "Friend"
            self.play_animation(CharacterState.CELEBRATING, duration_sec=3.0)
            self.renderer._spawn_burst("star", 16)
            self.renderer.squish_x = 1.25
            self.renderer.squish_y = 0.75
            greetings = [
                f"High five, {user_name}! ✋✨",
                f"Fist bump, {user_name}! 👊✨",
                f"Great to see you, {user_name}! 🚀"
            ]
            msg = random.choice(greetings)
            self.say(msg, 3000)
            try:
                from core.voice_engine import get_voice_engine
                get_voice_engine().speak(msg)
            except Exception:
                pass
            event.accept()
        else:
            super().mouseDoubleClickEvent(event)

    def _on_pet_clicked(self):
        """Click reaction: wakes up if sleeping, otherwise greets or opens chat."""
        if self.is_sleeping():
            self.toggle_sleep()
        else:
            from core.memory_manager import get_memory_manager
            user_name = get_memory_manager().get_user_name()
            self.play_animation(CharacterState.HAPPY, duration_sec=2.0)
            self.renderer.squish_x = 1.15
            self.renderer.squish_y = 0.85
            if user_name:
                self.say(f"Hi, {user_name}! What can I do for you? ✦", 2500)
            else:
                self.say("Hello! What's your name? ✦", 2500)
            self.chat_requested.emit()

    # --- Animation Tick & Painting ---

    def _animation_tick(self):
        now = time.time()
        dt = min(0.08, now - self.last_frame_time)
        self.last_frame_time = now

        # Calculate relative mouse cursor position for gaze tracking
        if self.settings.get("look_at_cursor", True):
            cursor_pos = QCursor.pos()
            pet_center_x = self.x() + self.width() / 2.0
            pet_center_y = self.y() + self.height() / 2.0
            
            # Normalized offset (-1.0 to 1.0)
            rel_x = (cursor_pos.x() - pet_center_x) / 350.0
            rel_y = (cursor_pos.y() - pet_center_y) / 250.0
        else:
            rel_x, rel_y = 0.0, 0.0

        # Update physics
        self.renderer.update_physics(dt, rel_x, rel_y)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        self.renderer.render(painter, self.width(), self.height())

    # --- Controller Actions called from menus & signals ---

    def show_pet(self):
        self.show()
        self.raise_()
        self.activateWindow()

    def open_chat(self):
        self.chat_requested.emit()

    def open_quick_ask(self):
        self.quick_ask_requested.emit()

    def toggle_voice(self):
        self.voice_toggle_requested.emit()

    def open_settings(self):
        self.settings_requested.emit()

    def open_memory(self):
        self.memory_requested.emit()

    def open_control_panel(self):
        self.control_panel_requested.emit()

    def open_games(self):
        self.games_requested.emit()

    def trigger_tool(self, tool_name: str, params: dict):
        self.tool_requested.emit(tool_name, params)

    def trigger_emergency_stop(self):
        self.emergency_stop_requested.emit()

    def pet_the_pet(self):
        """Petting interaction: spawns hearts, squishes body, awards bond XP, plays happy animation."""
        self.renderer._spawn_burst("heart", 16)
        self.renderer.squish_x = 1.15
        self.renderer.squish_y = 0.85
        self.play_animation(CharacterState.HAPPY, duration_sec=3.0)
        
        from core.memory_manager import get_memory_manager
        mm = get_memory_manager()
        stats = mm.add_bond_xp(5)
        name = mm.get_user_name()
        
        if stats.get("leveled_up"):
            chosen = f"⭐ Bond Level Up! We are now {stats['title']}! (+5 XP)"
        else:
            phrases = [
                f"Thank you, {name}! Companion feeling loved! 💖" if name else "Thank you! Companion feeling loved! 💖",
                "Hehehe, that tickles! 😊",
                "Affection acknowledged and appreciated! ✨ (+5 XP)",
                "NEXUS feels energized and happy! 💖"
            ]
            chosen = random.choice(phrases)
            
        self.say(chosen, 3000)
        try:
            from core.voice_engine import get_voice_engine
            get_voice_engine().speak(chosen)
        except Exception:
            pass

    def high_five(self):
        """High-five interaction: bursts stars, awards bond XP, plays celebration animation."""
        self.renderer._spawn_burst("star", 18)
        self.play_animation(CharacterState.CELEBRATING, duration_sec=3.5)
        from core.memory_manager import get_memory_manager
        mm = get_memory_manager()
        stats = mm.add_bond_xp(10)
        name = mm.get_user_name()
        
        if stats.get("leveled_up"):
            msg = f"🙌 High-Five! Bond Level Up to {stats['title']}! (+10 XP)"
        else:
            msg = f"🙌 High-five, {name}! We make a great team! (+10 XP)" if name else "🙌 High-five! We make a great team! (+10 XP)"
            
        self.say(msg, 3500)
        try:
            from core.voice_engine import get_voice_engine
            get_voice_engine().speak(msg)
        except Exception:
            pass

    def sparkle_cheer(self):
        """Cheer interaction: bursts sparkles, awards bond XP, plays celebration."""
        self.renderer._spawn_burst("star", 20)
        self.play_animation(CharacterState.CELEBRATING, duration_sec=3.5)
        from core.memory_manager import get_memory_manager
        mm = get_memory_manager()
        mm.add_bond_xp(5)
        name = mm.get_user_name()
        msg = f"⭐ Sparkle cheer! You've got this, {name}! 🚀" if name else "⭐ Sparkle cheer! Keep crushing it! 🚀"
        self.say(msg, 3500)
        try:
            from core.voice_engine import get_voice_engine
            get_voice_engine().speak(msg)
        except Exception:
            pass

    # Compatibility aliases for previous interactions
    def feed_karak_chai(self):
        self.high_five()

    def toss_gold_coin(self):
        self.sparkle_cheer()

    def turn_off(self):
        self.power_toggle_requested.emit()

    def quit_application(self):
        self.bubble.close()
        self.close()
        QApplication.instance().quit()
