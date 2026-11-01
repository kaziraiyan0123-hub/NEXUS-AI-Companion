"""Desktop GUI package for NEXUS."""
from .pet import DesktopPet
from .pet_renderer import PetRenderer
from .context_menu import PetContextMenu
from .quick_bubble import QuickBubble
from .tray import NexusTrayIcon
from .chat_window import AdvancedChatWindow, ChatInputEdit
from .chat_bubble_widget import MessageBubbleWidget, ThinkingBubbleWidget

__all__ = [
    "DesktopPet", 
    "PetRenderer", 
    "PetContextMenu", 
    "QuickBubble", 
    "NexusTrayIcon",
    "AdvancedChatWindow",
    "ChatInputEdit",
    "MessageBubbleWidget",
    "ThinkingBubbleWidget"
]
