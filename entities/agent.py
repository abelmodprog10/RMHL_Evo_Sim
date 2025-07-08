import math
import random
from core import config
from evolution.genome import Genome
from systems import vision
from systems.vision import update_agent_vision, get_vision_data_for_nn
from systems.colour import Colour
from systems.size import Size
class Agent:
    def __init__(self, genome=None):
        self.genome = genome or Genome()  # Use Genome class instead of dict
        self.x = 0
        self.y = 0
        self.energy = config.MAX_ENERGY // 2
        self.energy_cost = 0
        self.health = 100
        self.world = None
        self.type = "Agent"
        self.angle = random.uniform(0, 2 * math.pi)
        self.age = 0
        self.reproduction_count = 0
        self.colour = Colour(self)
        self.size = Size(self)
        self.get_energy_cost()
        self.get_health()
    
    def move_step(self):
        if self.world is None:
            return

        base_speed = getattr(config, f"{self.type.upper()}_SPEED", config.DEFAULT_SPEED)
        base_turn_rate = getattr(config, f"{self.type.upper()}_TURN_RATE", config.DEFAULT_TURN_RATE)

        speed = self.genome.get_modified_value(base_speed, 'speed', 0.5, 2.0)
        turn_rate = self.genome.get_modified_value(base_turn_rate, 'neuroplasticity', 0.5, 1.5)

        self.angle += random.uniform(-turn_rate, turn_rate)

        new_x = self.x + math.cos(self.angle) * speed
        new_y = self.y + math.sin(self.angle) * speed
        self.world.move_entity(self, new_x, new_y)

        # Deduct energy cost (recalculate if speed or size changed this step)
        self.get_energy_cost()
        self.energy -= self.energy_cost


    def step(self):
        self.age += 1
        seen = self.see()
        # energy loss implemented in move_step
        #self.energy -= config.ENERGY_PER_STEP

        # Die if energy is depleted
        if self.energy <= 0:
            self.die()
            return

        # Take damage if energy is low
        if self.energy < config.MAX_ENERGY // 2:
            self.take_damage(1)

        self.reproduce()
        self.move_step()

    def eat(self, food_value):
        # Gain energy from eating, but don't exceed max
        self.energy = min(config.MAX_ENERGY, self.energy + food_value)

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.die()

    def die(self):
        if self.world:
            self.world.remove_entity(self)

    def reproduce(self):
        # Use genome to modify reproduction threshold
        base_threshold = config.MAX_ENERGY * 0.8
        threshold = self.genome.get_modified_value(base_threshold, 'n_children', 0.6, 1.0)
        
        if self.energy < threshold:
            return

        if self.world is None:
            return  # or handle gracefully

        nearby_agents = self.world.get_entities_in_radius(self.x, self.y, config.REPRO_DISTANCE)
        mates = [a for a in nearby_agents if a is not self and a.type == self.type and a.energy >= threshold]

        if not mates:
            return

        mate = random.choice(mates)

        # set chance to reproduce
        if random.random() > config.REPRO_CHANCE:
            return

        # Create child genome using crossover and mutation
        #child_genome = self.genome.crossover(mate.genome).mutate()
        #Try out hybrid crossover
        child_genome = self.genome.crossover_hybrid(mate.genome).mutate()
        child = self.__class__(genome=child_genome)
        child_x = (self.x + mate.x) / 2 #+ random.uniform(-1, 1)
        child_y = (self.y + mate.y) / 2 #+ random.uniform(-1, 1)
        self.world.add_entity(child, child_x, child_y)

        # Reduce parents' energy after reproduction
        reproduction_energy = config.MAX_ENERGY // 3
        self.energy -= reproduction_energy
        mate.energy -= reproduction_energy
        
        # Track reproduction for fitness
        self.reproduction_count += 1
        mate.reproduction_count += 1

        print(f"{self.type} reproduced - Parent1: ({self.x:.1f},{self.y:.1f}), Parent2: ({mate.x:.1f},{mate.y:.1f}), Child: ({child_x:.1f},{child_y:.1f})")
        # In your reproduce() method, add after creating the child:
        print(f"Parent1 color: {self.genome.get_trait('colour'):.3f} -> RGB {self.colour.get_rgb()}")
        print(f"Parent2 color: {mate.genome.get_trait('colour'):.3f} -> RGB {mate.colour.get_rgb()}")
        print(f"Child color: {child_genome.get_trait('colour'):.3f} -> RGB {child.colour.get_rgb()}")

        print(f"Parent1 speed: {self.genome.get_trait('speed')}")
        print(f"Parent2 speed: {mate.genome.get_trait('speed')}")
        print(f"Child speed: {child_genome.get_trait('speed')}")

        # Sizes:
        print(f"Parent1 size: {self.size.get_size()}")
        print(f"Parent2 size: {mate.size.get_size()}")
        print(f"Child size: {child.size.get_size()}")

        # Energy costs (make sure energy_cost is updated before print)
        print(f"Parent1 energy cost: {self.energy_cost:.3f}")
        print(f"Parent2 energy cost: {mate.energy_cost:.3f}")
        print(f"Child energy cost: {child.energy_cost:.3f}")

        """Calculate fitness score for this agent"""
        return self.genome.fitness_score(self.age, self.reproduction_count, self.energy)
    
    def see(self):
        """Get vision data formatted for neural network"""
        update_agent_vision(self)
        return get_vision_data_for_nn(self)
    
    def get_energy_cost(self):
        base_speed = getattr(config, f"{self.type.upper()}_SPEED", config.DEFAULT_SPEED)
        base_size = 6  # Use your base size here or a config dict if available
        
        speed = self.genome.get_modified_value(base_speed, 'speed', 0.5, 2.0)
        size_value = self.size.get_size()
        size_multiplier = size_value / base_size

        speed_multiplier = speed / base_speed
        
        self.energy_cost = config.ENERGY_PER_STEP * speed_multiplier * size_multiplier
    def get_health(self):
        """Returns the size-adjusted health value"""
        base_health = self.health  # the class-specific base health set in __init__
        base_size = 6
        current_size = self.size.get_size()
        size_multiplier = current_size / base_size
        return int(base_health * size_multiplier)
