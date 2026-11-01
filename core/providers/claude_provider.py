"""
NEXUS Anthropic Claude AI Provider
Connects to Anthropic Messages API with streaming SSE support.
"""
import json
import time
import logging
from typing import List, Dict, Any, Generator, Tuple, Optional
import httpx

from core.providers.base_provider import BaseAIProvider

logger = logging.getLogger("NEXUS.AI.Claude")

class ClaudeProvider(BaseAIProvider):
    """Anthropic Claude API Provider."""

    MODELS = [
        "claude-3-7-sonnet-20250219",
        "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-20241022"
    ]

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key=api_key)
        self.api_base = "https://api.anthropic.com/v1"

    @property
    def name(self) -> str:
        return "claude"

    @property
    def display_name(self) -> str:
        return "Anthropic Claude"

    @property
    def default_model(self) -> str:
        return "claude-3-7-sonnet-20250219"

    @property
    def available_models(self) -> List[str]:
        return self.MODELS

    def _headers(self) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        if self.api_key:
            headers["x-api-key"] = self.api_key
        return headers

    def test_connection(self) -> Tuple[bool, str]:
        """Verifies Claude API key with a minimal message request."""
        if not self.api_key:
            return False, "Claude API key is not configured."

        start_time = time.time()
        url = f"{self.api_base}/messages"
        payload = {
            "model": "claude-3-5-haiku-20241022",
            "max_tokens": 1,
            "messages": [{"role": "user", "content": "ping"}]
        }
        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.post(url, headers=self._headers(), json=payload)
                latency = int((time.time() - start_time) * 1000)
                if resp.status_code == 200:
                    return True, f"Connected to Anthropic API ({latency}ms latency)"
                else:
                    err = resp.json().get("error", {}).get("message", resp.text)
                    return False, f"Claude Error ({resp.status_code}): {err}"
        except httpx.ConnectError:
            return False, "Connection failed: Unable to reach Anthropic servers."
        except httpx.TimeoutException:
            return False, "Connection timed out."
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"

    def _prepare_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        formatted = []
        for m in messages:
            role = "assistant" if m.get("role") in ("assistant", "model") else "user"
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
            raise ValueError("Claude API key not configured.")

        target_model = model or self.default_model
        url = f"{self.api_base}/messages"
        payload = {
            "model": target_model,
            "max_tokens": int(max_tokens),
            "temperature": float(temperature),
            "messages": self._prepare_messages(messages)
        }
        if system_prompt:
            payload["system"] = system_prompt

        with httpx.Client(timeout=45.0) as client:
            resp = client.post(url, headers=self._headers(), json=payload)
            if resp.status_code != 200:
                err = resp.json().get("error", {}).get("message", resp.text)
                raise RuntimeError(f"Claude API Error [{resp.status_code}]: {err}")

            data = resp.json()
            parts = [b.get("text", "") for b in data.get("content", []) if b.get("type") == "text"]
            return "".join(parts)

    def generate_stream(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = "",
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1500
    ) -> Generator[str, None, None]:
        if not self.api_key:
            raise ValueError("Claude API key not configured.")

        target_model = model or self.default_model
        url = f"{self.api_base}/messages"
        payload = {
            "model": target_model,
            "max_tokens": int(max_tokens),
            "temperature": float(temperature),
            "messages": self._prepare_messages(messages),
            "stream": True
        }
        if system_prompt:
            payload["system"] = system_prompt

        with httpx.Client(timeout=60.0) as client:
            with client.stream("POST", url, headers=self._headers(), json=payload) as response:
                if response.status_code != 200:
                    raw = response.read().decode("utf-8")
                    try:
                        err = json.loads(raw).get("error", {}).get("message", raw)
                    except Exception:
                        err = raw
                    raise RuntimeError(f"Claude Streaming Error [{response.status_code}]: {err}")

                for line in response.iter_lines():
                    if not line:
                        continue
                    if line.startswith("data: "):
                        data_str = line[6:].strip()
                        try:
                            event_data = json.loads(data_str)
                            event_type = event_data.get("type")
                            if event_type == "content_block_delta":
                                delta = event_data.get("delta", {})
                                if delta.get("type") == "text_delta":
                                    yield delta.get("text", "")
                            elif event_type == "message_stop":
                                break
                        except Exception as e:
                            logger.debug(f"Error parsing Claude stream chunk: {e}")
