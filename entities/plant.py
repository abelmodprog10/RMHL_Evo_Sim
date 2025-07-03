from core import config
from entities.agent import Agent

class Plant(Agent):
    def __init__(self, genome=None):
        super().__init__(genome)
        self.type = "Plant"
        self.energy = config.MAX_ENERGY  # Plants might have max energy by default
        self.health = 150  # maybe plants are tougher?

    def step(self):
        # Example: Plants might grow or spread here later
        pass