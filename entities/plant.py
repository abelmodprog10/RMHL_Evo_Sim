from core import config
import random
import math

class Plant:
    def __init__(self):
        self.type = "Plant"
        self.x = 0.0
        self.y = 0.0
        self.world = None
        self.energy_value = config.PLANT_ENERGY_VALUE  # Energy provided when eaten
        self.growth_stage = 1  # Could be used for plant growth mechanics
        self.age = 0  # Track how long plant has been alive
        self.size = random.uniform(3, 8)  # Variable plant size
        self.spread_radius = config.PLANT_SPREAD_RADIUS  # How far plants can spread
    
    def step(self):
        # Plants age each step
        self.age += 1
        
        # Plants grow slightly over time (affects visual size and energy value)
        if self.age % 10 == 0 and self.growth_stage < 3:
            self.growth_stage += 1
            self.size = min(self.size + 1, 10)
            self.energy_value = int(self.energy_value * 1.2)
        
        # Chance to spread/reproduce if mature enough
        if self.age > config.PLANT_MATURITY_AGE and random.random() < config.PLANT_SPREAD_CHANCE:
            self.attempt_spread()
    
    def attempt_spread(self):
        """Try to spread to a nearby area in continuous space"""
        existing_plants = self.world.get_all_entities_by_type("Plant") if self.world else []
        
        if not self.world:
            return
        
        # Try multiple spread attempts
        if len(existing_plants) >= config.MAX_PLANTS:
            return
        for _ in range(3):  # Try up to 3 times
            # Random direction and distance
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(self.spread_radius * 0.5, self.spread_radius)
            
            new_x = self.x + math.cos(angle) * distance
            new_y = self.y + math.sin(angle) * distance
            
            # Handle world wrapping
            new_x = new_x % self.world.width
            new_y = new_y % self.world.height
            
            # Check if the area is relatively empty (small radius to avoid overcrowding)
            if not self.world.is_occupied(new_x, new_y, radius=8):
                # Create new plant
                new_plant = Plant()
                try:
                    self.world.add_entity(new_plant, new_x, new_y)
                    #print(f"Plant spread from ({self.x:.1f},{self.y:.1f}) to ({new_x:.1f},{new_y:.1f})")
                    break  # Only spread once per attempt
                except (ValueError, RuntimeError):
                    # Area became occupied or world is full
                    continue
    
    def get_display_size(self):
        """Get size for display purposes"""
        base_size = 4
        growth_bonus = (self.growth_stage - 1) * 2
        size_variation = (self.size - 5) * 0.5  # Normalize around size 5
        return max(2, int(base_size + growth_bonus + size_variation))
    
    def get_energy_value(self):
        """Get current energy value (may change as plant grows)"""
        return self.energy_value
    
    def can_be_eaten(self):
        """Check if plant can be eaten (always true for basic plants)"""
        return True
    
    def on_eaten(self):
        """Called when plant is eaten - could trigger special effects"""
        pass  # Basic plants don't do anything special when eaten