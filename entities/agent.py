# your_sim/entities/agent.py
from core import config

class Agent:
    directions = [
        (0,1), (0,-1), (1,0), (-1,0),
        (1,1), (-1,-1), (1,-1), (-1,1)
    ]
    def __init__(self, genome=None):
        self.genome = genome or config.GENOME_DEFAULTS.copy()
        self.x = 0
        self.y = 0
        self.energy = config.MAX_ENERGY // 2
        self.hunger = 0
        self.health = 100

    def step(self):
        
        pass
