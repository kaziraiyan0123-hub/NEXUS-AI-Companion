"""
NEXUS Desktop Arcade & Brain Games Suite
Includes:
1. Tic-Tac-Toe (Player vs Companion & Autonomous Bot Self-Play Mode)
2. Memory Matrix (Sequence Recall Cognitive Game & Bot Self-Play)
3. AI Brain Trivia & Riddles Challenge
Includes autonomous idle mode where the bot plays by itself, reacts with emotes,
and accumulates idle XP for the player!
"""
import random
import logging
from typing import List, Optional

from PySide6.QtCore import Qt, QPoint, QTimer, Signal
from PySide6.QtGui import QFont, QCursor, QColor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGridLayout, QTabWidget, QFrame, QProgressBar, QMessageBox
)

from config.settings import get_settings

logger = logging.getLogger("NEXUS.Games")


class GamesWindow(QWidget):
    """Arcade and Brain Games dialog for NEXUS desktop companion."""

    xp_earned = Signal(int, str)  # (xp_amount, reason)

    def __init__(self, pet_controller=None, parent=None):
        super().__init__(parent)
        self.pet_controller = pet_controller
        self.settings = get_settings()
        self.drag_pos = QPoint()

        self._setup_window()
        self._build_ui()

    def _setup_window(self):
        self.setWindowTitle("NEXUS Arcade & Brain Games")
        self.resize(520, 560)
        self.setMinimumSize(480, 520)
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.WindowCloseButtonHint
        )
        self.setStyleSheet("""
            QWidget {
                background-color: #0c1017;
                color: #e2e8f0;
                font-family: 'Segoe UI', system-ui, sans-serif;
            }
            QTabWidget::pane {
                border: 1px solid #1e293b;
                background: #0f172a;
                border-radius: 12px;
                padding: 10px;
            }
            QTabBar::tab {
                background: #1e293b;
                color: #94a3b8;
                padding: 8px 18px;
                margin-right: 4px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: 600;
                font-size: 13px;
            }
            QTabBar::tab:selected {
                background: #0284c7;
                color: #ffffff;
            }
            QPushButton {
                background: #1e293b;
                border: 1px solid #334155;
                border-radius: 8px;
                color: #f1f5f9;
                font-weight: 600;
                padding: 8px 14px;
            }
            QPushButton:hover {
                background: #334155;
                border-color: #38bdf8;
            }
            QPushButton:pressed {
                background: #0284c7;
            }
            QProgressBar {
                background: #1e293b;
                border-radius: 6px;
                height: 10px;
                text-align: center;
                font-size: 10px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #38bdf8, stop:1 #0284c7);
                border-radius: 6px;
            }
        """)

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 14, 16, 16)
        main_layout.setSpacing(12)

        # Header with Title and XP summary
        header_layout = QHBoxLayout()
        title_lbl = QLabel("🎮 NEXUS Arcade & Brain Lab")
        title_lbl.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        title_lbl.setStyleSheet("color: #38bdf8;")
        header_layout.addWidget(title_lbl)

        header_layout.addStretch()

        self.xp_badge = QLabel("✨ +0 XP Today")
        self.xp_badge.setStyleSheet("""
            background: rgba(56, 189, 248, 0.15);
            border: 1px solid #38bdf8;
            border-radius: 12px;
            padding: 4px 10px;
            font-size: 12px;
            font-weight: bold;
            color: #38bdf8;
        """)
        header_layout.addWidget(self.xp_badge)
        main_layout.addLayout(header_layout)

        # Tab widget for games
        tabs = QTabWidget()
        tabs.addTab(self._build_tictactoe_tab(), "❌ Tic-Tac-Toe")
        tabs.addTab(self._build_memory_tab(), "🧠 Memory Matrix")
        tabs.addTab(self._build_trivia_tab(), "⚡ AI Trivia Quiz")
        main_layout.addWidget(tabs)

    # -------------------------------------------------------------
    # 1. Tic-Tac-Toe Game
    # -------------------------------------------------------------
    def _build_tictactoe_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)

        # Mode controls & Bot Self-Play toggle
        top_bar = QHBoxLayout()
        self.ttt_status_lbl = QLabel("Your Turn! Tap a square to play X.")
        self.ttt_status_lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        self.ttt_status_lbl.setStyleSheet("color: #f8fafc;")
        top_bar.addWidget(self.ttt_status_lbl)

        top_bar.addStretch()

        self.ttt_self_play_btn = QPushButton("🤖 Bot Self-Play: OFF")
        self.ttt_self_play_btn.setCheckable(True)
        self.ttt_self_play_btn.clicked.connect(self._toggle_ttt_self_play)
        top_bar.addWidget(self.ttt_self_play_btn)

        reset_btn = QPushButton("🔄 Reset")
        reset_btn.clicked.connect(self._reset_ttt)
        top_bar.addWidget(reset_btn)
        layout.addLayout(top_bar)

        # 3x3 Grid
        grid_frame = QFrame()
        grid_frame.setStyleSheet("background: #090d16; border-radius: 10px; padding: 8px;")
        grid_layout = QGridLayout(grid_frame)
        grid_layout.setSpacing(8)

        self.ttt_buttons: List[QPushButton] = []
        self.ttt_board = [""] * 9
        self.ttt_current_player = "X"
        self.ttt_game_over = False
        self.ttt_self_play_active = False

        for i in range(9):
            btn = QPushButton("")
            btn.setFixedSize(90, 90)
            btn.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
            btn.setStyleSheet("""
                QPushButton {
                    background: #1e293b;
                    border: 2px solid #334155;
                    border-radius: 8px;
                    color: #38bdf8;
                }
                QPushButton:hover {
                    background: #334155;
                    border-color: #38bdf8;
                }
            """)
            btn.clicked.connect(lambda _, idx=i: self._on_ttt_click(idx))
            self.ttt_buttons.append(btn)
            grid_layout.addWidget(btn, i // 3, i % 3)

        layout.addWidget(grid_frame, alignment=Qt.AlignmentFlag.AlignCenter)

        # Bot speech / commentary banner
        self.ttt_dialogue_lbl = QLabel("NEXUS: 'Let's see if you can outsmart my neural net!'")
        self.ttt_dialogue_lbl.setStyleSheet("color: #94a3b8; font-style: italic; font-size: 11px;")
        self.ttt_dialogue_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.ttt_dialogue_lbl)

        self.ttt_timer = QTimer(self)
        self.ttt_timer.setInterval(900)
        self.ttt_timer.timeout.connect(self._ttt_self_play_step)

        return widget

    def _on_ttt_click(self, idx: int):
        if self.ttt_game_over or self.ttt_board[idx] != "":
            return

        self._make_ttt_move(idx, self.ttt_current_player)
        if not self.ttt_game_over:
            # Pet turn
            self.ttt_status_lbl.setText("NEXUS is calculating move...")
            QTimer.singleShot(400, self._ttt_pet_move)

    def _make_ttt_move(self, idx: int, player: str):
        self.ttt_board[idx] = player
        btn = self.ttt_buttons[idx]
        btn.setText(player)
        btn.setStyleSheet(f"""
            background: #1e293b;
            border: 2px solid {'#38bdf8' if player == 'X' else '#f59e0b'};
            border-radius: 8px;
            color: {'#38bdf8' if player == 'X' else '#f59e0b'};
        """)

        # Check win
        winner = self._check_ttt_winner()
        if winner:
            self.ttt_game_over = True
            if self.ttt_timer.isActive():
                self.ttt_timer.stop()
            if winner == "Tie":
                self.ttt_status_lbl.setText("🤝 Great game! It's a draw!")
                self.ttt_dialogue_lbl.setText("NEXUS: 'Stalemate! Our neural paths are equally matched.'")
                self._award_xp(10, "Tic-Tac-Toe Tie")
            elif winner == "X":
                self.ttt_status_lbl.setText("🏆 Player X Wins!")
                self.ttt_dialogue_lbl.setText("NEXUS: 'Incredible move! You beat my algorithm!'")
                self._award_xp(25, "Tic-Tac-Toe Victory")
            else:
                self.ttt_status_lbl.setText("🤖 NEXUS Wins!")
                self.ttt_dialogue_lbl.setText("NEXUS: 'Three in a row! Better luck next round!'")
                self._award_xp(15, "Tic-Tac-Toe Match")
            return

        self.ttt_current_player = "O" if player == "X" else "X"

    def _ttt_pet_move(self):
        if self.ttt_game_over:
            return

        empty = [i for i, v in enumerate(self.ttt_board) if v == ""]
        if not empty:
            return

        # Check winning or blocking moves
        move = None
        for test_player in ["O", "X"]:
            for idx in empty:
                self.ttt_board[idx] = test_player
                if self._check_ttt_winner() == test_player:
                    move = idx
                    self.ttt_board[idx] = ""
                    break
                self.ttt_board[idx] = ""
            if move is not None:
                break

        if move is None:
            # Prefer center, then corners, then random
            if 4 in empty and random.random() < 0.7:
                move = 4
            else:
                move = random.choice(empty)

        comments = [
            "Analyzing flanking vectors...",
            "Taking strategic coordinates!",
            "I see what you did there!",
            "Counter-maneuver initiated!"
        ]
        self.ttt_dialogue_lbl.setText(f"NEXUS: '{random.choice(comments)}'")
        self._make_ttt_move(move, "O")
        if not self.ttt_game_over:
            self.ttt_status_lbl.setText("Your Turn! Place X.")

    def _toggle_ttt_self_play(self):
        self.ttt_self_play_active = self.ttt_self_play_btn.isChecked()
        if self.ttt_self_play_active:
            self.ttt_self_play_btn.setText("🤖 Bot Self-Play: ON")
            self.ttt_self_play_btn.setStyleSheet("background: #0284c7; color: white;")
            if self.ttt_game_over:
                self._reset_ttt()
            self.ttt_timer.start()
        else:
            self.ttt_self_play_btn.setText("🤖 Bot Self-Play: OFF")
            self.ttt_self_play_btn.setStyleSheet("")
            self.ttt_timer.stop()

    def _ttt_self_play_step(self):
        if self.ttt_game_over:
            # Auto-restart in self-play mode after brief pause
            self._reset_ttt()
            return

        empty = [i for i, v in enumerate(self.ttt_board) if v == ""]
        if not empty:
            return

        # Bot picks a smart or playful move for current player
        move = random.choice(empty)
        player = self.ttt_current_player
        self.ttt_dialogue_lbl.setText(
            f"NEXUS (Self-Play): 'Evaluating node {move} as player {player}...' "
        )
        self._make_ttt_move(move, player)

    def _check_ttt_winner(self) -> Optional[str]:
        lines = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],
            [0, 3, 6], [1, 4, 7], [2, 5, 8],
            [0, 4, 8], [2, 4, 6]
        ]
        for a, b, c in lines:
            if self.ttt_board[a] and self.ttt_board[a] == self.ttt_board[b] == self.ttt_board[c]:
                return self.ttt_board[a]
        if all(x != "" for x in self.ttt_board):
            return "Tie"
        return None

    def _reset_ttt(self):
        self.ttt_board = [""] * 9
        self.ttt_game_over = False
        self.ttt_current_player = "X"
        for btn in self.ttt_buttons:
            btn.setText("")
            btn.setStyleSheet("""
                QPushButton {
                    background: #1e293b;
                    border: 2px solid #334155;
                    border-radius: 8px;
                    color: #38bdf8;
                }
                QPushButton:hover {
                    background: #334155;
                    border-color: #38bdf8;
                }
            """)
        self.ttt_status_lbl.setText("Fresh Board! Tap to play X.")
        self.ttt_dialogue_lbl.setText("NEXUS: 'New board initialized. Show me your best!'")

    # -------------------------------------------------------------
    # 2. Memory Matrix (Sequence Memory Challenge)
    # -------------------------------------------------------------
    def _build_memory_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)

        top_bar = QHBoxLayout()
        self.mem_status_lbl = QLabel("Watch the glowing pattern, then repeat it!")
        self.mem_status_lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        top_bar.addWidget(self.mem_status_lbl)

        top_bar.addStretch()

        self.mem_self_play_btn = QPushButton("🤖 Bot Self-Play: OFF")
        self.mem_self_play_btn.setCheckable(True)
        self.mem_self_play_btn.clicked.connect(self._toggle_mem_self_play)
        top_bar.addWidget(self.mem_self_play_btn)

        start_btn = QPushButton("▶️ Start Round")
        start_btn.clicked.connect(self._start_memory_round)
        top_bar.addWidget(start_btn)
        layout.addLayout(top_bar)

        # 4 Colored Pads Grid
        pad_frame = QFrame()
        pad_frame.setStyleSheet("background: #090d16; border-radius: 10px; padding: 10px;")
        pad_layout = QGridLayout(pad_frame)
        pad_layout.setSpacing(12)

        self.pad_colors = [
            ("#0284c7", "#38bdf8", "Cyan Pulse"),
            ("#b45309", "#f59e0b", "Amber Flare"),
            ("#047857", "#10b981", "Emerald Matrix"),
            ("#7e22ce", "#c084fc", "Purple Void")
        ]
        self.mem_pads: List[QPushButton] = []
        for i in range(4):
            bg, active, name = self.pad_colors[i]
            btn = QPushButton(name)
            btn.setFixedSize(140, 110)
            btn.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {bg};
                    border: 2px solid {active};
                    border-radius: 10px;
                    color: white;
                }}
            """)
            btn.clicked.connect(lambda _, idx=i: self._on_memory_pad_click(idx))
            self.mem_pads.append(btn)
            pad_layout.addWidget(btn, i // 2, i % 2)

        layout.addWidget(pad_frame, alignment=Qt.AlignmentFlag.AlignCenter)

        self.mem_sequence: List[int] = []
        self.mem_player_index = 0
        self.mem_level = 1
        self.mem_playback_index = 0
        self.mem_accepting_input = False
        self.mem_self_play_active = False

        self.mem_playback_timer = QTimer(self)
        self.mem_playback_timer.setInterval(650)
        self.mem_playback_timer.timeout.connect(self._mem_playback_step)

        self.mem_dialogue_lbl = QLabel("NEXUS: 'Memory Matrix strengthens synaptic plasticity!'")
        self.mem_dialogue_lbl.setStyleSheet("color: #94a3b8; font-style: italic; font-size: 11px;")
        self.mem_dialogue_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.mem_dialogue_lbl)

        return widget

    def _start_memory_round(self):
        self.mem_accepting_input = False
        if not self.mem_sequence:
            self.mem_sequence = [random.randint(0, 3) for _ in range(3)]
        else:
            self.mem_sequence.append(random.randint(0, 3))

        self.mem_player_index = 0
        self.mem_playback_index = 0
        self.mem_status_lbl.setText(f"Sequence Level {len(self.mem_sequence)}: Memorizing...")
        self.mem_dialogue_lbl.setText("NEXUS: 'Synchronizing buffer sequence...'")
        self.mem_playback_timer.start()

    def _mem_playback_step(self):
        if self.mem_playback_index < len(self.mem_sequence):
            pad_idx = self.mem_sequence[self.mem_playback_index]
            self._flash_pad(pad_idx)
            self.mem_playback_index += 1
        else:
            self.mem_playback_timer.stop()
            self.mem_status_lbl.setText("Your Turn! Repeat the sequence.")
            self.mem_dialogue_lbl.setText("NEXUS: 'Awaiting your recall entry!'")
            self.mem_accepting_input = True

            if self.mem_self_play_active:
                QTimer.singleShot(500, self._mem_self_play_solve)

    def _flash_pad(self, idx: int):
        btn = self.mem_pads[idx]
        btn.setStyleSheet("background: #ffffff; color: #000000; border: 2px solid #ffffff;")
        QTimer.singleShot(350, lambda: self._restore_pad(idx))

    def _restore_pad(self, idx: int):
        bg, active, _ = self.pad_colors[idx]
        self.mem_pads[idx].setStyleSheet(f"""
            QPushButton {{
                background: {bg};
                border: 2px solid {active};
                border-radius: 10px;
                color: white;
            }}
        """)

    def _on_memory_pad_click(self, idx: int):
        if not self.mem_accepting_input:
            return

        self._flash_pad(idx)
        expected = self.mem_sequence[self.mem_player_index]
        if idx == expected:
            self.mem_player_index += 1
            if self.mem_player_index == len(self.mem_sequence):
                self.mem_accepting_input = False
                self.mem_status_lbl.setText(f"🎉 Round Complete! Level {len(self.mem_sequence)} Cleared!")
                self.mem_dialogue_lbl.setText("NEXUS: 'Flawless recall! Upgrading sequence length...'")
                self._award_xp(20, f"Memory Level {len(self.mem_sequence)}")
                QTimer.singleShot(1200, self._start_memory_round)
        else:
            self.mem_accepting_input = False
            self.mem_status_lbl.setText("❌ Pattern Missed! Tap 'Start Round' to retry.")
            self.mem_dialogue_lbl.setText("NEXUS: 'Good attempt! Let's calibrate and try again.'")
            self.mem_sequence = []

    def _toggle_mem_self_play(self):
        self.mem_self_play_active = self.mem_self_play_btn.isChecked()
        if self.mem_self_play_active:
            self.mem_self_play_btn.setText("🤖 Bot Self-Play: ON")
            self.mem_self_play_btn.setStyleSheet("background: #0284c7; color: white;")
            self._start_memory_round()
        else:
            self.mem_self_play_btn.setText("🤖 Bot Self-Play: OFF")
            self.mem_self_play_btn.setStyleSheet("")

    def _mem_self_play_solve(self):
        if not self.mem_self_play_active or not self.mem_sequence:
            return

        def click_step(step_idx):
            if not self.mem_self_play_active:
                return
            if step_idx < len(self.mem_sequence):
                target = self.mem_sequence[step_idx]
                self._on_memory_pad_click(target)
                QTimer.singleShot(400, lambda: click_step(step_idx + 1))

        click_step(0)

    # -------------------------------------------------------------
    # 3. AI Brain Trivia Quiz
    # -------------------------------------------------------------
    TRIVIA_QUESTIONS = [
        {
            "q": "Which gas is released by green plants during photosynthesis?",
            "options": ["Oxygen (O2)", "Carbon Dioxide (CO2)", "Methane (CH4)", "Helium (He)"],
            "correct": 0,
            "explanation": "Plants take in CO2 and release Oxygen as a byproduct of the light reactions!"
        },
        {
            "q": "In Python, which built-in function returns the number of items in an object?",
            "options": ["count()", "size()", "len()", "length()"],
            "correct": 2,
            "explanation": "len() returns the length (the number of items) of an object."
        },
        {
            "q": "What is the universal gravitational constant symbolized by in Newton's gravity law?",
            "options": ["g", "G", "C", "h"],
            "correct": 1,
            "explanation": "Big 'G' represents the universal gravitational constant (approx 6.674×10^-11 m³/kg/s²)."
        },
        {
            "q": "Who coded the NEXUS AI Companion architecture?",
            "options": ["Raiyan", "Anonymous Corporation", "OpenAI", "NASA"],
            "correct": 0,
            "explanation": "Raiyan coded me! I am NEXUS, your personal autonomous AI companion."
        },
        {
            "q": "What is the fastest sorting algorithm on average for general purpose arrays?",
            "options": ["Bubble Sort", "Quick Sort / Timsort", "Selection Sort", "Bogo Sort"],
            "correct": 1,
            "explanation": "Quick Sort and Timsort operate at O(n log n) average time complexity."
        }
    ]

    def _build_trivia_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)

        top_bar = QHBoxLayout()
        self.trivia_status_lbl = QLabel("Test your knowledge and earn XP!")
        self.trivia_status_lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        top_bar.addWidget(self.trivia_status_lbl)

        top_bar.addStretch()

        self.trivia_self_play_btn = QPushButton("🤖 Bot Auto-Answer: OFF")
        self.trivia_self_play_btn.setCheckable(True)
        self.trivia_self_play_btn.clicked.connect(self._toggle_trivia_self_play)
        top_bar.addWidget(self.trivia_self_play_btn)

        next_btn = QPushButton("⏭️ Next Question")
        next_btn.clicked.connect(self._next_trivia_question)
        top_bar.addWidget(next_btn)
        layout.addLayout(top_bar)

        # Question Card
        card = QFrame()
        card.setStyleSheet("background: #090d16; border: 1px solid #1e293b; border-radius: 10px; padding: 14px;")
        card_layout = QVBoxLayout(card)

        self.trivia_q_lbl = QLabel("Question Loading...")
        self.trivia_q_lbl.setWordWrap(True)
        self.trivia_q_lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        self.trivia_q_lbl.setStyleSheet("color: #38bdf8; margin-bottom: 10px;")
        card_layout.addWidget(self.trivia_q_lbl)

        self.trivia_buttons: List[QPushButton] = []
        for i in range(4):
            btn = QPushButton("")
            btn.setFont(QFont("Segoe UI", 11))
            btn.setStyleSheet("""
                QPushButton {
                    background: #1e293b;
                    border: 1px solid #334155;
                    border-radius: 8px;
                    padding: 8px;
                    text-align: left;
                }
                QPushButton:hover {
                    background: #334155;
                    border-color: #38bdf8;
                }
            """)
            btn.clicked.connect(lambda _, opt_idx=i: self._on_trivia_answer(opt_idx))
            self.trivia_buttons.append(btn)
            card_layout.addWidget(btn)

        self.trivia_explain_lbl = QLabel("")
        self.trivia_explain_lbl.setWordWrap(True)
        self.trivia_explain_lbl.setStyleSheet("color: #34d399; font-size: 11px; margin-top: 6px;")
        card_layout.addWidget(self.trivia_explain_lbl)

        layout.addWidget(card)

        self.curr_trivia_idx = 0
        self.trivia_answered = False
        self.trivia_self_play_active = False

        self._load_trivia_question(0)
        return widget

    def _load_trivia_question(self, idx: int):
        self.curr_trivia_idx = idx % len(self.TRIVIA_QUESTIONS)
        q = self.TRIVIA_QUESTIONS[self.curr_trivia_idx]
        self.trivia_q_lbl.setText(f"Q{self.curr_trivia_idx + 1}. {q['q']}")
        self.trivia_explain_lbl.setText("")
        self.trivia_answered = False

        for i, opt in enumerate(q["options"]):
            btn = self.trivia_buttons[i]
            btn.setText(f"{chr(65 + i)}) {opt}")
            btn.setStyleSheet("""
                QPushButton {
                    background: #1e293b;
                    border: 1px solid #334155;
                    border-radius: 8px;
                    padding: 8px;
                    text-align: left;
                    color: #f1f5f9;
                }
                QPushButton:hover {
                    background: #334155;
                    border-color: #38bdf8;
                }
            """)

        if self.trivia_self_play_active:
            QTimer.singleShot(900, self._trivia_bot_answer)

    def _on_trivia_answer(self, selected_idx: int):
        if self.trivia_answered:
            return
        self.trivia_answered = True
        q = self.TRIVIA_QUESTIONS[self.curr_trivia_idx]
        correct = q["correct"]

        for i, btn in enumerate(self.trivia_buttons):
            if i == correct:
                btn.setStyleSheet("background: #065f46; border: 2px solid #10b981; color: white;")
            elif i == selected_idx:
                btn.setStyleSheet("background: #7f1d1d; border: 2px solid #ef4444; color: white;")

        if selected_idx == correct:
            self.trivia_explain_lbl.setText(f"✅ Correct! {q['explanation']}")
            self._award_xp(20, "Trivia Correct Answer")
        else:
            self.trivia_explain_lbl.setText(f"❌ Not quite. {q['explanation']}")

    def _next_trivia_question(self):
        self._load_trivia_question(self.curr_trivia_idx + 1)

    def _toggle_trivia_self_play(self):
        self.trivia_self_play_active = self.trivia_self_play_btn.isChecked()
        if self.trivia_self_play_active:
            self.trivia_self_play_btn.setText("🤖 Bot Auto-Answer: ON")
            self.trivia_self_play_btn.setStyleSheet("background: #0284c7; color: white;")
            self._trivia_bot_answer()
        else:
            self.trivia_self_play_btn.setText("🤖 Bot Auto-Answer: OFF")
            self.trivia_self_play_btn.setStyleSheet("")

    def _trivia_bot_answer(self):
        if not self.trivia_self_play_active or self.trivia_answered:
            return
        q = self.TRIVIA_QUESTIONS[self.curr_trivia_idx]
        # Bot reasons and chooses correct answer 90% of the time
        choice = q["correct"] if random.random() < 0.9 else random.randint(0, 3)
        self._on_trivia_answer(choice)
        QTimer.singleShot(2500, self._next_trivia_question)

    def _award_xp(self, amount: int, reason: str):
        self.xp_badge.setText(f"✨ +{amount} XP ({reason})")
        self.xp_earned.emit(amount, reason)
        if self.pet_controller and hasattr(self.pet_controller, "character_state"):
            self.pet_controller.character_state.add_xp(amount)
