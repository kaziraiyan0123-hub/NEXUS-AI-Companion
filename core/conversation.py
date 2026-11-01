"""
NEXUS Conversation & Message Data Models
Handles multi-session conversation history, message threads, and search.
"""
import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict

@dataclass
class ChatMessage:
    role: str               # "user" | "assistant" | "system"
    content: str
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    timestamp: float = field(default_factory=time.time)
    attachments: List[str] = field(default_factory=list)
    is_error: bool = False

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "ChatMessage":
        return cls(
            role=data.get("role", "user"),
            content=data.get("content", ""),
            id=data.get("id", str(uuid.uuid4())[:8]),
            timestamp=data.get("timestamp", time.time()),
            attachments=data.get("attachments", []),
            is_error=data.get("is_error", False)
        )

@dataclass
class Conversation:
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str = "New Conversation"
    messages: List[ChatMessage] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def add_message(self, role: str, content: str, attachments: List[str] = None) -> ChatMessage:
        msg = ChatMessage(role=role, content=content, attachments=attachments or [])
        self.messages.append(msg)
        self.updated_at = time.time()
        
        # Auto-generate title from first user message
        if len(self.messages) == 1 and role == "user":
            first_line = content.strip().split("\n")[0]
            self.title = first_line[:32] + ("..." if len(first_line) > 32 else "")
        return msg

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "messages": [m.to_dict() for m in self.messages],
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Conversation":
        conv = cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            title=data.get("title", "New Conversation"),
            created_at=data.get("created_at", time.time()),
            updated_at=data.get("updated_at", time.time())
        )
        conv.messages = [ChatMessage.from_dict(m) for m in data.get("messages", [])]
        return conv

class ConversationManager:
    """Manages active conversation and conversation history."""

    def __init__(self):
        self.conversations: Dict[str, Conversation] = {}
        self.active_id: Optional[str] = None
        
        # Create initial conversation
        self.new_conversation("Welcome to NEXUS")

    def new_conversation(self, title: str = "New Conversation") -> Conversation:
        conv = Conversation(title=title)
        self.conversations[conv.id] = conv
        self.active_id = conv.id
        return conv

    def get_active(self) -> Conversation:
        if not self.active_id or self.active_id not in self.conversations:
            return self.new_conversation()
        return self.conversations[self.active_id]

    def add_message(self, role: str, content: str, attachments: List[str] = None) -> ChatMessage:
        """Appends a message directly to the active conversation."""
        return self.get_active().add_message(role, content, attachments)

    def set_active(self, conv_id: str) -> Optional[Conversation]:
        if conv_id in self.conversations:
            self.active_id = conv_id
            return self.conversations[conv_id]
        return None

    def search_messages(self, query: str) -> List[tuple[str, ChatMessage]]:
        """Search query across all conversation messages."""
        results = []
        q = query.lower()
        for c_id, conv in self.conversations.items():
            for msg in conv.messages:
                if q in msg.content.lower():
                    results.append((conv.title, msg))
        return results

    def list_conversations(self) -> List[Conversation]:
        return sorted(self.conversations.values(), key=lambda c: c.updated_at, reverse=True)
