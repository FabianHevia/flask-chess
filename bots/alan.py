from .base_bot import BaseBot
import chess
import random
import time

class AlanBot(BaseBot):
    def __init__(self):
        super().__init__("Alan", 500)
    
    def get_move(self, board):
        # Simular "pensamiento"
        time.sleep(self.think_time())
        # Bot básico que hace movimientos aleatorios legales
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return None  # No hay movimientos legales disponibles
        
        if any(board.is_capture(move) for move in legal_moves):
            time.sleep(random.uniform(0.5, 1.5))
            
        # Debug: imprimir movimientos disponibles
        print(f"Legal moves for Alan: {[move.uci() for move in legal_moves]}")
        
        selected_move = random.choice(legal_moves)
        print(f"Alan selected move: {selected_move.uci()}")
        
        return selected_move