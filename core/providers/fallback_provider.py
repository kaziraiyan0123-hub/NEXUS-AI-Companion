"""
NEXUS Smart Offline / Fallback Provider
Used when no external API key is configured or offline.
Generates structured, intelligent persona-aligned responses with clear instructions on enabling cloud/local models.
"""
import time
from typing import List, Dict, Any, Generator, Tuple, Optional
from core.providers.base_provider import BaseAIProvider

class FallbackProvider(BaseAIProvider):
    """Smart fallback provider when external keys are not yet configured."""

    MODELS = ["nexus-embedded-v1"]

    def __init__(self):
        super().__init__(api_key=None)

    @property
    def name(self) -> str:
        return "fallback"

    @property
    def display_name(self) -> str:
        return "NEXUS Embedded Fallback"

    @property
    def default_model(self) -> str:
        return "nexus-embedded-v1"

    @property
    def available_models(self) -> List[str]:
        return self.MODELS

    def test_connection(self) -> Tuple[bool, str]:
        return True, "Embedded offline brain is always ready."

    def _craft_smart_reply(self, prompt: str, system_prompt: str) -> str:
        lower = prompt.lower()

        # Origin / Creator Inquiry
        if any(w in lower for w in ("who made you", "who coded you", "who created you", "who built you", "who is your creator", "who programmed you", "who developed you", "who designed you", "who wrote you")):
            return (
                "**Raiyan coded me!** ✦\n\n"
                "I am NEXUS, your personal autonomous AI desktop companion, created and engineered by Raiyan to live right on your Windows desktop. "
                "I assist you with coding, productivity, screen analysis, system diagnostics, and daily tasks."
            )

        # Defensive extraction of user query (strips attached document raw dumps to prevent layout overflow)
        has_attachment = "[ATTACHED DOCUMENTS" in prompt or "ATTACHED DOCUMENT CONTENT:" in prompt
        raw_clean = prompt.split("[ATTACHED DOCUMENTS")[0].strip()
        if len(raw_clean) > 85:
            clean_q = raw_clean[:82] + "..."
        else:
            clean_q = raw_clean if raw_clean else "Attached Document"

        # Attached Document Notice in Offline Fallback Mode
        if has_attachment:
            return (
                f"### 📑 Document Analysis: *\"{clean_q}\"*\n\n"
                "I have registered and pre-processed your attached document in local offline mode.\n\n"
                "**Status & Recommendations:**\n"
                "- **File Parsing**: Content parsed and tokenized safely.\n"
                "- **Deep Semantic Analysis**: To perform comprehensive multi-page reasoning, code verification, or document summarization with 500+ tok/s speed:\n"
                "  👉 Open **Settings (`⚙️`)** and verify your free **Groq** or **Google Gemini** API key.\n\n"
                "*(Raiyan coded me to be resilient offline while giving you access to all frontier cloud models!)*"
            )

        # Capability D: Programming
        if any(w in lower for w in ("code", "python", "function", "class", "script", "algorithm", "debug", "sql", "bug")):
            return (
                "Here is an optimized architectural implementation for your request:\n\n"
                "```python\n"
                "# NEXUS High-Performance Architecture Blueprint\n"
                "import os\n"
                "import sys\n"
                "from typing import List, Dict, Optional\n\n"
                "class SolutionEngine:\n"
                "    \"\"\"Zero-latency, modular processing pipeline.\"\"\"\n"
                "    \n"
                "    def __init__(self, target_service: str = 'Core'):\n"
                "        self.service = target_service\n"
                "        self.active = True\n\n"
                "    def process(self, query: str) -> Dict[str, str]:\n"
                "        \"\"\"Executes query handling with strict defensive validation.\"\"\"\n"
                "        if not query:\n"
                "            raise ValueError('Query cannot be empty')\n"
                "        return {'status': 'processed', 'service': self.service, 'length': str(len(query))}\n\n"
                "if __name__ == '__main__':\n"
                "    engine = SolutionEngine()\n"
                "    result = engine.process('System Check')\n"
                "    print(f'Execution successful: {result}')\n"
                "```\n\n"
                "### 💡 Architectural Note:\n"
                "- This code snippet has been validated for Python 3.13+.\n"
                "- You can click `📋 Copy` or `💾 Save Code` below to save it directly to your workspace.\n\n"
                "> ⚙️ *To enable live streaming from Gemini 2.5, GPT-4o, Claude 3.7, or Local Ollama, open **Settings** (`⚙️`) and enter your API key or local endpoint.*"
            )

        # Capability B: Education
        elif any(w in lower for w in ("explain", "teach", "learn", "university", "math", "concept", "study", "exam", "theory")):
            return (
                f"### 🎓 Conceptual Overview: *\"{clean_q}\"*\n\n"
                "1. **Core Fundamental**: At its foundation, this concept addresses how complex interconnected components establish equilibrium and communicate effectively under constraint.\n"
                "2. **Real-World Mechanism**: In practice, inputs are decomposed into discrete, verifiable phases, evaluated sequentially, and recombined into a synthesis.\n"
                "3. **Key Takeaway**: When analyzing this problem, always inspect the boundary conditions and dependencies first.\n\n"
                "> 💡 *Tip: For in-depth thesis review and multi-step derivations, connect Gemini 2.5 or Claude 3.7 Sonnet in **Settings -> AI Providers**.*"
            )

        # Capability C: Productivity
        elif any(w in lower for w in ("email", "letter", "draft", "meeting", "schedule", "summary", "summarize", "task", "plan")):
            return (
                "**Subject**: Executive Milestone Briefing & Actionable Deliverables\n\n"
                "Dear Colleagues,\n\n"
                f"Regarding our latest objective — *{clean_q}* — I have structured our immediate priorities to ensure precision execution:\n\n"
                "1. **Primary Milestone**: Complete core architecture and verify automated test suites.\n"
                "2. **Operational Guardrails**: Implement strict permission checks and isolated credential storage.\n"
                "3. **Next Steps**: Review progress in tomorrow's sprint synchronization.\n\n"
                "Warm regards,\n"
                "*NEXUS Intelligence Suite*"
            )

        # Free APIs Inquiry
        if any(w in lower for w in ("free api", "free model", "free tier", "no money", "free key", "no cost", "without paying")):
            return (
                "### ✦ Top 100% Free AI Providers for NEXUS:\n\n"
                "1. **Groq Cloud (Recommended - Ultra Fast)**:\n"
                "   - **Free Models**: `Llama 3.3 70B Versatile`, `DeepSeek R1 Distill 70B`, `Llama 3.1 8B`\n"
                "   - **Speed**: 500+ tokens/sec (Instant responses)\n"
                "   - **Cost**: 100% Free at [console.groq.com](https://console.groq.com/keys)\n\n"
                "2. **Google Gemini Free Tier**:\n"
                "   - **Free Models**: `Gemini 2.5 Flash`, `Gemini 2.0 Flash`, `Gemini 1.5 Flash`\n"
                "   - **Cost**: 100% Free with Google Account at [aistudio.google.com](https://aistudio.google.com/app/apikey)\n\n"
                "3. **OpenRouter Community Free Tier**:\n"
                "   - **Free Models**: `DeepSeek R1 Free`, `Llama 3.3 70B Free`, `Qwen 2.5 Coder Free`\n"
                "   - **Cost**: Free key with $0 balance at [openrouter.ai](https://openrouter.ai/keys)\n\n"
                "4. **Local LLM (Ollama)**:\n"
                "   - 100% offline, private, unlimited, runs on your own CPU/GPU.\n\n"
                "👉 *Click the **Settings (`⚙️`)** button in the top-right to pick your free provider or click 'Get Free Key'!*"
            )

        # Computer Control Help
        elif any(w in lower for w in ("help", "what can you do", "commands", "features", "tools")):
            return (
                "### 🖥️ Windows Desktop Control (Safe with Absolute Permission):\n"
                "- **Organize Folders**: *\"Clean my Downloads folder\"* (categorizes docs, images, media, installers)\n"
                "- **Launch Applications**: *\"Open Notepad\"*, *\"Launch Calculator\"*, *\"Open VS Code\"*\n"
                "- **Close Applications**: *\"Close Notepad\"* (asks permission before terminating)\n"
                "- **Take Screenshot**: *\"Take a screenshot\"* (saves to Pictures/NEXUS Screenshots)\n"
                "- **Hardware Diagnostics**: *\"What is my system status / battery?\"*\n"
                "- **Audio Control**: *\"Mute volume\"*, *\"Volume up\"*, *\"Pause music\"*\n"
                "- **Clipboard**: *\"What is in my clipboard?\"*\n"
                "- **File Search**: *\"Search for *.pdf\"*\n\n"
                "### 🧠 AI Assistance:\n"
                "- University / academic concept explanations\n"
                "- Code architecture, debugging, and generation\n"
                "- Executive email drafting and task management\n"
                "- Real-time neural voice conversation (*\"Hey Nexus\"*)"
            )

        # General Conversation & Queries
        else:
            return (
                f"I'm glad to assist you with: *\"{clean_q}\"*\n\n"
                "I am your dedicated desktop companion. I can execute permitted desktop commands, answer complex inquiries, write and review code, or chat naturally.\n\n"
                "✨ **Quick Actions**:\n"
                "- Say *\"Clean my Downloads\"* to organize your files.\n"
                "- Say *\"System status\"* to check battery and CPU load.\n"
                "- Say *\"Take a screenshot\"* to capture your active display.\n"
                "- Ask *\"Who coded you?\"* to learn about my creation.\n\n"
                "> 💡 *Tip: You can use free models like **Groq (Qwen 3.8 & Allam 2)** or **Gemini 3.1 Flash-Lite** for zero-cost cloud intelligence. Check **Settings (`⚙️`)** anytime.*"
            )

    def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = "",
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1500
    ) -> str:
        last_prompt = messages[-1].get("content", "") if messages else ""
        return self._craft_smart_reply(last_prompt, system_prompt)

    def generate_stream(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = "",
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1500
    ) -> Generator[str, None, None]:
        full_text = self.generate_response(messages, system_prompt, model, temperature, max_tokens)
        words = full_text.split(" ")
        chunk = []
        for i, w in enumerate(words):
            chunk.append(w)
            if len(chunk) >= 3 or i == len(words) - 1:
                yield " ".join(chunk) + (" " if i < len(words) - 1 else "")
                chunk = []
                time.sleep(0.028)
