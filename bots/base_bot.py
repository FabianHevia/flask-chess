# bots/base_bot.py
import chess
import random
import time
from abc import ABC, abstractmethod

class BaseBot(ABC):
    def __init__(self, name, elo):
        self.name = name
        self.elo = elo
    
    def think_time(self):
        """
        Calcula el tiempo de pensamiento basado en el ELO.
        Bots más fuertes "piensan" más consistentemente.
        """
        base_time = 1.0  # tiempo base en segundos
        
        if self.elo < 1000:  # Bot principiante (Alan)
            return random.uniform(0.5, 2.5)
        elif self.elo < 1500:  # Bot intermedio (Elena)
            return random.uniform(1.0, 3.0)
        else:  # Bot avanzado (Ricardo)
            return random.uniform(2.0, 4.0)
    
    @abstractmethod
    def get_move(self, board):
        pass