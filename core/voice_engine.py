"""
NEXUS Voice & Speech Engine
High-Fidelity Neural Text-to-Speech (Edge Neural TTS) + Native Windows SAPI5 Fallback.
Provides natural, human-grade, emotional vocal delivery with instant interruption,
volume/rate modulation, and thread-safe Qt event loop signaling.
"""
import os
import re
import time
import asyncio
import logging
import tempfile
from typing import List, Dict, Optional, Any
from PySide6.QtCore import QObject, Signal, QThread, QTimer, Slot

from config.settings import get_settings
from security.secure_storage import get_secure_storage

logger = logging.getLogger("NEXUS.VoiceEngine")

# SAPI constants
SVS_FLAGS_ASYNC = 1
SVSF_PURGE_BEFORE_SPEAK = 2

ELEVENLABS_VOICES = [
    {
        "id": "eleven_21m00Tcm4TlvDq8ikWAM",
        "voice_id": "21m00Tcm4TlvDq8ikWAM",
        "name": "✨ ElevenLabs: Rachel (Ultra-Realistic Natural Female)",
        "gender": "Female",
        "neural": True,
        "is_eleven": True
    },
    {
        "id": "eleven_pNInz6obpgDQGcFmaJgB",
        "voice_id": "pNInz6obpgDQGcFmaJgB",
        "name": "✨ ElevenLabs: Adam (Natural Conversational Human Male)",
        "gender": "Male",
        "neural": True,
        "is_eleven": True
    },
    {
        "id": "eleven_EXAVITQu4vr4xnSDxMaL",
        "voice_id": "EXAVITQu4vr4xnSDxMaL",
        "name": "✨ ElevenLabs: Bella (Expressive Warm Female)",
        "gender": "Female",
        "neural": True,
        "is_eleven": True
    },
    {
        "id": "eleven_ErXwobaYiN019PkySvjV",
        "voice_id": "ErXwobaYiN019PkySvjV",
        "name": "✨ ElevenLabs: Antoni (Sophisticated Human Male)",
        "gender": "Male",
        "neural": True,
        "is_eleven": True
    },
    {
        "id": "eleven_TxGEqnHWrfWFTfGW9XjX",
        "voice_id": "TxGEqnHWrfWFTfGW9XjX",
        "name": "✨ ElevenLabs: Josh (Deep Natural Human Male)",
        "gender": "Male",
        "neural": True,
        "is_eleven": True
    },
    {
        "id": "eleven_AZnzlk1XvdvUeBnXmlld",
        "voice_id": "AZnzlk1XvdvUeBnXmlld",
        "name": "✨ ElevenLabs: Domi (Energetic Confident Female)",
        "gender": "Female",
        "neural": True,
        "is_eleven": True
    }
]

NEURAL_VOICES = [
    {
        "id": "en-US-AndrewMultilingualNeural",
        "name": "✦ Andrew (Ultra-Realistic Natural Human Male - Default)",
        "gender": "Male",
        "neural": True
    },
    {
        "id": "en-US-AvaMultilingualNeural",
        "name": "✦ Ava (Warm & Expressive Natural Female)",
        "gender": "Female",
        "neural": True
    },
    {
        "id": "en-US-BrianMultilingualNeural",
        "name": "✦ Brian (Intelligent & Sophisticated Male)",
        "gender": "Male",
        "neural": True
    },
    {
        "id": "en-US-EmmaMultilingualNeural",
        "name": "✦ Emma (Cheerful & Friendly Female)",
        "gender": "Female",
        "neural": True
    },
    {
        "id": "en-US-GuyNeural",
        "name": "✦ Guy (Conversational Male)",
        "gender": "Male",
        "neural": True
    },
    {
        "id": "en-US-AriaNeural",
        "name": "✦ Aria (Natural Studio Female)",
        "gender": "Female",
        "neural": True
    },
    {
        "id": "en-US-ChristopherNeural",
        "name": "✦ Christopher (Calm Professional Male)",
        "gender": "Male",
        "neural": True
    },
    {
        "id": "ar-AE-HamdanNeural",
        "name": "✦ Hamdan (Arabic Expressive Neural)",
        "gender": "Male",
        "neural": True
    }
]

def extract_spoken_highlight(text: str) -> str:
    """
    Intelligently extracts a concise, natural spoken punchline from a response.
    Avoids reading entire 500-word walls of text, bullet points, or code syntax aloud.
    """
    if not text:
        return ""

    raw = text.strip()

    # 1. Creator inquiry response
    if any(q in raw.lower() for q in ("who made you", "who coded you", "who created you", "who built you", "who is your creator")):
        return "Raiyan coded me! I am your personal AI desktop companion."

    # 2. Check if text has code
    has_code = "```" in raw

    # 3. Clean markdown structures
    cleaned = re.sub(r"```[\s\S]*?```", "", raw)
    cleaned = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", cleaned)
    cleaned = re.sub(r"https?://\S+", "", cleaned)
    cleaned = re.sub(r"[\*#_`~>|]", "", cleaned)

    # 4. Split into natural sentences
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", cleaned) if s.strip()]

    if has_code:
        if sentences:
            lead = sentences[0]
            if len(lead) < 120 and not lead.endswith(":"):
                return f"{lead} I've placed the code snippet in your chat."
            return "Here is the solution to your request. The code snippet is in your chat."
        return "I've generated the solution and placed the code in your chat."

    # If long multi-sentence response, extract only the first 1-2 punchy sentences
    if len(sentences) > 2:
        highlight = f"{sentences[0]} {sentences[1]}"
        if len(highlight) > 160:
            highlight = sentences[0]
        if len(highlight) > 180:
            highlight = highlight[:177] + "..."
        return highlight

    if sentences:
        highlight = " ".join(sentences)
        return highlight[:180]

    return raw[:150]


class ElevenLabsTTSWorker(QThread):
    """Generates ultra-realistic human speech using ElevenLabs API."""
    generation_finished = Signal(str)
    generation_failed = Signal(str)

    def __init__(self, text: str, voice_id: str, api_key: str, parent=None):
        super().__init__(parent)
        self.text = text
        self.voice_id = voice_id.replace("eleven_", "")
        self.api_key = api_key
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        import httpx
        temp_dir = tempfile.gettempdir()
        out_file = os.path.join(temp_dir, f"nexus_eleven_{int(time.time()*1000)}.mp3")

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        payload = {
            "text": self.text,
            "model_id": "eleven_turbo_v2_5",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.8,
                "style": 0.2,
                "use_speaker_boost": True
            }
        }

        try:
            with httpx.Client(timeout=15.0) as client:
                resp = client.post(url, json=payload, headers=headers)
                if self._is_cancelled:
                    return

                if resp.status_code == 200:
                    with open(out_file, "wb") as f:
                        f.write(resp.content)
                    if os.path.exists(out_file) and os.path.getsize(out_file) > 200:
                        self.generation_finished.emit(out_file)
                        return
                else:
                    err_msg = f"ElevenLabs HTTP {resp.status_code}: {resp.text[:120]}"
                    logger.warning(err_msg)
                    self.generation_failed.emit(err_msg)
        except Exception as e:
            logger.warning(f"ElevenLabs TTS exception: {e}")
            self.generation_failed.emit(str(e))


class NeuralTTSWorker(QThread):
    """Asynchronously generates high-fidelity neural audio without blocking the UI."""
    generation_finished = Signal(str)
    generation_failed = Signal(str)

    def __init__(self, text: str, voice_id: str, rate_str: str, volume_str: str, parent=None):
        super().__init__(parent)
        self.text = text
        self.voice_id = voice_id
        self.rate_str = rate_str
        self.volume_str = volume_str
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        import edge_tts
        temp_dir = tempfile.gettempdir()
        
        # Retry loop up to 2 times for resilient generation
        for attempt in range(2):
            if self._is_cancelled:
                return
            out_file = os.path.join(temp_dir, f"nexus_speech_{int(time.time()*1000)}.mp3")
            try:
                async def _generate():
                    communicate = edge_tts.Communicate(
                        self.text,
                        voice=self.voice_id,
                        rate=self.rate_str,
                        volume=self.volume_str
                    )
                    await communicate.save(out_file)

                asyncio.run(_generate())

                if self._is_cancelled:
                    if os.path.exists(out_file):
                        try: os.remove(out_file)
                        except Exception: pass
                    return

                if os.path.exists(out_file) and os.path.getsize(out_file) > 200:
                    self.generation_finished.emit(out_file)
                    return
            except Exception as e:
                logger.warning(f"Neural TTS attempt {attempt+1} error: {e}")
                time.sleep(0.2)

        self.generation_failed.emit("Failed to generate neural audio after 2 attempts.")


class VoiceEngine(QObject):
    """High-fidelity Neural + SAPI speech synthesis engine for NEXUS."""

    speech_started = Signal()
    speech_finished = Signal()

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(VoiceEngine, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, parent=None):
        if self._initialized:
            return
        super().__init__(parent)
        self.settings = get_settings()
        self.secure_storage = get_secure_storage()
        self._is_speaking = False
        self._current_worker: Optional[QThread] = None
        self._current_audio_file: Optional[str] = None
        self._pygame_initialized = False

        # Windows SAPI COM object (Offline Fallback)
        self._sp_voice = None
        self._init_sp_voice()

        # Audio status monitor timer
        self.poll_timer = QTimer(self)
        self.poll_timer.setInterval(60)
        self.poll_timer.timeout.connect(self._check_playback_status)

        self._init_audio_mixer()
        self._initialized = True

    def _init_audio_mixer(self):
        """Initializes pygame mixer for seamless, low-latency audio playback."""
        try:
            import pygame
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=24000, size=-16, channels=2, buffer=1024)
            self._pygame_initialized = True
        except Exception as e:
            logger.warning(f"Pygame audio mixer initialization failed: {e}")
            self._pygame_initialized = False

    def _init_sp_voice(self):
        """Initializes native Windows SAPI.SpVoice COM object as offline fallback."""
        try:
            import win32com.client
            self._sp_voice = win32com.client.Dispatch("SAPI.SpVoice")
            logger.info("Windows SAPI.SpVoice initialized as offline fallback.")
        except Exception as e:
            logger.warning(f"SAPI initialization: {e}")
            self._sp_voice = None

    def get_available_voices(self) -> List[Dict[str, Any]]:
        """Returns ElevenLabs voices, High-Def Neural voices, and system SAPI voices."""
        voices = list(ELEVENLABS_VOICES) + list(NEURAL_VOICES)

        # Append Windows local voices
        if self._sp_voice:
            try:
                tokens = self._sp_voice.GetVoices()
                for i in range(tokens.Count):
                    t = tokens.Item(i)
                    desc = t.GetDescription()
                    voices.append({
                        "id": f"sapi_{t.Id}",
                        "name": f"🖥️ {desc} (Windows Offline)",
                        "gender": "Male" if "David" in desc else "Female",
                        "neural": False
                    })
            except Exception:
                pass

        return voices

    def stop(self):
        """Immediately interrupts any ongoing speech synthesis or audio playback."""
        # Cancel any ongoing worker
        if self._current_worker and self._current_worker.isRunning():
            if hasattr(self._current_worker, 'cancel'):
                self._current_worker.cancel()
            self._current_worker = None

        # Stop pygame playback
        if self._pygame_initialized:
            try:
                import pygame
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.stop()
                    pygame.mixer.music.unload()
            except Exception:
                pass

        # Clean up temp audio file
        self._cleanup_audio_file()

        # Stop SAPI
        if self._sp_voice:
            try:
                self._sp_voice.Speak("", SVSF_PURGE_BEFORE_SPEAK)
            except Exception:
                pass

        if self.poll_timer.isActive():
            self.poll_timer.stop()

        if self._is_speaking:
            self._is_speaking = False
            self.speech_finished.emit()
            logger.debug("Speech synthesis interrupted.")

    def is_speaking(self) -> bool:
        return self._is_speaking

    def speak(
        self,
        text: str,
        on_start=None,
        on_finish=None
    ):
        """Synthesizes natural speech asynchronously without blocking GUI."""
        if not self.settings.get("tts_enabled", True):
            if on_finish:
                on_finish()
            return

        # Smart selective spoken highlight: Never speak full walls of code or 500-word essays
        punchline = extract_spoken_highlight(text)
        clean_text = self._clean_for_speech(punchline)
        if not clean_text:
            if on_finish:
                on_finish()
            return

        # Stop previous speech
        self.stop()

        # Wire one-shot callbacks
        if on_start:
            def single_start():
                on_start()
                try:
                    self.speech_started.disconnect(single_start)
                except Exception:
                    pass
            self.speech_started.connect(single_start)

        if on_finish:
            def single_finish():
                on_finish()
                try:
                    self.speech_finished.disconnect(single_finish)
                except Exception:
                    pass
            self.speech_finished.connect(single_finish)

        target_voice = self.settings.get("tts_voice", "default")
        eleven_key = self.secure_storage.get_api_key("elevenlabs") or self.settings.get("elevenlabs_api_key", "").strip()

        # 1. Use ElevenLabs if selected or if key is provided
        if (target_voice.startswith("eleven_") or (eleven_key and target_voice == "default")) and eleven_key:
            voice_id = target_voice if target_voice.startswith("eleven_") else "eleven_21m00Tcm4TlvDq8ikWAM"
            self._current_worker = ElevenLabsTTSWorker(
                clean_text,
                voice_id=voice_id,
                api_key=eleven_key,
                parent=self
            )
            self._current_worker.generation_finished.connect(self._on_neural_audio_ready)
            self._current_worker.generation_failed.connect(lambda err: self._speak_neural(clean_text, "en-US-AndrewMultilingualNeural"))
            self._current_worker.start()
            return

        # 2. Check SAPI directly
        if target_voice.startswith("sapi_"):
            self._speak_sapi(clean_text, target_voice)
            return

        # 3. High-Fidelity Edge Neural TTS (Default)
        if target_voice == "default" or target_voice.startswith("eleven_"):
            target_voice = "en-US-AndrewMultilingualNeural"

        self._speak_neural(clean_text, target_voice)

    def _speak_neural(self, clean_text: str, target_voice: str):
        """Asynchronously synthesizes high-fidelity Edge Neural TTS."""
        vol_fraction = float(self.settings.get("tts_volume", 0.90))
        vol_pct = int(max(0.1, min(1.0, vol_fraction)) * 100)
        volume_str = f"+{vol_pct - 100}%" if vol_pct >= 100 else f"-{100 - vol_pct}%"

        speed_fraction = float(self.settings.get("tts_speed", 1.0))
        speed_pct = int((speed_fraction - 1.0) * 100)
        rate_str = f"+{speed_pct}%" if speed_pct >= 0 else f"{speed_pct}%"

        self._current_worker = NeuralTTSWorker(
            clean_text,
            voice_id=target_voice,
            rate_str=rate_str,
            volume_str=volume_str,
            parent=self
        )
        self._current_worker.generation_finished.connect(self._on_neural_audio_ready)
        self._current_worker.generation_failed.connect(lambda err: self._speak_sapi(clean_text, "default"))
        self._current_worker.start()

    @Slot(str)
    def _on_neural_audio_ready(self, file_path: str):
        """Called when neural audio mp3 is generated."""
        self._cleanup_audio_file()
        self._current_audio_file = file_path

        if not self._pygame_initialized:
            self._init_audio_mixer()

        if self._pygame_initialized and os.path.exists(file_path):
            try:
                import pygame
                pygame.mixer.music.load(file_path)
                vol_fraction = float(self.settings.get("tts_volume", 0.90))
                pygame.mixer.music.set_volume(max(0.0, min(1.0, vol_fraction)))
                pygame.mixer.music.play()

                self._is_speaking = True
                self.speech_started.emit()
                self.poll_timer.start()
                return
            except Exception as e:
                logger.error(f"Pygame playback failed: {e}")

        # Fallback if pygame fails
        self._cleanup_audio_file()
        self._is_speaking = False
        self.speech_finished.emit()

    def _speak_sapi(self, text: str, voice_token_id: str):
        """Fallback to native Windows SAPI."""
        if not self._sp_voice:
            self._init_sp_voice()

        if self._sp_voice:
            try:
                vol_fraction = float(self.settings.get("tts_volume", 0.85))
                self._sp_voice.Volume = int(max(0.0, min(1.0, vol_fraction)) * 100)

                speed_fraction = float(self.settings.get("tts_speed", 1.0))
                sapi_rate = int((speed_fraction - 1.0) * 8.0)
                self._sp_voice.Rate = max(-10, min(10, sapi_rate))

                if voice_token_id.startswith("sapi_"):
                    raw_id = voice_token_id[5:]
                    tokens = self._sp_voice.GetVoices()
                    for i in range(tokens.Count):
                        t = tokens.Item(i)
                        if t.Id == raw_id:
                            self._sp_voice.Voice = t
                            break

                self._sp_voice.Speak(text, SVS_FLAGS_ASYNC)
                self._is_speaking = True
                self.speech_started.emit()
                self.poll_timer.start()
            except Exception as e:
                logger.error(f"SAPI fallback failed: {e}")
                self._is_speaking = False
                self.speech_finished.emit()
        else:
            self._is_speaking = False
            self.speech_finished.emit()

    def _check_playback_status(self):
        """Polled every 60ms by QTimer on GUI thread to detect completion."""
        if not self._is_speaking:
            self.poll_timer.stop()
            return

        # Check neural pygame playback
        if self._pygame_initialized and self._current_audio_file:
            try:
                import pygame
                if not pygame.mixer.music.get_busy():
                    self.poll_timer.stop()
                    self._cleanup_audio_file()
                    self._is_speaking = False
                    self.speech_finished.emit()
                return
            except Exception:
                pass

        # Check SAPI
        if self._sp_voice:
            try:
                if self._sp_voice.WaitUntilDone(0):
                    self.poll_timer.stop()
                    self._is_speaking = False
                    self.speech_finished.emit()
            except Exception:
                self.poll_timer.stop()
                self._is_speaking = False
                self.speech_finished.emit()

    def _cleanup_audio_file(self):
        """Safely removes temporary generated mp3."""
        if self._current_audio_file:
            path = self._current_audio_file
            self._current_audio_file = None
            try:
                if os.path.exists(path):
                    os.remove(path)
            except Exception:
                pass

    def _clean_for_speech(self, text: str) -> str:
        """Thoroughly cleans and humanizes text for natural spoken dialogue."""
        if not text:
            return ""
        # Remove markdown code blocks completely
        text = re.sub(r"```[\s\S]*?```", " Here is the Code snippet in your chat. ", text)
        # Inline code
        text = re.sub(r"`([^`]+)`", r"\1", text)
        # Markdown links: [Title](url) -> Title
        text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
        # Remove raw URLs
        text = re.sub(r"https?://\S+", "", text)
        # Remove bold, italics, strikethrough
        text = re.sub(r"\*\*([^\*]+)\*\*", r"\1", text)
        text = re.sub(r"\*([^\*]+)\*", r"\1", text)
        text = re.sub(r"__([^_]+)__", r"\1", text)
        text = re.sub(r"_([^_]+)_", r"\1", text)
        # Remove header markers, bullet points, blockquotes
        text = re.sub(r"^[#\*\-\+>\s]+", "", text, flags=re.MULTILINE)
        # Remove decorative emojis that sound awkward when read aloud
        text = re.sub(r"[\U00010000-\U0010ffff]", "", text)
        text = re.sub(r"[\u2600-\u27ff]", "", text)
        # Convert mathematical / technical symbols into spoken words
        text = text.replace("&", " and ")
        text = text.replace("%", " percent ")
        text = text.replace("$", " dollars ")
        text = text.replace("@", " at ")
        text = text.replace("=", " equals ")
        text = text.replace("+", " plus ")
        text = text.replace("✓", " check ").replace("✕", " x ")
        # Compress whitespace
        text = re.sub(r"\s+", " ", text).strip()
        return text[:450]


_voice_engine_instance = None
def get_voice_engine() -> VoiceEngine:
    global _voice_engine_instance
    if _voice_engine_instance is None:
        _voice_engine_instance = VoiceEngine()
    return _voice_engine_instance
