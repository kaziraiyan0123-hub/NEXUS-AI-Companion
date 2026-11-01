"""
NEXUS Groq Cloud Provider (100% Free High-Speed Cloud API Tier)
Ultra-fast LPU inference (500+ tok/s) using latest high-speed models.
Free API keys available without credit card at https://console.groq.com
"""
from typing import List, Optional
from core.providers.openai_provider import OpenAIProvider

class GroqProvider(OpenAIProvider):
    """Groq Cloud High-Speed Free Tier Provider."""

    MODELS = [
        "qwen/qwen3.8-27b",
        "openai/gpt-oss-120b",
        "openai/gpt-oss-20b",
        "llama-3.3-70b-versatile",
        "deepseek-r1-distill-llama-70b",
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768",
        "gemma2-9b-it",
        "allam-2-7b"
    ]

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key=api_key, base_url="https://api.groq.com/openai/v1")

    @property
    def name(self) -> str:
        return "groq"

    @property
    def display_name(self) -> str:
        return "Groq Cloud (100% Free Ultra-Fast AI)"

    @property
    def default_model(self) -> str:
        return "qwen/qwen3.8-27b"

    @property
    def available_models(self) -> List[str]:
        return self.MODELS
