from core import config
from entities.agent import Agent
import random

class Predator(Agent):
    def __init__(self, genome=None):
        super().__init__(genome)
        self.type = "Predator"
        self.energy = config.MAX_ENERGY // 2
        self.health = 120  # maybe predators have more health?

    def step(self):
        dx, dy = random.choice(self.directions)
        new_x = self.x + dx
        new_y = self.y + dy
        # Check boundaries
        if 0 <= new_x < self.world.width and 0 <= new_y < self.world.height:
            if not self.world.get_entities_at(new_x, new_y):
                self.world.move_entity(self, new_x, new_y)