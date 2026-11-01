"""
NEXUS Google Gemini AI Provider
Connects directly to the Google Gemini v1beta REST API with streaming SSE support.
"""
import json
import time
import logging
from typing import List, Dict, Any, Generator, Tuple, Optional
import httpx

from core.providers.base_provider import BaseAIProvider

logger = logging.getLogger("NEXUS.AI.Gemini")

class GeminiProvider(BaseAIProvider):
    """Google Gemini AI Provider."""

    MODELS = [
        "gemini-2.5-flash",
        "gemini-2.5-pro",
        "gemini-2.5-flash-lite",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-3.1-flash-lite",
        "gemini-3-flash-preview",
        "gemini-flash-latest"
    ]

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key=api_key)
        self.api_base = "https://generativelanguage.googleapis.com/v1beta"

    @property
    def name(self) -> str:
        return "gemini"

    @property
    def display_name(self) -> str:
        return "Google Gemini (Free Tier)"

    @property
    def default_model(self) -> str:
        return "gemini-2.5-flash"

    @property
    def available_models(self) -> List[str]:
        return self.MODELS

    def _format_payload(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        temperature: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        """Formats conversation messages into Gemini API content payload."""
        contents = []
        for msg in messages:
            role = "user" if msg.get("role") == "user" else "model"
            text = msg.get("content", "")
            if text:
                contents.append({
                    "role": role,
                    "parts": [{"text": text}]
                })

        payload: Dict[str, Any] = {
            "contents": contents,
            "generationConfig": {
                "temperature": float(temperature),
                "maxOutputTokens": int(max_tokens)
            }
        }

        if system_prompt:
            payload["systemInstruction"] = {
                "parts": [{"text": system_prompt}]
            }

        return payload

    def test_connection(self) -> Tuple[bool, str]:
        """Verifies Gemini API key by listing available models."""
        if not self.api_key:
            return False, "Gemini API key is not configured."

        start_time = time.time()
        url = f"{self.api_base}/models?key={self.api_key}"
        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.get(url)
                latency = int((time.time() - start_time) * 1000)
                if resp.status_code == 200:
                    return True, f"Connected to Gemini API ({latency}ms latency)"
                else:
                    err = resp.json().get("error", {}).get("message", resp.text)
                    return False, f"Gemini Error ({resp.status_code}): {err}"
        except httpx.ConnectError:
            return False, "Connection failed: Unable to reach Google API servers."
        except httpx.TimeoutException:
            return False, "Connection timed out."
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"

    def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = "",
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1500
    ) -> str:
        """Generates a synchronous response."""
        if not self.api_key:
            raise ValueError("Gemini API key not configured.")

        target_model = model or self.default_model
        url = f"{self.api_base}/models/{target_model}:generateContent?key={self.api_key}"
        payload = self._format_payload(messages, system_prompt, temperature, max_tokens)

        with httpx.Client(timeout=30.0) as client:
            resp = client.post(url, json=payload)
            if resp.status_code != 200:
                err = resp.json().get("error", {}).get("message", resp.text)
                raise RuntimeError(f"Gemini API Error [{resp.status_code}]: {err}")

            data = resp.json()
            candidates = data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                return "".join([p.get("text", "") for p in parts])
            return ""

    def generate_stream(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = "",
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1500
    ) -> Generator[str, None, None]:
        """Streams response tokens using Server-Sent Events (SSE)."""
        if not self.api_key:
            raise ValueError("Gemini API key not configured.")

        target_model = model or self.default_model
        url = f"{self.api_base}/models/{target_model}:streamGenerateContent?alt=sse&key={self.api_key}"
        payload = self._format_payload(messages, system_prompt, temperature, max_tokens)

        with httpx.Client(timeout=45.0) as client:
            with client.stream("POST", url, json=payload) as response:
                if response.status_code != 200:
                    content = response.read().decode("utf-8")
                    try:
                        err = json.loads(content).get("error", {}).get("message", content)
                    except Exception:
                        err = content
                    raise RuntimeError(f"Gemini Streaming Error [{response.status_code}]: {err}")

                for line in response.iter_lines():
                    if not line:
                        continue
                    if line.startswith("data: "):
                        data_str = line[6:].strip()
                        if not data_str:
                            continue
                        try:
                            chunk_json = json.loads(data_str)
                            candidates = chunk_json.get("candidates", [])
                            if candidates:
                                parts = candidates[0].get("content", {}).get("parts", [])
                                for p in parts:
                                    text_chunk = p.get("text", "")
                                    if text_chunk:
                                        yield text_chunk
                        except Exception as e:
                            logger.debug(f"Error parsing Gemini SSE chunk: {e}")
