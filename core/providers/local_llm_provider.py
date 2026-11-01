"""
NEXUS Local LLM Provider
Connects to local inference servers (Ollama, LM Studio, vLLM, LocalAI)
using OpenAI-compatible endpoints with streaming support.
"""
import json
import time
import logging
from typing import List, Dict, Any, Generator, Tuple, Optional
import httpx

from core.providers.base_provider import BaseAIProvider

logger = logging.getLogger("NEXUS.AI.LocalLLM")

class LocalLLMProvider(BaseAIProvider):
    """Local LLM Provider for completely private and offline AI inference."""

    DEFAULT_BASE_URL = "http://localhost:11434/v1"

    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        url = base_url or self.DEFAULT_BASE_URL
        if not url.endswith("/v1"):
            url = f"{url.rstrip('/')}/v1"
        super().__init__(api_key=api_key or "local", base_url=url)
        self._cached_models: List[str] = ["llama3.3", "deepseek-r1", "mistral", "qwen2.5", "phi-4"]

    @property
    def name(self) -> str:
        return "local"

    @property
    def display_name(self) -> str:
        return "Local LLM (Ollama / LM Studio)"

    @property
    def default_model(self) -> str:
        return self._cached_models[0] if self._cached_models else "llama3.3"

    @property
    def available_models(self) -> List[str]:
        return self._cached_models

    def fetch_local_models(self) -> List[str]:
        """Queries local server for list of currently installed models."""
        url = f"{self.base_url}/models"
        try:
            with httpx.Client(timeout=4.0) as client:
                resp = client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    models = [m.get("id") for m in data.get("data", []) if m.get("id")]
                    if models:
                        self._cached_models = models
                        return models
        except Exception as e:
            logger.debug(f"Could not fetch models from {url}: {e}")
        return self._cached_models

    def test_connection(self) -> Tuple[bool, str]:
        """Tests if local LLM service (Ollama / LM Studio) is running and responsive."""
        start_time = time.time()
        url = f"{self.base_url}/models"
        try:
            with httpx.Client(timeout=5.0) as client:
                resp = client.get(url)
                latency = int((time.time() - start_time) * 1000)
                if resp.status_code == 200:
                    models = self.fetch_local_models()
                    m_count = len(models)
                    return True, f"Connected to Local LLM at {self.base_url} ({latency}ms, {m_count} models found)"
                else:
                    return False, f"Server responded with status {resp.status_code}: {resp.text}"
        except httpx.ConnectError:
            return False, f"Cannot connect to local server at {self.base_url}. Ensure Ollama or LM Studio is running."
        except httpx.TimeoutException:
            return False, "Connection to local LLM server timed out."
        except Exception as e:
            return False, f"Local connection error: {str(e)}"

    def _prepare_messages(self, messages: List[Dict[str, str]], system_prompt: str) -> List[Dict[str, str]]:
        formatted = []
        if system_prompt:
            formatted.append({"role": "system", "content": system_prompt})
        for m in messages:
            role = m.get("role", "user")
            content = m.get("content", "")
            if content:
                formatted.append({"role": role, "content": content})
        return formatted

    def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = "",
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1500
    ) -> str:
        target_model = model or self.default_model
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": target_model,
            "messages": self._prepare_messages(messages, system_prompt),
            "temperature": float(temperature),
            "max_tokens": int(max_tokens),
            "stream": False
        }

        with httpx.Client(timeout=120.0) as client:
            resp = client.post(url, json=payload)
            if resp.status_code != 200:
                raise RuntimeError(f"Local LLM Error [{resp.status_code}]: {resp.text}")
            data = resp.json()
            return data.get("choices", [{}])[0].get("message", {}).get("content", "")

    def generate_stream(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = "",
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1500
    ) -> Generator[str, None, None]:
        target_model = model or self.default_model
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": target_model,
            "messages": self._prepare_messages(messages, system_prompt),
            "temperature": float(temperature),
            "max_tokens": int(max_tokens),
            "stream": True
        }

        with httpx.Client(timeout=180.0) as client:
            with client.stream("POST", url, json=payload) as response:
                if response.status_code != 200:
                    raw = response.read().decode("utf-8")
                    raise RuntimeError(f"Local LLM Streaming Error [{response.status_code}]: {raw}")

                for line in response.iter_lines():
                    if not line:
                        continue
                    if line.startswith("data: "):
                        data_str = line[6:].strip()
                        if data_str == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data_str)
                            delta = chunk.get("choices", [{}])[0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                yield content
                        except Exception as e:
                            logger.debug(f"Error parsing Local LLM stream chunk: {e}")
