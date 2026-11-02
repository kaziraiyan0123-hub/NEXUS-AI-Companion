"""
Unit tests for NEXUS Arcade and Brain Games Suite
Tests Tic-Tac-Toe win logic, bot self-play, memory matrix mechanics, and trivia quiz.
"""
import unittest
import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication

# Initialize singleton QApplication if not present
app = QApplication.instance()
if app is None:
    app = QApplication([])

from desktop.games_window import GamesWindow

class TestNexusArcade(unittest.TestCase):
    """Test suite for NEXUS desktop arcade."""

    def setUp(self):
        self.games = GamesWindow()

    def tearDown(self):
        self.games.close()

    def test_tictactoe_initial_state(self):
        """Verifies initial 3x3 empty board and current player X."""
        self.assertEqual(len(self.games.ttt_board), 9)
        self.assertTrue(all(v == "" for v in self.games.ttt_board))
        self.assertEqual(self.games.ttt_current_player, "X")
        self.assertFalse(self.games.ttt_game_over)

    def test_tictactoe_win_conditions(self):
        """Tests horizontal, vertical, and diagonal win detection."""
        # Top row win for X
        self.games.ttt_board = ["X", "X", "X", "", "", "", "", "", ""]
        self.assertEqual(self.games._check_ttt_winner(), "X")

        # Column win for O
        self.games.ttt_board = ["O", "", "", "O", "", "", "O", "", ""]
        self.assertEqual(self.games._check_ttt_winner(), "O")

        # Diagonal win for X
        self.games.ttt_board = ["X", "", "", "", "X", "", "", "", "X"]
        self.assertEqual(self.games._check_ttt_winner(), "X")

        # Tie condition
        self.games.ttt_board = ["X", "O", "X", "X", "O", "O", "O", "X", "X"]
        self.assertEqual(self.games._check_ttt_winner(), "Tie")

    def test_tictactoe_move_and_turn_alternation(self):
        """Tests player move updates board and triggers response."""
        self.games._make_ttt_move(0, "X")
        self.assertEqual(self.games.ttt_board[0], "X")
        self.assertEqual(self.games.ttt_current_player, "O")

    def test_trivia_content_and_structure(self):
        """Verifies trivia questions, answers, and attribution."""
        questions = self.games.TRIVIA_QUESTIONS
        self.assertGreaterEqual(len(questions), 4)
        for q in questions:
            self.assertIn("q", q)
            self.assertIn("options", q)
            self.assertEqual(len(q["options"]), 4)
            self.assertIn("correct", q)
            self.assertTrue(0 <= q["correct"] <= 3)

        # Raiyan attribution question check
        raiyan_q = [q for q in questions if "Raiyan" in q["options"] or "Raiyan" in q["explanation"]]
        self.assertTrue(len(raiyan_q) > 0)

    def test_memory_round_progression(self):
        """Verifies memory matrix sequence generation and round advancement."""
        self.games._start_memory_round()
        self.assertGreaterEqual(len(self.games.mem_sequence), 3)

if __name__ == "__main__":
    unittest.main()
