"""
Character states and interaction modes for NEXUS.
"""
from enum import Enum, auto

class CharacterState(str, Enum):
    IDLE = "idle"
    WALKING = "walking"
    RUNNING = "running"
    FLOATING = "floating"
    SITTING = "sitting"
    SLEEPING = "sleeping"
    WAKING = "waking"
    LISTENING = "listening"
    THINKING = "thinking"
    TALKING = "talking"
    HAPPY = "happy"
    SAD = "sad"
    SURPRISED = "surprised"
    CONFUSED = "confused"
    WORKING = "working"
    ERROR = "error"
    CELEBRATING = "celebrating"

class InteractionMode(str, Enum):
    QUIET = "quiet"
    NORMAL = "normal"
    INTERACTIVE = "interactive"
    FOCUS = "focus"
    SLEEP = "sleep"
