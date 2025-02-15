# bots/elena.py
from .base_bot import BaseBot
import chess

class ElenaBot(BaseBot):
    def __init__(self):
        super().__init__("Elena", 1300)
    
    def get_move(self, board):
        # Bot intermedio que evalúa capturas y jaque
        best_move = None
        best_score = float('-inf')
        
        for move in board.legal_moves:
            score = 0
            # Priorizar capturas
            if board.is_capture(move):
                score += 10
            # Priorizar jaques
            board.push(move)
            if board.is_check():
                score += 5
            board.pop()
            
            if score > best_score:
                best_score = score
                best_move = move
        
        return best_move or list(board.legal_moves)[0]