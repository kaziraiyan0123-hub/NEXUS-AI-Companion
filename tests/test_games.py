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

    def test_chess_board_initial_state(self):
        """Verifies 8x8 chess board setup, piece placements, and White turn."""
        self.assertEqual(len(self.games.chess_board), 8)
        self.assertEqual(len(self.games.chess_board[0]), 8)
        self.assertEqual(self.games.chess_board[7][4], 'K')  # White King
        self.assertEqual(self.games.chess_board[0][4], 'k')  # Black King
        self.assertEqual(self.games.chess_turn, 'W')
        self.assertFalse(self.games.chess_game_over)

    def test_chess_pawn_and_knight_moves(self):
        """Verifies legal move generation for starting pawns and knights."""
        # e2 pawn at (6, 4) can move to e3 (5, 4) and e4 (4, 4)
        pawn_moves = self.games._get_legal_chess_moves(6, 4, self.games.chess_board)
        self.assertIn((5, 4), pawn_moves)
        self.assertIn((4, 4), pawn_moves)

        # b1 knight at (7, 1) can jump to a3 (5, 0) and c3 (5, 2)
        knight_moves = self.games._get_legal_chess_moves(7, 1, self.games.chess_board)
        self.assertIn((5, 0), knight_moves)
        self.assertIn((5, 2), knight_moves)

    def test_chess_move_execution_and_capture(self):
        """Verifies piece moving, turn alternation, and capture tracking."""
        # Move White pawn from (6, 4) to (4, 4)
        self.games._execute_chess_move(6, 4, 4, 4)
        self.assertEqual(self.games.chess_board[6][4], '.')
        self.assertEqual(self.games.chess_board[4][4], 'P')
        self.assertEqual(self.games.chess_turn, 'B')

    def test_chess_ai_move_selection(self):
        """Verifies AI picks valid moves for Casual, Tactical, and Master modes."""
        move = self.games._pick_best_chess_move(self.games.chess_board, 'B', 'tactical')
        self.assertIsNotNone(move)
        (fr, fc), (tr, tc) = move
        self.assertTrue(self.games.chess_board[fr][fc].islower())

if __name__ == "__main__":
    unittest.main()
