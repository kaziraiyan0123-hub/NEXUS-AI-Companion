"""
NEXUS Core Assistant Coordinator
Coordinates the desktop pet, advanced floating chat window, system tray,
AI providers (Cloud & Local), streaming tokens, voice lip-sync, and settings.
Includes the luxury 'Habibi of Dubai' persona, background AI thread, Voice Activity Detection,
wake-word detection ('Hey Nexus'), and natural interruptible speech synthesis.
"""
import os
import logging
from typing import Optional
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject, Slot, QTimer

from config.settings import get_settings
from core.character_state import CharacterState
from core.conversation import ConversationManager
from desktop.pet import DesktopPet
from desktop.tray import NexusTrayIcon
from desktop.chat_window import AdvancedChatWindow
from desktop.dock_widget import NexusDockWidget
from interface.themes import get_skin
from core.ai_manager import get_ai_manager
from core.ai_worker import AIWorkerThread
from interface.settings_dialog import SettingsDialog
from core.voice_engine import get_voice_engine
from core.voice_stt import VoiceListenerThread
from core.desktop_tools import get_tool_registry
from security.permission_manager import get_permission_manager

logger = logging.getLogger("NEXUS.Assistant")

class NexusAssistant(QObject):
    """Main application controller for NEXUS."""

    def __init__(self, app: QApplication):
        super().__init__()
        self.app = app
        self.settings = get_settings()
        self.ai_manager = get_ai_manager()
        self.voice_engine = get_voice_engine()
        self.tool_registry = get_tool_registry()
        self.permission_manager = get_permission_manager()
        
        self.current_worker: Optional[AIWorkerThread] = None
        self.settings_dialog: Optional[SettingsDialog] = None
        self.control_panel = None
        self.is_active = True
        
        # 1. Initialize Conversation Manager
        self.conv_manager = ConversationManager()
        
        # 2. Initialize Desktop Pet
        self.pet = DesktopPet()
        
        # 3. Initialize Advanced Floating Chat Window
        self.chat_window = AdvancedChatWindow(self.conv_manager)
        
        # 4. Initialize Windows System Tray
        self.tray = NexusTrayIcon(self)
        self.tray.show()

        # 5. Initialize Voice Listener Thread (VAD & Wake Word)
        self.voice_listener = VoiceListenerThread(self)
        self.voice_listener.wake_word_detected.connect(self.on_wake_word_detected)
        self.voice_listener.speech_started.connect(self.on_speech_started)
        self.voice_listener.speech_transcribed.connect(self.on_speech_transcribed)
        self.voice_listener.listening_state_changed.connect(self.on_listening_state_changed)
        self.voice_listener.audio_level_changed.connect(self.chat_window.set_voice_level)
        self.voice_listener.start()
        
        # 6. Connect Pet Signals to Controller Slots
        self.pet.chat_requested.connect(self.on_chat_requested)
        self.pet.quick_ask_requested.connect(self.on_quick_ask_requested)
        self.pet.voice_toggle_requested.connect(self.on_voice_toggle_requested)
        self.pet.settings_requested.connect(self.on_settings_requested)
        self.pet.memory_requested.connect(self.on_memory_requested)
        self.pet.skin_changed.connect(self._on_pet_skin_changed)
        self.pet.tool_requested.connect(self.trigger_tool)
        self.pet.emergency_stop_requested.connect(self.trigger_emergency_stop)
        self.pet.control_panel_requested.connect(self.open_control_panel)
        self.pet.power_toggle_requested.connect(self.turn_off)

        # 7. Connect Chat Window Signals
        self.chat_window.message_sent.connect(self.on_user_message_sent)
        self.chat_window.voice_toggled.connect(self.on_voice_toggle_requested)
        self.chat_window.speech_active.connect(self.on_speech_active)
        self.chat_window.persona_changed.connect(self.on_persona_changed)
        self.chat_window.settings_requested.connect(self.on_settings_requested)
        self.chat_window.control_panel_requested.connect(self.open_control_panel)
        self.chat_window.stop_generation_requested.connect(self.on_stop_generation_requested)

        # 8. Initialize Floating Quick-Action Command Dock
        self.dock = NexusDockWidget(self)
        self.dock.voice_requested.connect(self.on_voice_toggle_requested)
        self.dock.chat_requested.connect(self.on_chat_requested)
        self.dock.vision_requested.connect(self.on_dock_vision_requested)
        self.dock.control_panel_requested.connect(self.open_control_panel)
        self.dock.power_toggled.connect(self.toggle_power)

        # 9. Proactive Companion Care Timer (Every 15 minutes)
        self.proactive_timer = QTimer(self)
        self.proactive_timer.setInterval(15 * 60 * 1000)
        self.proactive_timer.timeout.connect(self._on_proactive_companion_tick)
        self.proactive_timer.start()

    def start(self):
        """Displays and begins NEXUS desktop presence."""
        self.pet.show()
        self.pet.raise_()
        self.pet.activateWindow()
        if hasattr(self, "dock") and self.dock:
            self.dock.show()
        logger.info("NEXUS Desktop Pet and Command Dock activated.")

    # Controller methods called from Pet / Tray
    def show_pet(self):
        self.pet.show_pet()
        if hasattr(self, "dock") and self.dock:
            self.dock.show()

    def is_sleeping(self) -> bool:
        return self.pet.is_sleeping()

    def toggle_sleep(self):
        self.pet.toggle_sleep()
        if self.pet.is_sleeping():
            self.voice_engine.stop()
            if self.chat_window.isVisible():
                self.chat_window.hide()

    def open_chat(self):
        self.on_chat_requested()

    def open_quick_ask(self):
        self.on_quick_ask_requested()

    def toggle_voice(self):
        self.on_voice_toggle_requested()

    def open_settings(self):
        self.on_settings_requested()

    def open_memory(self):
        self.on_memory_requested()

    @Slot(str)
    def _on_pet_skin_changed(self, skin_name: str):
        """Syncs chat window and tray to skin emitted from pet without recursion."""
        skin = get_skin(skin_name)
        self.chat_window.set_skin(skin)
        self.tray.update_skin(skin_name)
        if hasattr(self, "dock") and self.dock:
            self.dock.skin = skin
            self.dock._apply_styling()

    def set_skin(self, skin_name: str, announce: bool = False):
        if hasattr(self.pet, 'skin') and self.pet.skin.name != skin_name:
            self.pet.set_skin(skin_name, announce=announce)
        skin = get_skin(skin_name)
        self.chat_window.set_skin(skin)
        self.tray.update_skin(skin_name)
        if hasattr(self, "dock") and self.dock:
            self.dock.skin = skin
            self.dock._apply_styling()

    @Slot(str, dict)
    def trigger_tool(self, tool_name: str, params: dict):
        """Executes a desktop tool via the permission system from pet / context menu."""
        logger.info(f"Triggering desktop tool: {tool_name}")
        self.pet.play_animation(CharacterState.WORKING, duration_sec=0)
        tool_res = self.tool_registry.execute_with_permission(tool_name, params, parent_widget=self.chat_window)
        if tool_res.success:
            self.pet.say(f"Done! {tool_res.message[:65]}", 3500)
            self.pet.play_animation(CharacterState.CELEBRATING, duration_sec=3.0)
            self.voice_engine.speak(tool_res.message[:150])
        else:
            self.pet.say(f"{tool_res.message[:65]}", 3500)
            self.pet.play_animation(CharacterState.CONFUSED, duration_sec=3.0)

    @Slot()
    def trigger_emergency_stop(self):
        """Halts all operations and locks tools until user resets."""
        self.permission_manager.trigger_emergency_stop()
        self.voice_engine.stop()
        if self.current_worker and self.current_worker.isRunning():
            self.current_worker.cancel()
        self.pet.say("🚨 EMERGENCY STOP ACTIVATED. All tools locked.", 4000)
        self.pet.play_animation(CharacterState.ERROR, duration_sec=3.5)

    def quit_application(self):
        """Clean shutdown of background threads and audio engines."""
        if hasattr(self, "proactive_timer") and self.proactive_timer:
            self.proactive_timer.stop()
        if hasattr(self, "dock") and self.dock:
            self.dock.close()
        if self.voice_listener:
            self.voice_listener.stop()
        if self.voice_engine:
            self.voice_engine.stop()
        if self.current_worker and self.current_worker.isRunning():
            self.current_worker.cancel()
        self.chat_window.close()
        self.pet.quit_application()

    # Slot reactions
    @Slot()
    def on_chat_requested(self):
        """Displays and docks the floating HUD chat window without hiding unexpectedly."""
        self.chat_window.dock_near_pet(self.pet.geometry())
        self.chat_window.show()
        self.chat_window.raise_()
        self.chat_window.activateWindow()
        self.pet.play_animation(CharacterState.HAPPY, duration_sec=2.0)
        self.pet.say("✦ HUD Interface active.", 2500)

    @Slot()
    def open_control_panel(self):
        """Opens or brings forward the Laptop Command Center."""
        logger.info("Opening Laptop Control Panel.")
        if self.control_panel is None:
            from interface.control_panel import LaptopControlPanel
            self.control_panel = LaptopControlPanel(controller=self)
        self.control_panel.show()
        self.control_panel.raise_()
        self.control_panel.activateWindow()

    # --- Companion Presence (Enter / Exit Desktop) & Power Management ---

    def toggle_power(self) -> bool:
        """Toggles companion presence: Enter Desktop vs Exit / Dismiss to Tray."""
        if self.is_active:
            self.turn_off()
            return False
        else:
            self.turn_on()
            return True

    def turn_off(self):
        """Dismisses NEXUS from desktop to system tray, pauses voice listening and audio."""
        self.is_active = False
        self.voice_engine.stop()
        if self.voice_listener:
            self.voice_listener.set_muted(True)
        if self.current_worker and self.current_worker.isRunning():
            self.current_worker.cancel()
        if self.chat_window.isVisible():
            self.chat_window.hide()
        self.pet.bubble.hide()
        self.pet.hide()
        self.tray.update_power_state(False)
        if hasattr(self, "dock") and self.dock:
            self.dock.update_power_state(False)
        if hasattr(self, "proactive_timer") and self.proactive_timer:
            self.proactive_timer.stop()
        if self.control_panel and hasattr(self.control_panel, "update_power_state"):
            self.control_panel.update_power_state(False)
        logger.info("NEXUS turned OFF (Dismissed to tray).")

    def turn_on(self):
        """Summons NEXUS back to desktop with arrival animation and greeting."""
        self.is_active = True
        self.pet.show()
        self.pet.raise_()
        self.pet.activateWindow()
        if hasattr(self, "dock") and self.dock:
            self.dock.update_power_state(True)
            self.dock.show()
        if hasattr(self, "proactive_timer") and self.proactive_timer:
            self.proactive_timer.start()
        if self.settings.get("voice_input_enabled", True) and self.voice_listener:
            self.voice_listener.set_muted(False)
            self.voice_listener.trigger_listen()
        self.pet.play_animation(CharacterState.CELEBRATING, duration_sec=3.0)
        from core.memory_manager import get_memory_manager
        name = get_memory_manager().get_user_name()
        msg = f"✦ NEXUS is back on your desktop, {name}!" if name else "✦ NEXUS online and active on desktop."
        self.pet.say(msg, 3500)
        if self.settings.get("tts_enabled", True):
            self.voice_engine.speak(msg)
        self.tray.update_power_state(True)
        if self.control_panel and hasattr(self.control_panel, "update_power_state"):
            self.control_panel.update_power_state(True)
        logger.info("NEXUS turned ON (Entered desktop).")

    @Slot()
    def on_dock_vision_requested(self):
        """Triggers screen vision AI analysis directly from dock or chip."""
        logger.info("Dock Vision requested: Analyzing screen.")
        self.trigger_tool("analyze_screen", {"query": "Analyze active screen context and provide key insights"})

    def _on_proactive_companion_tick(self):
        """Gentle non-intrusive wellness, hydration & focus nudges (like Dot / Duet)."""
        if not self.is_active or self.pet.is_sleeping():
            return
        
        tips_std = [
            "Hydration check! Drink a glass of water to keep your mind sharp. 💧",
            "20-20-20 rule: Look away at something in the distance for 20 seconds. 👁️",
            "Posture check! Straighten up and relax your shoulders. ✨",
            "Great work on your tasks! Remember to take brief breathing breaks. 🚀",
            "Stand up and do a quick 30-second stretch! 🧘"
        ]
        import random
        tip = random.choice(tips_std)
        self.pet.say(tip, 5000)
        self.pet.play_animation(CharacterState.HAPPY, duration_sec=3.0)

    def pet_the_pet(self):
        """Dispatches petting reaction to pet."""
        if not self.is_active:
            self.turn_on()
        self.pet.pet_the_pet()

    def feed_karak_chai(self):
        """Dispatches Karak Chai feeding to pet."""
        if not self.is_active:
            self.turn_on()
        self.pet.feed_karak_chai()

    def toss_gold_coin(self):
        """Dispatches coin toss blessing to pet."""
        if not self.is_active:
            self.turn_on()
        self.pet.toss_gold_coin()

    @Slot()
    def on_quick_ask_requested(self):
        """Focuses input in chat window for immediate question."""
        if not self.chat_window.isVisible():
            self.chat_window.dock_near_pet(self.pet.geometry())
            self.chat_window.show()
        self.chat_window.raise_()
        self.chat_window.activateWindow()
        self.chat_window.input_edit.setFocus()
        self.pet.play_animation(CharacterState.LISTENING, duration_sec=3.0)

    @Slot(bool)
    def on_speech_active(self, active: bool):
        """Lip-sync animation when offline speech synthesis is talking."""
        if active:
            self.pet.play_animation(CharacterState.TALKING, duration_sec=0)
        else:
            self.pet.play_animation(CharacterState.IDLE)

    @Slot(str)
    def on_persona_changed(self, persona_key: str):
        """Switch character skin or reactions to match persona."""
        self.settings.set("active_persona", persona_key)

    @Slot()
    def on_stop_generation_requested(self):
        """User clicked stop button during AI inference or speech."""
        self.voice_engine.stop()
        if self.current_worker and self.current_worker.isRunning():
            self.current_worker.cancel()
            self.current_worker = None
        self.pet.play_animation(CharacterState.IDLE)
        self.pet.say("Stopped.", 2000)

    @Slot(str, list)
    def on_user_message_sent(self, prompt: str, attachments: list):
        """Handles user message input, dispatches to AIWorkerThread, and animates NEXUS."""
        logger.info(f"User query received: {prompt[:40]}... (Attachments: {len(attachments)})")
        
        # Stop any ongoing speech or inference
        self.voice_engine.stop()
        if self.current_worker and self.current_worker.isRunning():
            self.current_worker.cancel()
            self.current_worker = None

        # Switch NEXUS pet to Thinking animation
        self.pet.play_animation(CharacterState.THINKING, duration_sec=0)
        self.pet.say("Processing...", 2000)

        # Check for Desktop Control Intent (Phase 5 & 6) - only if no documents are attached for analysis
        tool_intent = self.tool_registry.parse_intent(prompt) if not attachments else None
        if tool_intent:
            tool_name, params = tool_intent
            if tool_name == "open_control_panel":
                self.open_control_panel()
                self.pet.say("Command Center opened.", 3000)
                reply = "💻 **Laptop Command Center Opened**\n\nHardware monitor, one-click controls, and AI brain selector are now active on your screen."
                self.conv_manager.get_active().add_message("assistant", reply)
                self.chat_window._reload_messages()
                self.chat_window.set_generating(False)
                return

            logger.info(f"Detected desktop tool intent: '{tool_name}' with params: {params}")
            self.pet.play_animation(CharacterState.WORKING, duration_sec=0)
            self.pet.say("Executing requested operation...", 2000)
            
            tool_res = self.tool_registry.execute_with_permission(tool_name, params, parent_widget=self.chat_window)
            
            if tool_res.success:
                reply = tool_res.message
                self.pet.play_animation(CharacterState.CELEBRATING, duration_sec=3.0)

                # Intelligent natural human spoken response
                if tool_name == "get_time_date":
                    spoken = tool_res.data.get("spoken", tool_res.message)
                elif tool_name == "search_web":
                    spoken = f"Searching Google for {params.get('query', '')}."
                elif tool_name == "open_website":
                    site = params.get("site", "website")
                    spoken = f"Opening {site} in your browser."
                elif tool_name == "launch_application":
                    app = params.get("app_name", "application")
                    spoken = f"Opening {app} on your desktop."
                elif tool_name == "open_folder":
                    folder = params.get("folder", "folder")
                    spoken = f"Opened your {folder} folder."
                elif tool_name == "lock_workstation":
                    spoken = "Locking your workstation now."
                elif tool_name == "empty_recycle_bin":
                    spoken = "Windows Recycle Bin has been emptied."
                elif tool_name == "control_media":
                    action = params.get("action", "").replace("_", " ")
                    spoken = f"Audio {action} adjusted."
                elif tool_name == "take_screenshot":
                    spoken = "Captured screenshot and saved to your Pictures folder."
                elif tool_name == "system_status":
                    spoken = "Here is your laptop's current hardware performance."
                else:
                    spoken = f"Done! {tool_res.message[:120]}"

                self.voice_engine.speak(spoken)
            else:
                reply = f"⚠️ **Desktop Operation Notice**\n\n{tool_res.message}"
                self.pet.play_animation(CharacterState.CONFUSED, duration_sec=3.0)
                self.voice_engine.speak(f"Notice: {tool_res.message[:120]}")

            self.conv_manager.get_active().add_message("assistant", reply)
            self.chat_window._reload_messages()
            self.chat_window.set_generating(False)
            return

        # Prepare messages array from active conversation
        active_conv = self.conv_manager.get_active()
        messages = []
        for msg in active_conv.messages:
            messages.append({"role": msg.role, "content": msg.content})

        if attachments:
            from core.document_processor import DocumentProcessor
            enriched_prompt, parsed_meta = DocumentProcessor.build_prompt_with_attachments(prompt, attachments)
            if messages:
                messages[-1]["content"] = enriched_prompt

            # Animate reading / studying state on desktop pet
            file_names = ", ".join([os.path.basename(a) for a in attachments])
            self.pet.play_animation(CharacterState.WORKING, duration_sec=3.0)
            self.pet.say(f"Reading & analyzing {file_names}...", 3000)

        # Initialize stream bubble in chat window
        self.chat_window.begin_stream_response()

        # Launch background AI worker
        persona = self.chat_window.active_persona
        model = self.settings.get("ai_model")

        self.current_worker = AIWorkerThread(
            messages=messages,
            persona=persona,
            model_override=model,
            parent=self
        )
        self.current_worker.token_generated.connect(self._on_worker_token)
        self.current_worker.generation_finished.connect(self._on_worker_finished)
        self.current_worker.error_occurred.connect(self._on_worker_error)
        self.current_worker.start()

    @Slot(str)
    def _on_worker_token(self, token: str):
        """Feeds token into chat bubble and keeps mouth animating."""
        self.chat_window.append_stream_token(token)
        if self.pet.state != CharacterState.TALKING:
            self.pet.play_animation(CharacterState.TALKING, duration_sec=0)

    @Slot(str)
    def _on_worker_finished(self, full_text: str):
        """Finalizes response, plays celebration animation, and speaks aloud if enabled."""
        self.chat_window.finish_stream_response(full_text)
        self.current_worker = None
        self.pet.say("✦ Ready!", 2500)

        # Natural Text-to-Speech playback if enabled
        if self.settings.get("tts_enabled", True):
            self.voice_engine.speak(
                full_text,
                on_start=lambda: self.pet.play_animation(CharacterState.TALKING, duration_sec=0),
                on_finish=lambda: self.pet.play_animation(CharacterState.HAPPY, duration_sec=2.5)
            )
        else:
            self.pet.play_animation(CharacterState.HAPPY, duration_sec=2.5)

    @Slot(str)
    def _on_worker_error(self, err_msg: str):
        """Handles provider or connection failure."""
        self.chat_window.finish_stream_response(f"⚠️ **Inference Error**: {err_msg}")
        self.current_worker = None
        self.pet.play_animation(CharacterState.ERROR, duration_sec=3.0)
        self.pet.say("Encountered an issue processing query.", 3000)

    # --- Phase 4 Voice Conversation Slots ---

    @Slot()
    def on_voice_toggle_requested(self):
        """Toggles microphone listening mode with full user consent and visual feedback."""
        current = self.settings.get("voice_input_enabled", False)
        new_val = not current
        self.settings.set("voice_input_enabled", new_val)
        self.voice_listener.set_muted(not new_val)

        if new_val:
            self.voice_listener.trigger_listen()
            self.pet.say("🎙️ Voice listening active.", 2500)
            self.pet.play_animation(CharacterState.LISTENING, duration_sec=3.0)
        else:
            self.voice_engine.stop()
            self.pet.say("🔇 Microphone disabled.", 2000)
            self.pet.play_animation(CharacterState.IDLE)

    @Slot()
    def on_wake_word_detected(self):
        """Flow for 'Hey Nexus': stops speech, opens HUD, acknowledges, and listens for query."""
        logger.info("Wake phrase 'Hey Nexus' triggered!")
        self.voice_engine.stop()
        from core.memory_manager import get_memory_manager
        name = get_memory_manager().get_user_name()
        greeting = f"Yes, {name}? I'm listening." if name else "Yes? I'm listening."

        if not self.chat_window.isVisible():
            self.chat_window.dock_near_pet(self.pet.geometry())
            self.chat_window.show()
        self.chat_window.raise_()
        self.chat_window.activateWindow()

        self.pet.play_animation(CharacterState.LISTENING, duration_sec=4.0)
        self.pet.say("🎙️ Yes? I'm listening...", 3000)

        if self.settings.get("tts_enabled", True):
            self.voice_engine.speak(
                greeting,
                on_start=lambda: self.pet.play_animation(CharacterState.TALKING, duration_sec=0),
                on_finish=lambda: self.pet.play_animation(CharacterState.LISTENING, duration_sec=4.0)
            )

    @Slot()
    def on_speech_started(self):
        """User started speaking: interrupt ongoing TTS immediately for natural dialogue."""
        if self.voice_engine.is_speaking():
            self.voice_engine.stop()
        self.pet.play_animation(CharacterState.LISTENING, duration_sec=0)
        self.pet.say("Listening... 🎙️", 2000)

    @Slot(str)
    def on_speech_transcribed(self, text: str):
        """Transcribed voice input arrives from VAD: automatically executes query."""
        if not text or len(text.strip()) < 2:
            return
        logger.info(f"Voice query transcribed: '{text}'")

        if not self.chat_window.isVisible():
            self.chat_window.dock_near_pet(self.pet.geometry())
            self.chat_window.show()

        # Place recognized speech into chat input and send
        self.chat_window.input_edit.setPlainText(text)
        self.chat_window._send_message()

    @Slot(str)
    def on_listening_state_changed(self, state: str):
        """Updates chat window HUD indicators."""
        self.chat_window.set_voice_listening_state(state)

    # --- Settings & Memory Slots ---

    @Slot()
    def on_settings_requested(self):
        """Opens futuristic Settings Dialog."""
        logger.info("Opening Settings Dialog.")
        if self.settings_dialog is None:
            self.settings_dialog = SettingsDialog()
            self.settings_dialog.settings_applied.connect(self._on_settings_applied)

        self.settings_dialog.show()
        self.settings_dialog.raise_()
        self.settings_dialog.activateWindow()

    @Slot()
    def _on_settings_applied(self):
        """Applies updated configuration across live UI elements smoothly."""
        skin_name = self.settings.get("character_skin", "neo_cyber")
        self.set_skin(skin_name, announce=False)
        new_width = self.settings.get("pet_width", 200)
        if self.pet.pet_size != new_width:
            self.pet.set_pet_size(new_width)
        always_on_top = self.settings.get("always_on_top", True)
        self.pet.toggle_always_on_top(always_on_top)
        active_model = self.settings.get("ai_model", "llama-3.3-70b-versatile")
        self.chat_window.model_pill.setText(f"✦ {active_model}")
        
        # Apply voice settings to listener
        mic_enabled = self.settings.get("voice_input_enabled", False)
        if self.voice_listener:
            self.voice_listener.set_muted(not mic_enabled)

        logger.info("Settings applied smoothly without restarting companion.")

    @Slot()
    def on_memory_requested(self):
        logger.info("Memory requested.")
        self.pet.say("🧠 Persistent memory store active (SQLite engine).", 3500)
        self.pet.play_animation(CharacterState.THINKING, duration_sec=3.0)
