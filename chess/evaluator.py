"""
Author: Sepehr Bayat | Open Source Chess MVP

Evaluator class for calculating move quality scores (0-100).
"""

from typing import Tuple
from chess.constants import PIECE_VALUES


class Evaluator:
    """Evaluates chess positions and moves using heuristic functions."""
    
    def __init__(self):
        """Initialize the evaluator."""
        self.piece_values = PIECE_VALUES
    
    def evaluate_move(self, board, move: Tuple[Tuple[int, int], Tuple[int, int]], 
                     color: str) -> int:
        """
        Evaluate a move and return a score from 0-100.
        
        Args:
            board: Board instance before the move
            move: ((start_row, start_col), (end_row, end_col))
            color: Color of the player making the move
            
        Returns:
            Score from 0-100 (higher is better for the player)
        """
        start, end = move
        start_row, start_col = start
        end_row, end_col = end
        
        # Create a copy of the board to evaluate the move
        temp_board = board.copy()
        piece = temp_board.get_piece(start_row, start_col)
        if piece is None:
            return 50  # Neutral score if invalid
        
        # A friendly piece on the destination means Chess960 castling
        # (king onto its own rook), not a capture
        captured_piece = temp_board.get_piece(end_row, end_col)
        if captured_piece is not None and captured_piece.color == piece.color:
            captured_piece = None
        
        # Make the move using the real move logic so castling (including
        # the rook relocation), en passant, and promotion are all applied
        temp_board.current_turn = piece.color
        if not temp_board.make_move(start, end):
            return 50  # Neutral score if invalid
        
        # Calculate base position evaluation
        position_score = self.evaluate_position(temp_board, color)
        
        # Calculate material gain/loss from the move
        material_score = 0
        if captured_piece:
            material_score = self.piece_values.get(captured_piece.piece_type, 0) * 10
        
        # Check bonus (putting opponent in check)
        check_bonus = 0
        opponent_color = 'black' if color == 'white' else 'white'
        if temp_board.is_in_check(opponent_color):
            check_bonus = 15
        
        # Center control bonus
        center_bonus = 0
        center_squares = [(3, 3), (3, 4), (4, 3), (4, 4)]
        if (end_row, end_col) in center_squares:
            center_bonus = 5
        
        # Piece activity (mobility)
        mobility_score = self._calculate_mobility(temp_board, color) * 2
        
        # Combine scores
        raw_score = position_score + material_score + check_bonus + center_bonus + mobility_score
        
        # Normalize to 0-100 scale
        # Base position is around 50, material can add/subtract up to 90 points
        # Check adds up to 15, center adds up to 5, mobility adds up to 20
        # So range is roughly -40 to 180, normalize to 0-100
        normalized_score = max(0, min(100, 50 + (raw_score - 50) * 0.5))
        
        return int(normalized_score)
    
    def evaluate_position(self, board, color: str) -> float:
        """
        Evaluate the overall position for a given color.
        
        Args:
            board: Board instance
            color: 'white' or 'black'
            
        Returns:
            Position evaluation score
        """
        material_balance = self.calculate_material_balance(board, color)
        position_score = self.calculate_position_score(board, color)
        
        return material_balance + position_score
    
    def calculate_material_balance(self, board, color: str) -> float:
        """
        Calculate material balance (piece values).
        
        Args:
            board: Board instance
            color: 'white' or 'black'
            
        Returns:
            Material score (positive is better for the color)
        """
        my_material = 0
        opponent_material = 0
        opponent_color = 'black' if color == 'white' else 'white'
        
        for row in range(8):
            for col in range(8):
                piece = board.get_piece(row, col)
                if piece:
                    value = self.piece_values.get(piece.piece_type, 0)
                    if piece.color == color:
                        my_material += value
                    else:
                        opponent_material += value
        
        # Return difference (positive means advantage)
        return (my_material - opponent_material) * 2
    
    def calculate_position_score(self, board, color: str) -> float:
        """
        Calculate position quality (center control, piece activity).
        
        Args:
            board: Board instance
            color: 'white' or 'black'
            
        Returns:
            Position score
        """
        score = 0
        
        # Center control bonus
        center_squares = [(3, 3), (3, 4), (4, 3), (4, 4)]
        extended_center = [(2, 2), (2, 3), (2, 4), (2, 5),
                          (3, 2), (3, 5), (4, 2), (4, 5),
                          (5, 2), (5, 3), (5, 4), (5, 5)]
        
        for row in range(8):
            for col in range(8):
                piece = board.get_piece(row, col)
                if piece and piece.color == color:
                    # Center control
                    if (row, col) in center_squares:
                        score += 2
                    elif (row, col) in extended_center:
                        score += 1
                    
                    # Piece activity (number of moves available)
                    moves = piece.get_valid_moves(board)
                    score += len(moves) * 0.5
        
        return score
    
    def _calculate_mobility(self, board, color: str) -> int:
        """
        Calculate piece mobility (number of legal moves).
        
        Args:
            board: Board instance
            color: 'white' or 'black'
            
        Returns:
            Mobility score
        """
        total_moves = 0
        for row in range(8):
            for col in range(8):
                piece = board.get_piece(row, col)
                if piece and piece.color == color:
                    moves = piece.get_valid_moves(board)
                    total_moves += len(moves)
        
        return total_moves

