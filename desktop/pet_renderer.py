"""
NEXUS Procedural Vector Animation & Rendering Engine
Renders the high-tech digital pet with real-time physics, cursor tracking,
particle systems, and 17 distinct animations without external image dependencies.
Includes the luxury 'Habibi of Dubai' traditional royal ghutra, agal, and gold aviators.
"""
import math
import random
import time
from typing import List, Tuple
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import (
    QPainter, QColor, QPen, QBrush, QLinearGradient, 
    QRadialGradient, QPainterPath, QFont
)
from core.character_state import CharacterState
from interface.themes import CharacterSkin

class Particle:
    """Lightweight visual particle for floating status effects."""
    def __init__(self, x: float, y: float, p_type: str, color: QColor):
        self.x = x
        self.y = y
        self.p_type = p_type  # 'zzz', 'star', 'sparkle', 'heart', 'ring', 'glitch', 'coin'
        self.color = color
        self.life = 1.0  # 1.0 to 0.0
        self.decay = random.uniform(0.015, 0.035)
        self.vx = random.uniform(-0.8, 0.8)
        self.vy = random.uniform(-1.8, -0.6)
        self.size = random.uniform(5.0, 11.0)
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-3, 3)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.rotation += self.rot_speed
        self.life -= self.decay

    @property
    def is_alive(self) -> bool:
        return self.life > 0.0

class PetRenderer:
    """Handles all drawing and animation math for NEXUS."""
    
    def __init__(self, skin: CharacterSkin):
        self.skin = skin
        self.state = CharacterState.IDLE
        self.previous_state = CharacterState.IDLE
        self.state_time = 0.0
        self.frame_count = 0
        
        # Physics & Transforms
        self.hover_offset = 0.0
        self.tilt_angle = 0.0
        self.walk_bounce = 0.0
        self.squish_x = 1.0
        self.squish_y = 1.0
        
        # Gaze tracking (relative offset -1.0 to 1.0)
        self.target_look_x = 0.0
        self.target_look_y = 0.0
        self.current_look_x = 0.0
        self.current_look_y = 0.0
        
        # Natural micro-saccades phase
        self.saccade_phase = random.uniform(0, 10.0)
        
        # Blinking logic
        self.blink_val = 0.0  # 0.0 = open, 1.0 = fully closed
        self.is_blinking = False
        self.next_blink_time = time.time() + random.uniform(2.5, 5.0)
        
        # Audio / Waveform animation for talking & listening
        self.wave_phase = 0.0
        
        # Holographic ring rotation angle
        self.ring_angle = 0.0
        
        # Particles
        self.particles: List[Particle] = []
        
        # Dragging flag
        self.is_dragged = False
        self.is_hovered = False

    def set_skin(self, skin: CharacterSkin):
        self.skin = skin

    def set_state(self, new_state: CharacterState):
        if self.state != new_state:
            self.previous_state = self.state
            self.state = new_state
            self.state_time = 0.0
            # Trigger state entry effects
            if new_state in (CharacterState.HAPPY, CharacterState.CELEBRATING):
                p_type = "coin" if self.skin.name == "habibi_dubai" else "star"
                self._spawn_burst(p_type, 14)
            elif new_state == CharacterState.SURPRISED:
                self.squish_x = 0.8
                self.squish_y = 1.25
            elif new_state == CharacterState.SLEEPING:
                self.particles.clear()

    def update_physics(self, dt: float, cursor_rel_x: float, cursor_rel_y: float):
        """Update mathematical animation positions and particles."""
        self.state_time += dt
        self.frame_count += 1
        
        # Update gaze with smooth easing
        target_x = max(-1.0, min(1.0, cursor_rel_x))
        target_y = max(-1.0, min(1.0, cursor_rel_y))
        if self.state == CharacterState.SLEEPING:
            target_x, target_y = 0.0, 0.3
        elif self.state == CharacterState.THINKING:
            target_x = math.sin(self.state_time * 2.0) * 0.6
            target_y = -0.7
        elif self.state == CharacterState.CONFUSED:
            target_x = 0.5
            target_y = -0.2
        else:
            # Natural biological eye micro-saccades (smooth lifelike micro-movements)
            if self.state != CharacterState.WORKING:
                saccade_x = math.sin(self.state_time * 0.95 + self.saccade_phase) * 0.07 + math.sin(self.state_time * 3.4) * 0.03
                saccade_y = math.cos(self.state_time * 1.15 + self.saccade_phase) * 0.05
                target_x = max(-1.0, min(1.0, target_x + saccade_x))
                target_y = max(-1.0, min(1.0, target_y + saccade_y))
            
        self.current_look_x += (target_x - self.current_look_x) * min(1.0, dt * 8.0)
        self.current_look_y += (target_y - self.current_look_y) * min(1.0, dt * 8.0)
        
        # Blinking update
        now = time.time()
        if self.state == CharacterState.SLEEPING:
            self.blink_val = 1.0
        else:
            if not self.is_blinking and now >= self.next_blink_time:
                self.is_blinking = True
                self.blink_val = 0.0
            
            if self.is_blinking:
                self.blink_val += dt * 14.0
                if self.blink_val >= 1.0:
                    self.blink_val = 1.0
                    if self.blink_val >= 1.0 and now > self.next_blink_time + 0.12:
                        self.is_blinking = False
                        self.blink_val = 0.0
                        self.next_blink_time = now + random.uniform(2.5, 6.0)
            else:
                self.blink_val = max(0.0, self.blink_val - dt * 10.0)

        # Orbiting ring angle
        ring_speed = 60.0
        if self.state in (CharacterState.THINKING, CharacterState.WORKING):
            ring_speed = 220.0
        elif self.state == CharacterState.CELEBRATING:
            ring_speed = 360.0
        elif self.state == CharacterState.SLEEPING:
            ring_speed = 15.0
        self.ring_angle = (self.ring_angle + ring_speed * dt) % 360.0

        # Sine wave hover physics
        if self.state == CharacterState.SLEEPING:
            self.hover_offset = math.sin(self.state_time * 1.5) * 4.0
            self.tilt_angle = math.sin(self.state_time * 0.8) * 2.0
        elif self.state == CharacterState.FLOATING:
            self.hover_offset = math.sin(self.state_time * 2.5) * 14.0
            self.tilt_angle = math.sin(self.state_time * 1.8) * 6.0
        elif self.state in (CharacterState.WALKING, CharacterState.RUNNING):
            speed_mult = 10.0 if self.state == CharacterState.RUNNING else 6.0
            self.walk_bounce = abs(math.sin(self.state_time * speed_mult)) * 10.0
            self.hover_offset = -self.walk_bounce
            self.tilt_angle = math.sin(self.state_time * speed_mult) * 8.0
        elif self.state == CharacterState.SITTING:
            self.hover_offset = 18.0
            self.tilt_angle = 0.0
        elif self.state == CharacterState.HAPPY:
            self.hover_offset = -abs(math.sin(self.state_time * 8.0)) * 16.0
            self.tilt_angle = math.sin(self.state_time * 6.0) * 5.0
        elif self.state == CharacterState.CELEBRATING:
            self.hover_offset = -abs(math.sin(self.state_time * 10.0)) * 22.0
            self.tilt_angle = math.sin(self.state_time * 12.0) * 15.0
        elif self.state == CharacterState.CONFUSED:
            self.hover_offset = math.sin(self.state_time * 2.0) * 5.0
            self.tilt_angle = 14.0
        else: # IDLE, LISTENING, TALKING, etc.
            self.hover_offset = math.sin(self.state_time * 2.2) * 6.5
            self.tilt_angle = math.sin(self.state_time * 1.2) * 3.0

        # Squish damping return to 1.0
        self.squish_x += (1.0 - self.squish_x) * min(1.0, dt * 10.0)
        self.squish_y += (1.0 - self.squish_y) * min(1.0, dt * 10.0)

        # Audio waveform phase for Talking/Listening
        self.wave_phase += dt * 8.0

        # Particle generation per state
        if self.state == CharacterState.SLEEPING and random.random() < 0.04:
            self.particles.append(Particle(90, 80, "zzz", self.skin.primary))
        elif self.state in (CharacterState.HAPPY, CharacterState.CELEBRATING) and random.random() < 0.28:
            if self.skin.name == "habibi_dubai":
                p_type = "coin" if random.random() < 0.4 else "star"
            else:
                p_type = "heart" if random.random() < 0.3 else "star"
            self.particles.append(Particle(random.uniform(50, 150), random.uniform(60, 130), p_type, self.skin.primary))
        elif self.state == CharacterState.ERROR and random.random() < 0.2:
            self.particles.append(Particle(random.uniform(60, 140), random.uniform(70, 120), "glitch", QColor(255, 60, 60)))
            
        # Update particles
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.is_alive]

    def _spawn_burst(self, p_type: str, count: int):
        for _ in range(count):
            p = Particle(100, 100, p_type, self.skin.primary)
            p.vx = random.uniform(-2.5, 2.5)
            p.vy = random.uniform(-3.5, 0.5)
            self.particles.append(p)

    def render(self, painter: QPainter, width: int, height: int):
        """Main drawing entry point. Renders NEXUS scaled to width/height."""
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

        # Reference coordinate space: 200 x 200
        painter.save()
        scale_x = width / 200.0
        scale_y = height / 200.0
        painter.scale(scale_x, scale_y)

        # Apply global hover & tilt transform
        cx, cy = 100.0, 105.0 + self.hover_offset
        painter.translate(cx, cy)
        painter.rotate(self.tilt_angle)
        painter.scale(self.squish_x, self.squish_y)
        painter.translate(-cx, -cy)

        # 1. Render bottom thruster / anti-gravity aura
        self._draw_thruster_aura(painter, cx, cy)

        # 2. Render back holographic orbiting ring
        self._draw_orbiting_ring(painter, cx, cy, is_back=True)

        # 2b. Render Habibi Ghutra Back Drapes (flowing behind the body)
        if self.skin.archetype == "habibi" or self.skin.name == "habibi_dubai":
            self._draw_ghutra_drapes(painter, cx, cy)

        # 3. Render distinct archetype physical features (Fox ears, Cat ears, Mech antennas, etc.)
        self._draw_archetype_features(painter, cx, cy)

        # 4. Render main chassis / cyber-orb body
        self._draw_body(painter, cx, cy)

        # 5. Render glossy OLED visor display
        self._draw_visor(painter, cx, cy)

        # 6. Render expressive eyes & face indicators
        self._draw_face(painter, cx, cy)

        # 6b. Render Habibi Ghutra Top Hood & Golden Agal Cord
        if self.skin.archetype == "habibi" or self.skin.name == "habibi_dubai":
            self._draw_ghutra_top_and_agal(painter, cx, cy)

        # 7. Render status badges (Exclamation, Question mark, Audio waves)
        self._draw_status_badges(painter, cx, cy)

        # 8. Render front holographic orbiting ring
        self._draw_orbiting_ring(painter, cx, cy, is_back=False)

        painter.restore()

        # 9. Render floating particles in absolute coordinates
        self._draw_particles(painter, scale_x, scale_y)

    def _draw_thruster_aura(self, painter: QPainter, cx: float, cy: float):
        """Draws the pulsing plasma levitation aura beneath NEXUS."""
        if self.state == CharacterState.SITTING:
            return
        
        pulse = 0.8 + 0.2 * math.sin(self.state_time * 6.0)
        aura_rad = 38.0 * pulse
        aura_rect = QRectF(cx - aura_rad, cy + 32.0, aura_rad * 2, 22.0 * pulse)

        grad = QRadialGradient(cx, cy + 42.0, aura_rad)
        aura_col = self.skin.aura
        if self.state == CharacterState.ERROR:
            aura_col = QColor(255, 60, 60, 70)
        grad.setColorAt(0.0, aura_col)
        grad.setColorAt(0.6, QColor(aura_col.red(), aura_col.green(), aura_col.blue(), 25))
        grad.setColorAt(1.0, QColor(0, 0, 0, 0))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(grad))
        painter.drawEllipse(aura_rect)

    def _draw_archetype_features(self, painter: QPainter, cx: float, cy: float):
        """Draws physical body additions based on the companion's archetype."""
        arch = getattr(self.skin, "archetype", "orb")
        fin_flap = math.sin(self.state_time * 4.0) * 3.0
        if self.state in (CharacterState.LISTENING, CharacterState.SURPRISED):
            fin_flap -= 5.0
        elif self.state in (CharacterState.SAD, CharacterState.SLEEPING):
            fin_flap += 5.0

        if arch == "fox":
            # 🦊 Quantum Kitsune: Tall Geometric Cyber-Fox Ears
            for side in (-1, 1):
                painter.save()
                bx = cx + side * 28
                by = cy - 44
                painter.translate(bx, by)
                painter.rotate(side * (18 + fin_flap))
                
                # Outer ear
                ear = QPainterPath()
                ear.moveTo(0, 0)
                ear.lineTo(side * 8, -32)
                ear.lineTo(side * 24, -4)
                ear.closeSubpath()
                painter.setPen(QPen(self.skin.body_rim, 2))
                painter.setBrush(QBrush(self.skin.body_fill))
                painter.drawPath(ear)

                # Inner glowing energy canal
                inner = QPainterPath()
                inner.moveTo(side * 2, -4)
                inner.lineTo(side * 8, -24)
                inner.lineTo(side * 18, -6)
                inner.closeSubpath()
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(self.skin.primary))
                painter.drawPath(inner)
                painter.restore()

        elif arch == "cat":
            # 🐱 Nebula Aether Cat: Curved Sleek Feline Ears & Starlight Halo
            for side in (-1, 1):
                painter.save()
                bx = cx + side * 30
                by = cy - 42
                painter.translate(bx, by)
                painter.rotate(side * (12 + fin_flap * 0.8))

                ear = QPainterPath()
                ear.moveTo(0, 0)
                ear.quadTo(side * 4, -26, side * 14, -28)
                ear.quadTo(side * 20, -14, side * 18, 4)
                ear.closeSubpath()
                painter.setPen(QPen(self.skin.body_rim, 2))
                painter.setBrush(QBrush(self.skin.body_fill))
                painter.drawPath(ear)

                # Soft starlight glow inside ear
                painter.setPen(QPen(self.skin.primary, 2))
                painter.drawLine(side * 6, -4, side * 12, -20)
                painter.restore()

            # Floating celestial halo above head
            halo_rect = QRectF(cx - 24, cy - 64 + fin_flap * 0.5, 48, 12)
            painter.setPen(QPen(self.skin.primary, 2))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(halo_rect)

        elif arch == "mech":
            # 🤖 Chrono Sentinel: Dual Tactical Antenna Fins & Visor HUD telemetry
            for side in (-1, 1):
                painter.save()
                bx = cx + side * 46
                by = cy - 14
                painter.translate(bx, by)
                painter.rotate(side * (5 + fin_flap * 0.5))

                fin = QPainterPath()
                fin.moveTo(0, 0)
                fin.lineTo(side * 6, -34)
                fin.lineTo(side * 18, -24)
                fin.lineTo(side * 12, 10)
                fin.closeSubpath()
                painter.setPen(QPen(self.skin.body_rim, 2.2))
                painter.setBrush(QBrush(self.skin.body_fill))
                painter.drawPath(fin)

                # Telemetry ticks
                painter.setPen(QPen(self.skin.primary, 1.8))
                painter.drawLine(side * 4, -8, side * 12, -4)
                painter.drawLine(side * 5, -16, side * 14, -12)
                painter.drawLine(side * 6, -24, side * 12, -21)
                painter.restore()

        elif arch == "phoenix":
            # 🔥 Solar Phoenix: Radiant Coronal Flare Crown & Prominence Winglets
            painter.save()
            crown_pulse = math.sin(self.state_time * 6.0) * 4.0
            crest = QPainterPath()
            crest.moveTo(cx - 18, cy - 48)
            crest.quadTo(cx - 10, cy - 70 - crown_pulse, cx, cy - 78 - crown_pulse)
            crest.quadTo(cx + 10, cy - 70 - crown_pulse, cx + 18, cy - 48)
            crest.closeSubpath()
            painter.setPen(QPen(self.skin.secondary, 1.8))
            painter.setBrush(QBrush(self.skin.primary))
            painter.drawPath(crest)
            painter.restore()

            self._draw_side_fins(painter, cx, cy)

        elif arch == "phantom":
            # 🖤 Obsidian Phantom: Stealth Swept-back Armor Winglets with Laser Edges
            for side in (-1, 1):
                painter.save()
                bx = cx + side * 50
                by = cy - 6
                painter.translate(bx, by)
                painter.rotate(side * (24 + fin_flap * 0.4))

                wing = QPainterPath()
                wing.moveTo(0, 0)
                wing.lineTo(side * 24, -12)
                wing.lineTo(side * 14, 18)
                wing.closeSubpath()
                painter.setPen(QPen(self.skin.primary, 1.8))
                painter.setBrush(QBrush(self.skin.body_fill))
                painter.drawPath(wing)
                painter.restore()

        elif arch == "habibi":
            # 👑 Royal Habibi of Dubai: Ghutra drapes and Agal canopy are layered in main render sequence
            pass

        else:
            # ✦ Neo Cyber Core (Default Orb): Dual Aerodynamic Propulsion Fins
            self._draw_side_fins(painter, cx, cy)

    def _draw_side_fins(self, painter: QPainter, cx: float, cy: float):
        """Dual aerodynamic cyber fins / audio sensor ears."""
        fin_flap = math.sin(self.state_time * 4.0) * 3.0
        if self.state in (CharacterState.LISTENING, CharacterState.SURPRISED):
            fin_flap -= 6.0
        elif self.state in (CharacterState.SAD, CharacterState.SLEEPING):
            fin_flap += 6.0

        # Left Fin
        painter.save()
        painter.translate(cx - 52, cy - 8 + fin_flap)
        painter.rotate(-15 + fin_flap)
        path_l = QPainterPath()
        path_l.moveTo(0, 0)
        path_l.lineTo(-20, -18)
        path_l.quadTo(-26, 0, -14, 16)
        path_l.closeSubpath()
        painter.setPen(QPen(self.skin.body_rim, 2))
        painter.setBrush(QBrush(self.skin.body_fill))
        painter.drawPath(path_l)
        
        painter.setPen(QPen(self.skin.primary, 1.5))
        painter.drawLine(-4, -2, -16, -10)
        painter.restore()

        # Right Fin
        painter.save()
        painter.translate(cx + 52, cy - 8 - fin_flap)
        painter.rotate(15 - fin_flap)
        path_r = QPainterPath()
        path_r.moveTo(0, 0)
        path_r.lineTo(20, -18)
        path_r.quadTo(26, 0, 14, 16)
        path_r.closeSubpath()
        painter.setPen(QPen(self.skin.body_rim, 2))
        painter.setBrush(QBrush(self.skin.body_fill))
        painter.drawPath(path_r)
        
        painter.setPen(QPen(self.skin.primary, 1.5))
        painter.drawLine(4, -2, 16, -10)
        painter.restore()

    def _draw_body(self, painter: QPainter, cx: float, cy: float):
        """Draws the main titanium/ceramic cyber-orb body chassis or Kandura robe."""
        body_rect = QRectF(cx - 55, cy - 50, 110, 100)

        rim_grad = QRadialGradient(cx, cy - 20, 65)
        rim_grad.setColorAt(0.0, self.skin.body_fill.lighter(115))
        rim_grad.setColorAt(0.7, self.skin.body_fill)
        rim_grad.setColorAt(1.0, self.skin.body_rim)

        painter.setPen(QPen(self.skin.body_rim, 2.5))
        painter.setBrush(QBrush(rim_grad))
        painter.drawRoundedRect(body_rect, 45, 45)

        # Standard top sensor antenna
        halo_rect = QRectF(cx - 10, cy - 58, 20, 9)
        painter.setPen(QPen(self.skin.body_rim, 1.5))
        painter.setBrush(QBrush(self.skin.primary if self.state != CharacterState.ERROR else QColor(255, 60, 60)))
        painter.drawRoundedRect(halo_rect, 4, 4)

    def _draw_visor(self, painter: QPainter, cx: float, cy: float):
        """Draws the curved high-gloss OLED screen visor."""
        visor_rect = QRectF(cx - 44, cy - 35, 88, 68)

        visor_grad = QLinearGradient(cx, cy - 35, cx, cy + 33)
        visor_grad.setColorAt(0.0, self.skin.visor_bg.lighter(120))
        visor_grad.setColorAt(0.7, self.skin.visor_bg)
        visor_grad.setColorAt(1.0, self.skin.visor_bg.darker(110))

        is_habibi = (self.skin.archetype == "habibi" or self.skin.name == "habibi_dubai")
        rim_pen = QPen(QColor(212, 175, 55) if is_habibi else self.skin.secondary.darker(120), 1.8)
        painter.setPen(rim_pen)
        painter.setBrush(QBrush(visor_grad))
        painter.drawRoundedRect(visor_rect, 24, 24)

        # Visor glass reflection arc (sheen highlight)
        sheen_path = QPainterPath()
        sheen_path.moveTo(cx - 36, cy - 28)
        sheen_path.quadTo(cx, cy - 33, cx + 36, cy - 28)
        sheen_path.quadTo(cx, cy - 26, cx - 36, cy - 28)
        painter.setPen(Qt.PenStyle.NoPen)
        sheen_col = QColor(255, 235, 150, 45) if is_habibi else QColor(255, 255, 255, 45)
        painter.setBrush(QBrush(sheen_col))
        painter.drawPath(sheen_path)

    def _draw_face(self, painter: QPainter, cx: float, cy: float):
        """Draws expressive eyes and dynamic facial expressions."""
        look_ox = self.current_look_x * 7.0
        look_oy = self.current_look_y * 5.0
        
        eye_y = cy - 4 + look_oy
        left_eye_x = cx - 18 + look_ox
        right_eye_x = cx + 18 + look_ox

        eye_color = self.skin.primary
        if self.state == CharacterState.ERROR:
            eye_color = QColor(255, 70, 70)
        elif self.state == CharacterState.SAD:
            eye_color = QColor(100, 180, 255)
        elif self.state == CharacterState.CELEBRATING:
            hue = int((self.frame_count * 3) % 360)
            eye_color = QColor.fromHsv(hue, 220, 255)

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        # Check if Habibi appearance: Luxury Gold Aviator Sunglasses
        if self.skin.archetype == "habibi" or self.skin.name == "habibi_dubai":
            self._draw_dubai_aviators(painter, cx, cy, eye_y, left_eye_x, right_eye_x, eye_color)
        else:
            # Standard high-expressivity eye renderer
            self._draw_standard_eyes(painter, cx, cy, eye_y, left_eye_x, right_eye_x, eye_color)

        # Rosy cheeks blush when HAPPY, CELEBRATING or hovered
        if self.state in (CharacterState.HAPPY, CharacterState.CELEBRATING) or self.is_hovered:
            painter.save()
            painter.setPen(Qt.PenStyle.NoPen)
            blush_col = QColor(255, 110, 150, 110)  # Soft rose pink glow
            painter.setBrush(QBrush(blush_col))
            painter.drawEllipse(QPointF(cx - 27, cy + 10), 6.5, 3.8)
            painter.drawEllipse(QPointF(cx + 27, cy + 10), 6.5, 3.8)
            painter.restore()

        # Dynamic Mouth / Audio Equalizer in visor
        if self.state in (CharacterState.TALKING, CharacterState.LISTENING):
            bar_y = cy + 18
            painter.setPen(Qt.PenStyle.NoPen)
            for i in range(5):
                bx = cx - 16 + i * 8
                if self.state == CharacterState.TALKING:
                    bh = 3.0 + abs(math.sin(self.wave_phase + i * 1.2)) * 12.0
                else:
                    bh = 2.0 + abs(math.sin(self.wave_phase * 0.6 + i * 0.8)) * 6.0
                painter.setBrush(QBrush(eye_color.lighter(120)))
                painter.drawRoundedRect(QRectF(bx - 2, bar_y - bh/2, 4, bh), 2, 2)
        elif self.state in (CharacterState.HAPPY, CharacterState.CELEBRATING):
            painter.setPen(QPen(eye_color, 2.2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            m_path = QPainterPath()
            m_path.moveTo(cx - 7, cy + 16)
            m_path.quadTo(cx, cy + 23, cx + 7, cy + 16)
            painter.drawPath(m_path)
        elif self.state == CharacterState.WORKING:
            painter.setPen(QPen(eye_color, 1.5))
            code_step = int((self.frame_count // 3) % 4)
            for i in range(4):
                bx = cx - 12 + i * 8
                by = cy + 17
                if i == code_step:
                    painter.setBrush(QBrush(eye_color))
                    painter.drawRect(QRectF(bx, by, 4, 3))

        painter.restore()

    def _draw_standard_eyes(self, painter: QPainter, cx: float, cy: float, eye_y: float,
                            left_eye_x: float, right_eye_x: float, eye_color: QColor):
        """Draws standard expressive eyes for other skins."""
        if self.state == CharacterState.SLEEPING or self.blink_val > 0.8:
            painter.setPen(QPen(eye_color, 3.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            path_l = QPainterPath()
            path_l.moveTo(left_eye_x - 9, eye_y + 1)
            path_l.quadTo(left_eye_x, eye_y + 6, left_eye_x + 9, eye_y + 1)
            painter.drawPath(path_l)
            path_r = QPainterPath()
            path_r.moveTo(right_eye_x - 9, eye_y + 1)
            path_r.quadTo(right_eye_x, eye_y + 6, right_eye_x + 9, eye_y + 1)
            painter.drawPath(path_r)

        elif self.state in (CharacterState.HAPPY, CharacterState.CELEBRATING):
            painter.setPen(QPen(eye_color, 3.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            path_l = QPainterPath()
            path_l.moveTo(left_eye_x - 10, eye_y + 4)
            path_l.quadTo(left_eye_x, eye_y - 8, left_eye_x + 10, eye_y + 4)
            painter.drawPath(path_l)
            path_r = QPainterPath()
            path_r.moveTo(right_eye_x - 10, eye_y + 4)
            path_r.quadTo(right_eye_x, eye_y - 8, right_eye_x + 10, eye_y + 4)
            painter.drawPath(path_r)

        elif self.state == CharacterState.SAD:
            painter.setPen(QPen(eye_color, 3.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            path_l = QPainterPath()
            path_l.moveTo(left_eye_x - 9, eye_y - 3)
            path_l.quadTo(left_eye_x, eye_y + 5, left_eye_x + 9, eye_y)
            painter.drawPath(path_l)
            path_r = QPainterPath()
            path_r.moveTo(right_eye_x - 9, eye_y)
            path_r.quadTo(right_eye_x, eye_y + 5, right_eye_x + 9, eye_y - 3)
            painter.drawPath(path_r)

        elif self.state == CharacterState.SURPRISED:
            painter.setPen(QPen(eye_color, 2.5))
            painter.setBrush(QBrush(eye_color.lighter(130)))
            painter.drawEllipse(QPointF(left_eye_x, eye_y), 11.0, 13.0)
            painter.drawEllipse(QPointF(right_eye_x, eye_y), 11.0, 13.0)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(self.skin.visor_bg))
            painter.drawEllipse(QPointF(left_eye_x, eye_y), 4.5, 4.5)
            painter.drawEllipse(QPointF(right_eye_x, eye_y), 4.5, 4.5)

        elif self.state == CharacterState.CONFUSED:
            painter.setPen(QPen(eye_color, 2.5))
            painter.setBrush(QBrush(eye_color))
            painter.drawRoundedRect(QRectF(left_eye_x - 9, eye_y - 10, 18, 20), 8, 8)
            painter.drawRoundedRect(QRectF(right_eye_x - 8, eye_y - 3, 16, 8), 4, 4)

        elif self.state == CharacterState.THINKING:
            t_angle = self.state_time * 5.0
            painter.setPen(QPen(eye_color, 2.0))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(QPointF(left_eye_x, eye_y), 9.0, 9.0)
            painter.drawEllipse(QPointF(right_eye_x, eye_y), 9.0, 9.0)
            ox = math.cos(t_angle) * 4.5
            oy = math.sin(t_angle) * 4.5
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(eye_color))
            painter.drawEllipse(QPointF(left_eye_x + ox, eye_y + oy), 3.0, 3.0)
            painter.drawEllipse(QPointF(right_eye_x + ox, eye_y + oy), 3.0, 3.0)

        elif self.state == CharacterState.ERROR:
            painter.setPen(QPen(eye_color, 3.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(left_eye_x - 7, eye_y - 7, left_eye_x + 7, eye_y + 7)
            painter.drawLine(left_eye_x - 7, eye_y + 7, left_eye_x + 7, eye_y - 7)
            painter.drawLine(right_eye_x - 7, eye_y - 7, right_eye_x + 7, eye_y + 7)
            painter.drawLine(right_eye_x - 7, eye_y + 7, right_eye_x + 7, eye_y - 7)

        else:
            eye_h = 17.0 * (1.0 - self.blink_val)
            eye_w = 12.0
            if eye_h > 1.0:
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(eye_color))
                painter.drawRoundedRect(QRectF(left_eye_x - eye_w/2, eye_y - eye_h/2, eye_w, eye_h), 5, 5)
                painter.drawRoundedRect(QRectF(right_eye_x - eye_w/2, eye_y - eye_h/2, eye_w, eye_h), 5, 5)
                
                painter.setBrush(QBrush(QColor(255, 255, 255, 220)))
                painter.drawEllipse(QPointF(left_eye_x - 2, eye_y - 3), 2.2, 2.2)
                painter.drawEllipse(QPointF(right_eye_x - 2, eye_y - 3), 2.2, 2.2)

    def _draw_ghutra_drapes(self, painter: QPainter, cx: float, cy: float):
        """Traditional white Ghutra drapes flowing over the shoulders with wind physics."""
        sway = math.sin(self.state_time * 3.0) * 3.5

        painter.save()
        painter.setPen(QPen(QColor(212, 175, 55, 180), 1.5))  # Subtle gold edge trim

        # Left flowing drape
        path_l = QPainterPath()
        path_l.moveTo(cx - 38, cy - 36)
        path_l.cubicTo(cx - 62, cy - 10, cx - 68 + sway, cy + 24, cx - 48 + sway, cy + 54)
        path_l.cubicTo(cx - 40, cy + 44, cx - 35, cy + 10, cx - 36, cy - 20)
        path_l.closeSubpath()

        # Silk gradient for drapery
        grad_l = QLinearGradient(cx - 65, cy, cx - 35, cy)
        grad_l.setColorAt(0.0, QColor(240, 244, 250, 245))
        grad_l.setColorAt(1.0, QColor(255, 255, 255, 255))
        painter.setBrush(QBrush(grad_l))
        painter.drawPath(path_l)

        # Right flowing drape
        path_r = QPainterPath()
        path_r.moveTo(cx + 38, cy - 36)
        path_r.cubicTo(cx + 62, cy - 10, cx + 68 - sway, cy + 24, cx + 48 - sway, cy + 54)
        path_r.cubicTo(cx + 40, cy + 44, cx + 35, cy + 10, cx + 36, cy - 20)
        path_r.closeSubpath()

        grad_r = QLinearGradient(cx + 35, cy, cx + 65, cy)
        grad_r.setColorAt(0.0, QColor(255, 255, 255, 255))
        grad_r.setColorAt(1.0, QColor(240, 244, 250, 245))
        painter.setBrush(QBrush(grad_r))
        painter.drawPath(path_r)
        painter.restore()

    def _draw_ghutra_top_and_agal(self, painter: QPainter, cx: float, cy: float):
        """Draws the pristine white Ghutra canopy over head and the double black & gold Agal."""
        painter.save()

        # 1. White Ghutra canopy wrapping over crown
        ghutra_path = QPainterPath()
        ghutra_path.moveTo(cx - 48, cy - 34)
        ghutra_path.cubicTo(cx - 50, cy - 58, cx - 25, cy - 65, cx, cy - 66)
        ghutra_path.cubicTo(cx + 25, cy - 65, cx + 50, cy - 58, cx + 48, cy - 34)
        ghutra_path.quadTo(cx, cy - 40, cx - 48, cy - 34)

        g_grad = QLinearGradient(cx, cy - 66, cx, cy - 34)
        g_grad.setColorAt(0.0, QColor(255, 255, 255))
        g_grad.setColorAt(1.0, QColor(242, 246, 252))
        painter.setPen(QPen(QColor(212, 175, 55, 180), 1.2))
        painter.setBrush(QBrush(g_grad))
        painter.drawPath(ghutra_path)

        # 2. Double Black Agal (Cords)
        # Upper Agal ring
        painter.setPen(QPen(QColor(18, 20, 26), 5.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        path_agal_upper = QPainterPath()
        path_agal_upper.moveTo(cx - 40, cy - 52)
        path_agal_upper.quadTo(cx, cy - 57, cx + 40, cy - 52)
        painter.drawPath(path_agal_upper)

        # Lower Agal ring
        painter.setPen(QPen(QColor(24, 26, 32), 5.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        path_agal_lower = QPainterPath()
        path_agal_lower.moveTo(cx - 42, cy - 46)
        path_agal_lower.quadTo(cx, cy - 51, cx + 42, cy - 46)
        painter.drawPath(path_agal_lower)

        # Gold decorative clasp rings on the Agal
        painter.setPen(QPen(QColor(255, 215, 0), 2.5))
        painter.drawLine(cx - 22, cy - 55, cx - 22, cy - 44)
        painter.drawLine(cx + 22, cy - 55, cx + 22, cy - 44)

        # Center Royal Dubai Gold Crest
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(255, 215, 0)))
        # Gold diamond crest
        d_path = QPainterPath()
        d_path.moveTo(cx, cy - 56)
        d_path.lineTo(cx + 4.5, cy - 49)
        d_path.lineTo(cx, cy - 42)
        d_path.lineTo(cx - 4.5, cy - 49)
        d_path.closeSubpath()
        painter.drawPath(d_path)

        painter.restore()

    def _draw_dubai_aviators(self, painter: QPainter, cx: float, cy: float, eye_y: float,
                             left_eye_x: float, right_eye_x: float, eye_color: QColor):
        """Renders luxury gold-framed aviator sunglasses with glowing eyes and lens glints."""
        # Aviator lens size
        aw, ah = 19.0, 16.0

        # Gold top bridge bar connecting shades
        painter.setPen(QPen(QColor(255, 215, 0), 2.2))
        painter.drawLine(left_eye_x + 5, eye_y - 8, right_eye_x - 5, eye_y - 8)

        # Mirrored dark aviator glass fill
        lens_grad = QLinearGradient(cx, eye_y - ah, cx, eye_y + ah)
        lens_grad.setColorAt(0.0, QColor(25, 20, 15, 230))
        lens_grad.setColorAt(0.6, QColor(10, 8, 5, 245))
        lens_grad.setColorAt(1.0, QColor(30, 25, 18, 230))

        for lx in (left_eye_x, right_eye_x):
            # Teardrop aviator lens path
            l_path = QPainterPath()
            l_path.moveTo(lx - aw/2, eye_y - ah/2)
            l_path.lineTo(lx + aw/2, eye_y - ah/2)
            l_path.cubicTo(lx + aw/2, eye_y + ah/2, lx + aw/4, eye_y + ah/2 + 2, lx, eye_y + ah/2 + 2)
            l_path.cubicTo(lx - aw/4, eye_y + ah/2 + 2, lx - aw/2, eye_y + ah/2, lx - aw/2, eye_y - ah/2)
            l_path.closeSubpath()

            # Fill lens
            painter.setPen(QPen(QColor(255, 215, 0), 1.8))
            painter.setBrush(QBrush(lens_grad))
            painter.drawPath(l_path)

            # Diagonal gold mirror reflection glint
            glint_path = QPainterPath()
            glint_path.moveTo(lx - aw/3, eye_y - ah/2 + 2)
            glint_path.lineTo(lx - aw/4, eye_y - ah/2 + 2)
            glint_path.lineTo(lx + aw/3, eye_y + ah/2 - 2)
            glint_path.lineTo(lx + aw/4, eye_y + ah/2 - 2)
            glint_path.closeSubpath()
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(255, 235, 160, 90)))
            painter.drawPath(glint_path)

        # Glowing golden pupils visible through the shades
        if self.state not in (CharacterState.SLEEPING,) and self.blink_val < 0.6:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(255, 215, 0, 200)))
            painter.drawEllipse(QPointF(left_eye_x, eye_y), 4.5, 4.5)
            painter.drawEllipse(QPointF(right_eye_x, eye_y), 4.5, 4.5)

        # Star glint on frame corner when happy or celebrating
        if self.state in (CharacterState.HAPPY, CharacterState.CELEBRATING):
            gx = right_eye_x + aw/2
            gy = eye_y - ah/2
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(255, 255, 255, 240)))
            # Mini 4-point star
            s = 4.5
            sp = QPainterPath()
            sp.moveTo(gx, gy - s)
            sp.lineTo(gx + s*0.3, gy)
            sp.lineTo(gx + s, gy)
            sp.lineTo(gx + s*0.3, gy)
            sp.lineTo(gx, gy + s)
            sp.lineTo(gx - s*0.3, gy)
            sp.lineTo(gx - s, gy)
            sp.lineTo(gx - s*0.3, gy)
            sp.closeSubpath()
            painter.drawPath(sp)

    def _draw_status_badges(self, painter: QPainter, cx: float, cy: float):
        """Draws overhead alert icons: '!', '?', radar arcs, error badges."""
        if self.state == CharacterState.SURPRISED:
            badge_y = cy - 68
            painter.setPen(QPen(self.skin.primary, 1.5))
            painter.setBrush(QBrush(self.skin.body_fill))
            painter.drawEllipse(QPointF(cx, badge_y), 12, 12)
            painter.setPen(QPen(self.skin.primary, 3.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(cx, badge_y - 6, cx, badge_y)
            painter.drawPoint(cx, badge_y + 5)

        elif self.state == CharacterState.CONFUSED:
            badge_y = cy - 68
            painter.setPen(QPen(self.skin.primary, 1.5))
            painter.setBrush(QBrush(self.skin.body_fill))
            painter.drawEllipse(QPointF(cx + 12, badge_y), 11, 11)
            painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            painter.setPen(self.skin.primary)
            painter.drawText(QRectF(cx + 2, badge_y - 10, 20, 20), Qt.AlignmentFlag.AlignCenter, "?")

        elif self.state == CharacterState.LISTENING:
            radar_y = cy - 62
            painter.setPen(Qt.PenStyle.NoPen)
            for r in range(1, 3):
                arc_rad = 12.0 + r * 8.0 + math.sin(self.wave_phase + r) * 3.0
                painter.setPen(QPen(QColor(self.skin.primary.red(), self.skin.primary.green(), self.skin.primary.blue(), 180 - r * 60), 2.0))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawArc(QRectF(cx - arc_rad, radar_y - arc_rad, arc_rad * 2, arc_rad * 2), 45 * 16, 90 * 16)

    def _draw_orbiting_ring(self, painter: QPainter, cx: float, cy: float, is_back: bool):
        """Renders 3D perspective holographic ring orbiting NEXUS."""
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(22)

        rad_x = 76.0
        rad_y = 22.0
        ring_rect = QRectF(-rad_x, -rad_y, rad_x * 2, rad_y * 2)

        painter.setBrush(Qt.BrushStyle.NoBrush)
        ring_pen = QPen(self.skin.secondary, 2.0, Qt.PenStyle.DashLine)
        if self.state == CharacterState.ERROR:
            ring_pen.setColor(QColor(255, 60, 60))
        painter.setPen(ring_pen)

        if is_back:
            painter.drawArc(ring_rect, 0 * 16, 180 * 16)
        else:
            painter.drawArc(ring_rect, 180 * 16, 180 * 16)

            rad = math.radians(self.ring_angle)
            node_x = math.cos(rad) * rad_x
            node_y = math.sin(rad) * rad_y
            if node_y >= 0:
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(self.skin.primary if self.state != CharacterState.ERROR else QColor(255, 90, 90)))
                painter.drawEllipse(QPointF(node_x, node_y), 4.5, 4.5)

        painter.restore()

    def _draw_particles(self, painter: QPainter, scale_x: float, scale_y: float):
        """Draws all active floating particles (Zzz, sparkles, hearts, stars, coins)."""
        painter.save()
        for p in self.particles:
            alpha = int(max(0.0, min(1.0, p.life)) * 255)
            p_col = QColor(p.color.red(), p.color.green(), p.color.blue(), alpha)
            
            px = p.x * scale_x
            py = p.y * scale_y
            
            if p.p_type == "zzz":
                painter.setFont(QFont("Segoe UI", int(p.size), QFont.Weight.Bold))
                painter.setPen(p_col)
                painter.drawText(QPointF(px, py), "Z")
            elif p.p_type == "coin":
                # Golden Dubai Dirham coin particle
                painter.setPen(QPen(QColor(212, 175, 55, alpha), 1.2))
                painter.setBrush(QBrush(QColor(255, 215, 0, alpha)))
                painter.drawEllipse(QPointF(px, py), p.size * 0.7, p.size * 0.7)
                painter.setPen(QPen(QColor(180, 140, 20, alpha), 1.0))
                painter.drawEllipse(QPointF(px, py), p.size * 0.45, p.size * 0.45)
            elif p.p_type in ("star", "sparkle"):
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(p_col))
                s = p.size
                path = QPainterPath()
                path.moveTo(px, py - s)
                path.lineTo(px + s * 0.4, py - s * 0.2)
                path.lineTo(px + s, py)
                path.lineTo(px + s * 0.4, py + s * 0.2)
                path.lineTo(px, py + s)
                path.lineTo(px - s * 0.4, py + s * 0.2)
                path.lineTo(px - s, py)
                path.lineTo(px - s * 0.4, py - s * 0.2)
                path.closeSubpath()
                painter.drawPath(path)
            elif p.p_type == "heart":
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(QColor(255, 100, 150, alpha)))
                s = p.size * 0.8
                path = QPainterPath()
                path.moveTo(px, py + s)
                path.cubicTo(px - s, py, px - s, py - s, px, py - s * 0.4)
                path.cubicTo(px + s, py - s, px + s, py, px, py + s)
                painter.drawPath(path)
            elif p.p_type == "glitch":
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(p_col))
                painter.drawRect(QRectF(px, py, p.size, 3))

        painter.restore()
