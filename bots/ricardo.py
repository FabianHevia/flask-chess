from .base_bot import BaseBot
import chess
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

class RicardoBot(BaseBot):
    def __init__(self):
        super().__init__("Ricardo", 2000)
        self.piece_values = {
            chess.PAWN: 100,
            chess.KNIGHT: 320,
            chess.BISHOP: 330,
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 20000
        }
        self.transposition_table = {}

    def get_move(self, board):
        self.nodes_evaluated = 0
        start_time = time.time()
        max_depth = 5  # Profundidad inicial ajustada
        
        best_move = self.iterative_deepening(board, max_depth, start_time)
        return best_move or list(board.legal_moves)[0]

    def iterative_deepening(self, board, max_depth, start_time):
        best_move = None
        
        for depth in range(1, max_depth + 1):
            if time.time() - start_time > self.think_time():
                break
                
            value, move = self.minimax(board, depth, float('-inf'), float('inf'), True, start_time)
            if move:
                best_move = move
                
        return best_move

    def minimax(self, board, depth, alpha, beta, maximizing, start_time):
        if time.time() - start_time > self.think_time():
            return None, None
        board_hash = hash(str(board))
        if board_hash in self.transposition_table and self.transposition_table[board_hash][0] >= depth:
            return self.transposition_table[board_hash][1], None
        if depth == 0 or board.is_game_over():
            evaluation = self.quiescence_search(board, alpha, beta)
            self.transposition_table[board_hash] = (depth, evaluation)
            return evaluation, None
        best_move = None
        if maximizing:
            max_eval = float('-inf')
            for move in self.order_moves(board):
                board.push(move)
                eval, _ = self.minimax(board, depth - 1, alpha, beta, False, start_time)
                board.pop()
                
                if eval is None:  # Tiempo agotado
                    return None, None
                    
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for move in self.order_moves(board):
                board.push(move)
                eval, _ = self.minimax(board, depth - 1, alpha, beta, True, start_time)
                board.pop()
                
                if eval is None:  # Tiempo agotado
                    return None, None
                    
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval, best_move

    def quiescence_search(self, board, alpha, beta):
        stand_pat = self.evaluate_position(board)
        if stand_pat >= beta:
            return beta
        if alpha < stand_pat:
            alpha = stand_pat
        for move in board.legal_moves:
            if board.is_capture(move):
                board.push(move)
                score = -self.quiescence_search(board, -beta, -alpha)
                board.pop()
                if score >= beta:
                    return beta
                if score > alpha:
                    alpha = score
        return alpha

    def evaluate_position(self, board):
        if board.is_checkmate():
            return -20000 if board.turn else 20000
        if board.is_stalemate() or board.is_insufficient_material():
            return 0
        score = 0
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                value = self.piece_values[piece.piece_type]
                
                # Bonificaciones posicionales
                if piece.piece_type == chess.PAWN:
                    if square in [chess.D4, chess.E4, chess.D5, chess.E5]:  # Control del centro
                        value += 20

                score += value if piece.color else -value

        # Control del centro
        central_squares = [chess.D4, chess.E4, chess.D5, chess.E5]
        for square in central_squares:
            if board.is_attacked_by(chess.WHITE, square):
                score += 10
            if board.is_attacked_by(chess.BLACK, square):
                score -= 10

        # Desarrollo en apertura
        if len(board.move_stack) < 20:
            for square in chess.SQUARES:
                piece = board.piece_at(square)
                if piece:
                    if piece.piece_type in [chess.KNIGHT, chess.BISHOP]:
                        if piece.color and square > chess.H2:
                            score += 20
                        elif not piece.color and square < chess.A7:
                            score -= 20

        return score if board.turn else -score

    def score_move(self, board, move):
        score = 0
        
        if board.is_capture(move):
            capturing_piece = board.piece_at(move.from_square)
            captured_piece = board.piece_at(move.to_square)
            if captured_piece:
                score += 10000 + self.piece_values[captured_piece.piece_type] - (self.piece_values[capturing_piece.piece_type] / 10)
        
        if move.promotion:
            score += 9000 + self.piece_values[move.promotion]
            
        to_rank, to_file = chess.square_rank(move.to_square), chess.square_file(move.to_square)
        center_distance = abs(3.5 - to_rank) + abs(3.5 - to_file)
        score += (4 - center_distance) * 10
        
        board.push(move)
        if board.is_check():
            score += 500
        board.pop()
        
        return score

    def order_moves(self, board):
        scored_moves = []
        for move in board.legal_moves:
            score = self.score_move(board, move)
            scored_moves.append((score, move))
        
        scored_moves.sort(reverse=True, key=lambda x: x[0])
        return [move for score, move in scored_moves]

    def parallel_minimax(self, board, depth, alpha, beta, maximizing, start_time):
        with ThreadPoolExecutor() as executor:
            futures = []
            for move in self.order_moves(board):
                board.push(move)
                futures.append(executor.submit(self.minimax, board, depth - 1, alpha, beta, not maximizing, start_time))
                board.pop()
            
            best_move = None
            best_value = float('-inf') if maximizing else float('inf')
            for future in as_completed(futures):
                eval, move = future.result()
                if eval is None:
                    continue
                if maximizing and eval > best_value:
                    best_value = eval
                    best_move = move
                elif not maximizing and eval < best_value:
                    best_value = eval
                    best_move = move
            return best_value, best_move