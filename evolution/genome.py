import random
from core import config

class Genome:
    """
    Represents the genetic makeup of an agent.
    Each trait is a value between 0.0 and 1.0 that affects agent behavior.
    """
    
    def __init__(self, traits=None):
        # Define the traits that make up the genome
        self.trait_names = [
            'n_eyes',
            'eye_pos',
            'n_legs',
            'brain_size',
            'speed',
            'n_children',
            'neuroplasticity',
            'size',
            'colour'

        ]
        if traits is None:
            # Generate random traits
            self.traits = {trait: random.random() for trait in self.trait_names}
        else:
            # Use provided traits
            self.traits = traits.copy()

    def get_trait(self, trait_name):
        """Get a specific trait value"""
        return self.traits.get(trait_name, 0.5)  # Fixed: default to 0.5 if not found
    
    def set_trait(self, trait_name, value):
        """Set a specific trait value (clamp between 0 and 1)"""
        self.traits[trait_name] = max(0.0, min(1.0, value))
    
    def mutate(self, mutation_rate=0.1, mutation_strength=0.1):
        """
        Mutate the genome by randomly changing traits
        mutation_rate: probability of each trait mutating
        mutation_strength: how much traits can change
        """
        new_traits = self.traits.copy()
        
        for trait_name in self.trait_names:
            if random.random() < mutation_rate:
                # Apply mutation
                current_value = new_traits[trait_name]
                mutation = random.uniform(-mutation_strength, mutation_strength)
                new_value = current_value + mutation
                
                # Clamp to valid range
                new_traits[trait_name] = max(0.0, min(1.0, new_value))
        
        return Genome(new_traits)
    
    def crossover(self, other_genome):
        """
        Create offspring genome by combining traits from two parents
        """
        new_traits = {}
        
        for trait_name in self.trait_names:
            # Randomly choose trait from either parent
            if random.random() < 0.5:
                new_traits[trait_name] = self.traits[trait_name]
            else:
                new_traits[trait_name] = other_genome.traits[trait_name]
            
            # Optional: blend traits instead of choosing
            # new_traits[trait_name] = (self.traits[trait_name] + other_genome.traits[trait_name]) / 2
        
        return Genome(new_traits)
    
    def crossover_hybrid(self, other_genome):
        """
        Hybrid approach: blend most traits, but randomly select some
        More realistic biological reproduction
        """
        new_traits = {}
        
        for trait_name in self.trait_names:
            if random.random() < 0.3:  # 30% chance of random selection
                if random.random() < 0.5:
                    new_traits[trait_name] = self.traits[trait_name]
                else:
                    new_traits[trait_name] = other_genome.traits[trait_name]
            else:  # 70% chance of blending
                new_traits[trait_name] = (self.traits[trait_name] + other_genome.traits[trait_name]) / 2
        
        return Genome(new_traits)
    
    def fitness_score(self, age, reproduction_count, energy_level):
        """
        Calculate fitness based on survival metrics
        Higher fitness = better genes
        """
        # Basic fitness calculation - can be expanded
        survival_bonus = age * 0.1
        reproduction_bonus = reproduction_count * 5
        energy_bonus = energy_level * 0.01
        
        # Size trait affects fitness (medium size is optimal)
        size_penalty = abs(self.traits['size'] - 0.5) * 2
        
        return survival_bonus + reproduction_bonus + energy_bonus - size_penalty
    
    def get_modified_value(self, base_value, trait_name, min_multiplier=0.5, max_multiplier=1.5):
        """
        Modify a base value using a trait
        trait of 0.0 = min_multiplier * base_value
        trait of 1.0 = max_multiplier * base_value
        trait of 0.5 = base_value
        """
        trait_value = self.get_trait(trait_name)
        multiplier = min_multiplier + (max_multiplier - min_multiplier) * trait_value
        return base_value * multiplier
    
    def __str__(self):
        """String representation of the genome"""
        trait_strs = []
        for trait_name in self.trait_names:
            value = self.traits[trait_name]
            trait_strs.append(f"{trait_name}: {value:.2f}")
        return f"Genome({', '.join(trait_strs)})"
    
    def to_dict(self):
        """Convert genome to dictionary for saving/loading"""
        return self.traits.copy()
    
    @classmethod
    def from_dict(cls, trait_dict):
        """Create genome from dictionary"""
        return cls(trait_dict)