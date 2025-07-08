import math
class Size:
    def __init__(self, agent, base_size=5, scale_range=(0.5, 1.5)):
        self.agent = agent
        self.base_size = base_size
        self.scale_range = scale_range

    def get_trait_value(self):
        if hasattr(self.agent, 'genome') and hasattr(self.agent.genome, 'get_trait'):
            trait = self.agent.genome.get_trait('size')
            return trait if trait is not None else 0.5
        return 0.5  # default if no genome or trait

    def get_size(self):
        trait = self.get_trait_value()
        min_scale, max_scale = self.scale_range
        scale = min_scale + trait * (max_scale - min_scale)
        return int(self.base_size * scale)
    def get_health_modifier(self):
        if not hasattr(self.agent, 'size'):
            return 1.0  # default if no size info
        
        size = self.agent.size.get_size()
        base_size = 6  # or get it from your entity_sizes dict for this agent type
        base_radius = base_size / 2
        base_area = math.pi * (base_radius ** 2)
        
        radius = size / 2
        area = math.pi * (radius ** 2)
        
        modifier = area / base_area
        
        return max(0.1, modifier)
