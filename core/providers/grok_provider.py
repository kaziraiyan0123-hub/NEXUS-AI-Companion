"""
NEXUS xAI Grok Provider
Connects to xAI API (OpenAI-compatible) with streaming SSE support.
"""
from typing import List, Optional
from core.providers.openai_provider import OpenAIProvider

class GrokProvider(OpenAIProvider):
    """xAI Grok API Provider."""

    MODELS = [
        "grok-2-1212",
        "grok-2-vision-1212",
        "grok-beta"
    ]

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key=api_key, base_url="https://api.x.ai/v1")

    @property
    def name(self) -> str:
        return "grok"

    @property
    def display_name(self) -> str:
        return "xAI Grok"

    @property
    def default_model(self) -> str:
        return "grok-2-1212"

    @property
    def available_models(self) -> List[str]:
        return self.MODELS
