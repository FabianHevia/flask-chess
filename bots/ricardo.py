from .base_bot import BaseBot
import chess

class RicardoBot(BaseBot):
    def __init__(self):
        super().__init__("Ricardo", 2000)
    
    def get_move(self, board):
        # Bot avanzado que usa minimax con profundidad 3
        def evaluate_position(board):
            if board.is_checkmate():
                return float('-inf') if board.turn else float('inf')
            
            piece_values = {
                chess.PAWN: 1,
                chess.KNIGHT: 3,
                chess.BISHOP: 3,
                chess.ROOK: 5,
                chess.QUEEN: 9,
                chess.KING: 0
            }
            
            score = 0
            for square in chess.SQUARES:
                piece = board.piece_at(square)
                if piece:
                    value = piece_values[piece.piece_type]
                    if piece.color:
                        score += value
                    else:
                        score -= value
            return score
        
        def minimax(board, depth, alpha, beta, maximizing):
            if depth == 0 or board.is_game_over():
                return evaluate_position(board)
            
            if maximizing:
                max_eval = float('-inf')
                for move in board.legal_moves:
                    board.push(move)
                    eval = minimax(board, depth - 1, alpha, beta, False)
                    board.pop()
                    max_eval = max(max_eval, eval)
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break
                return max_eval
            else:
                min_eval = float('inf')
                for move in board.legal_moves:
                    board.push(move)
                    eval = minimax(board, depth - 1, alpha, beta, True)
                    board.pop()
                    min_eval = min(min_eval, eval)
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break
                return min_eval
        
        best_move = None
        best_value = float('-inf')
        
        for move in board.legal_moves:
            board.push(move)
            value = minimax(board, 2, float('-inf'), float('inf'), False)
            board.pop()
            
            if value > best_value:
                best_value = value
                best_move = move
        
        return best_move