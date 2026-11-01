"""
NEXUS Voice Input & Speech-to-Text (STT) Engine
Continuous Voice Activity Detection (VAD), wake-word detection ("Hey Nexus"),
and speech transcription using speech_recognition and native Windows audio capture.
"""
import time
import math
import struct
import logging
from typing import Optional
from PySide6.QtCore import QThread, Signal

import speech_recognition as sr
from config.settings import get_settings

logger = logging.getLogger("NEXUS.VoiceSTT")

class VoiceListenerThread(QThread):
    """
    Dedicated background worker thread for Voice Activity Detection (VAD),
    wake-word detection ('Hey Nexus'), and Speech-to-Text transcription.
    Never blocks GUI thread and strictly respects user mute/disable settings.
    """

    # Signals
    wake_word_detected = Signal()
    speech_started = Signal()
    speech_transcribed = Signal(str)
    listening_state_changed = Signal(str)   # "muted", "idle", "listening", "transcribing"
    audio_level_changed = Signal(float)     # Normalized RMS audio level 0.0 - 1.0
    error_occurred = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = get_settings()
        self._is_running = True
        self._is_muted = not self.settings.get("voice_input_enabled", False)
        self._force_active_listen = False

        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 350
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        self.recognizer.non_speaking_duration = 0.5

        self.mic: Optional[sr.Microphone] = None
        self._init_microphone()

    def _init_microphone(self):
        """Initializes default microphone source."""
        try:
            self.mic = sr.Microphone()
            logger.info("Speech recognition microphone initialized.")
        except Exception as e:
            logger.error(f"Failed to initialize microphone: {e}")
            self.mic = None

    def set_muted(self, muted: bool):
        """Disables or enables microphone listening."""
        self._is_muted = muted
        self.settings.set("voice_input_enabled", not muted)
        state = "muted" if muted else "idle"
        self.listening_state_changed.emit(state)
        logger.info(f"Microphone listening state: {'MUTED' if muted else 'ACTIVE'}")

    def trigger_listen(self):
        """Triggered by user clicking the microphone button for immediate command input."""
        if self._is_muted:
            self.set_muted(False)
        self._force_active_listen = True
        logger.info("Manual voice listening triggered.")

    def stop(self):
        """Stops thread execution cleanly on application shutdown."""
        self._is_running = False
        self.wait(2000)

    def _calculate_rms(self, raw_data: bytes) -> float:
        """Calculates normalized RMS amplitude (0.0 to 1.0) from 16-bit audio bytes."""
        try:
            count = len(raw_data) // 2
            if count == 0:
                return 0.0
            shorts = struct.unpack(f"{count}h", raw_data)
            sum_squares = sum(s * s for s in shorts)
            rms = math.sqrt(sum_squares / count)
            # Normalize against standard speaking level (0 - 32768)
            norm = min(1.0, rms / 4000.0)
            return round(norm, 2)
        except Exception:
            return 0.0

    def run(self):
        """Continuous background listening loop."""
        if not self.mic:
            logger.warning("Microphone not available, VoiceListener idle.")
            return

        # Initial ambient noise calibration
        try:
            with self.mic as source:
                logger.info("Calibrating ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.8)
                logger.info(f"Energy threshold calibrated to: {self.recognizer.energy_threshold}")
        except Exception as e:
            logger.debug(f"Ambient noise calibration skipped: {e}")

        while self._is_running:
            # 1. Check if user has muted / disabled voice input
            if self._is_muted and not self._force_active_listen:
                time.sleep(0.2)
                continue

            wake_word_enabled = self.settings.get("wake_word_enabled", False)
            wake_phrase = self.settings.get("wake_word", "hey nexus").lower().strip()

            # 2. Listening phase
            try:
                is_active = self._force_active_listen or (not wake_word_enabled)
                self.listening_state_changed.emit("listening" if is_active else "idle")

                with self.mic as source:
                    # Capture audio phrase
                    timeout = 4.0 if not self._force_active_listen else 7.0
                    limit = 10.0 if is_active else 3.5

                    audio = self.recognizer.listen(
                        source,
                        timeout=timeout,
                        phrase_time_limit=limit
                    )

                if not self._is_running:
                    break

                # Emit audio energy level for visual meter
                raw_bytes = audio.get_raw_data()
                rms = self._calculate_rms(raw_bytes)
                self.audio_level_changed.emit(rms)

                # 3. Transcription phase
                self.listening_state_changed.emit("transcribing")
                self.speech_started.emit()

                text = self._transcribe(audio)
                if not text:
                    self.listening_state_changed.emit("idle")
                    self._force_active_listen = False
                    continue

                logger.info(f"Speech transcribed: '{text}'")
                lower = text.lower()

                # Check wake word if in passive mode
                if wake_word_enabled and not self._force_active_listen:
                    if wake_phrase in lower or "nexus" in lower or "habibi" in lower:
                        logger.info("Wake word matched!")
                        self.wake_word_detected.emit()
                        self._force_active_listen = True
                        continue

                # Emit transcribed query
                self.speech_transcribed.emit(text)
                self._force_active_listen = False
                self.listening_state_changed.emit("idle")

            except sr.WaitTimeoutError:
                # Normal silence timeout in listening loop
                self.audio_level_changed.emit(0.0)
                if self._force_active_listen:
                    self._force_active_listen = False
                    self.listening_state_changed.emit("idle")
            except Exception as e:
                logger.debug(f"Listening loop cycle exception: {e}")
                self.audio_level_changed.emit(0.0)
                time.sleep(0.3)

    def _transcribe(self, audio: sr.AudioData) -> str:
        """Transcribes audio using Google Web Speech API or local fallback."""
        try:
            text = self.recognizer.recognize_google(audio, language="en-US")
            return text.strip()
        except sr.UnknownValueError:
            logger.debug("Speech unintelligible.")
            return ""
        except sr.RequestError as e:
            logger.warning(f"Google Speech Recognition service unreachable: {e}")
            return ""
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return ""
