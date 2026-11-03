"""
NEXUS Groq Cloud Provider (100% Free High-Speed Cloud API Tier)
Ultra-fast LPU inference (500+ tok/s) using latest frontier high-speed models.
Free API keys available without credit card at https://console.groq.com
"""
from typing import List, Dict, Optional, Generator
from core.providers.openai_provider import OpenAIProvider

class GroqProvider(OpenAIProvider):
    """Groq Cloud High-Speed Frontier Provider."""

    MODELS = [
        "qwen/qwen3.8-27b",
        "openai/gpt-oss-120b",
        "openai/gpt-oss-20b",
        "allam-2-7b"
    ]

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key=api_key, base_url="https://api.groq.com/openai/v1")

    @property
    def name(self) -> str:
        return "groq"

    @property
    def display_name(self) -> str:
        return "Groq Cloud (100% Free Ultra-Fast Frontier AI)"

    @property
    def default_model(self) -> str:
        return "qwen/qwen3.8-27b"

    @property
    def available_models(self) -> List[str]:
        return self.MODELS

    def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = "",
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 800
    ) -> str:
        """Generates response with rate-limit protection (<= 800 tokens) and model rotation."""
        safe_max_tokens = min(max_tokens, 800)
        target = model or self.default_model
        models_to_try = [target] + [m for m in self.MODELS if m != target]

        last_err = None
        for m in models_to_try:
            try:
                return super().generate_response(
                    messages=messages,
                    system_prompt=system_prompt,
                    model=m,
                    temperature=temperature,
                    max_tokens=safe_max_tokens
                )
            except Exception as e:
                last_err = e
                continue
        if last_err:
            raise last_err
        return ""

    def generate_stream(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = "",
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 800
    ) -> Generator[str, None, None]:
        """Streams response with Groq free-tier rate-limit guard and auto-model rotation."""
        safe_max_tokens = min(max_tokens, 800)
        target = model or self.default_model
        models_to_try = [target] + [m for m in self.MODELS if m != target]

        last_err = None
        for m in models_to_try:
            try:
                yield from super().generate_stream(
                    messages=messages,
                    system_prompt=system_prompt,
                    model=m,
                    temperature=temperature,
                    max_tokens=safe_max_tokens
                )
                return
            except Exception as e:
                last_err = e
                continue
        if last_err:
            raise last_err
