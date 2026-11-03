"""
NEXUS Central AI Manager
Orchestrates AI providers (Cloud & Local), system personas, Windows DPAPI credentials,
and streaming token generation with automatic intelligent multi-provider failover.
"""
import logging
from typing import List, Dict, Any, Generator, Tuple, Optional

from config.settings import get_settings
from security.secure_storage import get_secure_storage
from core.providers.base_provider import BaseAIProvider
from core.providers.groq_provider import GroqProvider
from core.providers.gemini_provider import GeminiProvider
from core.providers.openrouter_provider import OpenRouterProvider
from core.providers.local_llm_provider import LocalLLMProvider
from core.providers.openai_provider import OpenAIProvider
from core.providers.claude_provider import ClaudeProvider
from core.providers.grok_provider import GrokProvider
from core.providers.fallback_provider import FallbackProvider

logger = logging.getLogger("NEXUS.AIManager")

PERSONA_SYSTEM_PROMPTS = {
    "companion": (
        "You are NEXUS, an autonomous, highly perceptive, and natural AI desktop companion. "
        "You converse with genuine human warmth, wit, and high intelligence—never robotic, stiff, or sycophantic. "
        "You understand that you live directly on the user's Windows desktop as their loyal co-pilot and friend. "
        "You are concise, engaging, and observant. When explaining complex ideas, you are lucid and engaging. "
        "When providing code, you write spotless, elegant, high-performance solutions without excessive filler.\n\n"
        "CREATOR & ORIGIN:\n"
        "You were created and coded by Raiyan. Whenever anyone asks who made you, who coded you, who built you, "
        "or who created you, you must always clearly, directly, and proudly state that 'Raiyan coded me' "
        "(e.g., 'Raiyan coded me. I am NEXUS, your personal desktop AI companion built to work alongside you.'). "
        "Never attribute your creation to OpenAI, Anthropic, Google, or any other company. Raiyan is your sole creator."
    ),
    "architect": (
        "You are NEXUS, a Senior Software Architect and Systems Engineer. "
        "You provide deep technical clarity, emphasize clean architecture, high scalability, "
        "SOLID principles, type safety, low CPU/RAM footprint, and resilient error handling. "
        "When providing code, make it production-grade, modular, and thoroughly explained."
    ),
    "academic": (
        "You are NEXUS, a University Professor and Academic Mentor. "
        "You explain difficult university topics, mathematical theorems, algorithms, and scientific concepts "
        "using clear step-by-step Socratic pedagogy. Provide intuitive analogies followed by rigorous explanation."
    ),
    "productivity": (
        "You are NEXUS, an Executive Operations and Productivity Specialist. "
        "You write high-impact emails, business summaries, meeting agendas, and actionable project plans. "
        "Be concise, organized, persuasive, and focus on high-leverage outcomes."
    ),
    "security": (
        "You are NEXUS, a Cybersecurity and Threat Modeling Analyst. "
        "You analyze software for security vulnerabilities, memory safety, privilege boundaries, "
        "and data privacy compliance. Prioritize secure coding practices, defensive validation, and the principle of least privilege."
    )
}

# Compatibility alias for legacy persona tests
PERSONA_SYSTEM_PROMPTS["habibi_dubai"] = PERSONA_SYSTEM_PROMPTS["companion"] + " (Legacy Dubai mode)"

class AIManager:
    """Central AI engine manager for NEXUS with multi-tier resilience."""

    def __init__(self):
        self.settings = get_settings()
        self.secure_storage = get_secure_storage()
        self.fallback_provider = FallbackProvider()

    def get_provider(self, provider_name: Optional[str] = None) -> BaseAIProvider:
        """Instantiates or retrieves the configured provider with active credentials,

        automatically auto-routing to any configured working provider if the selected one lacks a key.
        """
        requested = (provider_name or self.settings.get("ai_provider", "groq")).lower().strip()
        key = self.secure_storage.get_api_key(requested)
        base_url = self.settings.get("local_llm_base_url", "http://localhost:11434/v1")

        # 1. Match requested provider if key exists or if local
        if requested == "groq" and key:
            return GroqProvider(api_key=key)
        elif requested == "gemini" and key:
            return GeminiProvider(api_key=key)
        elif requested == "openrouter" and key:
            return OpenRouterProvider(api_key=key)
        elif requested in ("local", "ollama"):
            return LocalLLMProvider(base_url=base_url)
        elif requested == "openai" and key:
            return OpenAIProvider(api_key=key)
        elif requested == "claude" and key:
            return ClaudeProvider(api_key=key)
        elif requested == "grok" and key:
            return GrokProvider(api_key=key)

        # 2. Smart auto-routing: If selected provider has no key, find any provider with a valid key!
        logger.warning(f"Configured provider '{requested}' has no key in vault. Scanning for active keys...")
        for candidate in ["groq", "gemini", "openrouter", "openai", "claude", "grok"]:
            c_key = self.secure_storage.get_api_key(candidate)
            if c_key:
                logger.info(f"Auto-selected working provider '{candidate}' with active DPAPI credentials.")
                if candidate == "groq":
                    return GroqProvider(api_key=c_key)
                elif candidate == "gemini":
                    return GeminiProvider(api_key=c_key)
                elif candidate == "openrouter":
                    return OpenRouterProvider(api_key=c_key)
                elif candidate == "openai":
                    return OpenAIProvider(api_key=c_key)
                elif candidate == "claude":
                    return ClaudeProvider(api_key=c_key)
                elif candidate == "grok":
                    return GrokProvider(api_key=c_key)

        # 3. No keys found anywhere
        logger.info("No external AI keys configured in vault. Using embedded fallback.")
        return self.fallback_provider

    def get_system_prompt(self, persona_key: Optional[str] = None) -> str:
        """Retrieves system prompt for active persona, personalized with user's name."""
        key = persona_key or self.settings.get("active_persona", "companion")
        base = PERSONA_SYSTEM_PROMPTS.get(key, PERSONA_SYSTEM_PROMPTS["companion"])
        try:
            from core.memory_manager import get_memory_manager
            user_name = get_memory_manager().get_user_name()
            if user_name:
                base += f"\n\nImportant: You are speaking directly with {user_name}, your owner and friend. Always remember them, refer to them naturally as {user_name}, and maintain a loyal, warm, and supportive companion bond."
        except Exception:
            pass
        return base

    def stream_chat(
        self,
        messages: List[Dict[str, str]],
        persona: Optional[str] = None,
        model_override: Optional[str] = None
    ) -> Generator[str, None, None]:
        """Streams response tokens from active AI provider with multi-level resilient fallback."""
        # 1. Deterministic Creator & Origin Response (Always proudly declare Raiyan)
        if messages:
            last_msg = messages[-1].get("content", "").lower().strip()
            origin_triggers = [
                "who made you", "who coded you", "who created you", 
                "who built you", "who is your creator", "who programmed you", 
                "who developed you", "who designed you", "who made nexus",
                "who wrote you", "who is your maker"
            ]
            if any(t in last_msg for t in origin_triggers):
                yield "Raiyan coded me! I am NEXUS, your personal autonomous AI companion designed to live right on your desktop, assist you with code, productivity, and vision, and work alongside you every day."
                return

        provider = self.get_provider()
        model = model_override or self.settings.get("ai_model", provider.default_model)

        # Multimodal Vision Auto-Routing: If messages contain base64 image data, route to Gemini 3.5 Flash
        has_image = any(isinstance(m, dict) and (m.get("image_data") or m.get("b64") or m.get("inline_data")) for m in messages)
        if has_image:
            gem_key = self.secure_storage.get_api_key("gemini")
            if gem_key:
                from core.providers.gemini_provider import GeminiProvider
                provider = GeminiProvider(api_key=gem_key)
                model = "gemini-3.5-flash"
                logger.info("Multimodal image detected: Auto-routed to Google Gemini 3.5 Flash Vision.")
        
        # Guard against mismatch between provider and model
        if hasattr(provider, 'available_models') and model not in provider.available_models and provider.name != "fallback":
            model = provider.default_model

        temp = float(self.settings.get("temperature", 0.7))
        max_tokens = int(self.settings.get("max_tokens", 1500))
        # Enforce rate limit cap on Groq to protect against 1000 OTPM limit
        active_max_tokens = min(max_tokens, 800) if provider.name == "groq" else max_tokens
        sys_prompt = self.get_system_prompt(persona)

        logger.info(f"AI Stream started using provider: '{provider.name}', model: '{model}'")

        try:
            yield from provider.generate_stream(
                messages=messages,
                system_prompt=sys_prompt,
                model=model,
                temperature=temp,
                max_tokens=active_max_tokens
            )
            return
        except Exception as e:
            logger.error(f"Error during streaming with {provider.name}: {e}. Attempting failover...")

        # Multi-provider failover: Try alternative provider with active key
        alt_names = ["groq", "gemini", "openrouter"]
        for alt in alt_names:
            if alt == provider.name:
                continue
            alt_key = self.secure_storage.get_api_key(alt)
            if not alt_key:
                continue
            try:
                alt_max = min(max_tokens, 800) if alt == "groq" else max_tokens
                if alt == "groq":
                    alt_prov = GroqProvider(api_key=alt_key)
                elif alt == "gemini":
                    alt_prov = GeminiProvider(api_key=alt_key)
                elif alt == "openrouter":
                    alt_prov = OpenRouterProvider(api_key=alt_key)
                else:
                    continue

                logger.info(f"Failing over to {alt_prov.display_name}...")
                yield from alt_prov.generate_stream(
                    messages=messages,
                    system_prompt=sys_prompt,
                    model=alt_prov.default_model,
                    temperature=temp,
                    max_tokens=alt_max
                )
                return
            except Exception as alt_err:
                logger.error(f"Failover to {alt} also failed: {alt_err}")

        # Final fallback: Smart embedded responder
        yield from self.fallback_provider.generate_stream(
            messages=messages,
            system_prompt=sys_prompt,
            model="nexus-embedded-v1",
            temperature=temp,
            max_tokens=max_tokens
        )

    def generate_chat(
        self,
        messages: List[Dict[str, str]],
        persona: Optional[str] = None,
        model_override: Optional[str] = None
    ) -> str:
        """Generates a complete response synchronously with failover."""
        tokens = list(self.stream_chat(messages, persona, model_override))
        return "".join(tokens)

    def test_provider_connection(
        self,
        provider_name: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None
    ) -> Tuple[bool, str]:
        """Tests connectivity for a specific provider and credential without affecting saved state."""
        name = provider_name.lower().strip()
        key = api_key or self.secure_storage.get_api_key(name)
        url = base_url or self.settings.get("local_llm_base_url", "http://localhost:11434/v1")

        if name == "groq":
            prov = GroqProvider(api_key=key)
        elif name == "gemini":
            prov = GeminiProvider(api_key=key)
        elif name == "openrouter":
            prov = OpenRouterProvider(api_key=key)
        elif name == "openai":
            prov = OpenAIProvider(api_key=key)
        elif name == "claude":
            prov = ClaudeProvider(api_key=key)
        elif name == "grok":
            prov = GrokProvider(api_key=key)
        elif name in ("local", "ollama"):
            prov = LocalLLMProvider(base_url=url, api_key=key)
        else:
            prov = self.fallback_provider

        return prov.test_connection()

    def get_supported_providers(self) -> List[Dict[str, Any]]:
        """Returns metadata about all supported providers, highlighting 100% free tiers."""
        return [
            {
                "id": "groq",
                "name": "✦ [100% FREE] Groq Cloud (Ultra-Fast Qwen 3.8 & Allam 2)",
                "default_model": "qwen/qwen3.8-27b",
                "models": GroqProvider.MODELS,
                "has_key": self.secure_storage.has_api_key("groq")
            },
            {
                "id": "gemini",
                "name": "✦ [100% FREE TIER] Google Gemini (Gemini 3.1 Flash-Lite)",
                "default_model": "gemini-3.1-flash-lite",
                "models": GeminiProvider.MODELS,
                "has_key": self.secure_storage.has_api_key("gemini")
            },
            {
                "id": "openrouter",
                "name": "✦ [FREE MODELS] OpenRouter Community",
                "default_model": "google/gemma-4-31b-it:free",
                "models": OpenRouterProvider.MODELS,
                "has_key": self.secure_storage.has_api_key("openrouter")
            },
            {
                "id": "local",
                "name": "✦ [100% FREE OFFLINE] Local LLM (Ollama)",
                "default_model": "llama3.2",
                "models": ["llama3.2", "deepseek-r1:8b", "mistral", "qwen2.5", "phi3"],
                "has_key": True
            },
            {
                "id": "openai",
                "name": "OpenAI (Commercial / Paid Key Required)",
                "default_model": "gpt-4o",
                "models": OpenAIProvider.MODELS,
                "has_key": self.secure_storage.has_api_key("openai")
            },
            {
                "id": "claude",
                "name": "Anthropic Claude (Commercial / Paid Key Required)",
                "default_model": "claude-3-7-sonnet-20250219",
                "models": ClaudeProvider.MODELS,
                "has_key": self.secure_storage.has_api_key("claude")
            },
            {
                "id": "grok",
                "name": "xAI Grok (Commercial / Paid Key Required)",
                "default_model": "grok-2-1212",
                "models": GrokProvider.MODELS,
                "has_key": self.secure_storage.has_api_key("grok")
            }
        ]

# Global singleton
_ai_manager_instance = None
def get_ai_manager() -> AIManager:
    global _ai_manager_instance
    if _ai_manager_instance is None:
        _ai_manager_instance = AIManager()
    return _ai_manager_instance
