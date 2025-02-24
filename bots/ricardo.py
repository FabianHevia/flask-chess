from .base_bot import BaseBot
import chess
import random
import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed, ProcessPoolExecutor
from collections import defaultdict, OrderedDict

class RicardoBot(BaseBot):
    def __init__(self):
        super().__init__("Ricardo",2000)
        self.piece_values = {
            chess.PAWN: 100,
            chess.KNIGHT: 320,
            chess.BISHOP: 330,
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 20000
        }
        self.transposition_table = LimitedSizeDict(max_size=1_000_000)
        self.opening_book = self.load_opening_book('../static/openings.json')

    def load_opening_book(self, file_path='../static/openings.json'):
        if file_path:
            try:
                with open(file_path, "r") as file:
                    openings = json.load(file)
                    return {pos: [chess.Move.from_uci(move) for move in moves] for pos, moves in openings.items()}
            except (FileNotFoundError, json.JSONDecodeError):
                print("Error al cargar el libro de aperturas. Usando valores predeterminados.")

        # Aperturas por defecto
            return {
        # Inicio del juego - Múltiples primeras jugadas posibles
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1": [
            chess.Move.from_uci("e2e4"),  # Apertura clásica
            chess.Move.from_uci("d2d4"),  # Gambito de Dama
            chess.Move.from_uci("c2c4"),  # Inglesa
            chess.Move.from_uci("g1f3"),  # Reti
            chess.Move.from_uci("b2b3"),  # Larsen
        ],

        # Respuestas a 1.e4 (Defensas populares)
        "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1": [
            chess.Move.from_uci("e7e5"),  # Defensa Abierta
            chess.Move.from_uci("c7c5"),  # Defensa Siciliana
            chess.Move.from_uci("e7e6"),  # Defensa Francesa
            chess.Move.from_uci("c7c6"),  # Caro-Kann
            chess.Move.from_uci("g8f6"),  # Defensa Alekhine
            chess.Move.from_uci("d7d6"),  # Defensa Pirc
        ],

        # Respuestas a 1.d4 (Defensas principales)
        "rnbqkbnr/pppppppp/8/8/3PP3/8/PPP2PPP/RNBQKBNR b KQkq - 0 1": [
            chess.Move.from_uci("d7d5"),  # Defensa Ortodoxa
            chess.Move.from_uci("g8f6"),  # Defensa India de Rey
            chess.Move.from_uci("e7e6"),  # Defensa Francesa (transposición)
            chess.Move.from_uci("c7c5"),  # Defensa Benoni
            chess.Move.from_uci("f7f5"),  # Defensa Holandesa
        ],

        # Respuestas a 1.c4 (Apertura Inglesa)
        "rnbqkbnr/pppppppp/8/8/2P5/8/PP1PPPPP/RNBQKBNR b KQkq - 0 1": [
            chess.Move.from_uci("e7e5"),  # Variante Reversa de la Siciliana
            chess.Move.from_uci("c7c5"),  # Defensa Siciliana Inversa
            chess.Move.from_uci("g8f6"),  # Defensa India
            chess.Move.from_uci("e7e6"),  # Sistema Botvinnik
            chess.Move.from_uci("c7c6"),  # Defensa Caro-Kann (posible transposición)
        ],

        # Respuestas a 1.Nf3 (Apertura Reti)
        "rnbqkbnr/pppppppp/8/8/8/5N2/PPPPPPPP/RNBQKB1R b KQkq - 0 1": [
            chess.Move.from_uci("d7d5"),  # Variante Clásica
            chess.Move.from_uci("g8f6"),  # India de Rey
            chess.Move.from_uci("c7c5"),  # Defensa Siciliana Inversa
            chess.Move.from_uci("e7e6"),  # Defensa Francesa
            chess.Move.from_uci("c7c6"),  # Defensa Caro-Kann
        ],

        # Después de 1.e4 e5 2.Nf3 (Posibilidades negras)
        "rnbqkbnr/pppppppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 0 2": [
            chess.Move.from_uci("b8c6"),  # Defensa Española
            chess.Move.from_uci("g8f6"),  # Defensa Petrov
            chess.Move.from_uci("d7d6"),  # Defensa Philidor
            chess.Move.from_uci("f7f5"),  # Defensa Letona
            chess.Move.from_uci("c7c6"),  # Variante Caro-Kann
        ]
    }

    def get_move(self, board):
        # Intenta obtener un movimiento de la lista de aperturas
        opening_move = self.get_opening_move(board)
        if opening_move:
            return opening_move
        
        # Si no hay movimientos de apertura disponibles, usa el minimax
        self.nodes_evaluated = 0
        start_time = time.time()
        max_depth = 7  # Profundidad inicial ajustada
        
        best_move = self.iterative_deepening(board, max_depth, start_time)
        return best_move or list(board.legal_moves)[0]

    def get_opening_move(self, board):
        fen = board.fen()
        return self.opening_book.get(fen, None)

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
        best_move = None 
        if time.time() - start_time > self.think_time():
            return None, None

        board_hash = hash(str(board))
        if board_hash in self.transposition_table and self.transposition_table[board_hash][0] >= depth:
            return self.transposition_table[board_hash][1], self.transposition_table[board_hash][2]

        if depth == 0 or board.is_game_over():
            evaluation = self.quiescence_search(board, alpha, beta)
            self.transposition_table[board_hash] = (depth, evaluation, best_move or None)  # Almacenar evaluación sin movimiento
            return evaluation, None
        
        # Manejar caso sin movimientos legales
        if not list(board.legal_moves):
            return self.evaluate_position(board), None

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
            self.transposition_table[board_hash] = (depth, max_eval, best_move)
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
            self.transposition_table[board_hash] = (depth, min_eval, best_move)
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

        # Evaluar material
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                value = self.piece_values[piece.piece_type]
                
                # Bonificaciones posicionales
                if piece.piece_type == chess.PAWN:
                    rank = chess.square_rank(square)
                    if piece.color == chess.WHITE:
                        value += rank * 10  # Peones avanzados valen más
                    else:
                        value += (7 - rank) * 10  # Peones negros avanzados valen más
                
                # Centralidad
                file = chess.square_file(square)
                rank = chess.square_rank(square)
                distance_to_center = abs(3.5 - file) + abs(3.5 - rank)
                value += (7 - distance_to_center) * 5  # Piezas centrales valen más

                score += value if piece.color == chess.WHITE else -value

        # Control del centro
        central_squares = [chess.D4, chess.E4, chess.D5, chess.E5]
        for square in central_squares:
            if board.is_attacked_by(chess.WHITE, square):
                score += 10
            if board.is_attacked_by(chess.BLACK, square):
                score -= 10

        # Seguridad del rey
        king_square = board.king(chess.WHITE)
        if king_square:
            score += len(board.attackers(chess.WHITE, king_square)) * 5
            score -= len(board.attackers(chess.BLACK, king_square)) * 5

        king_square = board.king(chess.BLACK)
        if king_square:
            score -= len(board.attackers(chess.WHITE, king_square)) * 5
            score += len(board.attackers(chess.BLACK, king_square)) * 5

        # Movilidad
        score += len(list(board.legal_moves)) * 5 if board.turn == chess.WHITE else -len(list(board.legal_moves)) * 5

        # Penaliazción --
        # Penalizar peones doblados
        for color in [chess.WHITE, chess.BLACK]:
            doubled_pawns = 0
            for file in range(8):
                pawns_in_file = len([pawn for pawn in board.pieces(chess.PAWN, color) if chess.square_file(pawn) == file])
                if pawns_in_file > 1:
                    doubled_pawns += pawns_in_file - 1
            score += (-doubled_pawns * 50) if color == chess.WHITE else (doubled_pawns * 50)
        
        # Bonificación ++
        # Control de columnas abiertas con las torres

        for color in [chess.WHITE, chess.BLACK]:
            for file in range(8):
                if not any(board.piece_at(chess.square(rank, file)) for rank in range(8)):
                    rooks = board.pieces(chess.ROOK, color)
                    for rook in rooks:
                        if chess.square_file(rook) == file:
                            score += 30 if color == chess.WHITE else -30

         # Desarrollo de piezas
        developed_pieces = len([piece for piece in board.piece_map().values() if piece.piece_type in [chess.KNIGHT, chess.BISHOP]])
        score += developed_pieces * 20 if board.turn == chess.WHITE else -developed_pieces * 20

        return score if board.turn else -score

    def score_move(self, board, move):
        score = 0
        
        # Capturas tácticas
        if board.is_capture(move):
            capturing_piece = board.piece_at(move.from_square)
            captured_piece = board.piece_at(move.to_square)
            if captured_piece:
                score += 10000 + self.piece_values[captured_piece.piece_type] - (self.piece_values[capturing_piece.piece_type] / 10)
        
        # Promociones
        if move.promotion:
            score += 9000 + self.piece_values[move.promotion]
        
        # Centralidad
        to_rank, to_file = chess.square_rank(move.to_square), chess.square_file(move.to_square)
        center_distance = abs(3.5 - to_rank) + abs(3.5 - to_file)
        score += (4 - center_distance) * 10
        
        # Movimientos que dan jaque
        board.push(move)
        if board.is_check():
            score += 500
        board.pop()
        
        return score
    
    def has_immediate_threat(self, board):
        for move in board.legal_moves:
            if board.gives_check(move) or board.is_capture(move):
                return True
        return False

    def order_moves(self, board):
        scored_moves = []
        for move in board.legal_moves:
            score = self.score_move(board, move)
            scored_moves.append((score, move))
        
        scored_moves.sort(reverse=True, key=lambda x: x[0])
        return [move for score, move in scored_moves]

    def parallel_minimax(self, board, depth, alpha, beta, maximizing, start_time):
        with ThreadPoolExecutor(max_workers=4) as executor:  # Ajusta el número de hilos según tu CPU
            futures = []
            for move in self.order_moves(board):
                board.push(move)
                futures.append(executor.submit(self.minimax, board.copy(), depth - 1, alpha, beta, not maximizing, start_time))
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
        
class LimitedSizeDict(OrderedDict):
    def __init__(self, *args, max_size=1000000, **kwargs):
        self.max_size = max_size
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        if len(self) > self.max_size:
            self.popitem(last=False)