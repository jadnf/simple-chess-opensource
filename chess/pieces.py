"""
Author: Sepehr Bayat | Open Source Chess MVP

Piece classes: Base Piece class and all 6 piece subclasses with move validation.
"""

from typing import List, Tuple, Optional
from abc import ABC, abstractmethod


class Piece(ABC):
    """Base class for all chess pieces."""
    
    def __init__(self, color: str, row: int, col: int):
        """
        Initialize a chess piece.
        
        Args:
            color: 'white' or 'black'
            row: Row position (0-7)
            col: Column position (0-7)
        """
        self.color = color
        self.row = row
        self.col = col
        self.has_moved = False
        self.piece_type = self.__class__.__name__.lower()
    
    def get_position(self) -> Tuple[int, int]:
        """Get the current position of the piece."""
        return (self.row, self.col)
    
    def set_position(self, row: int, col: int):
        """Set the position of the piece."""
        self.row = row
        self.col = col
        self.has_moved = True
    
    @abstractmethod
    def get_valid_moves(self, board) -> List[Tuple[int, int]]:
        """
        Get all valid moves for this piece.
        
        Args:
            board: Board instance
            
        Returns:
            List of (row, col) tuples representing valid moves
        """
        pass
    
    @abstractmethod
    def get_symbol(self) -> str:
        """Get the Unicode symbol for this piece."""
        pass
    
    def copy(self):
        """Create a deep copy of this piece."""
        new_piece = self.__class__(self.color, self.row, self.col)
        new_piece.has_moved = self.has_moved
        return new_piece
    
    def __repr__(self):
        return f"{self.color.capitalize()} {self.piece_type.capitalize()} at ({self.row}, {self.col})"


class Pawn(Piece):
    """Pawn piece with forward movement and diagonal capture."""
    
    def get_valid_moves(self, board) -> List[Tuple[int, int]]:
        """Get valid moves for a pawn."""
        moves = []
        direction = -1 if self.color == 'white' else 1
        start_row = 6 if self.color == 'white' else 1
        
        # Forward move (one square)
        new_row = self.row + direction
        if 0 <= new_row < 8 and board.get_piece(new_row, self.col) is None:
            moves.append((new_row, self.col))
            
            # Double move from starting position
            if self.row == start_row:
                new_row2 = self.row + (2 * direction)
                if 0 <= new_row2 < 8 and board.get_piece(new_row2, self.col) is None:
                    moves.append((new_row2, self.col))
        
        # Diagonal captures
        for col_offset in [-1, 1]:
            new_col = self.col + col_offset
            new_row = self.row + direction
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target = board.get_piece(new_row, new_col)
                if target is not None and target.color != self.color:
                    moves.append((new_row, new_col))
        
        # En passant
        if board.en_passant_target:
            ep_row, ep_col = board.en_passant_target
            if (ep_row == self.row + direction and 
                abs(ep_col - self.col) == 1):
                moves.append((ep_row, ep_col))
        
        # Filter out moves that would leave king in check
        valid_moves = []
        for move in moves:
            if board.is_move_safe(self.row, self.col, move[0], move[1], self.color):
                valid_moves.append(move)
        
        return valid_moves
    
    def get_symbol(self) -> str:
        """Get pawn Unicode symbol."""
        from chess.constants import PAWN_WHITE, PAWN_BLACK
        return PAWN_WHITE if self.color == 'white' else PAWN_BLACK


class Rook(Piece):
    """Rook piece with horizontal and vertical movement."""
    
    def get_valid_moves(self, board) -> List[Tuple[int, int]]:
        """Get valid moves for a rook."""
        moves = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # Right, Left, Down, Up
        
        for dr, dc in directions:
            for i in range(1, 8):
                new_row = self.row + (dr * i)
                new_col = self.col + (dc * i)
                
                if not (0 <= new_row < 8 and 0 <= new_col < 8):
                    break
                
                target = board.get_piece(new_row, new_col)
                if target is None:
                    moves.append((new_row, new_col))
                elif target.color != self.color:
                    moves.append((new_row, new_col))
                    break
                else:
                    break
        
        # Filter out moves that would leave king in check
        valid_moves = []
        for move in moves:
            if board.is_move_safe(self.row, self.col, move[0], move[1], self.color):
                valid_moves.append(move)
        
        return valid_moves
    
    def get_symbol(self) -> str:
        """Get rook Unicode symbol."""
        from chess.constants import ROOK_WHITE, ROOK_BLACK
        return ROOK_WHITE if self.color == 'white' else ROOK_BLACK


class Knight(Piece):
    """Knight piece with L-shaped movement."""
    
    def get_valid_moves(self, board) -> List[Tuple[int, int]]:
        """Get valid moves for a knight."""
        moves = []
        knight_moves = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]
        
        for dr, dc in knight_moves:
            new_row = self.row + dr
            new_col = self.col + dc
            
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target = board.get_piece(new_row, new_col)
                if target is None or target.color != self.color:
                    moves.append((new_row, new_col))
        
        # Filter out moves that would leave king in check
        valid_moves = []
        for move in moves:
            if board.is_move_safe(self.row, self.col, move[0], move[1], self.color):
                valid_moves.append(move)
        
        return valid_moves
    
    def get_symbol(self) -> str:
        """Get knight Unicode symbol."""
        from chess.constants import KNIGHT_WHITE, KNIGHT_BLACK
        return KNIGHT_WHITE if self.color == 'white' else KNIGHT_BLACK


class Bishop(Piece):
    """Bishop piece with diagonal movement."""
    
    def get_valid_moves(self, board) -> List[Tuple[int, int]]:
        """Get valid moves for a bishop."""
        moves = []
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]  # All diagonals
        
        for dr, dc in directions:
            for i in range(1, 8):
                new_row = self.row + (dr * i)
                new_col = self.col + (dc * i)
                
                if not (0 <= new_row < 8 and 0 <= new_col < 8):
                    break
                
                target = board.get_piece(new_row, new_col)
                if target is None:
                    moves.append((new_row, new_col))
                elif target.color != self.color:
                    moves.append((new_row, new_col))
                    break
                else:
                    break
        
        # Filter out moves that would leave king in check
        valid_moves = []
        for move in moves:
            if board.is_move_safe(self.row, self.col, move[0], move[1], self.color):
                valid_moves.append(move)
        
        return valid_moves
    
    def get_symbol(self) -> str:
        """Get bishop Unicode symbol."""
        from chess.constants import BISHOP_WHITE, BISHOP_BLACK
        return BISHOP_WHITE if self.color == 'white' else BISHOP_BLACK


class Queen(Piece):
    """Queen piece with combined rook and bishop movement."""
    
    def get_valid_moves(self, board) -> List[Tuple[int, int]]:
        """Get valid moves for a queen."""
        moves = []
        directions = [
            (0, 1), (0, -1), (1, 0), (-1, 0),  # Rook moves
            (1, 1), (1, -1), (-1, 1), (-1, -1)  # Bishop moves
        ]
        
        for dr, dc in directions:
            for i in range(1, 8):
                new_row = self.row + (dr * i)
                new_col = self.col + (dc * i)
                
                if not (0 <= new_row < 8 and 0 <= new_col < 8):
                    break
                
                target = board.get_piece(new_row, new_col)
                if target is None:
                    moves.append((new_row, new_col))
                elif target.color != self.color:
                    moves.append((new_row, new_col))
                    break
                else:
                    break
        
        # Filter out moves that would leave king in check
        valid_moves = []
        for move in moves:
            if board.is_move_safe(self.row, self.col, move[0], move[1], self.color):
                valid_moves.append(move)
        
        return valid_moves
    
    def get_symbol(self) -> str:
        """Get queen Unicode symbol."""
        from chess.constants import QUEEN_WHITE, QUEEN_BLACK
        return QUEEN_WHITE if self.color == 'white' else QUEEN_BLACK


class King(Piece):
    """King piece with one-square movement and castling."""
    
    def get_valid_moves(self, board) -> List[Tuple[int, int]]:
        """Get valid moves for a king."""
        moves = []
        king_moves = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
        
        for dr, dc in king_moves:
            new_row = self.row + dr
            new_col = self.col + dc
            
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target = board.get_piece(new_row, new_col)
                if target is None or target.color != self.color:
                    moves.append((new_row, new_col))
        
        # Castling
        castling_moves: List[Tuple[int, int]] = []
        if not self.has_moved and not board.is_in_check(self.color):
            if board.variant == 'chess960':
                # Chess960 castling is entered as the king moving onto its
                # own rook's square
                for rook_col in board.initial_rook_cols:
                    if self._can_castle_960(board, rook_col):
                        castling_moves.append((self.row, rook_col))
            else:
                # Kingside castling
                if self._can_castle_kingside(board):
                    moves.append((self.row, self.col + 2))
                # Queenside castling
                if self._can_castle_queenside(board):
                    moves.append((self.row, self.col - 2))
        
        # Filter out moves that would leave king in check
        valid_moves = []
        for move in moves:
            if board.is_move_safe(self.row, self.col, move[0], move[1], self.color):
                valid_moves.append(move)
        
        # Chess960 castling safety is fully verified in _can_castle_960;
        # is_move_safe cannot simulate the rook relocation (the king may even
        # land on the rook's starting square)
        valid_moves.extend(castling_moves)
        
        return valid_moves
    
    def _can_castle_960(self, board, rook_col: int) -> bool:
        """
        Check if Chess960 castling with the rook that started on rook_col
        is possible.
        
        Chess960 rules: the king and the castling rook must be unmoved;
        the king lands on the c-file (queenside) or g-file (kingside) and
        the rook on the d/f-file, regardless of starting columns. All
        squares between each piece's start and destination must be empty
        (except for the king and the castling rook themselves), and the
        king may not pass through or land on an attacked square.
        """
        rook = board.get_piece(self.row, rook_col)
        if (rook is None or rook.piece_type != 'rook' or
                rook.color != self.color or rook.has_moved):
            return False
        
        kingside = rook_col > self.col
        king_dest = 6 if kingside else 2
        rook_dest = 5 if kingside else 3
        
        # King's path (including destination) must be empty except for the
        # castling rook, which vacates its square
        king_path = self._path_cols(self.col, king_dest)
        for col in king_path:
            occupant = board.get_piece(self.row, col)
            if occupant is not None and occupant is not rook:
                return False
        
        # King may not pass through an attacked square (destination safety
        # is verified by simulating the full castling move below)
        for col in king_path[:-1]:
            if board.is_square_attacked(self.row, col, self.color):
                return False
        
        # Rook's path (including destination) must be empty except for the
        # king, which vacates its square
        for col in self._path_cols(rook_col, rook_dest):
            occupant = board.get_piece(self.row, col)
            if occupant is not None and occupant is not self:
                return False
        
        # Simulate the full castling move (king and rook) to verify the
        # king does not end up in check
        temp_board = board.copy()
        temp_king = temp_board.get_piece(self.row, self.col)
        temp_rook = temp_board.get_piece(self.row, rook_col)
        temp_board._execute_960_castle(temp_king, temp_rook)
        return not temp_board.is_in_check(self.color)
    
    @staticmethod
    def _path_cols(start_col: int, dest_col: int) -> List[int]:
        """Columns from start (exclusive) to destination (inclusive)."""
        if start_col == dest_col:
            return []
        step = 1 if dest_col > start_col else -1
        return list(range(start_col + step, dest_col + step, step))
    
    def _can_castle_kingside(self, board) -> bool:
        """Check if kingside castling is possible."""
        if self.col != 4:  # King must be on e-file
            return False
        
        rook_col = 7
        rook = board.get_piece(self.row, rook_col)
        if rook is None or rook.piece_type != 'rook' or rook.has_moved:
            return False
        
        # Check if squares between are empty
        if (board.get_piece(self.row, 5) is not None or 
            board.get_piece(self.row, 6) is not None):
            return False
        
        # Check if king would pass through check
        if (board.is_square_attacked(self.row, 5, self.color) or
            board.is_square_attacked(self.row, 6, self.color)):
            return False
        
        return True
    
    def _can_castle_queenside(self, board) -> bool:
        """Check if queenside castling is possible."""
        if self.col != 4:  # King must be on e-file
            return False
        
        rook_col = 0
        rook = board.get_piece(self.row, rook_col)
        if rook is None or rook.piece_type != 'rook' or rook.has_moved:
            return False
        
        # Check if squares between are empty
        if (board.get_piece(self.row, 1) is not None or 
            board.get_piece(self.row, 2) is not None or
            board.get_piece(self.row, 3) is not None):
            return False
        
        # Check if king would pass through check
        if (board.is_square_attacked(self.row, 2, self.color) or
            board.is_square_attacked(self.row, 3, self.color)):
            return False
        
        return True
    
    def get_symbol(self) -> str:
        """Get king Unicode symbol."""
        from chess.constants import KING_WHITE, KING_BLACK
        return KING_WHITE if self.color == 'white' else KING_BLACK

