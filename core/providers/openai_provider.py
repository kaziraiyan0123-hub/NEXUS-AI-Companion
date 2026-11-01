"""
NEXUS OpenAI AI Provider
Connects to OpenAI Chat Completions API with streaming SSE support.
"""
import json
import time
import logging
from typing import List, Dict, Any, Generator, Tuple, Optional
import httpx

from core.providers.base_provider import BaseAIProvider

logger = logging.getLogger("NEXUS.AI.OpenAI")

class OpenAIProvider(BaseAIProvider):
    """OpenAI API Provider."""

    MODELS = [
        "gpt-4o",
        "gpt-4o-mini",
        "o3-mini",
        "o1"
    ]

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, extra_headers: Optional[Dict[str, str]] = None):
        super().__init__(api_key=api_key, base_url=base_url)
        self.api_base = (base_url or "https://api.openai.com/v1").rstrip("/")
        self.extra_headers = extra_headers or {}

    @property
    def name(self) -> str:
        return "openai"

    @property
    def display_name(self) -> str:
        return "OpenAI"

    @property
    def default_model(self) -> str:
        return "gpt-4o"

    @property
    def available_models(self) -> List[str]:
        return self.MODELS

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        headers.update(self.extra_headers)
        return headers

    def test_connection(self) -> Tuple[bool, str]:
        """Verifies OpenAI API key by querying models."""
        if not self.api_key:
            return False, "OpenAI API key is not configured."

        start_time = time.time()
        url = f"{self.api_base}/models"
        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.get(url, headers=self._headers())
                latency = int((time.time() - start_time) * 1000)
                if resp.status_code == 200:
                    return True, f"Connected to OpenAI API ({latency}ms latency)"
                else:
                    err = resp.json().get("error", {}).get("message", resp.text)
                    return False, f"OpenAI Error ({resp.status_code}): {err}"
        except httpx.ConnectError:
            return False, "Connection failed: Unable to reach OpenAI servers."
        except httpx.TimeoutException:
            return False, "Connection timed out."
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"

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
        if not self.api_key:
            raise ValueError("OpenAI API key not configured.")

        target_model = model or self.default_model
        url = f"{self.api_base}/chat/completions"
        payload = {
            "model": target_model,
            "messages": self._prepare_messages(messages, system_prompt),
            "temperature": float(temperature),
            "max_tokens": int(max_tokens),
            "stream": False
        }

        with httpx.Client(timeout=45.0) as client:
            resp = client.post(url, headers=self._headers(), json=payload)
            if resp.status_code != 200:
                err = resp.json().get("error", {}).get("message", resp.text)
                raise RuntimeError(f"OpenAI API Error [{resp.status_code}]: {err}")

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
        if not self.api_key:
            raise ValueError("OpenAI API key not configured.")

        target_model = model or self.default_model
        url = f"{self.api_base}/chat/completions"
        payload = {
            "model": target_model,
            "messages": self._prepare_messages(messages, system_prompt),
            "temperature": float(temperature),
            "max_tokens": int(max_tokens),
            "stream": True
        }

        with httpx.Client(timeout=60.0) as client:
            with client.stream("POST", url, headers=self._headers(), json=payload) as response:
                if response.status_code != 200:
                    raw = response.read().decode("utf-8")
                    try:
                        err = json.loads(raw).get("error", {}).get("message", raw)
                    except Exception:
                        err = raw
                    raise RuntimeError(f"OpenAI Streaming Error [{response.status_code}]: {err}")

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
                            logger.debug(f"Error parsing OpenAI stream chunk: {e}")
