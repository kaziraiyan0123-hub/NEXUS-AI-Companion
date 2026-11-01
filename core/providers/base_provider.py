"""
NEXUS Base AI Provider Interface
Defines the standard contract for all AI model providers (Cloud & Local).
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Generator, Tuple, Optional

class BaseAIProvider(ABC):
    """Abstract base class for all NEXUS AI providers."""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key
        self.base_url = base_url

    @property
    @abstractmethod
    def name(self) -> str:
        """Internal provider identifier (e.g. 'gemini', 'openai')."""
        pass

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable provider name."""
        pass

    @property
    @abstractmethod
    def default_model(self) -> str:
        """Default model identifier for this provider."""
        pass

    @property
    @abstractmethod
    def available_models(self) -> List[str]:
        """List of supported models."""
        pass

    @abstractmethod
    def test_connection(self) -> Tuple[bool, str]:
        """
        Tests connectivity and API credentials.
        Returns: (success: bool, status_message: str)
        """
        pass

    @abstractmethod
    def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = "",
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1500
    ) -> str:
        """Generates a complete response synchronously."""
        pass

    @abstractmethod
    def generate_stream(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = "",
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1500
    ) -> Generator[str, None, None]:
        """Yields streaming text chunks."""
        pass
