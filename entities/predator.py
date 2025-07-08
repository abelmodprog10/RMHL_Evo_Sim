import math
from core import config
from entities.agent import Agent

class Predator(Agent):
    def __init__(self, genome=None):
        super().__init__(genome)
        self.type = "Predator"
        self.energy = config.MAX_ENERGY // 2
        self.health = 150  # Predators might have higher base health

    def step(self):
        if self.world is None:
            return

        # Call parent step method to handle energy loss, damage, reproduction, movement, and vision
        super().step()

        # If the agent died from energy depletion or other causes, don't continue
        if self.world is None:
            return

        # Hunt for prey at current position
        self.hunt_prey()

    def hunt_prey(self):
        hunt_range = 15
        prey_list = [
            e for e in self.world.get_entities_in_radius(self.x, self.y, hunt_range)
            if getattr(e, 'type', None) == "Prey"
        ]

        if not prey_list:
            return

        closest_prey = min(prey_list, key=lambda p: math.hypot(p.x - self.x, p.y - self.y))
        closest_prey.take_damage(50)

        if closest_prey.world is None:  # Prey died from the attack
            self.eat(config.PREY_ENERGY_VALUE)