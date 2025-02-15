import chess
import random
from abc import ABC, abstractmethod

class BaseBot(ABC):
    def __init__(self, name, elo):
        self.name = name
        self.elo = elo
    
    @abstractmethod
    def get_move(self, board):
        """Debe retornar un movimiento válido para la posición actual"""
        pass