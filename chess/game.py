"""
Author: Sepehr Bayat | Open Source Chess MVP

Game class for managing the main game loop, input handling, and rendering.
"""

import pygame
from typing import Optional, Tuple, List
from chess.board import Board
from chess.evaluator import Evaluator
from chess.ai import ChessAI
from chess.menu import GameMenu
from chess.piece_images import PieceImageLoader
from chess.constants import (
    SQUARE_SIZE, BOARD_SIZE, UI_PANEL_WIDTH, WINDOW_WIDTH, WINDOW_HEIGHT,
    LIGHT_SQUARE, DARK_SQUARE, HIGHLIGHT, VALID_MOVE_HIGHLIGHT,
    UI_BACKGROUND, UI_TEXT, WHITE, BLACK
)


class Game:
    """Main game class managing the chess game loop and rendering."""
    
    def __init__(self):
        """Initialize the game."""
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Chess MVP - Sepehr Bayat")
        
        # Initialize font
        self.font_large = pygame.font.Font(None, 36)
        self.font_medium = pygame.font.Font(None, 28)
        self.font_small = pygame.font.Font(None, 24)
        
        # Initialize piece image loader
        self.image_loader = PieceImageLoader()
        
        # Game state
        self.board = Board()
        self.evaluator = Evaluator()
        self.selected_piece: Optional[Tuple[int, int]] = None
        self.valid_moves: List[Tuple[int, int]] = []
        self.last_move_score: Optional[int] = None
        self.last_move_color: Optional[str] = None
        self.game_status: str = "Playing"
        
        # Game mode
        self.game_mode: Optional[str] = None
        self.variant: str = "standard"
        self.ai_white: Optional[ChessAI] = None
        self.ai_black: Optional[ChessAI] = None
        self.ai_thinking = False
        
        # Clock for FPS control
        self.clock = pygame.time.Clock()
    
    def show_menu(self) -> bool:
        """
        Show the game mode selection menu, then the variant selection menu.
        
        Returns:
            True if a mode and variant were selected, False if closed
        """
        menu = GameMenu(self.screen)
        selected_mode = menu.run()
        
        if not selected_mode:
            return False
        
        variant_menu = GameMenu(
            self.screen,
            subtitle="Select Chess Variant",
            options=[
                ("Standard Chess", "standard"),
                ("Chess960 / Fischer Random", "chess960")
            ]
        )
        selected_variant = variant_menu.run()
        
        if not selected_variant:
            return False
        
        self.game_mode = selected_mode
        self.variant = selected_variant
        self.board = Board(variant=selected_variant)
        self._setup_game_mode()
        return True
    
    def _setup_game_mode(self):
        """Set up AI players based on selected game mode."""
        if self.game_mode == "user_vs_user":
            self.ai_white = None
            self.ai_black = None
        elif self.game_mode == "user_vs_ai_white":
            self.ai_white = ChessAI(depth=3)
            self.ai_black = None
        elif self.game_mode == "user_vs_ai_black":
            self.ai_white = None
            self.ai_black = ChessAI(depth=3)
        elif self.game_mode == "ai_vs_ai":
            self.ai_white = ChessAI(depth=3)
            self.ai_black = ChessAI(depth=3)
    
    def _is_ai_turn(self) -> bool:
        """Check if it's currently an AI player's turn."""
        if self.board.current_turn == 'white' and self.ai_white:
            return True
        if self.board.current_turn == 'black' and self.ai_black:
            return True
        return False
    
    def _make_ai_move(self):
        """Make a move for the AI player."""
        if self.ai_thinking:
            return
        
        ai_player = self.ai_white if self.board.current_turn == 'white' else self.ai_black
        if not ai_player:
            return
        
        self.ai_thinking = True
        
        # Get best move from AI
        best_move = ai_player.get_best_move(self.board, self.board.current_turn)
        
        if best_move:
            start, end = best_move
            move_color = self.board.current_turn
            move = (start, end)
            
            # Evaluate the move
            self.last_move_color = move_color
            self.last_move_score = self.evaluator.evaluate_move(
                self.board, move, move_color
            )
            
            # Make the move
            self.board.make_move(start, end)
            self._update_game_status()
        
        self.ai_thinking = False
    
    def handle_click(self, pos: Tuple[int, int]):
        """
        Handle mouse click events.
        
        Args:
            pos: (x, y) mouse position
        """
        # Don't handle clicks if it's AI's turn
        if self._is_ai_turn():
            return
        
        x, y = pos
        
        # Check if click is on the board
        if x < BOARD_SIZE:
            col = x // SQUARE_SIZE
            row = y // SQUARE_SIZE
            
            piece = self.board.get_piece(row, col)
            
            # If a piece is selected
            if self.selected_piece:
                start_row, start_col = self.selected_piece
                
                # Check if clicking on a valid move
                if (row, col) in self.valid_moves:
                    # Get the color and evaluate move before making it
                    move_color = self.board.current_turn
                    move = ((start_row, start_col), (row, col))
                    
                    # Evaluate the move on current board state
                    self.last_move_color = move_color
                    self.last_move_score = self.evaluator.evaluate_move(
                        self.board, move, move_color
                    )
                    
                    # Make the move
                    self.board.make_move((start_row, start_col), (row, col))
                    
                    # Check game status
                    self._update_game_status()
                    
                    # Clear selection
                    self.selected_piece = None
                    self.valid_moves = []
                else:
                    # Select new piece or deselect
                    if piece and piece.color == self.board.current_turn:
                        self.selected_piece = (row, col)
                        self.valid_moves = piece.get_valid_moves(self.board)
                    else:
                        self.selected_piece = None
                        self.valid_moves = []
            else:
                # Select a piece
                if piece and piece.color == self.board.current_turn:
                    self.selected_piece = (row, col)
                    self.valid_moves = piece.get_valid_moves(self.board)
    
    def _update_game_status(self):
        """Update the game status (check, checkmate, stalemate)."""
        if self.board.is_checkmate('white'):
            self.game_status = "Checkmate! Black Wins"
        elif self.board.is_checkmate('black'):
            self.game_status = "Checkmate! White Wins"
        elif self.board.is_stalemate(self.board.current_turn):
            self.game_status = "Stalemate - Draw"
        elif self.board.is_in_check(self.board.current_turn):
            self.game_status = f"{self.board.current_turn.capitalize()} in Check"
        else:
            self.game_status = "Playing"
    
    def draw(self):
        """Draw the game board and UI."""
        self.screen.fill(UI_BACKGROUND)
        
        # Draw board
        self._draw_board()
        
        # Draw pieces
        self._draw_pieces()
        
        # Draw highlights
        if self.selected_piece:
            self._draw_highlights()
        
        # Draw UI panel
        self._draw_ui_panel()
        
        pygame.display.flip()
    
    def _draw_board(self):
        """Draw the checkerboard pattern."""
        for row in range(8):
            for col in range(8):
                x = col * SQUARE_SIZE
                y = row * SQUARE_SIZE
                
                # Alternate square colors
                color = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE
                pygame.draw.rect(self.screen, color, (x, y, SQUARE_SIZE, SQUARE_SIZE))
    
    def _draw_pieces(self):
        """Draw all pieces on the board."""
        for row in range(8):
            for col in range(8):
                piece = self.board.get_piece(row, col)
                if piece:
                    x = col * SQUARE_SIZE + SQUARE_SIZE // 2
                    y = row * SQUARE_SIZE + SQUARE_SIZE // 2
                    
                    # Try to use image first
                    piece_image = self.image_loader.get_piece_image(piece.piece_type, piece.color)
                    
                    if piece_image:
                        # Draw image
                        img_rect = piece_image.get_rect(center=(x, y))
                        self.screen.blit(piece_image, img_rect)
                    else:
                        # Always use drawn chess pieces (they look much better than Unicode)
                        drawn_image = self.image_loader.create_simple_image(piece.piece_type, piece.color)
                        if drawn_image:
                            img_rect = drawn_image.get_rect(center=(x, y))
                            self.screen.blit(drawn_image, img_rect)
                        else:
                            # Last resort: Unicode symbol (shouldn't happen)
                            symbol = piece.get_symbol()
                            text_surface = self.font_large.render(symbol, True, BLACK if piece.color == 'white' else WHITE)
                            text_rect = text_surface.get_rect(center=(x, y))
                            self.screen.blit(text_surface, text_rect)
    
    def _draw_highlights(self):
        """Draw highlights for selected piece and valid moves."""
        if self.selected_piece:
            row, col = self.selected_piece
            x = col * SQUARE_SIZE
            y = row * SQUARE_SIZE
            
            # Highlight selected piece
            highlight_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
            highlight_surface.set_alpha(128)
            highlight_surface.fill(HIGHLIGHT)
            self.screen.blit(highlight_surface, (x, y))
            
            # Highlight valid moves
            for move_row, move_col in self.valid_moves:
                move_x = move_col * SQUARE_SIZE
                move_y = move_row * SQUARE_SIZE
                
                move_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
                move_surface.set_alpha(100)
                move_surface.fill(VALID_MOVE_HIGHLIGHT)
                self.screen.blit(move_surface, (move_x, move_y))
    
    def _draw_ui_panel(self):
        """Draw the UI panel with game information."""
        panel_x = BOARD_SIZE
        panel_y = 0
        
        # Draw panel background
        pygame.draw.rect(self.screen, UI_BACKGROUND, 
                        (panel_x, panel_y, UI_PANEL_WIDTH, WINDOW_HEIGHT))
        
        y_offset = 20
        
        # Title
        title = self.font_large.render("Chess MVP", True, UI_TEXT)
        self.screen.blit(title, (panel_x + 10, y_offset))
        y_offset += 50
        
        # Author
        author = self.font_small.render("By Sepehr Bayat", True, UI_TEXT)
        self.screen.blit(author, (panel_x + 10, y_offset))
        y_offset += 40
        
        # Game mode
        if self.game_mode:
            mode_text = self.game_mode.replace('_', ' ').title()
            mode_surface = self.font_small.render(f"Mode: {mode_text}", True, UI_TEXT)
            self.screen.blit(mode_surface, (panel_x + 10, y_offset))
            y_offset += 30
        
        # Chess variant
        variant_text = "Chess960" if self.variant == "chess960" else "Standard"
        variant_surface = self.font_small.render(f"Variant: {variant_text}", True, UI_TEXT)
        self.screen.blit(variant_surface, (panel_x + 10, y_offset))
        y_offset += 30
        
        # Current turn
        turn_text = f"Turn: {self.board.current_turn.capitalize()}"
        if self._is_ai_turn():
            turn_text += " (AI)"
        turn_surface = self.font_medium.render(turn_text, True, UI_TEXT)
        self.screen.blit(turn_surface, (panel_x + 10, y_offset))
        y_offset += 40
        
        # AI thinking indicator
        if self.ai_thinking:
            thinking_text = self.font_small.render("AI thinking...", True, UI_TEXT)
            self.screen.blit(thinking_text, (panel_x + 10, y_offset))
            y_offset += 30
        
        # Game status
        status_surface = self.font_medium.render(self.game_status, True, UI_TEXT)
        self.screen.blit(status_surface, (panel_x + 10, y_offset))
        y_offset += 50
        
        # Move score section
        score_title = self.font_medium.render("Move Score:", True, UI_TEXT)
        self.screen.blit(score_title, (panel_x + 10, y_offset))
        y_offset += 35
        
        if self.last_move_score is not None and self.last_move_color:
            score_text = f"{self.last_move_color.capitalize()}: {self.last_move_score}/100"
            score_surface = self.font_large.render(score_text, True, UI_TEXT)
            self.screen.blit(score_surface, (panel_x + 10, y_offset))
            y_offset += 40
            
            # Score interpretation
            if self.last_move_score >= 81:
                interpretation = "Excellent!"
            elif self.last_move_score >= 61:
                interpretation = "Good move"
            elif self.last_move_score >= 31:
                interpretation = "Neutral"
            else:
                interpretation = "Poor move"
            
            interp_surface = self.font_small.render(interpretation, True, UI_TEXT)
            self.screen.blit(interp_surface, (panel_x + 10, y_offset))
            y_offset += 30
        
        y_offset += 20
        
        # Instructions
        if self._is_ai_turn():
            instructions = [
                "Waiting for AI...",
                "",
                "Press ESC to quit"
            ]
        else:
            instructions = [
                "Click a piece to select",
                "Click a highlighted",
                "square to move",
                "",
                "Press ESC to quit"
            ]
        
        for instruction in instructions:
            if instruction:
                inst_surface = self.font_small.render(instruction, True, UI_TEXT)
                self.screen.blit(inst_surface, (panel_x + 10, y_offset))
            y_offset += 25
    
    def run(self):
        """Run the main game loop."""
        # Show menu first
        if not self.show_menu():
            pygame.quit()
            return
        
        running = True
        ai_move_timer = 0
        ai_move_delay = 30  # Frames to wait before AI makes move (for smoothness)
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        self.handle_click(event.pos)
            
            # Handle AI moves
            if self._is_ai_turn() and not self.ai_thinking:
                ai_move_timer += 1
                if ai_move_timer >= ai_move_delay:
                    self._make_ai_move()
                    ai_move_timer = 0
            else:
                ai_move_timer = 0
            
            self.draw()
            self.clock.tick(60)  # 60 FPS
        
        pygame.quit()
