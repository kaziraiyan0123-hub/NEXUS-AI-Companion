"""
NEXUS Unique Companion Appearance & Styling System
Provides futuristic cyber/HUD palettes, unique companion archetypes, and clean UI stylesheets.
Features distinctive procedural companion archetypes: Neo Core, Quantum Fox, Chrono Mech, Nebula Cat, Solar Phoenix, and Obsidian Phantom.
"""
from dataclasses import dataclass
from typing import Dict
from PySide6.QtGui import QColor

@dataclass
class CharacterSkin:
    name: str
    display_name: str
    archetype: str        # 'orb', 'fox', 'mech', 'cat', 'phoenix', 'phantom'
    primary: QColor       # Core glow & eye color
    secondary: QColor     # Accents & rings
    body_fill: QColor     # Chassis main
    body_rim: QColor      # Outer metallic rim
    visor_bg: QColor      # Visor background
    aura: QColor          # Floating aura / particles
    hud_border: str       # Hex string for UI CSS
    hud_bg: str           # Hex string for UI CSS

SKINS: Dict[str, CharacterSkin] = {
    "neo_cyber": CharacterSkin(
        name="neo_cyber",
        display_name="✦ Neo Cyber Core (Default)",
        archetype="orb",
        primary=QColor(0, 240, 255),          # Hyper-Cyan Laser
        secondary=QColor(56, 189, 248),        # Sky Accent
        body_fill=QColor(13, 17, 23, 245),     # Deep Carbon
        body_rim=QColor(30, 41, 59, 255),      # Titanium Alloy Rim
        visor_bg=QColor(8, 12, 18, 250),       # Stealth Visor
        aura=QColor(0, 240, 255, 65),          # Cyan Gyroscopic Aura
        hud_border="rgba(255, 255, 255, 0.08)",
        hud_bg="rgba(13, 17, 23, 0.96)"
    ),
    "quantum_fox": CharacterSkin(
        name="quantum_fox",
        display_name="🦊 Quantum Kitsune (Cyber Fox)",
        archetype="fox",
        primary=QColor(245, 158, 11),         # Radiant Amber Glow
        secondary=QColor(251, 191, 36),       # Warm Gold Accent
        body_fill=QColor(28, 18, 12, 245),     # Smoked Amber Carbon
        body_rim=QColor(78, 48, 25, 255),      # Polished Bronze Rim
        visor_bg=QColor(16, 10, 8, 250),       # Dark Amber Visor
        aura=QColor(245, 158, 11, 75),        # Foxfire Particle Aura
        hud_border="rgba(255, 255, 255, 0.08)",
        hud_bg="rgba(13, 17, 23, 0.96)"
    ),
    "chrono_mech": CharacterSkin(
        name="chrono_mech",
        display_name="🤖 Chrono Sentinel (Tactical Mecha)",
        archetype="mech",
        primary=QColor(56, 189, 248),         # Tactical HUD Blue
        secondary=QColor(99, 102, 241),       # Indigo Secondary
        body_fill=QColor(20, 27, 45, 245),     # Matte Navy Plating
        body_rim=QColor(51, 65, 85, 255),      # Armored Steel Rim
        visor_bg=QColor(10, 15, 28, 250),      # Polarized HUD Display
        aura=QColor(56, 189, 248, 60),         # Telemetry Wave Aura
        hud_border="rgba(255, 255, 255, 0.08)",
        hud_bg="rgba(13, 17, 23, 0.96)"
    ),
    "nebula_cat": CharacterSkin(
        name="nebula_cat",
        display_name="🐱 Nebula Aether Cat (Starlight Feline)",
        archetype="cat",
        primary=QColor(192, 132, 252),        # Ethereal Violet
        secondary=QColor(244, 114, 182),      # Cosmic Pink
        body_fill=QColor(24, 16, 36, 245),     # Deep Starlight Chassis
        body_rim=QColor(68, 45, 98, 255),      # Amethyst Rim
        visor_bg=QColor(14, 8, 22, 250),       # Galaxy Visor
        aura=QColor(192, 132, 252, 70),       # Star Dust Nebula Aura
        hud_border="rgba(255, 255, 255, 0.08)",
        hud_bg="rgba(13, 17, 23, 0.96)"
    ),
    "solar_phoenix": CharacterSkin(
        name="solar_phoenix",
        display_name="🔥 Solar Phoenix (Corona Fire)",
        archetype="phoenix",
        primary=QColor(251, 146, 60),         # Coronal Orange
        secondary=QColor(239, 68, 68),        # Solar Red
        body_fill=QColor(32, 16, 10, 245),     # Obsidian Volcanic
        body_rim=QColor(92, 40, 20, 255),      # Fire-Forged Rim
        visor_bg=QColor(20, 8, 6, 250),        # Solar Prominence Visor
        aura=QColor(251, 146, 60, 75),        # Plasma Flame Aura
        hud_border="rgba(255, 255, 255, 0.08)",
        hud_bg="rgba(13, 17, 23, 0.96)"
    ),
    "obsidian_phantom": CharacterSkin(
        name="obsidian_phantom",
        display_name="🖤 Obsidian Phantom (Stealth Shadow)",
        archetype="phantom",
        primary=QColor(244, 63, 94),          # Crimson Laser Slit
        secondary=QColor(225, 29, 72),        # Ruby Accent
        body_fill=QColor(10, 10, 12, 250),     # True Matte Pitch Black
        body_rim=QColor(35, 35, 42, 255),      # Shadow Carbon Rim
        visor_bg=QColor(4, 4, 6, 255),         # Void Visor
        aura=QColor(244, 63, 94, 55),          # Shadow Smoke Aura
        hud_border="rgba(255, 255, 255, 0.08)",
        hud_bg="rgba(13, 17, 23, 0.96)"
    ),
    "matrix_green": CharacterSkin(
        name="matrix_green",
        display_name="⚡ Matrix Emerald (Data Terminal)",
        archetype="orb",
        primary=QColor(52, 211, 153),         # Terminal Phosphor Green
        secondary=QColor(16, 185, 129),       # Emerald Accent
        body_fill=QColor(10, 24, 16, 245),     # Cyber Matrix Dark
        body_rim=QColor(25, 60, 40, 255),      # Cyber Alloy Rim
        visor_bg=QColor(6, 16, 10, 250),       # Green Phosphor Visor
        aura=QColor(52, 211, 153, 65),        # Data Glyph Aura
        hud_border="rgba(255, 255, 255, 0.08)",
        hud_bg="rgba(13, 17, 23, 0.96)"
    ),
    # Legacy & compatibility skins
    "cyber_cyan": CharacterSkin(
        name="cyber_cyan",
        display_name="✦ Cyber Cyan (Legacy)",
        archetype="orb",
        primary=QColor(0, 240, 255),
        secondary=QColor(56, 189, 248),
        body_fill=QColor(13, 17, 23, 245),
        body_rim=QColor(30, 41, 59, 255),
        visor_bg=QColor(8, 12, 18, 250),
        aura=QColor(0, 240, 255, 65),
        hud_border="rgba(255, 255, 255, 0.08)",
        hud_bg="rgba(13, 17, 23, 0.96)"
    ),
    "neon_purple": CharacterSkin(
        name="neon_purple",
        display_name="💜 Neon Purple (Legacy)",
        archetype="cat",
        primary=QColor(168, 85, 247),
        secondary=QColor(217, 70, 239),
        body_fill=QColor(20, 15, 30, 245),
        body_rim=QColor(50, 30, 75, 255),
        visor_bg=QColor(12, 8, 20, 250),
        aura=QColor(168, 85, 247, 70),
        hud_border="rgba(255, 255, 255, 0.08)",
        hud_bg="rgba(13, 17, 23, 0.96)"
    ),
    "sunset_amber": CharacterSkin(
        name="sunset_amber",
        display_name="🌅 Sunset Amber (Legacy)",
        archetype="fox",
        primary=QColor(245, 158, 11),
        secondary=QColor(251, 191, 36),
        body_fill=QColor(28, 18, 12, 245),
        body_rim=QColor(78, 48, 25, 255),
        visor_bg=QColor(16, 10, 8, 250),
        aura=QColor(245, 158, 11, 75),
        hud_border="rgba(255, 255, 255, 0.08)",
        hud_bg="rgba(13, 17, 23, 0.96)"
    ),
    "cosmic_white": CharacterSkin(
        name="cosmic_white",
        display_name="❄️ Cosmic White (Legacy)",
        archetype="orb",
        primary=QColor(226, 232, 240),
        secondary=QColor(148, 163, 184),
        body_fill=QColor(15, 23, 42, 245),
        body_rim=QColor(51, 65, 85, 255),
        visor_bg=QColor(10, 15, 30, 250),
        aura=QColor(226, 232, 240, 60),
        hud_border="rgba(255, 255, 255, 0.08)",
        hud_bg="rgba(13, 17, 23, 0.96)"
    ),
    "habibi_dubai": CharacterSkin(
        name="habibi_dubai",
        display_name="👑 Royal Habibi of Dubai (Gold Aviators)",
        archetype="habibi",
        primary=QColor(255, 215, 0),         # Pure Gold
        secondary=QColor(218, 165, 32),
        body_fill=QColor(248, 250, 252, 250), # White Silk Kandura
        body_rim=QColor(212, 175, 55, 255),   # Royal Gold Embroidery Rim
        visor_bg=QColor(10, 10, 12, 250),
        aura=QColor(255, 215, 0, 75),
        hud_border="rgba(255, 255, 255, 0.08)",
        hud_bg="rgba(13, 17, 23, 0.96)"
    )
}

# The unique canonical archetypes shown in UI menus
CANONICAL_SKINS = [
    "neo_cyber",
    "habibi_dubai",
    "quantum_fox",
    "chrono_mech",
    "nebula_cat",
    "solar_phoenix",
    "obsidian_phantom",
    "matrix_green"
]

def get_skin(name: str) -> CharacterSkin:
    if not name:
        return SKINS["neo_cyber"]
    return SKINS.get(name, SKINS["neo_cyber"])

def get_menu_stylesheet(skin_name: str = "neo_cyber") -> str:
    skin = get_skin(skin_name)
    accent = skin.primary.name()
    return f"""
    QMenu {{
        background-color: #161b22;
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 10px;
        padding: 5px;
        color: #f0f6fc;
        font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
        font-size: 12.5px;
        font-weight: 500;
    }}
    QMenu::item {{
        padding: 6px 20px 6px 10px;
        border-radius: 6px;
        margin: 1px 3px;
        color: #c9d1d9;
    }}
    QMenu::item:selected {{
        background-color: rgba(255, 255, 255, 0.08);
        color: #ffffff;
        border-left: 2px solid {accent};
    }}
    QMenu::separator {{
        height: 1px;
        background: rgba(255, 255, 255, 0.08);
        margin: 4px 6px;
    }}
    """
