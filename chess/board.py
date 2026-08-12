"""
Author: Sepehr Bayat | Open Source Chess MVP

Board class for managing the chess board state, moves, and game rules.
"""

import random
from typing import Optional, Tuple, List
from copy import deepcopy
from chess.pieces import Piece, Pawn, Rook, Knight, Bishop, Queen, King


class Board:
    """Chess board managing piece placement and game state."""
    
    def __init__(self, variant: str = 'standard'):
        """
        Initialize the board.
        
        Args:
            variant: 'standard' or 'chess960'
        """
        self.grid: List[List[Optional[Piece]]] = [[None for _ in range(8)] for _ in range(8)]
        self.current_turn = 'white'
        self.move_history: List[Tuple[Tuple[int, int], Tuple[int, int]]] = []
        self.en_passant_target: Optional[Tuple[int, int]] = None
        self.variant = variant
        self.initial_king_col = 4
        self.initial_rook_cols: Tuple[int, int] = (0, 7)
        # Cached king pieces per color, kept fresh lazily by is_in_check
        self._kings: dict = {'white': None, 'black': None}
        self._initialize_board()
    
    def _initialize_board(self):
        """Set up the initial chess board position."""
        # Place pawns
        for col in range(8):
            self.grid[6][col] = Pawn('white', 6, col)
            self.grid[1][col] = Pawn('black', 1, col)
        
        # Determine back rank piece order
        if self.variant == 'chess960':
            back_rank = self._generate_960_back_rank()
        else:
            back_rank = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        
        # Place back rank pieces (black mirrors white)
        for col, piece_class in enumerate(back_rank):
            self.grid[7][col] = piece_class('white', 7, col)
            self.grid[0][col] = piece_class('black', 0, col)
        
        # Record starting king/rook columns (needed for castling logic)
        self.initial_king_col = next(c for c, cls in enumerate(back_rank) if cls is King)
        self.initial_rook_cols = tuple(c for c, cls in enumerate(back_rank) if cls is Rook)
    
    @staticmethod
    def _generate_960_back_rank() -> List[type]:
        """
        Generate a random legal Chess960 back rank.
        
        Rules: bishops on opposite-colored squares, king between the rooks.
        
        Returns:
            List of 8 piece classes in column order
        """
        placement: List[Optional[type]] = [None] * 8
        
        # Bishops on opposite-colored squares
        placement[random.choice([0, 2, 4, 6])] = Bishop
        placement[random.choice([1, 3, 5, 7])] = Bishop
        
        empty = [c for c in range(8) if placement[c] is None]
        
        # Queen on a random remaining square
        queen_col = random.choice(empty)
        placement[queen_col] = Queen
        empty.remove(queen_col)
        
        # Knights on two random remaining squares
        for knight_col in random.sample(empty, 2):
            placement[knight_col] = Knight
            empty.remove(knight_col)
        
        # Remaining three squares (left to right): rook, king, rook —
        # this guarantees the king is between the rooks
        placement[empty[0]] = Rook
        placement[empty[1]] = King
        placement[empty[2]] = Rook
        
        return placement
    
    def get_piece(self, row: int, col: int) -> Optional[Piece]:
        """Get the piece at the given position."""
        if 0 <= row < 8 and 0 <= col < 8:
            return self.grid[row][col]
        return None
    
    def is_valid_position(self, row: int, col: int) -> bool:
        """Check if the position is valid (within board bounds)."""
        return 0 <= row < 8 and 0 <= col < 8
    
    def make_move(self, start: Tuple[int, int], end: Tuple[int, int]) -> bool:
        """
        Make a move on the board.
        
        Args:
            start: (row, col) of starting position
            end: (row, col) of ending position
            
        Returns:
            True if move was successful, False otherwise
        """
        start_row, start_col = start
        end_row, end_col = end
        
        piece = self.get_piece(start_row, start_col)
        if piece is None or piece.color != self.current_turn:
            return False
        
        # Check if move is valid
        valid_moves = piece.get_valid_moves(self)
        if end not in valid_moves:
            return False
        
        # Handle en passant capture
        captured_piece = self.get_piece(end_row, end_col)
        if (piece.piece_type == 'pawn' and 
            self.en_passant_target == (end_row, end_col) and
            captured_piece is None):
            # Capture the pawn that moved two squares
            direction = -1 if piece.color == 'white' else 1
            captured_pawn = self.get_piece(end_row - direction, end_col)
            if captured_pawn:
                self.grid[end_row - direction][end_col] = None
        
        # Handle castling
        if piece.piece_type == 'king':
            if self.variant == 'chess960':
                # Chess960 castling is represented as the king moving onto
                # its own rook's square
                target = self.get_piece(end_row, end_col)
                if (target is not None and target.piece_type == 'rook' and
                        target.color == piece.color):
                    self._execute_960_castle(piece, target)
                    self.en_passant_target = None
                    self.move_history.append((start, end))
                    self.current_turn = 'black' if self.current_turn == 'white' else 'white'
                    return True
            elif abs(end_col - start_col) == 2:
                if end_col > start_col:  # Kingside
                    rook = self.get_piece(start_row, 7)
                    self.grid[start_row][7] = None
                    self.grid[start_row][5] = rook
                    if rook:
                        rook.set_position(start_row, 5)
                else:  # Queenside
                    rook = self.get_piece(start_row, 0)
                    self.grid[start_row][0] = None
                    self.grid[start_row][3] = rook
                    if rook:
                        rook.set_position(start_row, 3)
        
        # Update en passant target
        self.en_passant_target = None
        if piece.piece_type == 'pawn' and abs(end_row - start_row) == 2:
            direction = -1 if piece.color == 'white' else 1
            self.en_passant_target = (start_row + direction, start_col)
        
        # Move the piece
        self.grid[start_row][start_col] = None
        self.grid[end_row][end_col] = piece
        piece.set_position(end_row, end_col)
        
        # Handle pawn promotion
        if piece.piece_type == 'pawn' and (end_row == 0 or end_row == 7):
            self.grid[end_row][end_col] = Queen(piece.color, end_row, end_col)
        
        # Record move
        self.move_history.append((start, end))
        
        # Switch turn
        self.current_turn = 'black' if self.current_turn == 'white' else 'white'
        
        return True
    
    def _execute_960_castle(self, king: Piece, rook: Piece):
        """
        Execute a Chess960 castling move: king lands on the c/g-file and the
        rook on the d/f-file, regardless of their starting columns.
        
        Args:
            king: The castling king
            rook: The rook the king is castling with
        """
        row = king.row
        kingside = rook.col > king.col
        king_dest = 6 if kingside else 2
        rook_dest = 5 if kingside else 3
        
        # Clear both origin squares first: either destination may overlap
        # the other piece's starting square
        self.grid[king.row][king.col] = None
        self.grid[rook.row][rook.col] = None
        
        self.grid[row][king_dest] = king
        king.set_position(row, king_dest)
        self.grid[row][rook_dest] = rook
        rook.set_position(row, rook_dest)
    
    def is_move_safe(self, start_row: int, start_col: int, 
                     end_row: int, end_col: int, color: str) -> bool:
        """
        Check if a move would leave the king in check.
        
        Args:
            start_row, start_col: Starting position
            end_row, end_col: Ending position
            color: Color of the piece making the move
            
        Returns:
            True if move is safe (doesn't leave king in check)
        """
        # Make the move in place, test for check, then undo. This runs for
        # every candidate move during move generation, so it must be cheap
        # (a full board copy here dominated the AI's search time).
        piece = self.grid[start_row][start_col]
        if piece is None:
            return False
        
        captured = self.grid[end_row][end_col]
        self.grid[start_row][start_col] = None
        self.grid[end_row][end_col] = piece
        piece.row, piece.col = end_row, end_col
        
        try:
            return not self.is_in_check(color)
        finally:
            self.grid[start_row][start_col] = piece
            self.grid[end_row][end_col] = captured
            piece.row, piece.col = start_row, start_col
    
    _KNIGHT_OFFSETS = ((-2, -1), (-2, 1), (-1, -2), (-1, 2),
                       (1, -2), (1, 2), (2, -1), (2, 1))
    _KING_OFFSETS = ((-1, -1), (-1, 0), (-1, 1), (0, -1),
                     (0, 1), (1, -1), (1, 0), (1, 1))
    _ORTHOGONAL_DIRS = ((0, 1), (0, -1), (1, 0), (-1, 0))
    _DIAGONAL_DIRS = ((1, 1), (1, -1), (-1, 1), (-1, -1))
    
    def is_square_attacked(self, row: int, col: int, by_color: str) -> bool:
        """
        Check if a square is attacked by opponent pieces.
        
        Works outward from the target square (reverse attack detection)
        instead of generating every opponent piece's move list, since this
        is one of the hottest functions in the AI search.
        
        Args:
            row, col: Square to check
            by_color: Color of the piece on the square (we check if opponent can attack)
            
        Returns:
            True if square is attacked by opponent
        """
        opponent_color = 'black' if by_color == 'white' else 'white'
        grid = self.grid
        
        # Knight attacks
        for dr, dc in self._KNIGHT_OFFSETS:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                piece = grid[r][c]
                if (piece is not None and piece.color == opponent_color and
                        piece.piece_type == 'knight'):
                    return True
        
        # Pawn attacks: an opponent pawn one row "behind" the square
        # (relative to its movement direction) on an adjacent file
        pawn_dir = -1 if opponent_color == 'white' else 1
        r = row - pawn_dir
        if 0 <= r < 8:
            for dc in (-1, 1):
                c = col + dc
                if 0 <= c < 8:
                    piece = grid[r][c]
                    if (piece is not None and piece.color == opponent_color and
                            piece.piece_type == 'pawn'):
                        return True
        
        # King attacks (adjacent squares)
        for dr, dc in self._KING_OFFSETS:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                piece = grid[r][c]
                if (piece is not None and piece.color == opponent_color and
                        piece.piece_type == 'king'):
                    return True
        
        # Sliding attacks: walk each ray until the first piece
        for dirs, attackers in ((self._ORTHOGONAL_DIRS, ('rook', 'queen')),
                                (self._DIAGONAL_DIRS, ('bishop', 'queen'))):
            for dr, dc in dirs:
                r, c = row + dr, col + dc
                while 0 <= r < 8 and 0 <= c < 8:
                    piece = grid[r][c]
                    if piece is not None:
                        if (piece.color == opponent_color and
                                piece.piece_type in attackers):
                            return True
                        break
                    r += dr
                    c += dc
        
        return False
    
    def is_in_check(self, color: str) -> bool:
        """
        Check if the king of the given color is in check.
        
        Args:
            color: 'white' or 'black'
            
        Returns:
            True if king is in check
        """
        # Use the cached king piece if it is still on the board at its
        # recorded square; otherwise re-scan (e.g. after a capture in a
        # speculative search line)
        king = self._kings.get(color)
        if king is None or self.grid[king.row][king.col] is not king:
            king = None
            for row_pieces in self.grid:
                for piece in row_pieces:
                    if (piece is not None and piece.piece_type == 'king' and
                            piece.color == color):
                        king = piece
                        break
                if king:
                    break
            self._kings[color] = king
        
        if king is None:
            return False
        
        # Check if any opponent piece can attack the king's square
        return self.is_square_attacked(king.row, king.col, color)
    
    def get_all_moves(self, color: str) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """
        Get all valid moves for a given color.
        
        Args:
            color: 'white' or 'black'
            
        Returns:
            List of ((start_row, start_col), (end_row, end_col)) tuples
        """
        moves = []
        for row in range(8):
            for col in range(8):
                piece = self.get_piece(row, col)
                if piece and piece.color == color:
                    valid_moves = piece.get_valid_moves(self)
                    for end_pos in valid_moves:
                        moves.append(((row, col), end_pos))
        return moves
    
    def is_checkmate(self, color: str) -> bool:
        """
        Check if the given color is in checkmate.
        
        Args:
            color: 'white' or 'black'
            
        Returns:
            True if checkmate
        """
        if not self.is_in_check(color):
            return False
        
        # Check if there are any valid moves
        moves = self.get_all_moves(color)
        return len(moves) == 0
    
    def is_stalemate(self, color: str) -> bool:
        """
        Check if the given color is in stalemate.
        
        Args:
            color: 'white' or 'black'
            
        Returns:
            True if stalemate
        """
        if self.is_in_check(color):
            return False
        
        # Check if there are any valid moves
        moves = self.get_all_moves(color)
        return len(moves) == 0
    
    def copy(self):
        """Create a deep copy of the board."""
        new_board = Board.__new__(Board)  # Create instance without calling __init__
        new_board.grid = [[None for _ in range(8)] for _ in range(8)]
        new_board._kings = {'white': None, 'black': None}
        
        # Copy all pieces
        for row in range(8):
            for col in range(8):
                piece = self.grid[row][col]
                if piece:
                    new_piece = piece.copy()
                    new_board.grid[row][col] = new_piece
                    if new_piece.piece_type == 'king':
                        new_board._kings[new_piece.color] = new_piece
        
        new_board.current_turn = self.current_turn
        # Copies are only used for speculative search/simulation, so the
        # move history (which is never read) is not carried over; copying
        # it made every copy slower as the game grew longer
        new_board.move_history = []
        new_board.en_passant_target = self.en_passant_target
        new_board.variant = self.variant
        new_board.initial_king_col = self.initial_king_col
        new_board.initial_rook_cols = self.initial_rook_cols
        
        return new_board

