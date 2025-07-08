import math
from core import config
from entities.agent import Agent

class Prey(Agent):
    def __init__(self, genome=None):
        super().__init__(genome)
        self.type = "Prey"
        self.energy = config.MAX_ENERGY // 2
        self.health = 100

    def step(self):
        # Check if world is set before trying to access it
        if self.world is None:
            return
        
        # Call parent step method to handle energy loss, damage, reproduction, and movement
        super().step()
        
        # If the agent died from energy depletion or other causes, don't continue
        if self.world is None:
            return
        
        # Look for food at current position
        self.look_for_food()

    def look_for_food(self):
        """Look for plants within vision range and eat them"""
        vision_range = 15
        eating_range = 8

        # Find nearby plants
        nearby_entities = self.world.get_entities_in_radius(self.x, self.y, vision_range)
        plants = [e for e in nearby_entities if getattr(e, 'type', None) == "Plant"]

        if not plants:
            return

        # Find the closest plant
        closest_plant = min(plants, key=lambda p: math.hypot(p.x - self.x, p.y - self.y))
        distance = math.hypot(closest_plant.x - self.x, closest_plant.y - self.y)

        if distance <= eating_range:
            food_value = getattr(closest_plant, 'energy_value', config.PLANT_ENERGY_VALUE)
            self.eat(food_value)
            self.world.remove_entity(closest_plant)