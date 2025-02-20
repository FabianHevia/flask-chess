from .base_bot import BaseBot
import chess
import random
import time

class ElenaBot(BaseBot):
    def __init__(self):
        super().__init__("Elena", 1300)
        self.piece_values = {
            chess.PAWN: 100,
            chess.KNIGHT: 320,
            chess.BISHOP: 330,
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 20000
        }
        
        # Sistema de aperturas mejorado con múltiples respuestas
        self.openings = {
            # Respuestas a 1.e4
            "e2e4": {
                # Siciliana
                "mainline": ["c7c5"],
                "responses": {
                    "g1f3": ["d7d6", "e7e6", "b8c6"],  # Respuestas a Cf3
                    "b1c3": ["b8c6", "e7e6"],          # Respuestas a Cc3
                    "c2c3": ["b8c6", "d7d5"],          # Respuestas a c3
                    "d2d4": ["c5d4"],                   # Captura obligada
                },
                "anti_theory": {
                    "f2f4": ["e7e6"],                  # Contra Grand Prix
                    "b2b4": ["c5b4"],                  # Contra Wing Gambit
                    "c2c4": ["b8c6"]                   # Contra c4
                },
                "follow_up": {
                    "d2d4 c5d4": ["c3d4"],             # Recaptura con Cc3
                    "g1f3 d7d6": ["f1b5"],             # Alfil a b5 (Siciliana Rossolimo)
                    "b1c3 e7e6": ["f1c4"],             # Alfil a c4 (Siciliana Clásica)
                }
            },
            # Caro-Kann
            "alternative1": {
                "mainline": ["c7c6"],
                "responses": {
                    "d2d4": ["d7d5"],
                    "b1c3": ["d7d5"],
                    "d2d3": ["d7d5"]
                },
                "follow_up": {
                    "e4e5": ["c8f5"],                  # Contra Advance
                    "e4d5": ["c6d5"],                  # Captura obligada
                    "b1d2": ["d7d5"],                  # Contra Two Knights
                    "c1f4": ["g8f6"],                  # Desarrollo del caballo
                },
                "anti_theory": {
                    "e4e6": ["d7d5"],                  # Contra Exchange Variation
                    "b1d2": ["g8f6"],                  # Desarrollo del caballo
                }
            },
            # Francesa
            "alternative2": {
                "mainline": ["e7e6"],
                "responses": {
                    "d2d4": ["d7d5"],
                    "b1c3": ["d7d5"],
                    "e4e5": ["c7c5"]
                },
                "anti_theory": {
                    "b1c3": ["d7d5"],                  # Contra Nc3
                    "e4d5": ["e6d5"],                  # Captura obligada
                },
                "follow_up": {
                    "e4e5 c7c5": ["f1b5"],             # Alfil a b5 (Tarrasch)
                    "b1c3 g8f6": ["f1d3"],             # Alfil a d3
                    "e4e5 f8b4": ["c1d2"],             # Alfil a d2
                }
            },
            # Respuestas a 1.d4
            "d2d4": {
                # India de Rey
                "mainline": ["g8f6"],
                "responses": {
                    "c2c4": ["g7g6"],                  # Setup India de Rey
                    "g1f3": ["g7g6"],                  # Transposición
                    "b1c3": ["g7g6"]                   # Transposición
                },
                "follow_up": {
                    "g1f3 g7g6": ["f8g7"],             # Fianchetto
                    "c2c4 g7g6": ["f8g7"],             # Fianchetto
                    "f1g2": ["f8g7"],                  # Alfil a g2
                },
                "anti_theory": {
                    "c4c5": ["f6e4"],                  # Caballo a e4
                    "e2e4": ["d7d6"],                  # Contra King's Indian Attack
                }
            },
            # Nimzoindia
            "alternative_d4": {
                "mainline": ["g8f6"],
                "responses": {
                    "c2c4": ["e7e6"],
                    "b1c3": ["f8b4"],                  # Pin al caballo
                    "g1f3": ["e7e6"]
                },
                "follow_up": {
                    "c2c4 e7e6": ["f8b4"],              # Setup Nimzoindia
                    "e2e3": ["c7c5"],                   # Break central
                    "f1d3": ["b8c6"],                   # Desarrollo del caballo
                },
                "anti_theory": {
                    "c4c5": ["f6e4"],                   # Caballo a e4
                    "b1d2": ["e7e6"],                   # Contra desarrollo alternativo
                }
            },
            # Grünfeld
            "alternative_grunfeld": {
                "mainline": ["g8f6"],
                "responses": {
                    "c2c4": ["d7d5"],                   # Centro agresivo
                    "g1f3": ["d7d5"],                   # Transposición
                    "b1c3": ["d7d5"]                    # Transposición
                },
                "follow_up": {
                    "c4d5 f6d5": ["e2e4"],              # Control del centro
                    "g1f3 d7d5": ["c1g5"],              # Alfil a g5
                    "b1c3 d7d5": ["f1d3"],              # Alfil a d3
                },
                "anti_theory": {
                    "e2e3": ["d7d5"],                   # Contra Colle System
                    "f1d3": ["b8c6"],                   # Desarrollo del caballo
                }
            },
            # Holandesa
            "alternative_holland": {
                "mainline": ["f7f5"],
                "responses": {
                    "g1f3": ["g8f6"],                   # Desarrollo del caballo
                    "d2d3": ["e7e6"],                   # Estructura sólida
                    "c2c4": ["e7e6"]                    # Transposición
                },
                "follow_up": {
                    "g1f3 g8f6": ["f1d3"],              # Alfil a d3
                    "c2c4 e7e6": ["f1g2"],              # Alfil a g2
                    "d2d3 e7e6": ["c1e3"],              # Alfil a e3
                },
                "anti_theory": {
                    "e2e4": ["f5e4"],                   # Captura en e4
                    "f1b5": ["c7c6"],                   # Contra fianchetto temprano
                }
            }
        }

    def get_opening_move(self, board):
        """Sistema de aperturas mejorado que considera múltiples respuestas"""
        moves_str = " ".join([move.uci() for move in board.move_stack])
        moves_list = moves_str.split()
        
        if not moves_list:
            return None
            
        # Primera jugada blanca determina la línea principal
        first_white = moves_list[0]
        opening_system = self.openings.get(first_white)
        
        if not opening_system:
            return None
            
        # Si es nuestra primera jugada, elegir una de las líneas principales
        if len(moves_list) == 1:
            mainline_moves = opening_system["mainline"]
            chosen_move = random.choice(mainline_moves)
            return chess.Move.from_uci(chosen_move)
            
        # Buscar respuestas a la última jugada del oponente
        last_move = moves_list[-1]
        
        # Verificar respuestas específicas
        if last_move in opening_system["responses"]:
            possible_responses = opening_system["responses"][last_move]
            chosen_response = random.choice(possible_responses)
            if self.is_move_legal(board, chosen_response):
                return chess.Move.from_uci(chosen_response)
                
        # Verificar anti-teoría
        if "anti_theory" in opening_system and last_move in opening_system["anti_theory"]:
            anti_theory_move = opening_system["anti_theory"][last_move]
            if self.is_move_legal(board, anti_theory_move):
                return chess.Move.from_uci(anti_theory_move)
                
        # Verificar continuaciones
        if "follow_up" in opening_system:
            for sequence, response in opening_system["follow_up"].items():
                if moves_str.endswith(sequence):
                    if self.is_move_legal(board, response):
                        return chess.Move.from_uci(response)
        
        # Si no encontramos una respuesta en la teoría, volvemos al análisis regular
        return None

    def is_move_legal(self, board, move_str):
        """Verifica si un movimiento en notación UCI es legal"""
        try:
            move = chess.Move.from_uci(move_str)
            return move in board.legal_moves
        except:
            return False
        
    def minimax(self, board, depth, maximizing_player, alpha=float('-inf'), beta=float('inf')):
        """
        Implementación del algoritmo Minimax con Alpha-Beta Pruning.
        :param board: Estado actual del tablero.
        :param depth: Profundidad restante para explorar.
        :param maximizing_player: True si es el turno del jugador maximizador (nosotros), False si es el oponente.
        :param alpha: Mejor valor encontrado para el jugador maximizador.
        :param beta: Mejor valor encontrado para el jugador minimizador.
        :return: La mejor puntuación y el mejor movimiento.
        """
        if depth == 0 or board.is_game_over():
            return self.evaluate_position(board), None

        legal_moves = list(board.legal_moves)
        best_move = None

        if maximizing_player:
            max_eval = float('-inf')
            for move in legal_moves:
                board.push(move)
                eval_score, _ = self.minimax(board, depth - 1, False, alpha, beta)
                board.pop()
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # Poda Alpha-Beta
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for move in legal_moves:
                board.push(move)
                eval_score, _ = self.minimax(board, depth - 1, True, alpha, beta)
                board.pop()
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  # Poda Alpha-Beta
            return min_eval, best_move

    def evaluate_position(self, board):
        """
        Evalúa la posición actual del tablero.
        """
        if board.is_checkmate():
            return -20000 if board.turn else 20000

        score = 0

        # Evaluar material y posición
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece is not None:  # Verificamos que la pieza existe
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

    def get_move(self, board):
        """
        Obtiene el mejor movimiento usando Minimax.
        """
        # Usar el tiempo de pensamiento de la clase base
        time.sleep(self.think_time())

        # Intentar jugada de apertura
        opening_move = self.get_opening_move(board)
        if opening_move and opening_move in board.legal_moves:
            return opening_move

        # Aplicar Minimax para encontrar el mejor movimiento
        _, best_move = self.minimax(board, depth=3, maximizing_player=board.turn)
        return best_move or random.choice(list(board.legal_moves))