from .alan import AlanBot
from .elena import ElenaBot
from .ricardo import RicardoBot

def load_bots():
    return {
        'alan': AlanBot(),
        'elena': ElenaBot(),
        'ricardo': RicardoBot()
    }