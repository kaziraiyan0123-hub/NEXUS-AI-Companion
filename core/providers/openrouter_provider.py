"""
NEXUS OpenRouter Free Tier Provider
Access 100% Free models (no credits needed) via OpenRouter API.
Free keys available at https://openrouter.ai/keys
"""
from typing import List, Optional
from core.providers.openai_provider import OpenAIProvider

class OpenRouterProvider(OpenAIProvider):
    """OpenRouter Provider for free and open models."""

    MODELS = [
        "google/gemma-4-31b-it:free",
        "liquid/lfm-2.5-2.6b:free",
        "nvidia/nemotron-3.5-lightning:free",
        "cohere/north-mini-code:free",
        "meta-llama/llama-3.3-70b-instruct:free",
        "deepseek/deepseek-r1:free"
    ]

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            extra_headers={
                "HTTP-Referer": "https://nexus.local",
                "X-Title": "NEXUS Desktop Companion"
            }
        )

    @property
    def name(self) -> str:
        return "openrouter"

    @property
    def display_name(self) -> str:
        return "OpenRouter (Free Community Models)"

    @property
    def default_model(self) -> str:
        return "google/gemma-4-31b-it:free"

    @property
    def available_models(self) -> List[str]:
        return self.MODELS
