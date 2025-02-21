from .base_bot import BaseBot
import chess
import random
import time

class RicardoBot(BaseBot):
    def __init__(self):
        super().__init__("Ricardo", 2000)
        # Tabla de transposición para almacenar posiciones evaluadas
        self.transposition_table = {}
        # Valores de las piezas ajustados
        self.piece_values = {
            chess.PAWN: 100,
            chess.KNIGHT: 320,
            chess.BISHOP: 330,
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 20000
        }
        # Tablas de posición para cada pieza
        self.pawn_table = [
            0,  0,  0,  0,  0,  0,  0,  0,
            50, 50, 50, 50, 50, 50, 50, 50,
            10, 10, 20, 30, 30, 20, 10, 10,
            5,  5, 10, 25, 25, 10,  5,  5,
            0,  0,  0, 20, 20,  0,  0,  0,
            5, -5,-10,  0,  0,-10, -5,  5,
            5, 10, 10,-20,-20, 10, 10,  5,
            0,  0,  0,  0,  0,  0,  0,  0
        ]
        
    def get_move(self, board):
        self.nodes_evaluated = 0
        start_time = time.time()
        max_depth = 4  # Aumentamos la profundidad
        
        best_move = self.iterative_deepening(board, max_depth, start_time)
        return best_move

    def iterative_deepening(self, board, max_depth, start_time):
        best_move = None
        
        for depth in range(1, max_depth + 1):
            if time.time() - start_time > self.think_time():
                break
                
            value, move = self.minimax(board, depth, float('-inf'), float('inf'), True, start_time)
            if move:
                best_move = move
                
        return best_move or list(board.legal_moves)[0]

    def minimax(self, board, depth, alpha, beta, maximizing, start_time):
        if time.time() - start_time > self.think_time():
            return None, None

        # Verificar tablas de transposición
        board_hash = hash(str(board))
        if board_hash in self.transposition_table and self.transposition_table[board_hash][0] >= depth:
            return self.transposition_table[board_hash][1], None

        if depth == 0 or board.is_game_over():
            evaluation = self.evaluate_position(board)
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

    def evaluate_position(self, board):
        if board.is_checkmate():
            return -20000 if board.turn else 20000
        if board.is_stalemate() or board.is_insufficient_material():
            return 0

        score = 0
        # Evaluación de material y posición
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                value = self.piece_values[piece.piece_type]
                # Añadir valor posicional para peones
                if piece.piece_type == chess.PAWN:
                    position_value = self.pawn_table[square if piece.color else chess.square_mirror(square)]
                    value += position_value
                
                if piece.color:
                    score += value
                else:
                    score -= value

        # Bonus por movilidad
        score += len(list(board.legal_moves)) * 10 if board.turn else -len(list(board.legal_moves)) * 10
        
        return score

    def score_move(self, board, move):
        """Calcula una puntuación para un movimiento específico"""
        score = 0
        
        # Priorizar capturas
        if board.is_capture(move):
            capturing_piece = board.piece_at(move.from_square)
            captured_piece = board.piece_at(move.to_square)
            if captured_piece:
                score += 10000 + self.piece_values[captured_piece.piece_type] - (self.piece_values[capturing_piece.piece_type] / 10)
        
        # Priorizar promociones
        if move.promotion:
            score += 9000 + self.piece_values[move.promotion]
            
        # Priorizar movimientos al centro del tablero
        to_rank, to_file = chess.square_rank(move.to_square), chess.square_file(move.to_square)
        center_distance = abs(3.5 - to_rank) + abs(3.5 - to_file)
        score += (4 - center_distance) * 10
        
        # Priorizar movimientos que dan jaque
        board.push(move)
        if board.is_check():
            score += 500
        board.pop()
        
        return score

    def order_moves(self, board):
        """Ordena los movimientos para mejorar la poda alfa-beta"""
        scored_moves = []
        for move in board.legal_moves:
            score = self.score_move(board, move)
            scored_moves.append((score, move))
        
        # Ordenar por puntuación de mayor a menor y devolver solo los movimientos
        scored_moves.sort(reverse=True, key=lambda x: x[0])
        return [move for score, move in scored_moves]