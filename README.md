# ✦ NEXUS — Autonomous AI Desktop Companion & Command Center
> **Engineered & Coded by Raiyan**  
> *A native, intelligent, animated desktop companion and productivity HUD for Windows with real-time desktop automation, document intelligence, and multi-model neural AI.*

[![Python](https://img.shields.io/badge/Python-3.13+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![GUI](https://img.shields.io/badge/GUI-PySide6%20Qt-41CD52?style=flat&logo=qt&logoColor=white)](https://www.qt.io/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-66%20Passed%20%E2%9C%93-brightgreen.svg)]()
[![Free AI Tier](https://img.shields.io/badge/Free%20AI-Gemini%20%7C%20Groq%20%7C%20OpenRouter-purple.svg)]()

---

## 🌟 What is NEXUS?

NEXUS is an autonomous AI desktop pet that lives directly on your Windows desktop. Unlike standard web chat interfaces, NEXUS possesses:
- **Spatial Awareness & Eye Tracking**: Procedural gaze physics, natural micro-saccades, and smooth floating anti-gravity animations.
- **Real-Time Desktop Automation**: Executes approved operations (opening apps, websites, searching Google, time/date lookups, volume adjustment, lock screen, and system health checks).
- **Deep Document & PDF Intelligence**: Drag and drop any PDF, Word doc, code file, or spreadsheet to get immediate, 100% accurate summaries, answers, and analysis.
- **Natural Human Speech Synthesis**: Features ultra-realistic, expressive human voices (via Edge Neural and ElevenLabs) with zero robotic speech.
- **Absolute Permission Security**: Three-tier security model with interactive permission dialogs, process blacklisting, and a global Emergency Stop button.

---

## 🚀 Key Features

### 1. 📄 Deep Document & PDF Intelligence (pypdf Powered)
- **Instant File Reading**: Attach or drag-and-drop `.pdf`, `.txt`, `.py`, `.json`, `.csv`, `.xlsx`, or code files into the chat HUD.
- **Full Text Extraction**: Extracts page-by-page text, preserving section headers, structure, and tabular data.
- **Accurate Document Q&A**: Ask *"What is this PDF about?"*, *"Summarize this"*, or ask specific questions based on homework, research papers, or business reports.

### 2. ⚡ Real-Time Desktop Control & Automation
- **Real-Time System Clock**: Instant answers for *"What time is it?"*, *"What day is today?"*, and *"Current date"*.
- **Web Navigation**: *"Open YouTube"*, *"Open GitHub"*, *"Open ChatGPT"*, *"Open Reddit"*, *"Open Netflix"*, or any URL.
- **Google Search**: *"Search Google for [query]"*, *"Google [query]"*, or *"Look up [query]"*.
- **Application Launcher**: *"Open Notepad"*, *"Open Calculator"*, *"Open VS Code"*, *"Open Terminal"*, *"Open Chrome"*, *"Open Spotify"*, etc.
- **System Actions**: *"Lock PC"*, *"Volume up / down / mute"*, *"Empty recycle bin"*, *"How is my laptop?"* (live CPU, RAM, battery, disk).

### 3. 🎨 8 Distinct Vector Character Archetypes
Switch between custom vector skins at any time:
1. 👑 **Royal Habibi of Dubai**: Pristine white silk Kandura, flowing Ghutra drapes, double black & gold Agal rings with gold crest, and pure gold-framed mirrored aviator sunglasses with lens glints and golden Dirham particles! *(Visual appearance only — conversation remains natural, intelligent companion dialogue)*.
2. ✦ **Neo Cyber Core**: Futuristic cyan HUD orb with dual aerodynamic propulsion fins.
3. 🦊 **Quantum Fox**: Holographic cyber-feline with expressive triangular ears.
4. 🤖 **Chrono Sentinel**: Tactical mecha with dual telemetry antenna fins and armor plating.
5. 🐱 **Nebula Aether Cat**: Ethereal violet-pink feline with starry ears and halo.
6. 🔥 **Solar Phoenix**: Coronal plasma flare crest and fire-forged winglets.
7. 🖤 **Obsidian Phantom**: Matte pitch-black stealth armor with crimson laser edges.
8. ⚡ **Matrix Emerald**: Phosphor terminal green data glyphs and cyber alloy rim.

### 4. 🧠 Multi-Model AI Brain & Seamless Failover
Connect to free or premium AI providers with automatic instant failover:
- **Google Gemini**: `gemini-2.5-flash`, `gemini-2.5-pro`, `gemini-2.0-flash`, `gemini-1.5-flash`.
- **Groq Cloud (100% Free)**: `llama-3.3-70b-versatile`, `deepseek-r1-distill-llama-70b`, `qwen/qwen3.8-27b`, `llama-3.1-8b-instant`.
- **OpenRouter (Free Community)**: `meta-llama/llama-3.3-70b-instruct:free`, `deepseek/deepseek-r1:free`, `google/gemma-4-31b-it:free`.
- **Anthropic Claude**: `claude-3-7-sonnet-20250219`, `claude-3-5-sonnet-20241022`, `claude-3-5-haiku-20241022`.
- **OpenAI**: `gpt-4o`, `gpt-4o-mini`, `o3-mini`, `o1`.
- **Local LLM**: Connect directly to Ollama (`localhost:11434`) for 100% private, offline AI.

### 5. 🎙️ Realistic Human Voice Studio
- **Edge Neural TTS**: 100% free, zero-key, ultra-natural human voices (e.g., `Andrew Neural`, `Rachel Neural`, `Brian Neural`).
- **ElevenLabs API**: Optional integration for studio-grade voice cloning and emotional realism.
- **Intelligent Spoken Highlights**: NEXUS speaks natural concise summaries aloud while rendering full markdown in the chat window.

---

## 💻 Quick Start & Installation

### Prerequisites
- **OS**: Windows 10 or Windows 11 (64-bit)
- **Python**: Python 3.10 to 3.13

### 1. Clone & Set Up Environment
```bash
git clone https://github.com/Raiyan/NEXUS-AI-Companion.git
cd NEXUS-AI-Companion

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install required dependencies
pip install -r requirements.txt
```

### 2. Launch NEXUS
Double-click `run_nexus.bat` or run:
```bash
python launch.py
```
NEXUS will appear floating smoothly on your Windows desktop!

---

## 🛡️ Security Architecture

NEXUS enforces an **Absolute Permission-First** model:
- **Level 1 (Information Only)**: Read-only answers and guidance; desktop modifications strictly blocked.
- **Level 2 (Interactive Confirmation)**: Shows an approval modal dialog before any file change or app launch.
- **Level 3 (Autonomous Companion)**: Permitted safe operations run seamlessly.
- **System Blacklist**: Core system processes (`explorer.exe`, `svchost.exe`, `csrss.exe`, `lsass.exe`, `winlogon.exe`) can never be terminated.
- **Emergency STOP**: Global one-click red alert button immediately halts all operations.

---

## 📁 Repository Structure

```
NEXUS/
├── main.py                     # Primary desktop entry point & GUI loop
├── launch.py                   # Desktop session spawner
├── run_nexus.bat               # Windows double-click launcher
├── requirements.txt            # Dependency specification
├── LICENSE                     # MIT Open Source License
├── README.md                   # Project documentation
│
├── core/                       # Brain, AI & Automation Engine
│   ├── ai_manager.py           # Multi-provider routing & resilient failover
│   ├── document_processor.py   # PDF, code, and document text extraction
│   ├── desktop_tools.py        # Safe Windows automation & intent parser
│   ├── voice_engine.py         # Neural TTS & speech coordinator
│   ├── memory_manager.py       # SQLite memory & bond progression
│   ├── conversation.py         # Multi-turn chat session manager
│   └── providers/              # Gemini, Groq, OpenRouter, Claude, OpenAI
│
├── desktop/                    # Desktop GUI & Visual Rendering
│   ├── pet.py                  # Transparent pet window & physics
│   ├── pet_renderer.py         # Vector graphics (Habibi aviators, ghutra, fins)
│   ├── chat_window.py          # HUD chat window with attachment support
│   ├── dock_widget.py          # Mini taskbar quick dock
│   ├── context_menu.py         # Modern Windows 11 popup menu
│   └── tray.py                 # System tray presence
│
├── interface/                  # UI Dialogs & Styling
│   ├── control_panel.py        # Laptop Command Center & Hardware Monitor
│   ├── settings_dialog.py      # Comprehensive settings & key manager
│   ├── themes.py               # 8 Canonical character skins & palettes
│   └── permission_dialog.py    # Absolute permission confirmation modal
│
├── website/                    # Official NEXUS Showcase Landing Page
│   ├── index.html              # Interactive showcase page with live vector preview
│   ├── style.css               # Modern futuristic dark theme CSS
│   └── app.js                  # Vector simulation & interactive controls
│
└── tests/                      # Automated Test Suite (66 Unit Tests)
    ├── test_phase1.py          # Animations & physics tests
    ├── test_phase2.py          # Chat HUD & streaming tests
    ├── test_phase3.py          # AI providers & failover tests
    ├── test_phase4.py          # Voice STT & TTS tests
    ├── test_phase5_phase6.py   # Permission architecture & tool tests
    ├── test_memory_and_identity.py # Memory & creator attribution tests
    └── test_do_anything_and_habibi_appearance.py # New desktop actions & Habibi skin tests
```

---

## 🧪 Testing

To run the complete automated test suite:
```bash
python -m unittest discover -s tests -p "test_*.py"
```
All **66 unit tests** run in under 10 seconds.

---

## 👨‍💻 Author & Credits

- **Creator & Lead Engineer**: **Raiyan**
- **Architecture**: Native PySide6 / Python 3.13, Vector Math Canvas, Absolute Permission Framework.
- **License**: Released under the [MIT License](LICENSE).
