"""
NEXUS Background AI Inference Worker
Runs AI generation and streaming on a dedicated QThread to ensure 60 FPS GUI smoothness.
"""
import logging
from typing import List, Dict, Optional
from PySide6.QtCore import QThread, Signal

from core.ai_manager import get_ai_manager

logger = logging.getLogger("NEXUS.AIWorker")

class AIWorkerThread(QThread):
    """Executes AI provider generation and streaming on a background thread."""

    token_generated = Signal(str)
    generation_finished = Signal(str)
    error_occurred = Signal(str)

    def __init__(
        self,
        messages: List[Dict[str, str]],
        persona: str = "companion",
        model_override: Optional[str] = None,
        parent=None
    ):
        super().__init__(parent)
        self.messages = messages
        self.persona = persona
        self.model_override = model_override
        self._is_cancelled = False
        self.ai_manager = get_ai_manager()

    def cancel(self):
        """Requests cancellation of ongoing generation."""
        self._is_cancelled = True
        logger.info("AI generation cancelled by user.")

    def run(self):
        accumulated = []
        try:
            for token in self.ai_manager.stream_chat(
                messages=self.messages,
                persona=self.persona,
                model_override=self.model_override
            ):
                if self._is_cancelled:
                    break
                accumulated.append(token)
                self.token_generated.emit(token)

            full_text = "".join(accumulated)
            self.generation_finished.emit(full_text)

        except Exception as e:
            logger.error(f"AI Worker thread encountered error: {e}")
            self.error_occurred.emit(str(e))
