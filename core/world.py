from collections import defaultdict
from random import randint, uniform
import random
import re
import math
from core import config
from entities.plant import Plant

class World:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.spatial_hash = {}  # For efficient spatial queries
        self.step_count = 0
        self.grid_size = 20  # Size of spatial hash grid cells
        self.entities = []
        self.entities_by_type = defaultdict(list)

    def _get_grid_key(self, x, y):
        """Get the grid key for spatial hashing"""
        grid_x = int(x // self.grid_size)
        grid_y = int(y // self.grid_size)
        return (grid_x, grid_y)

    def _add_to_spatial_hash(self, entity):
        """Add entity to spatial hash"""
        key = self._get_grid_key(entity.x, entity.y)
        if key not in self.spatial_hash:
            self.spatial_hash[key] = []
        self.spatial_hash[key].append(entity)

    def _remove_from_spatial_hash(self, entity):
        """Remove entity from spatial hash"""
        key = self._get_grid_key(entity.x, entity.y)
        if key in self.spatial_hash and entity in self.spatial_hash[key]:
            self.spatial_hash[key].remove(entity)
            if not self.spatial_hash[key]:
                del self.spatial_hash[key]

    def _update_spatial_hash(self, entity, old_x, old_y):
        """Update entity position in spatial hash"""
        old_key = self._get_grid_key(old_x, old_y)
        new_key = self._get_grid_key(entity.x, entity.y)
        
        if old_key != new_key:
            # Remove from old position
            if old_key in self.spatial_hash and entity in self.spatial_hash[old_key]:
                self.spatial_hash[old_key].remove(entity)
                if not self.spatial_hash[old_key]:
                    del self.spatial_hash[old_key]
            
            # Add to new position
            if new_key not in self.spatial_hash:
                self.spatial_hash[new_key] = []
            self.spatial_hash[new_key].append(entity)

    def is_occupied(self, x, y, radius=5, exclude_entity=None):
        entities = self.get_entities_in_radius(x, y, radius)
        if exclude_entity:
            entities = [e for e in entities if e != exclude_entity]
        return len(entities) > 0


    def add_entity(self, entity, x=None, y=None):
        """Add entity to world at specified or random position"""
        
        # Check population limits for prey and predators
        if entity.type == "Prey" and len(self.entities_by_type.get("Prey", [])) >= config.MAX_PREY:
            return False  # Don't add if at max capacity
        elif entity.type == "Predator" and len(self.entities_by_type.get("Predator", [])) >= config.MAX_PREDATORS:
            return False  # Don't add if at max capacity
        
        if x is None or y is None:
            # Try random positions until finding an unoccupied one
            attempts = 0
            while attempts < 1000:
                x_try = uniform(0, self.width)
                y_try = uniform(0, self.height)
                if not self.is_occupied(x_try, y_try):
                    x, y = x_try, y_try
                    break
                attempts += 1
            
            if attempts >= 1000:
                raise RuntimeError("Could not find an empty space to add entity.")
        
        # Ensure position is within bounds
        x = max(0, min(self.width, x))
        y = max(0, min(self.height, y))
        
        entity.x = x
        entity.y = y
        entity.world = self
        self.entities.append(entity)
        self.entities_by_type[entity.type].append(entity)  # Add to type dict
        self._add_to_spatial_hash(entity)
        
        return True  # Successfully added

    def remove_entity(self, entity):
        if entity in self.entities:
            self.entities.remove(entity)
            self.entities_by_type[entity.type].remove(entity)  # Remove from type dict
            self._remove_from_spatial_hash(entity)
            entity.world = None

    def move_entity(self, entity, new_x, new_y):
        """Move entity to new position with wrapping"""
        old_x, old_y = entity.x, entity.y
        
        # Handle wrapping
        new_x = new_x % self.width
        new_y = new_y % self.height
        
        # Check if target position is occupied
        if self.is_occupied(new_x, new_y, radius=0.01):
            return False
        
        entity.x = new_x
        entity.y = new_y
        self._update_spatial_hash(entity, old_x, old_y)
        return True

    def get_entities_in_radius(self, x, y, radius):
        """Get all entities within radius of (x,y)"""
        entities = []
        
        # Check multiple grid cells around the point
        grid_radius = int(radius // self.grid_size) + 1
        center_key = self._get_grid_key(x, y)
        
        for dx in range(-grid_radius, grid_radius + 1):
            for dy in range(-grid_radius, grid_radius + 1):
                key = (center_key[0] + dx, center_key[1] + dy)
                if key in self.spatial_hash:
                    for entity in self.spatial_hash[key]:
                        distance = math.sqrt((entity.x - x)**2 + (entity.y - y)**2)
                        if distance <= radius:
                            entities.append(entity)
        
        return entities

    def get_nearest_entities(self, entity, entity_type=None, count=5, max_distance=50):
        """Get nearest entities of specified type"""
        candidates = self.get_entities_in_radius(entity.x, entity.y, max_distance)
        
        # Filter by type if specified
        if entity_type:
            candidates = [e for e in candidates if hasattr(e, 'type') and e.type == entity_type]
        
        # Remove self from candidates
        candidates = [e for e in candidates if e != entity]
        
        # Sort by distance
        candidates.sort(key=lambda e: math.sqrt((e.x - entity.x)**2 + (e.y - entity.y)**2))
        
        return candidates[:count]

    def get_all_entities_by_type(self, entity_type):
        return self.entities_by_type.get(entity_type, [])
    def step(self):
        """Advance world simulation by one step"""
        self.step_count += 1
        # Let all entities step (make a copy to avoid modification during iteration)
        for entity in self.entities[:]:
            if hasattr(entity, 'step'):
                entity.step()

    def get_world_bounds(self):
        """Get world dimensions"""
        return (0, 0, self.width, self.height)
    def compute_trait_averages(self):
        species = {"Prey": [], "Predator": []}
        for entity in self.entities:
            if hasattr(entity, "genome"):
                species.get(entity.type, []).append(entity.genome)

        averages = {}
        for kind, genomes in species.items():
            if not genomes:
                continue
            trait_keys = genomes[0].trait_names
            averages[kind] = {
                trait: sum(g.get_trait(trait) for g in genomes) / len(genomes)
                for trait in trait_keys
            }
        return averages
