"""
Author: Sepehr Bayat | Open Source Chess MVP

Simple test script to verify the chess game components work correctly.
"""

import sys

def test_imports():
    """Test that all imports work correctly."""
    print("Testing imports...")
    try:
        from chess import constants
        print("[OK] constants imported")
        
        from chess.pieces import Piece, Pawn, Rook, Knight, Bishop, Queen, King
        print("[OK] pieces imported")
        
        from chess.board import Board
        print("[OK] board imported")
        
        from chess.evaluator import Evaluator
        print("[OK] evaluator imported")
        
        from chess.game import Game
        print("[OK] game imported")
        
        from chess.ai import ChessAI
        print("[OK] AI imported")
        
        from chess.menu import GameMenu
        print("[OK] menu imported")
        
        from chess.piece_images import PieceImageLoader
        print("[OK] piece_images imported")
        
        return True
    except Exception as e:
        print(f"[ERROR] Import error: {e}")
        return False

def test_board_initialization():
    """Test that board initializes correctly."""
    print("\nTesting board initialization...")
    try:
        from chess.board import Board
        board = Board()
        
        # Check that pieces are placed
        assert board.get_piece(7, 4) is not None, "White king should be at e1"
        assert board.get_piece(0, 4) is not None, "Black king should be at e8"
        assert board.get_piece(7, 4).piece_type == 'king', "Should be a king"
        assert board.get_piece(7, 4).color == 'white', "Should be white"
        
        print("[OK] Board initialized correctly")
        return True
    except Exception as e:
        print(f"[ERROR] Board initialization error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_piece_moves():
    """Test that pieces can generate valid moves."""
    print("\nTesting piece moves...")
    try:
        from chess.board import Board
        board = Board()
        
        # Test pawn moves
        pawn = board.get_piece(6, 0)  # White pawn
        assert pawn is not None, "Pawn should exist"
        moves = pawn.get_valid_moves(board)
        assert len(moves) > 0, "Pawn should have valid moves"
        print(f"[OK] Pawn has {len(moves)} valid moves")
        
        # Test knight moves
        knight = board.get_piece(7, 1)  # White knight
        assert knight is not None, "Knight should exist"
        moves = knight.get_valid_moves(board)
        assert len(moves) > 0, "Knight should have valid moves"
        print(f"[OK] Knight has {len(moves)} valid moves")
        
        return True
    except Exception as e:
        print(f"[ERROR] Piece moves error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_move_execution():
    """Test that moves can be executed."""
    print("\nTesting move execution...")
    try:
        from chess.board import Board
        board = Board()
        
        # Make a simple pawn move
        result = board.make_move((6, 0), (5, 0))
        assert result, "Move should succeed"
        assert board.get_piece(5, 0) is not None, "Piece should be at new position"
        assert board.get_piece(6, 0) is None, "Old position should be empty"
        assert board.current_turn == 'black', "Turn should switch to black"
        
        print("[OK] Move executed correctly")
        return True
    except Exception as e:
        print(f"[ERROR] Move execution error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_evaluator():
    """Test that evaluator works."""
    print("\nTesting evaluator...")
    try:
        from chess.board import Board
        from chess.evaluator import Evaluator
        
        board = Board()
        evaluator = Evaluator()
        
        # Evaluate a move
        move = ((6, 0), (5, 0))
        score = evaluator.evaluate_move(board, move, 'white')
        
        assert 0 <= score <= 100, f"Score should be 0-100, got {score}"
        print(f"[OK] Evaluator returned score: {score}/100")
        
        return True
    except Exception as e:
        print(f"[ERROR] Evaluator error: {e}")
        import traceback
        traceback.print_exc()
        return False

def _make_custom_960_board(rook_cols, king_col):
    """Create an empty Chess960 board for placing custom test positions."""
    from chess.board import Board
    board = Board(variant='chess960')
    board.grid = [[None for _ in range(8)] for _ in range(8)]
    board.initial_rook_cols = rook_cols
    board.initial_king_col = king_col
    return board

def test_chess960_setup():
    """Test that Chess960 boards are generated legally."""
    print("\nTesting Chess960 setup...")
    try:
        from chess.board import Board
        
        for _ in range(20):
            board = Board(variant='chess960')
            
            # Back rank has the right pieces
            white_types = sorted(board.get_piece(7, c).piece_type for c in range(8))
            assert white_types == sorted(['rook', 'knight', 'bishop', 'queen',
                                          'king', 'bishop', 'knight', 'rook']), \
                f"Wrong back rank pieces: {white_types}"
            
            # Black mirrors white
            for c in range(8):
                assert board.get_piece(0, c).piece_type == board.get_piece(7, c).piece_type, \
                    "Black back rank should mirror white"
            
            # Pawns in place
            for c in range(8):
                assert board.get_piece(6, c).piece_type == 'pawn', "White pawns missing"
                assert board.get_piece(1, c).piece_type == 'pawn', "Black pawns missing"
            
            # Bishops on opposite-colored squares
            bishop_cols = [c for c in range(8)
                           if board.get_piece(7, c).piece_type == 'bishop']
            assert bishop_cols[0] % 2 != bishop_cols[1] % 2, \
                f"Bishops on same-colored squares: {bishop_cols}"
            
            # King between the rooks
            king_col = next(c for c in range(8)
                            if board.get_piece(7, c).piece_type == 'king')
            rook_cols = [c for c in range(8)
                         if board.get_piece(7, c).piece_type == 'rook']
            assert rook_cols[0] < king_col < rook_cols[1], \
                f"King (col {king_col}) not between rooks {rook_cols}"
            
            # Recorded columns match the actual placement
            assert board.initial_king_col == king_col
            assert list(board.initial_rook_cols) == rook_cols
        
        print("[OK] Chess960 setup is legal (20 random positions)")
        return True
    except Exception as e:
        print(f"[ERROR] Chess960 setup error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_chess960_castling():
    """Test Chess960 castling legality and execution."""
    print("\nTesting Chess960 castling...")
    try:
        from chess.pieces import Rook, King, Bishop
        
        # King on b1, rooks on a1 and h1
        board = _make_custom_960_board(rook_cols=(0, 7), king_col=1)
        king = King('white', 7, 1)
        rook_a = Rook('white', 7, 0)
        rook_h = Rook('white', 7, 7)
        board.grid[7][1] = king
        board.grid[7][0] = rook_a
        board.grid[7][7] = rook_h
        board.grid[0][4] = King('black', 0, 4)
        
        moves = king.get_valid_moves(board)
        assert (7, 0) in moves, "Queenside castling (king onto a1 rook) should be legal"
        assert (7, 7) in moves, "Kingside castling (king onto h1 rook) should be legal"
        
        # Execute queenside: king b1 -> c1, rook a1 -> d1
        assert board.make_move((7, 1), (7, 0)), "Queenside castle should execute"
        assert board.get_piece(7, 2) is king, "King should land on c1"
        assert board.get_piece(7, 3) is rook_a, "Rook should land on d1"
        assert board.get_piece(7, 0) is None and board.get_piece(7, 1) is None
        print("[OK] Queenside castling: king b1->c1, rook a1->d1")
        
        # Execute kingside on a fresh board: king b1 -> g1, rook h1 -> f1
        board = _make_custom_960_board(rook_cols=(0, 7), king_col=1)
        king = King('white', 7, 1)
        rook_h = Rook('white', 7, 7)
        board.grid[7][1] = king
        board.grid[7][0] = Rook('white', 7, 0)
        board.grid[7][7] = rook_h
        board.grid[0][4] = King('black', 0, 4)
        
        assert board.make_move((7, 1), (7, 7)), "Kingside castle should execute"
        assert board.get_piece(7, 6) is king, "King should land on g1"
        assert board.get_piece(7, 5) is rook_h, "Rook should land on f1"
        print("[OK] Kingside castling: king b1->g1, rook h1->f1")
        
        # Overlap case: king d1, rook c1 - castling queenside swaps them
        board = _make_custom_960_board(rook_cols=(2, 7), king_col=3)
        king = King('white', 7, 3)
        rook_c = Rook('white', 7, 2)
        board.grid[7][3] = king
        board.grid[7][2] = rook_c
        board.grid[7][7] = Rook('white', 7, 7)
        board.grid[0][4] = King('black', 0, 4)
        
        moves = king.get_valid_moves(board)
        assert (7, 2) in moves, "Queenside castling with adjacent rook should be legal"
        assert board.make_move((7, 3), (7, 2)), "Adjacent-rook castle should execute"
        assert board.get_piece(7, 2) is king, "King should land on c1"
        assert board.get_piece(7, 3) is rook_c, "Rook should land on d1"
        print("[OK] Adjacent king/rook swap: king d1->c1, rook c1->d1")
        
        # Blocked path: bishop on e1 blocks kingside castling for king on b1
        board = _make_custom_960_board(rook_cols=(0, 7), king_col=1)
        king = King('white', 7, 1)
        board.grid[7][1] = king
        board.grid[7][0] = Rook('white', 7, 0)
        board.grid[7][7] = Rook('white', 7, 7)
        board.grid[7][4] = Bishop('white', 7, 4)
        board.grid[0][4] = King('black', 0, 4)
        
        moves = king.get_valid_moves(board)
        assert (7, 7) not in moves, "Kingside castling should be blocked by bishop on e1"
        assert (7, 0) in moves, "Queenside castling should still be legal"
        print("[OK] Blocked castling path rejected")
        
        # Castling into check: enemy rook on c8 attacks c1
        board = _make_custom_960_board(rook_cols=(0, 7), king_col=1)
        king = King('white', 7, 1)
        board.grid[7][1] = king
        board.grid[7][0] = Rook('white', 7, 0)
        board.grid[7][7] = Rook('white', 7, 7)
        board.grid[0][2] = Rook('black', 0, 2)
        board.grid[0][4] = King('black', 0, 4)
        
        moves = king.get_valid_moves(board)
        assert (7, 0) not in moves, "Castling into check (c1 attacked) should be illegal"
        print("[OK] Castling into check rejected")
        
        return True
    except Exception as e:
        print(f"[ERROR] Chess960 castling error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_standard_castling_unchanged():
    """Test that standard castling still works after the Chess960 changes."""
    print("\nTesting standard castling...")
    try:
        from chess.board import Board
        
        board = Board()
        # Clear f1 and g1 so white can castle kingside
        board.grid[7][5] = None
        board.grid[7][6] = None
        
        king = board.get_piece(7, 4)
        moves = king.get_valid_moves(board)
        assert (7, 6) in moves, "Standard kingside castling should be legal"
        
        assert board.make_move((7, 4), (7, 6)), "Standard castle should execute"
        assert board.get_piece(7, 6).piece_type == 'king', "King should be on g1"
        assert board.get_piece(7, 5).piece_type == 'rook', "Rook should be on f1"
        assert board.get_piece(7, 7) is None, "h1 should be empty"
        
        print("[OK] Standard castling works")
        return True
    except Exception as e:
        print(f"[ERROR] Standard castling error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("=" * 50)
    print("Chess MVP Test Suite")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_board_initialization,
        test_piece_moves,
        test_move_execution,
        test_evaluator,
        test_chess960_setup,
        test_chess960_castling,
        test_standard_castling_unchanged,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"[ERROR] Test {test.__name__} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"Tests passed: {passed}/{len(tests)}")
    print(f"Tests failed: {failed}/{len(tests)}")
    print("=" * 50)
    
    if failed == 0:
        print("\n[SUCCESS] All tests passed!")
        return 0
    else:
        print("\n[FAILED] Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())

